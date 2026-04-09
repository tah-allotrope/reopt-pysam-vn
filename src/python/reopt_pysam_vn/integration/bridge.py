"""Schema bridges between REopt outputs and PySAM finance inputs."""

from __future__ import annotations

from typing import Any

from reopt_pysam_vn.integration.assumptions import DEFAULT_TARGET_DEVELOPER_IRR_FRACTION
from reopt_pysam_vn.integration.ninhsim_solar_storage_60pct import (
    calculate_ninhsim_developer_revenue_path,
    calculate_ninhsim_fixed_strike,
    calculate_ninhsim_coverage_summary,
)
from reopt_pysam_vn.pysam.config import build_vietnam_finance_defaults
from reopt_pysam_vn.pysam.ppa import convert_vnd_to_usd
from reopt_pysam_vn.pysam.single_owner import (
    SingleOwnerInputs,
    build_single_owner_inputs,
)
from reopt_pysam_vn.reopt.preprocess import VNData, load_vietnam_data


def _float_list(values: list[Any]) -> list[float]:
    return [float(value) for value in values]


def _sum_series(*series_groups: list[float]) -> list[float]:
    lengths = {len(series) for series in series_groups}
    if len(lengths) != 1:
        raise ValueError(
            f"Generation series length mismatch in bridge inputs: {sorted(lengths)}"
        )
    return [sum(values) for values in zip(*series_groups)]


def _value_or_default(container: dict, key: str, default: float) -> float:
    value = container.get(key)
    if value is None:
        return float(default)
    return float(value)


def _build_ninhsim_generation_profile_kw(reopt_results: dict) -> list[float]:
    pv_to_load = _float_list(
        reopt_results.get("PV", {}).get("electric_to_load_series_kw", [])
    )
    wind_to_load = _float_list(
        reopt_results.get("Wind", {}).get("electric_to_load_series_kw", [])
    )
    storage_to_load = _float_list(
        reopt_results.get("ElectricStorage", {}).get("storage_to_load_series_kw", [])
    )

    if not pv_to_load or not wind_to_load or not storage_to_load:
        raise ValueError(
            "Ninhsim Phase 4 bridge requires PV, Wind, and ElectricStorage delivery series."
        )

    return _sum_series(pv_to_load, wind_to_load, storage_to_load)


def _build_solar_storage_generation_profile_kw(reopt_results: dict) -> list[float]:
    pv_to_load = _float_list(
        reopt_results.get("PV", {}).get("electric_to_load_series_kw", [])
    )
    storage_to_load = _float_list(
        reopt_results.get("ElectricStorage", {}).get("storage_to_load_series_kw", [])
    )
    pv_to_grid = _float_list(
        reopt_results.get("PV", {}).get("electric_to_grid_series_kw", [])
    )

    if not pv_to_load:
        raise ValueError(
            "Ninhsim 60% bridge requires PV.electric_to_load_series_kw in the REopt results."
        )
    if not storage_to_load:
        raise ValueError(
            "Ninhsim 60% bridge requires ElectricStorage.storage_to_load_series_kw in the REopt results."
        )
    if not pv_to_grid:
        pv_to_grid = [0.0] * len(pv_to_load)

    return _sum_series(pv_to_load, storage_to_load, pv_to_grid)


def _recommended_candidate(commercial_memo: dict) -> dict:
    memo = commercial_memo["commercial_candidate_memo"]
    recommended_label = memo["recommended_band_label"]
    for candidate in memo["candidates"]:
        if candidate["band_label"] == recommended_label:
            return candidate
    raise ValueError(
        f"Recommended candidate '{recommended_label}' not found in commercial memo"
    )


