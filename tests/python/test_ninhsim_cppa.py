"""
Regression tests for the Ninhsim bundled-CPPA optimization workflow.
"""

import math
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "python"))

from analyze_ninhsim_cppa import (  # noqa: E402
    build_summary,
    calculate_customer_bill_breakdown,
    calculate_customer_equivalent_strike,
)
from build_ninhsim_extracted_inputs import (  # noqa: E402
    PROJECT_SITE,
    build_extracted_inputs,
)
from build_ninhsim_reopt_input import (  # noqa: E402
    build_scenario_a,
    build_scenario_b,
)


def _synthetic_results() -> dict:
    renewable_to_load_kw = 10_000.0
    residual_grid_kw = 11_000.0
    return {
        "status": "optimal",
        "PV": {
            "size_kw": 18_000.0,
            "year_one_energy_produced_kwh": 40_000_000.0,
            "electric_to_load_series_kw": [6_000.0] * 8760,
            "electric_to_grid_series_kw": [200.0] * 8760,
        },
        "Wind": {
            "size_kw": 12_000.0,
            "year_one_energy_produced_kwh": 32_000_000.0,
            "electric_to_load_series_kw": [3_000.0] * 8760,
        },
        "ElectricStorage": {
            "size_kw": 4_000.0,
            "size_kwh": 16_000.0,
            "storage_to_load_series_kw": [1_000.0] * 8760,
        },
        "ElectricUtility": {
            "electric_to_load_series_kw": [residual_grid_kw] * 8760,
        },
        "Financial": {
            "npv": 12_500_000.0,
            "year_one_total_operating_cost_savings_before_tax": 1_700_000.0,
        },
        "_test_total_load_series_kw": [renewable_to_load_kw + residual_grid_kw] * 8760,
    }


def test_build_extracted_inputs_cleans_load_and_computes_weighted_evn_benchmark():
    extracted = build_extracted_inputs()

    assert extracted["project"].startswith("Ninhsim")
    assert extracted["site"] == PROJECT_SITE
    assert len(extracted["loads_kw"]) == 8760
    assert min(extracted["loads_kw"]) > 0.0
    assert extracted["load_cleaning"]["missing_count"] == 1
    assert extracted["load_cleaning"]["final_count"] == 8760
    assert math.isclose(
        extracted["benchmark"]["weighted_evn_price_usd_per_kwh"],
        0.076473,
        rel_tol=0,
        abs_tol=1e-6,
    )


def test_scenario_builders_preserve_capex_and_enable_wind_optimization():
    extracted = build_extracted_inputs()

    scenario_a = build_scenario_a(extracted)
    scenario_b = build_scenario_b(extracted)

    assert scenario_a["Site"] == {
        "latitude": PROJECT_SITE["latitude"],
        "longitude": PROJECT_SITE["longitude"],
    }
    assert scenario_a["_meta"]["site"] == PROJECT_SITE
    assert scenario_a["PV"]["installed_cost_per_kw"] == 750.0
    assert scenario_a["ElectricStorage"]["installed_cost_per_kw"] == 200.0
    assert scenario_a["ElectricStorage"]["installed_cost_per_kwh"] == 200.0
    assert scenario_a["Wind"]["installed_cost_per_kw"] == 1350.0
    assert scenario_a["Wind"]["max_kw"] == 0.0
    assert scenario_a["Financial"]["analysis_years"] == 20

    assert scenario_b["PV"]["min_kw"] == 0.0
    assert scenario_b["PV"]["max_kw"] > 0.0
    assert scenario_b["Wind"]["min_kw"] == 0.0
    assert scenario_b["Wind"]["max_kw"] > 0.0
    assert scenario_b["ElectricStorage"]["min_kwh"] == 0.0
    assert scenario_b["PV"].get("production_factor_series") is None


def test_customer_equivalent_strike_matches_weighted_price_target():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    bill = calculate_customer_bill_breakdown(results, extracted)
    strike = calculate_customer_equivalent_strike(results, extracted)

    assert bill["renewable_delivered_kwh"] == 87_600_000.0
    assert bill["grid_supplied_kwh"] == 96_360_000.0
    assert strike["max_cppa_strike_usd_per_kwh"] > 0.0
    assert (
        strike["max_cppa_strike_vnd_per_kwh"]
        > extracted["benchmark"]["wholesale_rate_vnd_per_kwh"]
    )
    assert math.isclose(
        strike["customer_blended_price_at_max_strike_usd_per_kwh"],
        extracted["benchmark"]["weighted_evn_price_usd_per_kwh"],
        rel_tol=0,
        abs_tol=1e-9,
    )


def test_build_summary_accepts_wind_annual_energy_key():
    extracted = build_extracted_inputs()
    results = _synthetic_results()
    results["Wind"].pop("year_one_energy_produced_kwh")
    results["Wind"]["annual_energy_produced_kwh"] = 32_000_000.0

    summary = build_summary(results, extracted)

    assert math.isclose(summary["year_one_energy"]["wind_gwh"], 32.0, abs_tol=1e-9)
