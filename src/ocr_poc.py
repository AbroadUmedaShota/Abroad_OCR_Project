import argparse
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import os
import csv
import zipfile

ocr = PaddleOCR(use_textline_orientation=True, lang='japan')
print("DEBUG: PaddleOCR initialized.")

def pdf_to_images(pdf_path, output_folder="temp_images"):
    """Converts each page of a PDF into an image."""
    print(f"DEBUG: Starting pdf_to_images for {pdf_path}")
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
    """Runs OCR on a list of image paths and returns the structured results."""
    all_ocr_results = []
    for page_num, img_path in enumerate(image_paths):
        print(f"--- Processing {img_path} ---")
        result = ocr.ocr(img_path)
        with open(f"debug_ocr_result_page_{page_num}.txt", "w", encoding="utf-8") as f:
            f.write(repr(result))
        if result is None or not result or not result[0]:
            print(f"DEBUG: No valid OCR results found for {img_path}")
            continue

        block_id = 0
        for line_info in result[0]:
            print(f"DEBUG: Processing line_info (type: {type(line_info)}): {repr(line_info)}")
            if not (isinstance(line_info, list) and len(line_info) == 2):
                continue

            bbox = line_info[0]
            text_info = line_info[1]

            if not (isinstance(bbox, list) and len(bbox) == 4 and
                    isinstance(text_info, tuple) and len(text_info) == 2):
                continue

            text, confidence = text_info

            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            x0, y0 = min(x_coords), min(y_coords)
            x1, y1 = max(x_coords), max(y_coords)

            all_ocr_results.append({
                'page': page_num,
                'block_id': block_id,
                'x0': x0,
                'y0': y0,
                'x1': x1,
                'y1': y1,
                'text': text,
                'confidence': confidence
            })
            block_id += 1
    print("\n")

    if output_csv_path:
        csv_results = []
        for res in all_ocr_results:
            csv_res = res.copy()
            csv_res['page'] = res['page'] + 1
            csv_results.append(csv_res)
            
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page', 'block_id', 'x0', 'y0', 'x1', 'y1', 'text', 'confidence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_results)
        print(f"OCR results saved to {output_csv_path}")
        
    return all_ocr_results

def create_searchable_pdf(original_pdf_path, ocr_results, output_pdf_path):
    """Creates a searchable PDF by adding an invisible text layer to the original PDF."""
    doc = fitz.open(original_pdf_path)

    for result in ocr_results:
        page_num = result['page']
        if page_num < len(doc):
            page = doc.load_page(page_num)
            
            img_rect = page.get_pixmap().irect
            pdf_rect = page.rect
            scale_x = pdf_rect.width / img_rect.width
            scale_y = pdf_rect.height / img_rect.height

            x0 = result['x0'] * scale_x
            y0 = result['y0'] * scale_y
            x1 = result['x1'] * scale_x
            y1 = result['y1'] * scale_y
            
            rect = fitz.Rect(x0, y0, x1, y1)

            page.insert_textbox(rect, 
                                result['text'], 
                                fontname="cjk",
                                fontsize=0,
                                render_mode=3)

    doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"Searchable PDF saved to {output_pdf_path}")

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
        pdf_dir = os.path.dirname(args.pdf_path)
        pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_csv_path = os.path.join(pdf_dir, f"{pdf_name}_ocr_results.csv")

    print("Running OCR on extracted images...")
    ocr_results = run_ocr(image_paths, output_csv_path)

    pdf_dir = os.path.dirname(args.pdf_path)
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    output_pdf_path = os.path.join(pdf_dir, f"{pdf_name}_searchable.pdf")
    create_searchable_pdf(args.pdf_path, ocr_results, output_pdf_path)

    if args.zip:
        zip_file_name = os.path.splitext(args.pdf_path)[0] + ".zip"
        with zipfile.ZipFile(zip_file_name, 'w') as zf:
            zf.write(output_pdf_path, os.path.basename(output_pdf_path))
            if output_csv_path and os.path.exists(output_csv_path):
                zf.write(output_csv_path, os.path.basename(output_csv_path))
        print(f"Archived searchable PDF and CSV to {zip_file_name}")

    print("OCR PoC finished.")

if __name__ == "__main__":
    main()