def build_ninhsim_single_owner_inputs(
    reopt_results: dict,
    scenario: dict,
    commercial_memo: dict,
    vn_data: VNData | None = None,
) -> SingleOwnerInputs:
    """Map canonical Ninhsim artifacts into a runnable Phase 4 Single Owner input set."""

    vn = vn_data or load_vietnam_data()
    defaults = build_vietnam_finance_defaults(vn)
    candidate = _recommended_candidate(commercial_memo)
    financial = scenario.get("Financial", {})
    generation_profile_kw = _build_ninhsim_generation_profile_kw(reopt_results)

    pv_size_kw = float(reopt_results.get("PV", {}).get("size_kw") or 0.0)
    wind_size_kw = float(reopt_results.get("Wind", {}).get("size_kw") or 0.0)
    storage_initial_capital_cost = float(
        reopt_results.get("ElectricStorage", {}).get("initial_capital_cost") or 0.0
    )

    fixed_om_usd_per_year = (
        pv_size_kw * float(scenario["PV"]["om_cost_per_kw"])
        + wind_size_kw * float(scenario["Wind"]["om_cost_per_kw"])
        + storage_initial_capital_cost
        * float(scenario["ElectricStorage"]["om_cost_fraction_of_installed_cost"])
    )

    ppa_price_vnd_per_kwh = float(candidate["year_one_cppa_strike_vnd_per_kwh"])

    return build_single_owner_inputs(
        system_capacity_kw=pv_size_kw + wind_size_kw,
        generation_profile_kw=generation_profile_kw,
        annual_generation_kwh=sum(generation_profile_kw),
        installed_cost_usd=float(
            reopt_results.get("Financial", {}).get(
                "initial_capital_costs_after_incentives"
            )
            or reopt_results.get("Financial", {}).get("initial_capital_costs")
            or 0.0
        ),
        fixed_om_usd_per_year=fixed_om_usd_per_year,
        ppa_price_input_usd_per_kwh=convert_vnd_to_usd(
            ppa_price_vnd_per_kwh,
            vn.exchange_rate,
        ),
        analysis_years=int(financial.get("analysis_years") or defaults.analysis_years),
        debt_fraction=defaults.debt_fraction,
        target_irr_fraction=DEFAULT_TARGET_DEVELOPER_IRR_FRACTION,
        owner_tax_rate_fraction=_value_or_default(
            financial,
            "owner_tax_rate_fraction",
            defaults.owner_tax_rate_fraction,
        ),
        owner_discount_rate_fraction=_value_or_default(
            financial,
            "owner_discount_rate_fraction",
            defaults.owner_discount_rate_fraction,
        ),
        offtaker_discount_rate_fraction=_value_or_default(
            financial,
            "offtaker_discount_rate_fraction",
            defaults.offtaker_discount_rate_fraction,
        ),
        inflation_rate_fraction=defaults.inflation_rate_fraction,
        debt_interest_rate_fraction=defaults.debt_interest_rate_fraction,
        debt_tenor_years=defaults.debt_tenor_years,
        ppa_escalation_rate_fraction=_value_or_default(
            financial,
            "elec_cost_escalation_rate_fraction",
            defaults.elec_cost_escalation_rate_fraction,
        ),
        om_escalation_rate_fraction=_value_or_default(
            financial,
            "om_cost_escalation_rate_fraction",
            defaults.om_cost_escalation_rate_fraction,
        ),
        depreciation_schedule=defaults.depreciation_schedule,
        metadata={
            "source_case": "ninhsim",
            "recommended_band_label": candidate["band_label"],
            "year_one_ppa_price_vnd_per_kwh": ppa_price_vnd_per_kwh,
            "developer_revenue_npv_usd": float(candidate["developer_revenue_npv_usd"]),
            "customer_savings_npv_usd": float(candidate["customer_savings_npv_usd"]),
            "reopt_npv_usd": float(
                reopt_results.get("Financial", {}).get("npv") or 0.0
            ),
        },
    )


