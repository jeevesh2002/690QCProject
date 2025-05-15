def apply_filter(fidelity: float, threshold: float = 0.9) -> bool:
    """Determines if a fidelity value passes a specified threshold.

    This function checks whether the given fidelity meets or exceeds the threshold value.

    Args:
        fidelity: The fidelity value to check.
        threshold: The minimum required fidelity threshold.

    Returns:
        True if the fidelity is greater than or equal to the threshold, False otherwise.
    """
    return fidelity >= threshold
