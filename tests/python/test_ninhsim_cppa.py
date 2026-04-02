"""
Regression tests for the Ninhsim bundled-CPPA optimization workflow.
"""

import math
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "python"))

from analyze_ninhsim_cppa import (  # noqa: E402
    build_commercial_candidate_memo,
    build_summary,
    calculate_customer_first_annual_path,
    calculate_cppa_sensitivity_bands,
    calculate_customer_bill_breakdown,
    calculate_customer_equivalent_strike,
    calculate_financial_screening_view,
    calculate_multi_year_cppa_path,
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


def test_multi_year_cppa_path_escalates_with_evn_tariff_growth():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    path = calculate_multi_year_cppa_path(results, extracted, analysis_years=4)

    assert path[0]["year"] == 1
    assert math.isclose(
        path[0]["cPPA_strike_usd_per_kwh"],
        calculate_customer_equivalent_strike(results, extracted)[
            "max_cppa_strike_usd_per_kwh"
        ],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        path[1]["weighted_evn_benchmark_usd_per_kwh"],
        path[0]["weighted_evn_benchmark_usd_per_kwh"] * 1.05,
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        path[3]["cPPA_strike_usd_per_kwh"],
        path[0]["cPPA_strike_usd_per_kwh"] * (1.05**3),
        rel_tol=0,
        abs_tol=1e-12,
    )
    for year in path:
        assert math.isclose(
            year["customer_blended_price_usd_per_kwh"],
            year["weighted_evn_benchmark_usd_per_kwh"],
            rel_tol=0,
            abs_tol=1e-12,
        )


def test_build_summary_includes_multi_year_cppa_path():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    summary = build_summary(results, extracted)

    assert summary["multi_year_cppa_path"]
    assert summary["multi_year_cppa_path"][0]["year"] == 1
    assert summary["multi_year_cppa_path"][-1]["year"] == 20


def test_financial_screening_view_projects_customer_cost_and_developer_revenue():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    view = calculate_financial_screening_view(results, extracted, analysis_years=3)

    assert view[0]["year"] == 1
    assert view[0]["developer_revenue_usd"] > 0.0
    assert math.isclose(
        view[0]["customer_total_cost_usd"],
        extracted["benchmark"]["annual_load_kwh"]
        * extracted["benchmark"]["weighted_evn_price_usd_per_kwh"],
        rel_tol=0,
        abs_tol=1e-6,
    )
    assert view[2]["developer_revenue_usd"] > view[0]["developer_revenue_usd"]
    assert view[2]["customer_savings_vs_evn_usd"] == 0.0


def test_build_summary_includes_financial_screening_view_and_npv_fields():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    summary = build_summary(results, extracted)

    assert summary["financial_screening_view"]
    assert summary["financial"]["developer_revenue_npv_usd"] > 0.0
    assert summary["financial"]["offtaker_cost_npv_usd"] > 0.0


def test_cppa_sensitivity_bands_capture_savings_and_premium_tradeoffs():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    bands = calculate_cppa_sensitivity_bands(
        results,
        extracted,
        strike_adjustment_fractions=[-0.10, -0.05, 0.0, 0.05],
        analysis_years=2,
    )

    assert [band["band_label"] for band in bands] == [
        "10% below ceiling",
        "5% below ceiling",
        "ceiling",
        "5% above ceiling",
    ]
    assert bands[0]["customer_savings_npv_usd"] > 0.0
    assert bands[0]["customer_premium_npv_usd"] == 0.0
    assert bands[2]["customer_savings_npv_usd"] == 0.0
    assert bands[2]["customer_premium_npv_usd"] == 0.0
    assert bands[3]["customer_premium_npv_usd"] > 0.0
    assert bands[3]["developer_revenue_npv_usd"] > bands[2]["developer_revenue_npv_usd"]


def test_build_summary_includes_strike_sensitivity_band_view():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    summary = build_summary(results, extracted)

    assert summary["strike_sensitivity_bands"]
    assert summary["strike_sensitivity_bands"][0]["relative_to_ceiling_fraction"] < 0.0
    assert summary["strike_sensitivity_bands"][-1]["relative_to_ceiling_fraction"] > 0.0


def test_customer_first_annual_path_applies_degradation_load_drift_and_caps_customer_exposure():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    annual_path = calculate_customer_first_annual_path(
        results,
        extracted,
        strike_adjustment_fraction=-0.05,
        analysis_years=3,
        annual_generation_degradation_fraction=0.01,
        annual_load_growth_fraction=0.02,
        unmatched_energy_price_fraction_of_evn=0.35,
    )

    assert annual_path[0]["band_label"] == "5% below ceiling"
    assert (
        annual_path[1]["renewable_delivered_kwh"]
        < annual_path[0]["renewable_delivered_kwh"]
    )
    assert annual_path[1]["total_load_kwh"] > annual_path[0]["total_load_kwh"]
    assert (
        annual_path[1]["unmatched_renewable_kwh"]
        >= annual_path[0]["unmatched_renewable_kwh"]
    )
    assert annual_path[0]["customer_savings_vs_evn_usd"] > 0.0
    assert (
        annual_path[0]["merchant_price_usd_per_kwh"]
        < annual_path[0]["residual_grid_price_usd_per_kwh"]
    )
    assert (
        annual_path[0]["customer_total_cost_usd"]
        < annual_path[0]["benchmark_evn_cost_usd"]
    )


def test_build_summary_includes_customer_first_recommendation_and_annual_path():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    summary = build_summary(results, extracted)

    assert (
        summary["customer_first_recommendation"]["recommended_band_label"]
        == "5% below ceiling"
    )
    assert summary["customer_first_annual_path"]
    assert summary["customer_first_annual_path"][0]["band_label"] == "5% below ceiling"


def test_commercial_candidate_memo_marks_shortlist_as_advance_hold_discard():
    extracted = build_extracted_inputs()
    results = _synthetic_results()
    summary = build_summary(results, extracted)

    memo = build_commercial_candidate_memo(summary)

    candidates = {
        candidate["band_label"]: candidate for candidate in memo["candidates"]
    }
    assert memo["recommended_band_label"] == "5% below ceiling"
    assert candidates["5% below ceiling"]["status"] == "advance"
    assert candidates["ceiling"]["status"] == "hold"
    assert candidates["5% above ceiling"]["status"] == "discard"
    assert candidates["5% above ceiling"]["customer_premium_npv_usd"] > 0.0


def test_build_summary_includes_commercial_candidate_memo():
    extracted = build_extracted_inputs()
    results = _synthetic_results()

    summary = build_summary(results, extracted)

    assert summary["commercial_candidate_memo"]
    assert (
        summary["commercial_candidate_memo"]["recommended_band_label"]
        == "5% below ceiling"
    )