def build_ninhsim_solar_storage_single_owner_inputs(
    reopt_results: dict,
    scenario: dict,
    extracted: dict,
    vn_data: VNData | None = None,
) -> SingleOwnerInputs:
    """Map the Ninhsim 60% solar-storage workflow into a Single Owner input set."""

    vn = vn_data or load_vietnam_data()
    defaults = build_vietnam_finance_defaults(vn)
    financial = scenario.get("Financial", {})
    fixed_strike = calculate_ninhsim_fixed_strike(reopt_results, extracted)
    coverage = calculate_ninhsim_coverage_summary(
        reopt_results,
        extracted,
        target_fraction=float(
            scenario.get("_meta", {}).get(
                "requested_renewable_delivered_fraction_of_load", 0.60
            )
        ),
        enforced_target_fraction=float(
            scenario.get("Site", {}).get("renewable_electricity_min_fraction", 0.60)
        ),
    )
    revenue_path = calculate_ninhsim_developer_revenue_path(
        reopt_results,
        extracted,
        fixed_strike,
        analysis_years=int(financial.get("analysis_years") or defaults.analysis_years),
    )
    generation_profile_kw = _build_solar_storage_generation_profile_kw(reopt_results)

    pv_size_kw = float(reopt_results.get("PV", {}).get("size_kw") or 0.0)
    storage_initial_capital_cost = float(
        reopt_results.get("ElectricStorage", {}).get("initial_capital_cost") or 0.0
    )
    fixed_om_usd_per_year = pv_size_kw * float(
        scenario["PV"]["om_cost_per_kw"]
    ) + storage_initial_capital_cost * float(
        scenario["ElectricStorage"]["om_cost_fraction_of_installed_cost"]
    )

    year_one = revenue_path[0]
    realized_price_usd_per_kwh = float(year_one["realized_blended_price_usd_per_kwh"])
    realized_price_vnd_per_kwh = float(year_one["realized_blended_price_vnd_per_kwh"])

    return build_single_owner_inputs(
        system_capacity_kw=pv_size_kw,
        generation_profile_kw=generation_profile_kw,
        annual_generation_kwh=sum(generation_profile_kw),
        installed_cost_usd=float(
            reopt_results.get("Financial", {}).get(
                "initial_capital_costs_after_incentives"
            )
            or reopt_results.get("Financial", {}).get("initial_capital_costs")
            or 0.0
        ),
        fixed_om_usd_per_year=fixed_om_usd_per_year,
        ppa_price_input_usd_per_kwh=realized_price_usd_per_kwh,
        analysis_years=int(financial.get("analysis_years") or defaults.analysis_years),
        debt_fraction=defaults.debt_fraction,
        target_irr_fraction=DEFAULT_TARGET_DEVELOPER_IRR_FRACTION,
        owner_tax_rate_fraction=_value_or_default(
            financial,
            "owner_tax_rate_fraction",
            defaults.owner_tax_rate_fraction,
        ),
        owner_discount_rate_fraction=_value_or_default(
            financial,
            "owner_discount_rate_fraction",
            defaults.owner_discount_rate_fraction,
        ),
        offtaker_discount_rate_fraction=_value_or_default(
            financial,
            "offtaker_discount_rate_fraction",
            defaults.offtaker_discount_rate_fraction,
        ),
        inflation_rate_fraction=defaults.inflation_rate_fraction,
        debt_interest_rate_fraction=defaults.debt_interest_rate_fraction,
        debt_tenor_years=defaults.debt_tenor_years,
        ppa_escalation_rate_fraction=_value_or_default(
            financial,
            "elec_cost_escalation_rate_fraction",
            defaults.elec_cost_escalation_rate_fraction,
        ),
        om_escalation_rate_fraction=_value_or_default(
            financial,
            "om_cost_escalation_rate_fraction",
            defaults.om_cost_escalation_rate_fraction,
        ),
        depreciation_schedule=defaults.depreciation_schedule,
        metadata={
            "source_case": "ninhsim_60pct_solar_storage",
            "requested_target_fraction": float(
                scenario.get("_meta", {}).get(
                    "requested_renewable_delivered_fraction_of_load", 0.60
                )
            ),
            "enforced_target_fraction": float(
                scenario.get("Site", {}).get("renewable_electricity_min_fraction", 0.60)
            ),
            "achieved_delivered_fraction_of_load": float(
                coverage["achieved_delivered_fraction_of_load"]
            ),
            "year_one_strike_vnd_per_kwh": float(
                fixed_strike["year_one_strike_vnd_per_kwh"]
            ),
            "year_one_realized_price_vnd_per_kwh": realized_price_vnd_per_kwh,
            "year_one_customer_price_vnd_per_kwh": float(
                fixed_strike["year_one_strike_vnd_per_kwh"]
            ),
            "year_one_merchant_price_vnd_per_kwh": float(
                year_one["merchant_price_vnd_per_kwh"]
            ),
            "year_one_customer_served_kwh": float(year_one["renewable_delivered_kwh"]),
            "year_one_merchant_sold_kwh": float(year_one["merchant_sold_kwh"]),
            "developer_revenue_npv_usd": float(
                sum(entry["developer_revenue_usd"] for entry in revenue_path)
            ),
            "reopt_npv_usd": float(
                reopt_results.get("Financial", {}).get("npv") or 0.0
            ),
        },
    )
