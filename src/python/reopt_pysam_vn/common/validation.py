"""Shared validation helpers."""


def require_positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return float(value)
