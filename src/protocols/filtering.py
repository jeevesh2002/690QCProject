def apply_filter(fidelity: float, threshold: float = 0.9) -> bool:
    """Discard pairs below fidelity threshold."""
    return fidelity >= threshold
