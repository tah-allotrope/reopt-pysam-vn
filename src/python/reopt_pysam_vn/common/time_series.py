"""Shared time-series helpers."""


def constant_series(value: float, length: int) -> list[float]:
    return [float(value)] * int(length)
