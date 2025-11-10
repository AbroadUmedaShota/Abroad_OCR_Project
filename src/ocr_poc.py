import argparse
import csv
import os
import re
import unicodedata

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - optional dependency during tests
    fitz = None

try:
    from paddleocr import PaddleOCR
except ImportError:  # pragma: no cover - optional dependency during tests
    PaddleOCR = None

from scripts.kenlm_corrector import KenLMCorrector


_CJK_CHAR_RANGES = "\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uFF66-\uFF9F"
_CJK_CHAR_PATTERN = re.compile(rf"[{_CJK_CHAR_RANGES}]")
_NO_SPACE_EAW = {"F", "W"}
_ADDITIONAL_NO_SPACE_CHARS = {"…", "‥", "―", "—"}


def _is_cjk_like(char: str) -> bool:
    """Return True when the character belongs to scripts that do not use inter-word spacing."""
    if not char:
        return False
    if _CJK_CHAR_PATTERN.match(char):
        return True
    if unicodedata.east_asian_width(char) in _NO_SPACE_EAW:
        return True
    if char in _ADDITIONAL_NO_SPACE_CHARS:
        return True
    return False


def _remove_redundant_cjk_spaces(text: str) -> str:
    """Collapse spaces that were artificially inserted between consecutive CJK characters."""
    if not text:
        return text
    cleaned_chars = []
    length = len(text)
    for index, char in enumerate(text):
        if char in (" ", "\u3000"):
            prev_char = ""
            next_char = ""

            for rev_index in range(index - 1, -1, -1):
                candidate = text[rev_index]
                if candidate not in (" ", "\u3000"):
                    prev_char = candidate
                    break

            for fwd_index in range(index + 1, length):
                candidate = text[fwd_index]
                if candidate not in (" ", "\u3000"):
                    next_char = candidate
                    break

            if _is_cjk_like(prev_char) and _is_cjk_like(next_char):
                continue
        cleaned_chars.append(char)
    return "".join(cleaned_chars)

def pdf_to_images(pdf_path, output_folder="temp_images"):
    """Converts each page of a PDF into an image."""
    print(f"DEBUG: Starting pdf_to_images for {pdf_path}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is required for pdf_to_images but is not installed.")

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
    # Initialize multiple OCR engines for ensemble voting
    if PaddleOCR is None:
        raise RuntimeError("PaddleOCR is required for run_ocr but is not installed.")

    ocr_engine_1 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++')
    ocr_engine_2 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++') # Placeholder for another engine (e.g., Tesseract)
    ocr_engine_3 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++') # Placeholder for a third engine (e.g., Mistral-OCR LoRA)

    # Initialize KenLM Corrector within the function
    # NOTE: KenLM model loading is temporarily commented out due to installation issues.
    # kenlm_corrector = KenLMCorrector("/path/to/your/kenlm_model.arpa")

    print("DEBUG: OCR Engines initialized for ensemble voting.")

    all_ocr_results = []
    for page_num, img_path in enumerate(image_paths):
        print(f"--- Processing {img_path} ---")

        # Get results from each engine
        result_engine_1 = ocr_engine_1.ocr(img_path, cls=True)
        result_engine_2 = ocr_engine_2.ocr(img_path, cls=True) # Simulate result from engine 2
        result_engine_3 = ocr_engine_3.ocr(img_path, cls=True) # Simulate result from engine 3

        # Ensemble Voting (Weighted Voting Fusion)
        # For simplicity, we'll choose the result with the highest confidence for each line.
        # In a real scenario, weights would be applied (conf * weight_engine) and then compared.
        final_result_for_page = []
        # Assuming results are structured similarly and can be iterated line by line
        # This is a simplified example and might need more sophisticated alignment for real-world scenarios
        max_lines = max(len(result_engine_1[0]) if result_engine_1 and result_engine_1[0] else 0,
                        len(result_engine_2[0]) if result_engine_2 and result_engine_2[0] else 0,
                        len(result_engine_3[0]) if result_engine_3 and result_engine_3[0] else 0)

        for i in range(max_lines):
            best_line_info = None
            best_confidence = -1.0

            # Check engine 1
            if result_engine_1 and result_engine_1[0] and i < len(result_engine_1[0]):
                line_info = result_engine_1[0][i]
                if line_info and len(line_info) == 2 and line_info[1] and len(line_info[1]) == 2:
                    if line_info[1][1] > best_confidence:
                        best_confidence = line_info[1][1]
                        best_line_info = line_info

            # Check engine 2
            if result_engine_2 and result_engine_2[0] and i < len(result_engine_2[0]):
                line_info = result_engine_2[0][i]
                if line_info and len(line_info) == 2 and line_info[1] and len(line_info[1]) == 2:
                    if line_info[1][1] > best_confidence:
                        best_confidence = line_info[1][1]
                        best_line_info = line_info

            # Check engine 3
            if result_engine_3 and result_engine_3[0] and i < len(result_engine_3[0]):
                line_info = result_engine_3[0][i]
                if line_info and len(line_info) == 2 and line_info[1] and len(line_info[1]) == 2:
                    if line_info[1][1] > best_confidence:
                        best_confidence = line_info[1][1]
                        best_line_info = line_info
            
            if best_line_info:
                final_result_for_page.append(best_line_info)

        if not final_result_for_page:
            print(f"DEBUG: No valid OCR results found for {img_path}")
            continue

        block_id = 0
        for line_info in final_result_for_page:
            # Ensure line_info is in the expected format before processing
            if not (isinstance(line_info, list) and len(line_info) == 2 and
                    isinstance(line_info[0], list) and # bbox
                    isinstance(line_info[1], tuple) and len(line_info[1]) == 2): # (text, confidence)
                print(f"DEBUG: Skipping malformed line_info: {line_info}")
                continue

            bbox = line_info[0]
            text, confidence = line_info[1]

            # KenLM Correction Framework
            # corrected_text = kenlm_corrector.correct(text) # Temporarily disabled due to kenlm installation issues
            corrected_text = text # For now, no correction is applied
            corrected_text = _remove_redundant_cjk_spaces(corrected_text)
            print(f"DEBUG: Original text: {text}, Corrected text: {corrected_text}")

            # Convert bbox to x0, y0, x1, y1 format
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
                'text': corrected_text,
                'confidence': confidence
            })
            # IoU Check Framework (Placeholder)
            # In a real scenario, you would compare the detected bbox with a ground truth bbox
            # and calculate IoU here.
            # Example: iou_value = calculate_iou([x0, y0, x1, y1], ground_truth_bbox)
            # print(f"DEBUG: IoU for this bbox: {iou_value}")
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

def main():
    parser = argparse.ArgumentParser(description="PDF to CSV OCR PoC.")
    parser.add_argument("pdf_path", type=str, help="Path to the input PDF file.")
    parser.add_argument("--output_folder", type=str, default="temp_images",
                        help="Folder to save intermediate images.")
    parser.add_argument("--no-csv", action="store_true",
                        help="Do not output OCR results to CSV file.")
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
        if not pdf_dir: # Handle case where path is just a filename
            pdf_dir = "."
        pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
        output_csv_path = os.path.join(pdf_dir, f"{pdf_name}_ocr_results.csv")

    print("Running OCR on extracted images...")
    run_ocr(image_paths, output_csv_path)

    print("OCR PoC finished.")

if __name__ == "__main__":
    main()
