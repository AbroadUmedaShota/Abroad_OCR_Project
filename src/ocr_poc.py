import argparse
import fitz  # PyMuPDF
from paddleocr import PaddleOCR, build_logger
import os

# Initialize PaddleOCR (this can be configured later for specific models)
# For a basic PoC, we'll use the default English model.
# For Japanese, it would be `lang='japan'` and potentially `use_gpu=True` if available.
# logger = build_logger(name="OCR_PoC", log_file="ocr_poc.log")
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) # Simplified for PoC

def pdf_to_images(pdf_path, output_folder="temp_images"):
    """Converts each page of a PDF into an image."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    image_paths = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        img_path = os.path.join(output_folder, f"page_{i+1}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    doc.close()
    return image_paths

def run_ocr(image_paths):
    """Runs OCR on a list of image paths and prints the results."""
    for img_path in image_paths:
        print(f"--- Processing {img_path} ---")
        result = ocr.ocr(img_path, cls=True)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                print(line)
        print("\n")

def main():
    parser = argparse.ArgumentParser(description="PDF to searchable PDF OCR PoC.")
    parser.add_argument("pdf_path", type=str, help="Path to the input PDF file.")
    parser.add_argument("--output_folder", type=str, default="temp_images",
                        help="Folder to save intermediate images.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        return

    print(f"Converting {args.pdf_path} to images...")
    image_paths = pdf_to_images(args.pdf_path, args.output_folder)
    print(f"Converted {len(image_paths)} pages to images.")

    print("Running OCR on extracted images...")
    run_ocr(image_paths)
    print("OCR PoC finished.")

if __name__ == "__main__":
    main()
