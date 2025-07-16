#!/usr/bin/env python3
"""
Arcee Agent Function Calling Implementation

This script demonstrates how to use the Arcee Agent model for function calling
and tool use with a dataset containing queries, tools, and expected answers.

Usage:
    # For VLLM OpenAI compatible server
    poetry run python main.py --model arcee-ai/Arcee-Agent --base_url http://127.0.0.1:8000/v1 --api_key dummy
    
    # For local quantized model
    poetry run python main.py --model arcee-agent-local --use_local_model --model_path ./models/arcee-agent-q4_k_m.gguf
"""

from openai import OpenAI
import argparse
import datasets
import json
import os
import sys
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_function_calling_prompt(query: str, tools: List[Dict[str, Any]]) -> str:
    """
    Create a function calling prompt for the Arcee Agent model.
    
    Args:
        query: User query
        tools: List of available tools with their descriptions and parameters
        
    Returns:
        Formatted prompt for function calling
    """
    tools_str = json.dumps(tools, indent=2)
    
    prompt = f"""You are an AI assistant with access to the following tools:

{tools_str}

Based on the user's query, determine which tool(s) to call and with what arguments.
Your response should be a JSON array of tool calls in the format:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

User Query: {query}

Tool Calls:"""
    
    return prompt


def parse_tool_calls(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse the model response to extract tool calls.
    
    Args:
        response_text: Raw response from the model
        
    Returns:
        List of tool calls or empty list if parsing fails
    """
    try:
        # Try to find JSON in the response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx == -1 or end_idx == 0:
            # Look for single tool call format
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                tool_call = json.loads(json_str)
                return [tool_call]
            return []
            
        json_str = response_text[start_idx:end_idx]
        tool_calls = json.loads(json_str)
        
        # Validate the format
        if isinstance(tool_calls, list):
            for call in tool_calls:
                if not isinstance(call, dict) or 'name' not in call:
                    logger.warning(f"Invalid tool call format: {call}")
                    return []
            return tool_calls
        elif isinstance(tool_calls, dict) and 'name' in tool_calls:
            return [tool_calls]
            
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        logger.warning(f"Response text: {response_text}")
    except Exception as e:
        logger.warning(f"Unexpected error parsing tool calls: {e}")
    
    return []


def validate_dataset_row(row: Dict[str, Any]) -> bool:
    """
    Validate if a dataset row has all required fields.
    
    Args:
        row: Dataset row
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['query', 'tools']
    for field in required_fields:
        if field not in row or not row[field]:
            logger.warning(f"Missing or empty field '{field}' in row")
            return False
    
    try:
        # Validate tools field is valid JSON
        if isinstance(row['tools'], str):
            json.loads(row['tools'])
        return True
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in tools field: {row['tools']}")
        return False


def process_dataset(
    ds: datasets.Dataset, 
    model: str, 
    base_url: str, 
    api_key: str,
    use_local_model: bool = False,
    model_path: Optional[str] = None,
    max_samples: Optional[int] = None
) -> datasets.Dataset:
    """
    Process the dataset and generate tool calls using the Arcee Agent model.
    
    Args:
        ds: Input dataset
        model: Model name
        base_url: Base URL for the API
        api_key: API key
        use_local_model: Whether to use a local quantized model
        model_path: Path to local model file
        max_samples: Maximum number of samples to process (for testing)
        
    Returns:
        Dataset with added 'my_answers' column containing tool calls
    """
    logger.info(f"Processing dataset with {len(ds)} rows")
    
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))
        logger.info(f"Limited processing to {len(ds)} samples")
    
    # Initialize the OpenAI client (works with VLLM OpenAI-compatible server)
    if not use_local_model:
        client = OpenAI(base_url=base_url, api_key=api_key)
    else:
        # For local model, you would need to implement a local inference method
        # This is a placeholder - in practice you'd use llama-cpp-python or similar
        logger.warning("Local model inference not fully implemented in this example")
        client = OpenAI(base_url=base_url, api_key=api_key)

    my_answers = []
    processed_count = 0
    error_count = 0

    # Process each row in the dataset
    for i, (query, tools_str) in enumerate(zip(ds["query"], ds["tools"])):
        try:
            # Validate the row
            row = {'query': query, 'tools': tools_str}
            if not validate_dataset_row(row):
                logger.warning(f"Skipping invalid row {i}")
                my_answers.append("[]")  # Empty tool calls for invalid rows
                continue
            
            # Parse tools from JSON string
            if isinstance(tools_str, str):
                tools = json.loads(tools_str)
            else:
                tools = tools_str
            
            # Create the function calling prompt
            prompt = create_function_calling_prompt(query, tools)
            
            # Call the Arcee Agent model
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that excels at function calling. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=model,
                temperature=0.1,  # Low temperature for more consistent function calling
                max_tokens=512,
            )
            
            response_text = response.choices[0].message.content
            logger.debug(f"Model response for query {i}: {response_text}")
            
            # Parse the tool calls from the response
            tool_calls = parse_tool_calls(response_text)
            
            # Convert to JSON string format expected by the dataset
            answer = json.dumps(tool_calls)
            my_answers.append(answer)
            
            processed_count += 1
            
            if processed_count % 5 == 0:
                logger.info(f"Processed {processed_count}/{len(ds)} samples")
                
        except Exception as e:
            logger.error(f"Error processing row {i}: {e}")
            error_count += 1
            # Add empty tool calls for errors
            my_answers.append("[]")
    
    # Validate the length of the new column data equals number of rows in the dataset
    ds_length = len(ds)
    my_answers_length = len(my_answers)
    
    if my_answers_length != ds_length:
        fill_length = ds_length - my_answers_length
        logger.warning(f"Filling {fill_length} missing answers with empty tool calls")
        for _ in range(fill_length):
            my_answers.append("[]")

    logger.info(f"Processing complete. Successfully processed: {processed_count}, Errors: {error_count}")
    
    # Add new column 'my_answers' with the generated tool calls to the dataset
    return ds.add_column("my_answers", my_answers)

