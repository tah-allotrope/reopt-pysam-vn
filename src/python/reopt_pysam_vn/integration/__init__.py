"""Bridge modules spanning REopt and PySAM workflows."""

from reopt_pysam_vn.integration.dppa_case_2 import (
    build_dppa_case_2_assumptions_register,
    build_dppa_case_2_buyer_benchmark,
    build_dppa_case_2_edge_case_matrix,
    build_dppa_case_2_market_proxy,
    build_dppa_case_2_physical_summary,
    build_dppa_case_2_phase_a_definition,
    build_dppa_case_2_settlement_inputs,
    build_dppa_case_2_settlement_design,
    build_dppa_case_2_settlement_schema,
    build_scenario_dppa_case_2,
    run_dppa_case_2_buyer_settlement,
)
from reopt_pysam_vn.integration.ninhsim_solar_storage_60pct import (
    build_combined_decision_artifact,
    build_ninhsim_60pct_analysis,
    build_target_fraction_candidates,
    calculate_ninhsim_coverage_summary,
    calculate_ninhsim_developer_revenue_path,
    calculate_ninhsim_fixed_strike,
)

__all__ = [
    "build_dppa_case_2_assumptions_register",
    "build_dppa_case_2_buyer_benchmark",
    "build_dppa_case_2_edge_case_matrix",
    "build_dppa_case_2_market_proxy",
    "build_dppa_case_2_physical_summary",
    "build_dppa_case_2_phase_a_definition",
    "build_dppa_case_2_settlement_inputs",
    "build_dppa_case_2_settlement_design",
    "build_dppa_case_2_settlement_schema",
    "build_scenario_dppa_case_2",
    "run_dppa_case_2_buyer_settlement",
    "build_combined_decision_artifact",
    "build_ninhsim_60pct_analysis",
    "build_target_fraction_candidates",
    "calculate_ninhsim_coverage_summary",
    "calculate_ninhsim_developer_revenue_path",
    "calculate_ninhsim_fixed_strike",
]
