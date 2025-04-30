def apply_filter(pair_fidelity, threshold=0.9):
    """Discard pairs below fidelity threshold."""
    return pair_fidelity >= threshold
