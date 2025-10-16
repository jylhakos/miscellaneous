"""
Advanced LLM OCR Script - Using transformers with CNN and BERT
This script combines CNN for visual feature extraction, OCR for text extraction,
and BERT for contextual understanding of extracted text.
"""

import os
import sys
from pathlib import Path
import torch
import numpy as np
from PIL import Image
import pytesseract
import json

# Check if transformers is available
try:
    from transformers import (
        BertTokenizer, 
        BertModel,
        ViTImageProcessor, 
        ViTModel
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers library not available. Install with: pip install transformers")


class CNNBERTOCRProcessor:
    """Process images using CNN + OCR + BERT for advanced understanding."""
    
    def __init__(self, use_gpu=False):
        """
        Initialize the CNN+BERT OCR processor.
        
        Args:
            use_gpu (bool): Use GPU if available
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is required. Install with: pip install transformers")
        
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Initialize Vision Transformer (ViT) for image feature extraction
        print("Loading Vision Transformer model...")
        self.vit_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.vit_model = ViTModel.from_pretrained('google/vit-base-patch16-224')
        self.vit_model.to(self.device)
        self.vit_model.eval()
        
        # Initialize BERT for text understanding
        print("Loading BERT model...")
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.bert_model.to(self.device)
        self.bert_model.eval()
        
        print("Models loaded successfully")
    
    def extract_visual_features(self, image_path):
        """
        Extract visual features using Vision Transformer (CNN alternative).
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Visual feature vector
        """
        print(f"Extracting visual features from: {image_path}")
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        inputs = self.vit_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Extract features
        with torch.no_grad():
            outputs = self.vit_model(**inputs)
            # Get the last hidden state (CLS token representation)
            features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return features[0]
    
    def extract_text_ocr(self, image_path):
        """
        Extract text using Tesseract OCR.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text
        """
        print(f"Extracting text with OCR from: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    
    def extract_text_features(self, text):
        """
        Extract contextual features from text using BERT.
        
        Args:
            text (str): Input text
            
        Returns:
            numpy.ndarray: Text feature vector
        """
        if not text:
            print("Warning: No text to process")
            return np.zeros(768)  # Return zero vector
        
        print("Extracting text features with BERT...")
        
        # Tokenize and encode text
        inputs = self.bert_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Extract features
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            # Get the CLS token representation
            features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return features[0]
    
    def process_image_multimodal(self, image_path, output_path=None):
        """
        Process image using multimodal approach (Visual + Text features).
        
        Args:
            image_path (str): Path to the image file
            output_path (str, optional): Path to save results
            
        Returns:
            dict: Multimodal analysis results
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"\nProcessing image: {image_path}")
        print("=" * 50)
        
        # Extract visual features
        visual_features = self.extract_visual_features(image_path)
        print(f"Visual feature vector shape: {visual_features.shape}")
        
        # Extract text with OCR
        extracted_text = self.extract_text_ocr(image_path)
        print(f"Extracted text length: {len(extracted_text)} characters")
        
        # Extract text features
        text_features = self.extract_text_features(extracted_text)
        print(f"Text feature vector shape: {text_features.shape}")
        
        # Combine features (simple concatenation)
        combined_features = np.concatenate([visual_features, text_features])
        print(f"Combined feature vector shape: {combined_features.shape}")
        
        # Analyze text content
        analysis = self._analyze_text_content(extracted_text)
        
        # Compile results
        results = {
            'image_path': image_path,
            'extracted_text': extracted_text,
            'text_analysis': analysis,
            'visual_feature_dim': int(visual_features.shape[0]),
            'text_feature_dim': int(text_features.shape[0]),
            'combined_feature_dim': int(combined_features.shape[0]),
            # Convert numpy arrays to lists for JSON serialization
            'visual_features': visual_features.tolist(),
            'text_features': text_features.tolist(),
            'combined_features': combined_features.tolist()
        }
        
        # Save results
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                # Save without feature vectors for readability
                readable_results = {k: v for k, v in results.items() 
                                  if not k.endswith('_features')}
                json.dump(readable_results, f, indent=2, ensure_ascii=False)
            
            # Save full results with features
            features_path = Path(output_path).with_suffix('.features.json')
            with open(features_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nResults saved to: {output_path}")
            print(f"Features saved to: {features_path}")
        
        return results
    
    def _analyze_text_content(self, text):
        """
        Analyze text content to extract insights.
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Text analysis results
        """
        import re
        
        analysis = {
            'word_count': len(text.split()),
            'character_count': len(text),
            'line_count': len(text.split('\n')),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
            'has_urls': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
            'has_dates': bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)),
        }
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        analysis['numbers_found'] = numbers[:10]  # First 10 numbers
        
        return analysis


def main():
    """Main function to demonstrate CNN+BERT OCR."""
    
    print("=" * 50)
    print("CNN+BERT Multimodal OCR Processor")
    print("=" * 50)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\nError: transformers library is required")
        print("Install with: pip install transformers torch torchvision")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "multimodal_output.json"
        
        use_gpu = '--gpu' in sys.argv
        
        try:
            processor = CNNBERTOCRProcessor(use_gpu=use_gpu)
            
            # Process image
            results = processor.process_image_multimodal(input_file, output_file)
            
            # Print summary
            print("\n" + "=" * 50)
            print("ANALYSIS SUMMARY")
            print("=" * 50)
            print(f"Extracted text length: {results['text_analysis']['character_count']} characters")
            print(f"Word count: {results['text_analysis']['word_count']}")
            print(f"Line count: {results['text_analysis']['line_count']}")
            print(f"Has numbers: {results['text_analysis']['has_numbers']}")
            print(f"Has emails: {results['text_analysis']['has_emails']}")
            print(f"Has dates: {results['text_analysis']['has_dates']}")
            
            print("\n--- Extracted Text (Preview - First 300 characters) ---")
            print(results['extracted_text'][:300])
            if len(results['extracted_text']) > 300:
                print(f"\n... ({len(results['extracted_text']) - 300} more characters)")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input_image> [output_json] [--gpu]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} document.jpg analysis.json")
        print(f"  python {sys.argv[0]} invoice.png output.json --gpu")
        print("\nOptions:")
        print("  --gpu    Use GPU acceleration (requires CUDA)")
        print("\nNote: This script requires:")
        print("  - transformers library (pip install transformers)")
        print("  - PyTorch (pip install torch torchvision)")
        print("  - Tesseract OCR (sudo apt-get install tesseract-ocr)")


if __name__ == "__main__":
    main()
