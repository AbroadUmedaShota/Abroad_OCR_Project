import csv

def calculate_cer(ocr_csv_path, ground_truth_txt_path):
    """Calculates the Character Error Rate (CER)."""
    try:
        with open(ocr_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ocr_text = "".join(row['text'] for row in reader)

        with open(ground_truth_txt_path, 'r', encoding='utf-8') as f:
            ground_truth_text = f.read().strip()

        # Simple CER calculation (Levenshtein distance)
        if not ground_truth_text:
            return 1.0 if ocr_text else 0.0

        dp = [[0] * (len(ocr_text) + 1) for _ in range(len(ground_truth_text) + 1)]

        for i in range(len(ground_truth_text) + 1):
            dp[i][0] = i
        for j in range(len(ocr_text) + 1):
            dp[0][j] = j

        for i in range(1, len(ground_truth_text) + 1):
            for j in range(1, len(ocr_text) + 1):
                cost = 0 if ground_truth_text[i - 1] == ocr_text[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1,        # Deletion
                               dp[i][j - 1] + 1,        # Insertion
                               dp[i - 1][j - 1] + cost) # Substitution

        return dp[len(ground_truth_text)][len(ocr_text)] / len(ground_truth_text)

    except FileNotFoundError as e:
        print(f"Error in CER calculation: {e}")
        return 1.0 # Return max error if a file is not found