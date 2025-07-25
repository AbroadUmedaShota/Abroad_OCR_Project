import argparse
import csv
import json
from collections import defaultdict
from scripts.calculate_cer import calculate_cer
from scripts.calculate_iou import calculate_iou

def load_ocr_results(csv_path):
    """
    Loads OCR results from a CSV file.
    Expected CSV format: page,block_id,x0,y0,x1,y1,text,confidence
    """
    results = defaultdict(list)
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            page = int(row['page'])
            bbox = [float(row['x0']), float(row['y0']), float(row['x1']), float(row['y1'])]
            text = row['text']
            confidence = float(row['confidence'])
            results[page].append({'bbox': bbox, 'text': text, 'confidence': confidence})
    return results

def load_ground_truth(json_path):
    """
    Loads ground truth data from a JSON file.
    Expected JSON format: {"page_num": [{"bbox": [x0,y0,x1,y1], "text": "ground truth text"}, ...]}
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
    
    # Convert string keys to int for page numbers
    return {int(k): v for k, v in gt_data.items()}

def match_boxes(gt_boxes, ocr_boxes, iou_threshold=0.5):
    """
    Matches OCR bounding boxes to ground truth bounding boxes based on IoU.
    Returns a list of tuples: (gt_box_info, ocr_box_info) for matched pairs.
    """
    matched_pairs = []
    matched_ocr_indices = set()

    for gt_idx, gt_box_info in enumerate(gt_boxes):
        best_iou = -1
        best_ocr_idx = -1

        for ocr_idx, ocr_box_info in enumerate(ocr_boxes):
            if ocr_idx in matched_ocr_indices: # Skip already matched OCR boxes
                continue
            
            iou = calculate_iou(gt_box_info['bbox'], ocr_box_info['bbox'])
            if iou > best_iou:
                best_iou = iou
                best_ocr_idx = ocr_idx
        
        if best_iou >= iou_threshold and best_ocr_idx != -1:
            matched_pairs.append((gt_box_info, ocr_boxes[best_ocr_idx]))
            matched_ocr_indices.add(best_ocr_idx)
    
    return matched_pairs

def main():
    parser = argparse.ArgumentParser(description="OCR Accuracy Reviewer.")
    parser.add_argument("--ocr_csv", type=str, required=True,
                        help="Path to the OCR results CSV file.")
    parser.add_argument("--ground_truth_json", type=str, required=True,
                        help="Path to the ground truth JSON file.")
    parser.add_argument("--iou_threshold", type=float, default=0.5,
                        help="IoU threshold for matching bounding boxes.")
    args = parser.parse_args()

    ocr_results = load_ocr_results(args.ocr_csv)
    ground_truth = load_ground_truth(args.ground_truth_json)

    total_cer = 0
    total_iou = 0
    total_matched_pairs = 0
    total_gt_texts = 0

    print("\n--- OCR Accuracy Report ---")

    for page_num in sorted(ground_truth.keys()):
        gt_page_data = ground_truth[page_num]
        ocr_page_data = ocr_results.get(page_num, [])

        if not gt_page_data:
            print(f"Page {page_num}: No ground truth data found.")
            continue

        if not ocr_page_data:
            print(f"Page {page_num}: No OCR results found.")
            # Calculate CER for missing OCR results (all insertions/deletions)
            for gt_item in gt_page_data:
                total_cer += calculate_cer(gt_item['text'], "") * len(gt_item['text'])
                total_gt_texts += len(gt_item['text'])
            continue

        matched_pairs = match_boxes(gt_page_data, ocr_page_data, args.iou_threshold)
        
        page_cer_sum = 0
        page_iou_sum = 0
        page_gt_char_count = 0

        for gt_item, ocr_item in matched_pairs:
            cer = calculate_cer(gt_item['text'], ocr_item['text'])
            iou = calculate_iou(gt_item['bbox'], ocr_item['bbox'])
            
            page_cer_sum += cer * len(gt_item['text'])
            page_iou_sum += iou
            page_gt_char_count += len(gt_item['text'])
            total_matched_pairs += 1

        if page_gt_char_count > 0:
            avg_page_cer = page_cer_sum / page_gt_char_count
            print(f"Page {page_num}: Average CER = {avg_page_cer:.4f}, Matched Boxes = {len(matched_pairs)}")
            total_cer += page_cer_sum
            total_gt_texts += page_gt_char_count
        else:
            print(f"Page {page_num}: No ground truth characters for CER calculation.")

        if len(matched_pairs) > 0:
            avg_page_iou = page_iou_sum / len(matched_pairs)
            print(f"Page {page_num}: Average IoU = {avg_page_iou:.4f}")
            total_iou += page_iou_sum

    print("\n--- Overall Metrics ---")
    if total_gt_texts > 0:
        overall_cer = total_cer / total_gt_texts
        print(f"Overall Average CER: {overall_cer:.4f}")
    else:
        print("Overall Average CER: N/A (No ground truth text found)")

    if total_matched_pairs > 0:
        overall_iou = total_iou / total_matched_pairs
        print(f"Overall Average IoU: {overall_iou:.4f}")
    else:
        print("Overall Average IoU: N/A (No matched bounding boxes found)")

if __name__ == "__main__":
    main()