"""
BIM OCR Script - Extract data from Building Information Modeling images
This script processes BIM images (blueprints, floor plans, drawings) and extracts text,
dimensions, and structured data using OCR and machine learning.
"""

import os
import sys
from pathlib import Path
import easyocr
import pytesseract
import cv2
import numpy as np
from PIL import Image
import json
import re


class BIMOCRProcessor:
    """Process BIM images and extract structured data."""
    
    def __init__(self, languages=['en'], gpu=False):
        """
        Initialize the BIM OCR processor.
        
        Args:
            languages (list): List of language codes (default: ['en'])
            gpu (bool): Use GPU acceleration if available (default: False)
        """
        print(f"Initializing EasyOCR with languages: {languages}")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        print("BIM OCR Processor initialized successfully")
    
    def preprocess_image(self, image_path):
        """
        Preprocess BIM image for better OCR results.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        print(f"Preprocessing image: {image_path}")
        
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # Edge detection for structure
        edges = cv2.Canny(denoised, 50, 150)
        
        return img, gray, binary, denoised, edges
    
    def extract_text_with_positions(self, image_path):
        """
        Extract text along with bounding box positions.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            list: List of detected text with positions and confidence
        """
        print(f"Extracting text with positions from: {image_path}")
        result = self.reader.readtext(image_path)
        
        extracted_data = []
        for detection in result:
            bbox, text, confidence = detection
            extracted_data.append({
                'text': text,
                'bbox': bbox,
                'confidence': confidence,
                'center': self._calculate_center(bbox)
            })
        
        return extracted_data
    
    def _calculate_center(self, bbox):
        """Calculate center point of bounding box."""
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (center_x, center_y)
    
    def extract_dimensions(self, text_data):
        """
        Extract dimension measurements from text.
        
        Args:
            text_data (list): List of extracted text data
            
        Returns:
            list: List of detected dimensions
        """
        dimensions = []
        
        # Patterns for dimensions (e.g., "10.5m", "5'6\"", "2400mm")
        patterns = [
            r'(\d+\.?\d*)\s*(?:m|mm|cm|ft|in|\'|")',  # Metric and imperial
            r'(\d+)\s*[\']\s*(\d+)\s*["]',  # Feet and inches
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',  # Dimensions like "10x20"
        ]
        
        for item in text_data:
            text = item['text']
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    dimensions.append({
                        'value': match.group(0),
                        'position': item['center'],
                        'confidence': item['confidence']
                    })
        
        return dimensions
    
    def extract_room_names(self, text_data):
        """
        Extract room names and labels from text.
        
        Args:
            text_data (list): List of extracted text data
            
        Returns:
            list: List of detected room names
        """
        room_keywords = [
            'room', 'bedroom', 'bathroom', 'kitchen', 'living', 'dining',
            'office', 'hall', 'corridor', 'lobby', 'entrance', 'garage',
            'balcony', 'terrace', 'storage', 'utility', 'closet'
        ]
        
        rooms = []
        for item in text_data:
            text = item['text'].lower()
            for keyword in room_keywords:
                if keyword in text:
                    rooms.append({
                        'name': item['text'],
                        'type': keyword,
                        'position': item['center'],
                        'confidence': item['confidence']
                    })
                    break
        
        return rooms
    
    def process_bim_image(self, image_path, output_path=None):
        """
        Process a BIM image and extract structured data.
        
        Args:
            image_path (str): Path to the BIM image
            output_path (str, optional): Path to save extracted data (JSON)
            
        Returns:
            dict: Structured data extracted from the image
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Extract text with positions
        text_data = self.extract_text_with_positions(image_path)
        
        # Extract structured information
        dimensions = self.extract_dimensions(text_data)
        rooms = self.extract_room_names(text_data)
        
        # Compile results
        results = {
            'image_path': image_path,
            'total_text_elements': len(text_data),
            'text_data': text_data,
            'dimensions': dimensions,
            'rooms': rooms,
            'all_text': ' '.join([item['text'] for item in text_data])
        }
        
        # Save to JSON if output path is provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Data saved to: {output_path}")
        
        return results
    
    def visualize_detections(self, image_path, text_data, output_path):
        """
        Visualize detected text on the image.
        
        Args:
            image_path (str): Path to the original image
            text_data (list): List of detected text data
            output_path (str): Path to save visualization
        """
        img = cv2.imread(image_path)
        
        for item in text_data:
            bbox = item['bbox']
            text = item['text']
            
            # Convert bbox to integer coordinates
            points = np.array(bbox, dtype=np.int32)
            
            # Draw rectangle
            cv2.polylines(img, [points], True, (0, 255, 0), 2)
            
            # Put text
            cv2.putText(img, text, (int(bbox[0][0]), int(bbox[0][1] - 10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        cv2.imwrite(output_path, img)
        print(f"Visualization saved to: {output_path}")


def main():
    """Main function to demonstrate BIM OCR."""
    
    print("=" * 50)
    print("BIM OCR Processor")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "bim_output.json"
        
        use_gpu = '--gpu' in sys.argv
        visualize = '--visualize' in sys.argv
        
        try:
            processor = BIMOCRProcessor(languages=['en'], gpu=use_gpu)
            
            # Process BIM image
            results = processor.process_bim_image(input_file, output_file)
            
            # Print summary
            print("\n" + "=" * 50)
            print("EXTRACTION SUMMARY")
            print("=" * 50)
            print(f"Total text elements: {results['total_text_elements']}")
            print(f"Dimensions found: {len(results['dimensions'])}")
            print(f"Rooms found: {len(results['rooms'])}")
            
            print("\n--- Detected Rooms ---")
            for room in results['rooms']:
                print(f"  - {room['name']} (Type: {room['type']}, Confidence: {room['confidence']:.2f})")
            
            print("\n--- Detected Dimensions ---")
            for dim in results['dimensions'][:10]:  # Show first 10
                print(f"  - {dim['value']} (Confidence: {dim['confidence']:.2f})")
            
            # Visualize if requested
            if visualize:
                vis_path = Path(output_file).with_suffix('.png')
                processor.visualize_detections(input_file, results['text_data'], str(vis_path))
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input_image> [output_json] [--gpu] [--visualize]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} blueprint.jpg bim_data.json --visualize")
        print("\nOptions:")
        print("  --gpu        Use GPU acceleration (requires CUDA)")
        print("  --visualize  Create visualization with bounding boxes")


if __name__ == "__main__":
    main()
