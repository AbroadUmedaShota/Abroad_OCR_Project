import argparse
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import os
import csv

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

def run_ocr(image_paths, output_csv_path=None, lora_path=None):
    """Runs OCR on a list of image paths and returns the structured results."""
    # Initialize PaddleOCR within the function to ensure models are loaded correctly.
    ocr_engine_1 = PaddleOCR(use_angle_cls=True, lang='japan', use_det=True, use_rec=True)
    # Simulate another OCR engine (e.g., Tesseract or Mistral-OCR LoRA in future)
    ocr_engine_2 = PaddleOCR(use_angle_cls=True, lang='japan', use_det=True, use_rec=True) # Placeholder for another engine
    
    # Initialize the LoRA model engine
    if lora_path and os.path.exists(lora_path):
        print(f"DEBUG: Loading LoRA model from {lora_path}")
        # In a real implementation, you would load the LoRA weights into the model here.
        # For PaddleOCR, this might involve setting `rec_model_dir` or similar parameters
        # if the fine-tuned model is saved in a compatible format.
        # As a placeholder, we'll initialize a separate engine and print a debug message.
        ocr_engine_3 = PaddleOCR(use_angle_cls=True, lang='japan', use_det=True, use_rec=True, rec_model_dir=lora_path)
        print("DEBUG: LoRA model loaded.")
    else:
        print("DEBUG: No LoRA model path provided or path not found. Using standard model.")
        ocr_engine_3 = PaddleOCR(use_angle_cls=True, lang='japan', use_det=True, use_rec=True) # Fallback to standard model

    print("DEBUG: OCR Engines initialized inside run_ocr.")

    all_ocr_results = []
    for page_num, img_path in enumerate(image_paths):
        print(f"--- Processing {img_path} ---")

        # Simulate results from multiple engines
        result_engine_1 = ocr_engine_1.ocr(img_path, det=True, rec=True, cls=True)
        result_engine_2 = ocr_engine_2.ocr(img_path, det=True, rec=True, cls=True) # Placeholder result
        result_engine_3 = ocr_engine_3.ocr(img_path, det=True, rec=True, cls=True) # Placeholder result for LoRA

        # Ensemble Voting Framework (Weighted Voting Fusion)
        # For simplicity, we'll choose the result with the highest confidence for each line.
        # In a real scenario, weights would be applied (conf * weight_engine) and then compared.
        final_result_for_page = []
        if result_engine_1 and result_engine_1[0]:
            for i, line_info_1 in enumerate(result_engine_1[0]):
                best_line_info = line_info_1
                best_confidence = line_info_1[1][1]

                # Compare with engine 2 (if available and has results for this line)
                if result_engine_2 and result_engine_2[0] and i < len(result_engine_2[0]):
                    line_info_2 = result_engine_2[0][i]
                    if line_info_2[1][1] > best_confidence:
                        best_line_info = line_info_2
                        best_confidence = line_info_2[1][1]
                
                # Compare with engine 3 (LoRA) (if available and has results for this line)
                if result_engine_3 and result_engine_3[0] and i < len(result_engine_3[0]):
                    line_info_3 = result_engine_3[0][i]
                    if line_info_3[1][1] > best_confidence:
                        best_line_info = line_info_3
                        best_confidence = line_info_3[1][1]
                
                final_result_for_page.append(best_line_info)
        
        if not final_result_for_page:
            print(f"DEBUG: No valid OCR results found for {img_path}")
            continue

        block_id = 0 # Initialize block_id here
        for line_info in final_result_for_page:
            print(f"DEBUG: Processing line_info (type: {type(line_info)}): {repr(line_info)}")
            if not (isinstance(line_info, list) and len(line_info) == 2):
                continue

            bbox = line_info[0]
            text_info = line_info[1]

            if not (isinstance(bbox, list) and len(bbox) == 4 and
                    isinstance(text_info, tuple) and len(text_info) == 2):
                continue

            text, confidence = text_info

            # KenLM Correction Framework
            # This is a placeholder for KenLM correction. In a real scenario,
            # you would load a KenLM model and apply it to the 'text' variable.
            corrected_text = text # For now, no correction is applied
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
    parser.add_argument("--lora_path", type=str, default=None,
                        help="Path to the fine-tuned LoRA model directory.")
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
    run_ocr(image_paths, output_csv_path, args.lora_path)

    print("OCR PoC finished.")

if __name__ == "__main__":
    main()