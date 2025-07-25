
def calculate_cer(ground_truth: str, recognized_text: str) -> float:
    """
    Calculates the Character Error Rate (CER) between two strings.
    CER is calculated as (substitutions + insertions + deletions) / total_characters_in_ground_truth.
    A simple Levenshtein distance based approach is used.
    """
    # Simple implementation of Levenshtein distance for CER
    # This can be replaced with a more robust library like python-Levenshtein for production

    n = len(ground_truth)
    m = len(recognized_text)

    if n == 0:
        return 1.0 if m > 0 else 0.0 # If ground truth is empty, CER is 1.0 if recognized text exists, else 0.0

    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ground_truth[i-1] == recognized_text[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1,      # Deletion
                           dp[i][j-1] + 1,      # Insertion
                           dp[i-1][j-1] + cost) # Substitution

    return dp[n][m] / n

if __name__ == '__main__':
    # Example Usage:
    gt = "This is a test"
    rec = "Thiss is a testt"
    cer_score = calculate_cer(gt, rec)
    print(f"Ground Truth: {gt}")
    print(f"Recognized:   {rec}")
    print(f"CER: {cer_score:.4f}")

    gt2 = "Hello World"
    rec2 = "Hell World"
    cer_score2 = calculate_cer(gt2, rec2)
    print(f"\nGround Truth: {gt2}")
    print(f"Recognized:   {rec2}")
    print(f"CER: {cer_score2:.4f}")

    gt3 = ""
    rec3 = "abc"
    cer_score3 = calculate_cer(gt3, rec3)
    print(f"\nGround Truth: '{gt3}'")
    print(f"Recognized:   '{rec3}'")
    print(f"CER: {cer_score3:.4f}")

    gt4 = "abc"
    rec4 = ""
    cer_score4 = calculate_cer(gt4, rec4)
    print(f"\nGround Truth: '{gt4}'")
    print(f"Recognized:   '{rec4}'")
    print(f"CER: {cer_score4:.4f}")
