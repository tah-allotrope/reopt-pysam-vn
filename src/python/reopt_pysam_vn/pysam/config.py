"""Configuration helpers for PySAM-backed Vietnam finance workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PySAMRuntimeConfig:
    """Minimal runtime configuration for PySAM model assembly."""

    model_name: str = "SingleOwner"
    currency: str = "USD"
    country: str = "Vietnam"
