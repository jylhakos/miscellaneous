#!/usr/bin/env python3
"""
Fine-tune Arcee Agent model on function calling dataset

This script provides LoRA-based fine-tuning for the Arcee Agent model
using your custom function calling dataset.

Requirements:
- NVIDIA GPU with 16GB+ VRAM
- CUDA toolkit installed
- transformers, peft, bitsandbytes packages

Usage:
    python fine_tune_arcee.py --dataset_path ./dataset --output_dir ./fine_tuned_model
"""

import torch
import argparse
import json
import os
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from datasets import load_from_disk
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gpu():
    """Check if GPU is available and suitable for training."""
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Fine-tuning requires GPU.")
    
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory: {gpu_memory:.1f} GB")
    
    if gpu_memory < 15:
        logger.warning("GPU has less than 16GB memory. Training may fail or be very slow.")
    
    return True

def prepare_training_data(dataset, tokenizer, max_length=2048):
    """Prepare dataset for fine-tuning."""
    
    def format_training_example(example):
        """Format each example for training."""
        try:
            query = example['query']
            tools = json.loads(example['tools']) if isinstance(example['tools'], str) else example['tools']
            answers = json.loads(example['answers']) if isinstance(example['answers'], str) else example['answers']
            
            # Create the training prompt
            tools_str = json.dumps(tools, indent=2)
            prompt = f"""You are an AI assistant with access to the following tools:

{tools_str}

Based on the user's query, determine which tool(s) to call and with what arguments.
Your response should be a JSON array of tool calls in the format:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

User Query: {query}

Tool Calls: {json.dumps(answers)}"""
            
            return {"text": prompt}
        except Exception as e:
            logger.warning(f"Error formatting example: {e}")
            return {"text": ""}
    
    # Format the dataset
    logger.info("Formatting dataset for training...")
    formatted_dataset = dataset.map(format_training_example)
    
    # Filter out empty examples
    formatted_dataset = formatted_dataset.filter(lambda x: len(x["text"]) > 0)
    
    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
    
    logger.info("Tokenizing dataset...")
    tokenized_dataset = formatted_dataset.map(
        tokenize_function, 
        batched=True, 
        remove_columns=formatted_dataset.column_names
    )
    
    return tokenized_dataset

def setup_model_and_tokenizer(model_name, use_quantization=True):
    """Set up model and tokenizer for training."""
    logger.info(f"Loading model: {model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    model_kwargs = {
        "trust_remote_code": True,
        "device_map": "auto",
    }
    
    if use_quantization:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        model_kwargs["quantization_config"] = bnb_config
        logger.info("Using 4-bit quantization for training")
    else:
        model_kwargs["torch_dtype"] = torch.float16
    
    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    
    return model, tokenizer

def setup_lora_config():
    """Configure LoRA for efficient fine-tuning."""
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    
    logger.info("LoRA configuration:")
    logger.info(f"  Rank (r): {lora_config.r}")
    logger.info(f"  Alpha: {lora_config.lora_alpha}")
    logger.info(f"  Dropout: {lora_config.lora_dropout}")
    logger.info(f"  Target modules: {lora_config.target_modules}")
    
    return lora_config

def main():
    parser = argparse.ArgumentParser(description="Fine-tune Arcee Agent model")
    parser.add_argument("--dataset_path", default="./dataset", help="Path to dataset")
    parser.add_argument("--output_dir", default="./fine_tuned_arcee_agent", help="Output directory")
    parser.add_argument("--model_name", default="arcee-ai/Arcee-Agent", help="Model name")
    parser.add_argument("--max_length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=1, help="Training batch size")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--no_quantization", action="store_true", help="Disable 4-bit quantization")
    parser.add_argument("--eval_split", type=float, default=0.2, help="Evaluation split ratio")
    
    args = parser.parse_args()
    
    # Check prerequisites
    check_gpu()
    
    # Load dataset
    logger.info(f"Loading dataset from {args.dataset_path}")
    try:
        dataset = load_from_disk(args.dataset_path)
        logger.info(f"Dataset loaded with {len(dataset)} examples")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return 1
    
    # Setup model and tokenizer
    try:
        model, tokenizer = setup_model_and_tokenizer(
            args.model_name, 
            use_quantization=not args.no_quantization
        )
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return 1
    
    # Setup LoRA
    lora_config = setup_lora_config()
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
    
    # Prepare training data
    train_dataset = prepare_training_data(dataset, tokenizer, args.max_length)
    
    # Split dataset
    train_size = int((1 - args.eval_split) * len(train_dataset))
    train_ds = train_dataset.select(range(train_size))
    eval_ds = train_dataset.select(range(train_size, len(train_dataset)))
    
    logger.info(f"Training samples: {len(train_ds)}")
    logger.info(f"Evaluation samples: {len(eval_ds)}")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_steps=100,
        learning_rate=args.learning_rate,
        fp16=True,
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=100,
        save_total_limit=3,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        report_to=None,  # Disable wandb logging by default
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds if len(eval_ds) > 0 else None,
        data_collator=data_collator,
    )
    
    # Start training
    logger.info("Starting fine-tuning...")
    try:
        trainer.train()
        
        # Save the fine-tuned model
        trainer.save_model(args.output_dir)
        tokenizer.save_pretrained(args.output_dir)
        
        logger.info(f"Fine-tuning completed! Model saved to {args.output_dir}")
        
        # Save training info
        training_info = {
            "model_name": args.model_name,
            "dataset_size": len(dataset),
            "train_size": len(train_ds),
            "eval_size": len(eval_ds),
            "num_epochs": args.num_epochs,
            "learning_rate": args.learning_rate,
            "batch_size": args.batch_size,
            "max_length": args.max_length,
            "lora_config": {
                "r": lora_config.r,
                "alpha": lora_config.lora_alpha,
                "dropout": lora_config.lora_dropout,
                "target_modules": lora_config.target_modules
            }
        }
        
        with open(os.path.join(args.output_dir, "training_info.json"), "w") as f:
            json.dump(training_info, f, indent=2)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
