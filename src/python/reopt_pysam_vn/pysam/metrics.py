"""Metric extraction helpers for Phase 4 PySAM result normalization."""

from __future__ import annotations

import math


def _clean_number(value: float) -> float | None:
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def _last_number(value) -> float | None:
    if isinstance(value, (list, tuple)):
        if not value:
            return None
        value = value[-1]
    return _clean_number(value)


def _percent_to_fraction(value) -> float | None:
    cleaned = _last_number(value)
    if cleaned is None:
        return None
    return cleaned / 100.0


def extract_single_owner_outputs(financial_model) -> dict:
    """Normalize the finance metrics used by the Phase 4 artifact."""

    outputs = financial_model.Outputs
    return {
        "project_return_aftertax_npv_usd": float(outputs.project_return_aftertax_npv),
        "project_return_aftertax_irr_fraction": _percent_to_fraction(
            outputs.project_return_aftertax_irr
        ),
        "project_return_pretax_npv_usd": _last_number(
            outputs.cf_project_return_pretax_npv
        ),
        "project_return_pretax_irr_fraction": _percent_to_fraction(
            outputs.cf_project_return_pretax_irr
        ),
        "size_of_debt_usd": float(outputs.size_of_debt),
        "debt_fraction": float(outputs.debt_fraction) / 100.0,
        "min_dscr": _clean_number(outputs.min_dscr),
        "npv_ppa_revenue_usd": float(outputs.npv_ppa_revenue),
    }
