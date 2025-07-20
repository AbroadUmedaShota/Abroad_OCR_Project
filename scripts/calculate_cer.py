import Levenshtein

def calculate_cer(s1, s2):
    """
    Calculates the Character Error Rate (CER) between two strings.

    Args:
        s1 (str): The ground truth string.
        s2 (str): The hypothesis string.

    Returns:
        float: The Character Error Rate.
    """
    if len(s1) == 0:
        return 1.0 if len(s2) > 0 else 0.0
    return Levenshtein.distance(s1, s2) / len(s1)