import argparse
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import os
import csv
from scripts.kenlm_corrector import KenLMCorrector

# Add imports for LoRA model
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch

# Define a placeholder/mock for the Mistral-OCR LoRA Engine
class MistralOCR_LoRA_Engine:
    def __init__(self, base_model_name, lora_adapter_path):
        self.base_model_name = base_model_name
        self.lora_adapter_path = lora_adapter_path
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        print(f"Loading base model: {self.base_model_name}")
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16 # Use bfloat16 for potentially lower memory usage
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"Loading LoRA adapters from: {self.lora_adapter_path}")
        # Load LoRA adapters
        self.model = PeftModel.from_pretrained(self.model, self.lora_adapter_path)
        self.model.eval() # Set to evaluation mode

        print("Mistral-OCR LoRA model loaded successfully.")

    def ocr(self, image_path):
        """
        Performs OCR using the LoRA model.
        This is a simplified example. In a real scenario, you would:
        1. Preprocess the image (e.g., convert to text, or use a multimodal model).
        2. Prepare the input for the LoRA-tuned language model.
        3. Run inference to generate text.
        4. (Optional) Implement a mechanism to extract bounding boxes if the model supports it.
        5. Format the output to match PaddleOCR's result format.
        """
        print(f"Running LoRA OCR for {image_path}")
        
        # For this PoC, we'll simulate image-to-text conversion.
        # In a real application, you'd feed the image (or a representation of it) to the model.
        # For a text-based LoRA model, you might need an initial OCR step (e.g., PaddleOCR)
        # to get text, then use the LoRA model for correction/refinement.
        
        # For now, let's assume we get some input text from an image (e.g., from another OCR engine)
        # and the LoRA model refines it.
        # This part needs to be adapted based on how your LoRA model processes images.
        
        # Example: If your LoRA model is a text-to-text model, you'd feed it a prompt.
        # For a true OCR LoRA, you'd need a multimodal model or a pre-processing step.
        
        # For demonstration, let's use a simple prompt and generate text.
        # This is NOT a full OCR solution, but demonstrates the LoRA model's integration.
        prompt = f"Extract text from the following image: {os.path.basename(image_path)}. Text: "
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=100, num_return_sequences=1)
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process the generated text to extract only the OCR result part
        # This is a very basic example and needs refinement based on actual model output format.
        ocr_result_text = generated_text.replace(prompt, "").strip()
        
        # Simulate bounding box and confidence for compatibility with PaddleOCR format
        # In a real scenario, if your LoRA model provides bounding boxes, you'd extract them.
        # Otherwise, you might use a separate detection model or rely on a base OCR for bboxes.
        dummy_bbox = [[10, 10, 100, 20], [100, 20, 10, 100], [10, 100, 100, 90], [100, 90, 10, 10]] # A simple square bbox
        confidence = 0.9 # Placeholder confidence
        
        # PaddleOCR expects a list of pages, each containing a list of results.
        # Each result is [bbox, (text, confidence)].
        results = [
            [dummy_bbox, (ocr_result_text, confidence)]
        ]
        return [results] # Return as a list of pages, each containing a list of results.

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
    # Initialize multiple OCR engines for ensemble voting
    ocr_engine_1 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++')
    ocr_engine_2 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++') # Placeholder for another engine (e.g., Tesseract)
    
    # Initialize Mistral-OCR LoRA Engine
    # NOTE: Replace with actual model name and path
    lora_base_model_name = "mistralai/Mistral-7B-v0.1" # Example base model
    lora_adapter_path = "./lora_finetuned_model/lora_adapters" # Path where finetuned adapters are saved
    
    try:
        ocr_engine_3 = MistralOCR_LoRA_Engine(lora_base_model_name, lora_adapter_path)
    except Exception as e:
        print(f"Warning: Could not load Mistral-OCR LoRA engine: {e}. Using PaddleOCR as fallback for engine 3.")
        ocr_engine_3 = PaddleOCR(use_angle_cls=True, lang='japan', det_algorithm='DB++') # Fallback

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
        result_engine_3 = ocr_engine_3.ocr(img_path) # Use the LoRA engine

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

            # Check engine 3 (LoRA engine)
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
            if not (isinstance(line_info, list) and len(line_info) == 2 and \
                    isinstance(line_info[0], list) and \
                    isinstance(line_info[1], tuple) and len(line_info[1]) == 2):
                print(f"DEBUG: Skipping malformed line_info: {line_info}")
                continue

            bbox = line_info[0]
            text, confidence = line_info[1]

            # KenLM Correction Framework
            # corrected_text = kenlm_corrector.correct(text) # Temporarily disabled due to kenlm installation issues
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