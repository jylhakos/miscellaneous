"""
PDF OCR Script - Approach 1: pdf2image + pytesseract
This script converts PDF pages to images and extracts text using Tesseract OCR.
Suitable for scanned PDFs.
"""

import os
import sys
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class PDFOCRProcessor:
    """Process PDF files and extract text using OCR."""
    
    def __init__(self, dpi=600):
        """
        Initialize the PDF OCR processor.
        
        Args:
            dpi (int): Resolution for converting PDF to images (default: 600)
        """
        self.dpi = dpi
    
    def extract_text_from_pdf(self, pdf_path, output_path=None):
        """
        Extract text from a scanned PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_path (str, optional): Path to save extracted text
            
        Returns:
            str: Extracted text from the PDF
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Converting PDF to images at {self.dpi} DPI...")
        try:
            # Convert PDF pages to PIL Image objects
            pages = convert_from_path(pdf_path, self.dpi)
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            print("Make sure poppler-utils is installed: sudo apt-get install poppler-utils")
            raise
        
        print(f"Extracting text from {len(pages)} page(s)...")
        text_data = ''
        
        for i, page in enumerate(pages, 1):
            print(f"Processing page {i}...")
            text = pytesseract.image_to_string(page)
            text_data += f"\n--- Page {i} ---\n{text}\n"
        
        # Save to file if output path is provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_data)
            print(f"Text saved to: {output_path}")
        
        return text_data
    
    def extract_text_from_image(self, image_path, output_path=None):
        """
        Extract text from a single image file.
        
        Args:
            image_path (str): Path to the image file
            output_path (str, optional): Path to save extracted text
            
        Returns:
            str: Extracted text from the image
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        print(f"Loading image: {image_path}")
        image = Image.open(image_path)
        
        print("Extracting text...")
        text = pytesseract.image_to_string(image)
        
        # Save to file if output path is provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text saved to: {output_path}")
        
        return text


def main():
    """Main function to demonstrate PDF OCR."""
    
    # Example usage
    processor = PDFOCRProcessor(dpi=600)
    
    # Example 1: Process a scanned PDF
    print("=" * 50)
    print("PDF OCR Processor - pytesseract")
    print("=" * 50)
    
    # Check if file path is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
        
        file_ext = Path(input_file).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                text = processor.extract_text_from_pdf(input_file, output_file)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                text = processor.extract_text_from_image(input_file, output_file)
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
            sys.exit(1)
    else:
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input_file> [output_file]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} scanned.pdf output.txt")
        print(f"  python {sys.argv[0]} image.jpg output.txt")
        print("\nNote: Make sure Tesseract OCR is installed:")
        print("  sudo apt-get install tesseract-ocr")
        print("  sudo apt-get install poppler-utils")


if __name__ == "__main__":
    main()
