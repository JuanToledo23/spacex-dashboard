"""Shared calculation utilities for success rates and metrics."""


def success_rate(successes: int, total: int) -> float:
    """Calculate a success-rate percentage, safe against zero division."""
    return round((successes / total) * 100, 1) if total > 0 else 0.0
