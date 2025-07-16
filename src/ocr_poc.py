import argparse
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import os
import csv
import zipfile

ocr = PaddleOCR(use_textline_orientation=True, lang='japan')

def pdf_to_images(pdf_path, output_folder="temp_images"):
    """Converts each page of a PDF into an image."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    print(f"PDF has {len(doc)} pages.")
    image_paths = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        img_path = os.path.join(output_folder, f"page_{i+1}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    doc.close()
    return image_paths

def run_ocr(image_paths, output_csv_path=None):
    """Runs OCR on a list of image paths and prints/saves the results."""
    all_ocr_results = []
    for page_num, img_path in enumerate(image_paths):
        print(f"--- Processing {img_path} ---")
        result = ocr.predict(img_path)
        print(f"DEBUG: Full result for {img_path} = {result}") # Full result debug print
        block_id = 0
        if result is not None and len(result) > 0 and result[0] is not None:
            for line in result[0]: # Assuming result[0] contains the list of blocks for the current page
                print(f"DEBUG: line = {line}") # Debug print
                # line format: [[x0, y0], [x1, y1], [x2, y2], [x3, y3]], (text, confidence)
                
                # Defensive check for line structure
                if not (isinstance(line, list) and len(line) == 2):
                    print(f"DEBUG: Skipping malformed line (not a list of 2): {line}")
                    continue
                
                bbox = line[0]
                text_info = line[1]

                # Defensive check for text_info structure
                if not (isinstance(text_info, tuple) and len(text_info) == 2):
                    print(f"DEBUG: Skipping malformed text_info (not a tuple of 2): {text_info}")
                    continue

                text = text_info[0]
                confidence = text_info[1]

                # Calculate min/max x/y for bounding box
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                x0, y0 = min(x_coords), min(y_coords)
                x1, y1 = max(x_coords), max(y_coords)

                all_ocr_results.append({
                    'page': page_num + 1,
                    'block_id': block_id,
                    'x0': x0,
                    'y0': y0,
                    'x1': x1,
                    'y1': y1,
                    'text': text,
                    'confidence': confidence
                })
                print(f"Page {page_num + 1}, Block {block_id}: {text} (Conf: {confidence:.2f})")
                block_id += 1
        print("\n")

    if output_csv_path:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page', 'block_id', 'x0', 'y0', 'x1', 'y1', 'text', 'confidence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_ocr_results)
        print(f"OCR results saved to {output_csv_path}")

def main():
    parser = argparse.ArgumentParser(description="PDF to searchable PDF OCR PoC.")
    parser.add_argument("pdf_path", type=str, help="Path to the input PDF file.")
    parser.add_argument("--output_folder", type=str, default="temp_images",
                        help="Folder to save intermediate images.")
    parser.add_argument("--no-csv", action="store_true",
                        help="Do not output OCR results to CSV file.")
    parser.add_argument("--zip", action="store_true",
                        help="Archive PDF and CSV into a single ZIP file.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found at {args.pdf_path}")
        return

    print(f"Converting {args.pdf_path} to images...")
    image_paths = pdf_to_images(args.pdf_path, args.output_folder)
    print(f"Converted {len(image_paths)} pages to images.")

    output_csv_path = None
    if not args.no_csv:
        # Determine output CSV path based on PDF path
        pdf_dir = os.path.dirname(args.pdf_path)
        pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_csv_path = os.path.join(pdf_dir, f"{pdf_name}_ocr_results.csv")

    print("Running OCR on extracted images...")
    run_ocr(image_paths, output_csv_path)

    if args.zip:
        zip_file_name = os.path.splitext(args.pdf_path)[0] + ".zip"
        with zipfile.ZipFile(zip_file_name, 'w') as zf:
            zf.write(args.pdf_path, os.path.basename(args.pdf_path))
            if output_csv_path and os.path.exists(output_csv_path):
                zf.write(output_csv_path, os.path.basename(output_csv_path))
        print(f"Archived PDF and CSV to {zip_file_name}")

    print("OCR PoC finished.")

if __name__ == "__main__":
    main()
