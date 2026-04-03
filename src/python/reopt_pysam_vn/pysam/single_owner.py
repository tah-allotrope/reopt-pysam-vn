"""Single Owner entry points for PySAM finance modeling."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SingleOwnerInputs:
    """Normalized developer-finance inputs for the initial PySAM MVP."""

    system_capacity_kw: float
    analysis_years: int = 20
    debt_fraction: float = 0.7
    target_irr_fraction: float = 0.15
    metadata: dict = field(default_factory=dict)


def build_single_owner_inputs(
    system_capacity_kw: float, **overrides
) -> SingleOwnerInputs:
    """Create a normalized Single Owner input bundle.

    This intentionally stops short of invoking PySAM until the finance mapping layer lands.
    """

    return SingleOwnerInputs(system_capacity_kw=system_capacity_kw, **overrides)
