"""Contract-level helpers for PySAM-backed PPA workflows."""

from __future__ import annotations


def strike_price_series(
    base_price: float, years: int, escalation_rate: float = 0.0
) -> list[float]:
    """Build an annual strike-price series from a year-one price and escalation."""

    return [
        float(base_price) * ((1.0 + float(escalation_rate)) ** year)
        for year in range(int(years))
    ]


def convert_vnd_series_to_usd(
    values_vnd: list[float], exchange_rate_vnd_per_usd: float
) -> list[float]:
    """Convert a VND-denominated annual series to USD."""

    return [float(value) / float(exchange_rate_vnd_per_usd) for value in values_vnd]


def convert_vnd_to_usd(value_vnd: float, exchange_rate_vnd_per_usd: float) -> float:
    """Convert a single VND-denominated price or cost to USD."""

    return float(value_vnd) / float(exchange_rate_vnd_per_usd)
