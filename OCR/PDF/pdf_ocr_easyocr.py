"""
PDF OCR Script - Approach 2: PyMuPDF + EasyOCR
This script converts PDF pages to PNG images using PyMuPDF and extracts text using EasyOCR.
EasyOCR uses deep learning and supports multiple languages.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import numpy as np


class PDFOCREasyProcessor:
    """Process PDF files and extract text using EasyOCR."""
    
    def __init__(self, languages=['en'], gpu=False, zoom=4):
        """
        Initialize the PDF OCR processor with EasyOCR.
        
        Args:
            languages (list): List of language codes (default: ['en'])
            gpu (bool): Use GPU acceleration if available (default: False)
            zoom (int): Zoom factor for PDF to image conversion (default: 4)
        """
        self.zoom = zoom
        print(f"Initializing EasyOCR with languages: {languages}")
        self.reader = easyocr.Reader(languages, gpu=gpu)
        print("EasyOCR initialized successfully")
    
    def pdf_to_images(self, pdf_path, output_dir=None):
        """
        Convert PDF pages to PNG images.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str, optional): Directory to save images
            
        Returns:
            list: List of image file paths
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Opening PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        mat = fitz.Matrix(self.zoom, self.zoom)
        
        image_paths = []
        
        # Create output directory if specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(pdf_path).parent / "temp_images"
            output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting {len(doc)} page(s) to images...")
        for i in range(len(doc)):
            image_path = output_dir / f"page_{i+1}.png"
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat)
            pix.save(str(image_path))
            image_paths.append(str(image_path))
            print(f"Saved page {i+1} to {image_path}")
        
        doc.close()
        return image_paths
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from an image using EasyOCR.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text
        """
        print(f"Processing image: {image_path}")
        result = self.reader.readtext(image_path, detail=0)
        return '\n'.join(result)
    
    def extract_text_from_pdf(self, pdf_path, output_path=None, keep_images=False):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_path (str, optional): Path to save extracted text
            keep_images (bool): Keep temporary images (default: False)
            
        Returns:
            str: Extracted text from the PDF
        """
        # Convert PDF to images
        image_dir = Path(pdf_path).parent / "temp_images"
        image_paths = self.pdf_to_images(pdf_path, str(image_dir))
        
        # Extract text from each image
        all_text = ""
        for i, image_path in enumerate(image_paths, 1):
            print(f"\nExtracting text from page {i}...")
            text = self.extract_text_from_image(image_path)
            all_text += f"\n--- Page {i} ---\n{text}\n"
        
        # Clean up temporary images if not keeping
        if not keep_images:
            print("\nCleaning up temporary images...")
            for image_path in image_paths:
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Could not delete {image_path}: {e}")
            try:
                image_dir.rmdir()
            except:
                pass
        
        # Save to file if output path is provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(all_text)
            print(f"\nText saved to: {output_path}")
        
        return all_text


def main():
    """Main function to demonstrate PDF OCR with EasyOCR."""
    
    print("=" * 50)
    print("PDF OCR Processor - EasyOCR")
    print("=" * 50)
    
    # Check if file path is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
        
        # Check for GPU flag
        use_gpu = '--gpu' in sys.argv
        keep_images = '--keep-images' in sys.argv
        
        file_ext = Path(input_file).suffix.lower()
        
        try:
            processor = PDFOCREasyProcessor(languages=['en'], gpu=use_gpu)
            
            if file_ext == '.pdf':
                text = processor.extract_text_from_pdf(
                    input_file, 
                    output_file, 
                    keep_images=keep_images
                )
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                text = processor.extract_text_from_image(input_file)
                if output_file:
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"Text saved to: {output_file}")
            else:
                print(f"Unsupported file type: {file_ext}")
                print("Supported types: .pdf, .jpg, .jpeg, .png, .bmp, .tiff")
                sys.exit(1)
            
            print("\n" + "=" * 50)
            print("EXTRACTED TEXT (Preview - First 500 characters):")
            print("=" * 50)
            print(text[:500])
            if len(text) > 500:
                print(f"\n... ({len(text) - 500} more characters)")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input_file> [output_file] [--gpu] [--keep-images]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} scanned.pdf output.txt")
        print(f"  python {sys.argv[0]} image.jpg output.txt --gpu")
        print("\nOptions:")
        print("  --gpu          Use GPU acceleration (requires CUDA)")
        print("  --keep-images  Keep temporary images from PDF conversion")


if __name__ == "__main__":
    main()
