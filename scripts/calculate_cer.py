try:
    import Levenshtein  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Levenshtein = None


def _levenshtein_distance(s1: str, s2: str) -> int:
    if Levenshtein:
        return Levenshtein.distance(s1, s2)

    # Fallback dynamic programming implementation
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1, start=1):
        current_row = [i]
        for j, c2 in enumerate(s2, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

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
    return _levenshtein_distance(s1, s2) / len(s1)