def download_quantized_model(model_path: str) -> bool:
    """
    Download the quantized Arcee Agent model if it doesn't exist.
    
    Args:
        model_path: Path where to save the model
        
    Returns:
        True if successful, False otherwise
    """
    if os.path.exists(model_path):
        logger.info(f"Model already exists at {model_path}")
        return True
    
    try:
        from huggingface_hub import hf_hub_download
        
        # Create models directory
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        logger.info("Downloading quantized Arcee Agent model...")
        # Download from the quantized repository
        downloaded_path = hf_hub_download(
            repo_id="crusoeai/Arcee-Agent-GGUF",
            filename="arcee-agent-q4_k_m.gguf",  # ~4.3GB quantized model
            local_dir="./models",
            local_dir_use_symlinks=False
        )
        
        logger.info(f"Model downloaded to {downloaded_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False


def evaluate_predictions(ds: datasets.Dataset) -> Dict[str, float]:
    """
    Evaluate the model predictions against ground truth answers.
    
    Args:
        ds: Dataset with 'answers' and 'my_answers' columns
        
    Returns:
        Evaluation metrics
    """
    if 'answers' not in ds.column_names or 'my_answers' not in ds.column_names:
        logger.warning("Cannot evaluate: missing answers or my_answers column")
        return {}
    
    correct_tools = 0
    correct_args = 0
    total_samples = 0
    
    for i, (ground_truth, prediction) in enumerate(zip(ds['answers'], ds['my_answers'])):
        try:
            gt_calls = json.loads(ground_truth) if isinstance(ground_truth, str) else ground_truth
            pred_calls = json.loads(prediction) if isinstance(prediction, str) else prediction
            
            total_samples += 1
            
            # Check if tool names match
            gt_tools = {call.get('name', '') for call in gt_calls}
            pred_tools = {call.get('name', '') for call in pred_calls}
            
            if gt_tools == pred_tools:
                correct_tools += 1
                
                # Check if arguments match (simplified check)
                if gt_calls == pred_calls:
                    correct_args += 1
                    
        except Exception as e:
            logger.warning(f"Error evaluating sample {i}: {e}")
    
    if total_samples == 0:
        return {}
    
    return {
        'tool_accuracy': correct_tools / total_samples,
        'exact_match': correct_args / total_samples,
        'total_samples': total_samples
    }


def main():
    """Main function to run the Arcee Agent function calling pipeline."""
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Generate tool calls using Arcee Agent model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using VLLM OpenAI-compatible server
    python main.py --model arcee-ai/Arcee-Agent --base_url http://127.0.0.1:8000/v1
    
    # Using local quantized model
    python main.py --model arcee-agent-local --use_local_model --model_path ./models/arcee-agent-q4_k_m.gguf
    
    # Process only a few samples for testing
    python main.py --model arcee-ai/Arcee-Agent --base_url http://127.0.0.1:8000/v1 --max_samples 5
        """
    )
    
    parser.add_argument("--model", required=True, help="Name of the model to use")
    parser.add_argument(
        "--base_url",
        default="http://127.0.0.1:8000/v1",
        help="Base URL of the inference server (default: http://127.0.0.1:8000/v1)"
    )
    parser.add_argument(
        "--api_key", 
        default="dummy",
        help="API key for the inference server (default: dummy)"
    )
    parser.add_argument(
        "--use_local_model",
        action="store_true",
        help="Use local quantized model instead of API"
    )
    parser.add_argument(
        "--model_path",
        default="./models/arcee-agent-q4_k_m.gguf",
        help="Path to local model file"
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        help="Maximum number of samples to process (for testing)"
    )
    parser.add_argument(
        "--download_model",
        action="store_true",
        help="Download the quantized model before processing"
    )
    parser.add_argument(
        "--dataset_path",
        default="./dataset/",
        help="Path to the dataset directory"
    )
    parser.add_argument(
        "--output_path",
        default="./my_dataset",
        help="Path to save the processed dataset"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate predictions against ground truth"
    )
    
    args = parser.parse_args()
    
    # Download model if requested
    if args.download_model:
        if not download_quantized_model(args.model_path):
            logger.error("Failed to download model. Exiting.")
            sys.exit(1)
    
    # Check if local model exists when using local model
    if args.use_local_model and not os.path.exists(args.model_path):
        logger.error(f"Local model not found at {args.model_path}")
        logger.info("Use --download_model flag to download the quantized model")
        sys.exit(1)
    
    # Load the dataset
    try:
        logger.info(f"Loading dataset from {args.dataset_path}")
        ds = datasets.load_from_disk(args.dataset_path)
        assert isinstance(ds, datasets.Dataset)
        logger.info(f"Loaded dataset with {len(ds)} rows")
        logger.info(f"Dataset columns: {ds.column_names}")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        sys.exit(1)
    
    # Process the dataset and generate tool calls
    try:
        logger.info("Starting dataset processing...")
        submission_ds = process_dataset(
            ds, 
            args.model, 
            args.base_url, 
            args.api_key,
            args.use_local_model,
            args.model_path,
            args.max_samples
        )
        
        logger.info(f"Processed dataset: {submission_ds}")
        
        # Save the resulting dataset
        logger.info(f"Saving processed dataset to {args.output_path}")
        submission_ds.save_to_disk(args.output_path)
        logger.info("Dataset saved successfully")
        
        # Evaluate if ground truth is available
        if args.evaluate and 'answers' in submission_ds.column_names:
            logger.info("Evaluating predictions...")
            metrics = evaluate_predictions(submission_ds)
            if metrics:
                logger.info("Evaluation Results:")
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        logger.info(f"  {metric}: {value:.3f}")
                    else:
                        logger.info(f"  {metric}: {value}")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
