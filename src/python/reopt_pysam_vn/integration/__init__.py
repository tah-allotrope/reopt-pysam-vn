"""Bridge modules spanning REopt and PySAM workflows."""

from reopt_pysam_vn.integration.ninhsim_solar_storage_60pct import (
    build_combined_decision_artifact,
    build_ninhsim_60pct_analysis,
    build_target_fraction_candidates,
    calculate_ninhsim_coverage_summary,
    calculate_ninhsim_developer_revenue_path,
    calculate_ninhsim_fixed_strike,
)

__all__ = [
    "build_combined_decision_artifact",
    "build_ninhsim_60pct_analysis",
    "build_target_fraction_candidates",
    "calculate_ninhsim_coverage_summary",
    "calculate_ninhsim_developer_revenue_path",
    "calculate_ninhsim_fixed_strike",
]
