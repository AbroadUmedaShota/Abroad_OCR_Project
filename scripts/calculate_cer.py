import argparse
import csv
from Levenshtein import distance

def calculate_cer(ocr_csv_path, ground_truth_txt_path):
    """Calculates Character Error Rate (CER) from OCR results and ground truth.

    Args:
        ocr_csv_path (str): Path to the OCR results CSV file.
        ground_truth_txt_path (str): Path to the ground truth text file.

    Returns:
        float: The calculated CER.
    """
    ocr_text = ""
    with open(ocr_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ocr_text += row['text']

    with open(ground_truth_txt_path, 'r', encoding='utf-8') as f:
        ground_truth_text = f.read().strip()

    if not ground_truth_text:
        return 0.0 # Avoid division by zero if ground truth is empty

    edit_distance = distance(ocr_text, ground_truth_text)
    cer = edit_distance / len(ground_truth_text)
    return cer

def main():
    parser = argparse.ArgumentParser(description="Calculate Character Error Rate (CER).")
    parser.add_argument("ocr_csv_path", type=str, help="Path to the OCR results CSV file.")
    parser.add_argument("ground_truth_txt_path", type=str, help="Path to the ground truth text file.")
    args = parser.parse_args()

    cer = calculate_cer(args.ocr_csv_path, args.ground_truth_txt_path)
    print(f"Character Error Rate (CER): {cer:.4f}")

if __name__ == "__main__":
    main()
