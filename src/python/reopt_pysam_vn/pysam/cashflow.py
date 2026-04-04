"""Cash-flow helpers for PySAM wrappers."""

from __future__ import annotations


def years_index(analysis_years: int) -> list[int]:
    return list(range(1, int(analysis_years) + 1))


def trim_year_zero(
    values: list[float] | tuple[float, ...], analysis_years: int
) -> list[float]:
    """Drop year-zero entries from PySAM annual arrays and cap to the analysis period."""

    series = list(values)
    if len(series) >= int(analysis_years) + 1:
        series = series[1 : int(analysis_years) + 1]
    return [float(value) for value in series[: int(analysis_years)]]


def build_annual_cashflow_table(
    analysis_years: int,
    revenue_usd: list[float],
    aftertax_cash_usd: list[float],
    debt_service_usd: list[float],
    debt_balance_usd: list[float],
    dscr: list[float],
) -> list[dict]:
    """Build a normalized annual cash-flow table from PySAM output sequences."""

    rows = []
    for idx, year in enumerate(years_index(analysis_years)):
        rows.append(
            {
                "year": year,
                "total_revenue_usd": float(revenue_usd[idx]),
                "aftertax_cashflow_usd": float(aftertax_cash_usd[idx]),
                "debt_service_usd": float(debt_service_usd[idx]),
                "debt_balance_usd": float(debt_balance_usd[idx]),
                "dscr": float(dscr[idx]),
            }
        )
    return rows
