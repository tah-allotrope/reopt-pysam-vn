"""Helpers for Ninhsim DPPA Case 2 definition, physical summary, and settlement."""

from __future__ import annotations

from reopt_pysam_vn.reopt.preprocess import apply_vietnam_defaults, load_vietnam_data

DEFAULT_STRIKE_DISCOUNT_FRACTION = 0.05
DEFAULT_STRIKE_ESCALATION_FRACTION = 0.05
DEFAULT_DPPA_ADDER_VND_PER_KWH = 523.34
DEFAULT_KPP_FACTOR = 1.027263
DEFAULT_SETTLEMENT_QUANTITY_RULE = "min_load_and_contracted_generation"
DEFAULT_EXCESS_GENERATION_TREATMENT = "excluded_from_buyer_settlement"
DEFAULT_CONTRACT_STRUCTURE = "synthetic_financial_dppa"
DEFAULT_MARKET_PRICE_SOURCE_PRIORITY = [
    "actual_hourly_cfmp_or_fmp_series",
    "repo_proxy_hourly_series",
]


def _pad_to_8760(series: list[float]) -> list[float]:
    if len(series) >= 8760:
        return [float(value) for value in series[:8760]]
    return [float(value) for value in series] + [0.0] * (8760 - len(series))


def _sum_series(*series_list: list[float]) -> list[float]:
    padded = [_pad_to_8760(series) for series in series_list]
    return [sum(values) for values in zip(*padded)]


def _annual_energy_kwh(tech_results: dict) -> float:
    return float(
        tech_results.get("year_one_energy_produced_kwh")
        or tech_results.get("annual_energy_produced_kwh")
        or 0.0
    )


def _financial_value(results: dict, key: str, default: float) -> float:
    return float(results.get("Financial", {}).get(key) or default)


def _proxy_market_fraction(extracted: dict) -> float:
    weighted = float(extracted["benchmark"]["weighted_evn_price_vnd_per_kwh"])
    wholesale = float(extracted["benchmark"].get("wholesale_rate_vnd_per_kwh") or 0.0)
    return wholesale / weighted if weighted else 0.0


def _load_series(values: list[float]) -> list[float]:
    return [float(value) for value in values]


def _load_retail_series(extracted: dict) -> list[float]:
    return _load_series(extracted["evn_tariff"]["tou_energy_rates_vnd_per_kwh"])


def _pad_to_length(series: list[float], length: int) -> list[float]:
    values = [float(value) for value in series[:length]]
    if len(values) < length:
        values.extend([0.0] * (length - len(values)))
    return values


def _sum_series_to_length(length: int, *series_list: list[float]) -> list[float]:
    padded = [_pad_to_length(series, length) for series in series_list]
    return [sum(values) for values in zip(*padded)]


def _load_reopt_delivery_profile(results: dict) -> list[float]:
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    storage = results.get("ElectricStorage", {})
    return _sum_series(
        pv.get("electric_to_load_series_kw", []),
        wind.get("electric_to_load_series_kw", []),
        storage.get("storage_to_load_series_kw", []),
    )


def _load_reopt_export_profile(results: dict) -> list[float]:
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    return _sum_series(
        pv.get("electric_to_grid_series_kw", []),
        wind.get("electric_to_grid_series_kw", []),
    )


def _load_reopt_charge_profile(results: dict) -> list[float]:
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    return _sum_series(
        pv.get("electric_to_storage_series_kw", []),
        wind.get("electric_to_storage_series_kw", []),
    )


def _load_reopt_curtailment_profile(results: dict) -> list[float]:
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    return _sum_series(
        pv.get("electric_curtailed_series_kw", []),
        wind.get("electric_curtailed_series_kw", []),
    )


def _load_reopt_grid_supply_profile(results: dict) -> list[float]:
    utility = results.get("ElectricUtility", {})
    return _pad_to_8760(utility.get("electric_to_load_series_kw", []))


def _strike_vnd_per_kwh(
    extracted: dict,
    strike_discount_fraction: float = DEFAULT_STRIKE_DISCOUNT_FRACTION,
) -> float:
    weighted_vnd = float(extracted["benchmark"]["weighted_evn_price_vnd_per_kwh"])
    return weighted_vnd * (1.0 - float(strike_discount_fraction))


def _strike_usd_per_kwh(
    extracted: dict,
    strike_discount_fraction: float = DEFAULT_STRIKE_DISCOUNT_FRACTION,
) -> float:
    weighted_usd = float(extracted["benchmark"]["weighted_evn_price_usd_per_kwh"])
    return weighted_usd * (1.0 - float(strike_discount_fraction))


def build_dppa_case_2_phase_a_definition(extracted: dict) -> dict:
    strike_vnd = _strike_vnd_per_kwh(extracted)
    strike_usd = _strike_usd_per_kwh(extracted)
    return {
        "model": "Ninhsim DPPA Case 2 Phase A Definition",
        "status": "agreed_user_reviewed",
        "case_identity": {
            "scenario_family": "DPPA Case 2",
            "slug": "ninhsim_dppa_case_2",
            "contract_structure": DEFAULT_CONTRACT_STRUCTURE,
            "project_basis": "ninhsim_8760_load_reuse",
            "customer_priority": "customer_best_interest_first",
            "main_business_questions": [
                "buyer_all_in_cost_vs_evn",
                "developer_finance_at_negotiated_strike",
                "contract_shape_risk_minimization",
            ],
        },
        "site_load_basis": {
            "site": dict(extracted["site"]),
            "annual_load_kwh": float(extracted["benchmark"]["annual_load_kwh"]),
            "annual_load_gwh": float(extracted["benchmark"]["annual_load_gwh"]),
            "load_profile_source": extracted.get("source_load_path"),
            "tariff_source": extracted.get("source_tariff_path"),
        },
        "strike_basis": {
            "anchor": "weighted_evn_tariff_discount",
            "strike_discount_fraction": float(DEFAULT_STRIKE_DISCOUNT_FRACTION),
            "weighted_evn_price_vnd_per_kwh": float(
                extracted["benchmark"]["weighted_evn_price_vnd_per_kwh"]
            ),
            "weighted_evn_price_usd_per_kwh": float(
                extracted["benchmark"]["weighted_evn_price_usd_per_kwh"]
            ),
            "year_one_strike_vnd_per_kwh": strike_vnd,
            "year_one_strike_usd_per_kwh": strike_usd,
            "strike_escalation_basis": "matches_case_financial_electricity_escalation",
            "default_strike_escalation_fraction": float(
                DEFAULT_STRIKE_ESCALATION_FRACTION
            ),
        },
        "physical_scope": {
            "technologies_in_scope": ["PV", "ElectricStorage", "ElectricUtility"],
            "technologies_out_of_scope": ["Wind", "Generator", "Resilience"],
            "battery_requirement": "reopt_may_optimize_storage_away",
            "export_posture": "reported_separately_not_settled_to_buyer",
        },
        "decision_metrics": {
            "primary_metrics": [
                "buyer_savings_vs_evn",
                "project_irr",
                "payback_years",
            ],
            "secondary_metrics": [
                "matched_renewable_delivery",
                "developer_finance_review",
                "contract_shape_risk",
            ],
        },
    }


def build_dppa_case_2_assumptions_register(extracted: dict) -> dict:
    strike_vnd = _strike_vnd_per_kwh(extracted)
    return {
        "model": "Ninhsim DPPA Case 2 Phase A Assumptions Register",
        "status": "agreed_user_reviewed",
        "questions": {
            "business_questions": {
                "selected_answer": "buyer_cost_developer_finance_and_contract_risk",
                "summary": [
                    "Can a synthetic DPPA lower buyer all-in cost versus EVN?",
                    "Can a synthetic DPPA work for developer at one negotiated strike?",
                    "What contract shape minimizes buyer excess-settlement risk?",
                ],
            },
            "contract_structure": {
                "selected_answer": DEFAULT_CONTRACT_STRUCTURE,
                "summary": "Synthetic / financial DPPA is the only structure in scope for Case 2.",
            },
            "settlement_quantity_rule": {
                "selected_answer": DEFAULT_SETTLEMENT_QUANTITY_RULE,
                "summary": "Match quantity equals min(load, contracted generation) in each interval.",
            },
            "excess_generation_treatment": {
                "selected_answer": DEFAULT_EXCESS_GENERATION_TREATMENT,
                "summary": "Excess generation is reported separately and excluded from buyer settlement.",
            },
            "strike_treatment": {
                "selected_answer": "five_percent_below_weighted_evn_with_escalation",
                "summary": (
                    f"Year-one strike anchors at {strike_vnd:.6f} VND/kWh, or 5% below the current Ninhsim weighted EVN tariff, with escalation logic retained."
                ),
            },
            "adder_and_kpp": {
                "selected_answer": "fixed_dppa_adder_and_fixed_kpp",
                "summary": (
                    f"Use fixed DPPA adder {DEFAULT_DPPA_ADDER_VND_PER_KWH:.2f} VND/kWh and fixed KPP {DEFAULT_KPP_FACTOR:.6f} in the first pass."
                ),
            },
            "market_price_source": {
                "selected_answer": "actual_fmp_cfmp_if_available_else_proxy",
                "summary": "Prefer actual hourly FMP/CFMP series; fall back to a proxy series from repo data only if no trusted actual series is available.",
            },
            "battery_requirement": {
                "selected_answer": "allow_reopt_to_optimize_storage_away",
                "summary": "Battery is optional; PV-only remains a valid outcome if REopt does not select storage.",
            },
            "reopt_objective": {
                "selected_answer": "minimum_buyer_cost_plus_maximum_matched_renewable_delivery",
                "summary": "Physical solve should favor minimum buyer cost under physical constraints while maximizing matched renewable delivery.",
            },
            "pysam_scope": {
                "selected_answer": "full_buyer_plus_developer_workflow_in_one_pass",
                "summary": "The first implementation pass should include PySAM rather than deferring developer-side validation.",
            },
            "pass_fail_metrics": {
                "selected_answer": "buyer_savings_project_irr_payback_years",
                "summary": "Primary pass/fail metrics are buyer savings, project IRR, and payback years.",
            },
            "customer_priority": {
                "selected_answer": "customer_best_interest_over_nonfinanceable_overlap",
                "summary": "Customer best interest remains the reporting priority even if no financeable developer overlap appears.",
            },
        },
        "known_open_inputs": [
            "Identify whether trusted Ninhsim hourly FMP/CFMP data exists locally or requires external research.",
            "Confirm the exact proxy source to use if actual Ninhsim market series cannot be sourced.",
        ],
    }


def build_dppa_case_2_settlement_design(
    phase_a_definition: dict,
    assumptions_register: dict,
) -> dict:
    strike = phase_a_definition["strike_basis"]
    return {
        "model": "Ninhsim DPPA Case 2 Phase B Settlement Design",
        "status": "draft_ready_for_implementation",
        "contract_structure": phase_a_definition["case_identity"]["contract_structure"],
        "hourly_settlement": {
            "settlement_quantity_rule": DEFAULT_SETTLEMENT_QUANTITY_RULE,
            "excess_generation_treatment": DEFAULT_EXCESS_GENERATION_TREATMENT,
            "matched_quantity_formula": "min(load_kwh, contracted_generation_kwh)",
            "shortfall_quantity_formula": "max(0, load_kwh - matched_quantity_kwh)",
            "excess_quantity_formula": "max(0, contracted_generation_kwh - matched_quantity_kwh)",
            "buyer_evn_matched_payment_formula": "matched_quantity_kwh * market_reference_price_vnd_per_kwh * kpp_factor",
            "buyer_dppa_charge_formula": "matched_quantity_kwh * dppa_adder_vnd_per_kwh",
            "buyer_shortfall_payment_formula": "shortfall_quantity_kwh * evn_retail_rate_vnd_per_kwh",
            "buyer_cfd_formula": "matched_quantity_kwh * (strike_price_vnd_per_kwh - market_reference_price_vnd_per_kwh)",
            "buyer_total_payment_formula": "evn_matched_payment + dppa_charge + shortfall_payment + buyer_cfd_payment",
            "buyer_blended_cost_formula": "buyer_total_payment / total_consumed_load_kwh",
            "negative_cfd_credit_allowed": True,
        },
        "fixed_parameters": {
            "year_one_strike_vnd_per_kwh": float(strike["year_one_strike_vnd_per_kwh"]),
            "year_one_strike_usd_per_kwh": float(strike["year_one_strike_usd_per_kwh"]),
            "strike_discount_fraction": float(strike["strike_discount_fraction"]),
            "strike_escalation_fraction": float(
                strike["default_strike_escalation_fraction"]
            ),
            "dppa_adder_vnd_per_kwh": float(DEFAULT_DPPA_ADDER_VND_PER_KWH),
            "kpp_factor": float(DEFAULT_KPP_FACTOR),
        },
        "market_price_source_priority": list(DEFAULT_MARKET_PRICE_SOURCE_PRIORITY),
        "market_price_source_notes": [
            "Use actual hourly CFMP or FMP series if available for Ninhsim or a credible directly transferable benchmark.",
            "If no trusted actual series is available, build a documented proxy series from repo data and mark it as provisional.",
        ],
        "separate_outputs": {
            "buyer_view": [
                "buyer_total_payment_vnd",
                "buyer_blended_cost_vnd_per_kwh",
                "buyer_savings_vs_evn_vnd",
                "buyer_cfd_payment_vnd",
                "buyer_shortfall_payment_vnd",
            ],
            "developer_view": [
                "developer_strike_revenue_vnd",
                "project_irr_fraction",
                "payback_years",
            ],
            "risk_view": [
                "matched_quantity_kwh",
                "shortfall_quantity_kwh",
                "excess_quantity_kwh",
                "hours_with_negative_cfd_credit",
            ],
        },
        "assumptions_trace": assumptions_register["questions"],
    }


def build_dppa_case_2_settlement_schema() -> dict:
    hourly_series = {
        "type": "array",
        "minItems": 8760,
        "maxItems": 8760,
        "items": {"type": "number"},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Ninhsim DPPA Case 2 Settlement Input Schema",
        "type": "object",
        "required": [
            "matched_quantity_rule",
            "excess_generation_treatment",
            "load_kwh_series",
            "contracted_generation_kwh_series",
            "market_reference_price_vnd_per_kwh_series",
            "evn_retail_rate_vnd_per_kwh_series",
            "strike_price_vnd_per_kwh",
            "dppa_adder_vnd_per_kwh",
            "kpp_factor",
        ],
        "properties": {
            "settlement_quantity_rule": {
                "type": "string",
                "enum": [DEFAULT_SETTLEMENT_QUANTITY_RULE],
            },
            "matched_quantity_rule": {
                "type": "string",
                "enum": [DEFAULT_SETTLEMENT_QUANTITY_RULE],
            },
            "excess_generation_treatment": {
                "type": "string",
                "enum": [DEFAULT_EXCESS_GENERATION_TREATMENT],
            },
            "market_reference_price_type": {
                "type": "string",
                "enum": ["cfmp", "fmp", "proxy_cfmp_or_fmp"],
            },
            "load_kwh_series": hourly_series,
            "contracted_generation_kwh_series": hourly_series,
            "market_reference_price_vnd_per_kwh_series": hourly_series,
            "evn_retail_rate_vnd_per_kwh_series": hourly_series,
            "strike_price_vnd_per_kwh": {"type": "number"},
            "dppa_adder_vnd_per_kwh": {"type": "number"},
            "kpp_factor": {"type": "number"},
            "notes": {"type": "array", "items": {"type": "string"}},
        },
    }


def build_dppa_case_2_edge_case_matrix() -> dict:
    return {
        "model": "Ninhsim DPPA Case 2 Phase B Edge Case Matrix",
        "status": "draft_ready_for_tests",
        "cases": [
            {
                "case_name": "matched_hour_with_positive_buyer_cfd",
                "inputs": {
                    "load_kwh": 1000.0,
                    "contracted_generation_kwh": 800.0,
                    "market_reference_price_vnd_per_kwh": 1700.0,
                    "strike_price_vnd_per_kwh": 1917.9345481618014,
                },
                "expected_behavior": "Buyer pays positive CfD top-up on matched quantity only.",
            },
            {
                "case_name": "matched_hour_with_negative_buyer_cfd_credit",
                "inputs": {
                    "load_kwh": 1000.0,
                    "contracted_generation_kwh": 800.0,
                    "market_reference_price_vnd_per_kwh": 2200.0,
                    "strike_price_vnd_per_kwh": 1917.9345481618014,
                },
                "expected_behavior": "Buyer receives a negative CfD credit because market price is above strike on matched quantity.",
            },
            {
                "case_name": "shortfall_hour_with_retail_top_up",
                "inputs": {
                    "load_kwh": 1200.0,
                    "contracted_generation_kwh": 500.0,
                    "evn_retail_rate_vnd_per_kwh": 1895.49633,
                },
                "expected_behavior": "Shortfall quantity is billed at EVN retail tariff on top of the matched DPPA block.",
            },
            {
                "case_name": "excess_generation_hour_excluded_from_buyer_settlement",
                "inputs": {
                    "load_kwh": 500.0,
                    "contracted_generation_kwh": 900.0,
                    "market_reference_price_vnd_per_kwh": 1700.0,
                },
                "expected_behavior": "Buyer settlement caps at matched quantity and excludes excess generation from CfD and EVN matched payment calculations.",
            },
        ],
    }


def build_scenario_dppa_case_2(extracted: dict) -> dict:
    scenario = {
        "Site": {
            "latitude": extracted["site"]["latitude"],
            "longitude": extracted["site"]["longitude"],
        },
        "ElectricLoad": {
            "loads_kw": _load_series(extracted["loads_kw"]),
            "year": extracted.get("data_year", 2024),
        },
        "PV": {
            "min_kw": 0.0,
            "max_kw": 80_000.0,
            "installed_cost_per_kw": 750.0,
            "om_cost_per_kw": 6.0,
            "location": "ground",
            "tilt": extracted["site"]["latitude"],
            "azimuth": 180.0,
            "dc_ac_ratio": 1.2,
            "losses": 0.14,
            "can_wholesale": True,
            "can_net_meter": False,
            "can_export_beyond_nem_limit": True,
            "can_curtail": True,
        },
        "Wind": {
            "min_kw": 0.0,
            "max_kw": 0.0,
            "production_factor_series": [],
        },
        "ElectricStorage": {
            "min_kw": 0.0,
            "max_kw": 30_000.0,
            "min_kwh": 0.0,
            "max_kwh": 120_000.0,
            "installed_cost_per_kw": 200.0,
            "installed_cost_per_kwh": 200.0,
            "installed_cost_constant": 0.0,
            "replace_cost_per_kw": 100.0,
            "replace_cost_per_kwh": 100.0,
            "battery_replacement_year": 10,
            "inverter_replacement_year": 10,
            "soc_min_fraction": 0.15,
            "charge_efficiency": 0.95,
            "discharge_efficiency": 0.95,
            "om_cost_fraction_of_installed_cost": 0.01,
            "can_grid_charge": False,
        },
        "Financial": {
            "analysis_years": 20,
            "owner_tax_rate_fraction": 0.0575,
            "offtaker_tax_rate_fraction": 0.20,
            "owner_discount_rate_fraction": 0.08,
            "offtaker_discount_rate_fraction": 0.10,
            "elec_cost_escalation_rate_fraction": DEFAULT_STRIKE_ESCALATION_FRACTION,
            "om_cost_escalation_rate_fraction": 0.04,
        },
        "_meta": {
            "scenario": "DPPA_CASE_2",
            "name": "Ninhsim DPPA Case 2 - synthetic DPPA buyer-cost workflow",
            "site": dict(extracted["site"]),
            "description": (
                "Synthetic / financial DPPA physical sizing case for Ninhsim. "
                "REopt handles PV plus optional storage sizing and hourly energy flows, while buyer settlement is computed in post-processing under a matched-volume CfD ledger."
            ),
            "contract_type": DEFAULT_CONTRACT_STRUCTURE,
            "buyer_settlement_model": "post_processed_hourly_cfd",
            "settlement_quantity_rule": DEFAULT_SETTLEMENT_QUANTITY_RULE,
            "excess_generation_treatment": DEFAULT_EXCESS_GENERATION_TREATMENT,
            "battery_grid_charging_allowed": False,
            "storage_requirement": "optional_reopt_choice",
            "strike_discount_fraction": DEFAULT_STRIKE_DISCOUNT_FRACTION,
            "strike_anchor": "95_percent_of_weighted_evn_tariff",
            "strike_escalation": "matches_evn_escalation",
            "market_price_source_priority": list(DEFAULT_MARKET_PRICE_SOURCE_PRIORITY),
            "reopt_objective": "minimum_lifecycle_cost_with_post_processed_buyer_settlement_screen",
            "customer_priority": "customer_best_interest_first",
        },
    }
    vietnam_data = load_vietnam_data()
    apply_vietnam_defaults(
        scenario,
        vietnam_data,
        customer_type=extracted["site"]["customer_type"],
        voltage_level=extracted["site"]["voltage_level"],
        region=extracted["site"]["region"],
        pv_type="ground",
        wind_type="onshore",
        apply_financials=False,
        apply_tariff=True,
        apply_emissions=True,
        apply_tech_costs=False,
        apply_export_rules=True,
        apply_zero_incentives=True,
    )
    scenario["ElectricTariff"].pop("tou_energy_rates_vnd_per_kwh", None)
    return scenario


def build_dppa_case_2_market_proxy(extracted: dict) -> dict:
    retail_series = _load_retail_series(extracted)
    fraction = _proxy_market_fraction(extracted)
    hourly = [rate * fraction for rate in retail_series]
    return {
        "model": "Ninhsim DPPA Case 2 Market Proxy",
        "status": "proxy",
        "market_reference_price_type": "proxy_cfmp_or_fmp",
        "proxy_method": "hourly_evn_tariff_scaled_by_weighted_wholesale_ratio",
        "proxy_fraction_of_evn": fraction,
        "hourly_series_vnd_per_kwh": hourly,
        "notes": [
            "Proxy uses the repo wholesale benchmark divided by the weighted EVN tariff and scales the hourly EVN retail series by that ratio.",
            "Replace with actual hourly CFMP/FMP once a trusted market series is available.",
        ],
    }


def build_dppa_case_2_settlement_inputs(
    results: dict,
    extracted: dict,
    scenario: dict,
    *,
    actual_market_series_vnd_per_kwh: list[float] | None = None,
    market_reference_price_type: str | None = None,
) -> dict:
    load_series = _load_series(extracted["loads_kw"])
    horizon = len(load_series)
    contracted_generation = _sum_series_to_length(
        horizon,
        results.get("PV", {}).get("electric_to_load_series_kw", []),
        results.get("PV", {}).get("electric_to_grid_series_kw", []),
        results.get("Wind", {}).get("electric_to_load_series_kw", []),
        results.get("Wind", {}).get("electric_to_grid_series_kw", []),
    )
    if actual_market_series_vnd_per_kwh is None:
        proxy = build_dppa_case_2_market_proxy(extracted)
        market_series = _pad_to_length(proxy["hourly_series_vnd_per_kwh"], horizon)
        market_type = proxy["market_reference_price_type"]
        notes = list(proxy["notes"])
    else:
        market_series = _pad_to_length(actual_market_series_vnd_per_kwh, horizon)
        market_type = market_reference_price_type or "cfmp"
        notes = [
            "Settlement uses an externally supplied hourly market reference series."
        ]
    return {
        "settlement_quantity_rule": DEFAULT_SETTLEMENT_QUANTITY_RULE,
        "matched_quantity_rule": DEFAULT_SETTLEMENT_QUANTITY_RULE,
        "excess_generation_treatment": DEFAULT_EXCESS_GENERATION_TREATMENT,
        "market_reference_price_type": market_type,
        "load_kwh_series": load_series,
        "contracted_generation_kwh_series": contracted_generation,
        "market_reference_price_vnd_per_kwh_series": market_series,
        "evn_retail_rate_vnd_per_kwh_series": _pad_to_length(
            _load_retail_series(extracted), horizon
        ),
        "strike_price_vnd_per_kwh": _strike_vnd_per_kwh(extracted),
        "dppa_adder_vnd_per_kwh": DEFAULT_DPPA_ADDER_VND_PER_KWH,
        "kpp_factor": DEFAULT_KPP_FACTOR,
        "exchange_rate_vnd_per_usd": float(
            extracted["benchmark"].get("exchange_rate_vnd_per_usd") or 25_000.0
        ),
        "notes": notes,
        "scenario_metadata": scenario.get("_meta", {}),
    }


def build_dppa_case_2_physical_summary(
    results: dict,
    extracted: dict,
    scenario: dict,
) -> dict:
    delivery = _load_reopt_delivery_profile(results)
    exports = _load_reopt_export_profile(results)
    charge = _load_reopt_charge_profile(results)
    curtailed = _load_reopt_curtailment_profile(results)
    grid = _load_reopt_grid_supply_profile(results)
    renewable_generation = _sum_series(
        results.get("PV", {}).get("electric_to_load_series_kw", []),
        results.get("PV", {}).get("electric_to_grid_series_kw", []),
        results.get("Wind", {}).get("electric_to_load_series_kw", []),
        results.get("Wind", {}).get("electric_to_grid_series_kw", []),
    )
    total_load_kwh = sum(
        max(0.0, value) for value in _load_series(extracted["loads_kw"])
    )
    delivered_kwh = sum(max(0.0, value) for value in delivery)
    export_kwh = sum(max(0.0, value) for value in exports)
    contracted_generation_kwh = sum(max(0.0, value) for value in renewable_generation)
    charge_kwh = sum(max(0.0, value) for value in charge)
    curtailed_kwh = sum(max(0.0, value) for value in curtailed)
    grid_kwh = sum(max(0.0, value) for value in grid)
    pv_size_kw = float(results.get("PV", {}).get("size_kw") or 0.0)
    wind_size_kw = float(results.get("Wind", {}).get("size_kw") or 0.0)
    battery_power_kw = float(results.get("ElectricStorage", {}).get("size_kw") or 0.0)
    battery_capacity_kwh = float(
        results.get("ElectricStorage", {}).get("size_kwh") or 0.0
    )
    duration_hours = (
        battery_capacity_kwh / battery_power_kw if battery_power_kw else 0.0
    )
    matched_fraction = delivered_kwh / total_load_kwh if total_load_kwh else 0.0
    contracted_fraction = (
        contracted_generation_kwh / total_load_kwh if total_load_kwh else 0.0
    )

    return {
        "model": "Ninhsim DPPA Case 2 Physical Summary",
        "status": results.get("status", "unknown"),
        "case_identity": {
            "scenario_family": "DPPA Case 2",
            "contract_structure": DEFAULT_CONTRACT_STRUCTURE,
            "settlement_quantity_rule": DEFAULT_SETTLEMENT_QUANTITY_RULE,
            "excess_generation_treatment": DEFAULT_EXCESS_GENERATION_TREATMENT,
        },
        "site_load_basis": {
            "annual_load_gwh": float(extracted["benchmark"]["annual_load_gwh"]),
            "customer_type": extracted["site"]["customer_type"],
            "voltage_level": extracted["site"]["voltage_level"],
            "region": extracted["site"]["region"],
        },
        "optimal_mix": {
            "pv_size_mw": pv_size_kw / 1_000.0,
            "wind_size_mw": wind_size_kw / 1_000.0,
            "bess_mw": battery_power_kw / 1_000.0,
            "bess_mwh": battery_capacity_kwh / 1_000.0,
            "bess_duration_hours": duration_hours,
        },
        "energy_summary": {
            "pv_gwh": _annual_energy_kwh(results.get("PV", {})) / 1_000_000.0,
            "wind_gwh": _annual_energy_kwh(results.get("Wind", {})) / 1_000_000.0,
            "matched_delivery_kwh": delivered_kwh,
            "contracted_generation_kwh": contracted_generation_kwh,
            "grid_supplied_kwh": grid_kwh,
            "exported_generation_kwh": export_kwh,
            "curtailed_generation_kwh": curtailed_kwh,
            "renewable_charged_to_battery_kwh": charge_kwh,
            "total_load_kwh": total_load_kwh,
            "matched_fraction_of_load": matched_fraction,
            "contracted_fraction_of_load": contracted_fraction,
        },
        "design_checks": {
            "wind_disabled": wind_size_kw <= 1e-9,
            "storage_is_optional": scenario.get("_meta", {}).get("storage_requirement")
            == "optional_reopt_choice",
            "battery_grid_charging_requested": bool(
                scenario.get("ElectricStorage", {}).get("can_grid_charge", False)
            ),
        },
        "financial": {
            "reopt_npv_usd": float(results.get("Financial", {}).get("npv") or 0.0),
            "analysis_years": int(
                results.get("Financial", {}).get("analysis_years") or 20
            ),
            "owner_discount_rate_fraction": _financial_value(
                results, "owner_discount_rate_fraction", 0.08
            ),
            "offtaker_discount_rate_fraction": _financial_value(
                results, "offtaker_discount_rate_fraction", 0.10
            ),
            "elec_cost_escalation_rate_fraction": _financial_value(
                results,
                "elec_cost_escalation_rate_fraction",
                DEFAULT_STRIKE_ESCALATION_FRACTION,
            ),
        },
        "notes": [
            "Physical summary keeps REopt sizing and hourly energy flows separate from buyer-side synthetic DPPA settlement.",
            "Contracted generation is limited to renewable generator output before the matched-load cap is applied in settlement; storage discharge is tracked separately inside physical delivery.",
        ],
    }


def run_dppa_case_2_buyer_settlement(settlement_inputs: dict) -> dict:
    load_series = _load_series(settlement_inputs["load_kwh_series"])
    generation_series = _load_series(
        settlement_inputs["contracted_generation_kwh_series"]
    )
    market_series = _load_series(
        settlement_inputs["market_reference_price_vnd_per_kwh_series"]
    )
    retail_series = _load_series(
        settlement_inputs["evn_retail_rate_vnd_per_kwh_series"]
    )
    strike = float(settlement_inputs["strike_price_vnd_per_kwh"])
    adder = float(settlement_inputs["dppa_adder_vnd_per_kwh"])
    kpp = float(settlement_inputs["kpp_factor"])
    exchange_rate = float(
        settlement_inputs.get("exchange_rate_vnd_per_usd") or 25_000.0
    )

    hourly_ledger = []
    matched_total = 0.0
    shortfall_total = 0.0
    excess_total = 0.0
    evn_matched_total = 0.0
    dppa_charge_total = 0.0
    shortfall_payment_total = 0.0
    cfd_total = 0.0
    buyer_total = 0.0
    negative_cfd_hours = 0

    for index, values in enumerate(
        zip(load_series, generation_series, market_series, retail_series), start=1
    ):
        load_kwh, generation_kwh, market_price, retail_price = [
            float(v) for v in values
        ]
        matched_quantity = min(load_kwh, generation_kwh)
        shortfall_quantity = max(0.0, load_kwh - matched_quantity)
        excess_quantity = max(0.0, generation_kwh - matched_quantity)
        evn_matched_payment = matched_quantity * market_price * kpp
        dppa_charge = matched_quantity * adder
        shortfall_payment = shortfall_quantity * retail_price
        buyer_cfd_payment = matched_quantity * (strike - market_price)
        buyer_total_payment = (
            evn_matched_payment + dppa_charge + shortfall_payment + buyer_cfd_payment
        )
        if buyer_cfd_payment < 0.0:
            negative_cfd_hours += 1

        hourly_ledger.append(
            {
                "hour_index": index,
                "load_kwh": load_kwh,
                "contracted_generation_kwh": generation_kwh,
                "matched_quantity_kwh": matched_quantity,
                "shortfall_quantity_kwh": shortfall_quantity,
                "excess_quantity_kwh": excess_quantity,
                "market_reference_price_vnd_per_kwh": market_price,
                "evn_retail_rate_vnd_per_kwh": retail_price,
                "buyer_evn_matched_payment_vnd": evn_matched_payment,
                "buyer_dppa_charge_vnd": dppa_charge,
                "buyer_shortfall_payment_vnd": shortfall_payment,
                "buyer_cfd_payment_vnd": buyer_cfd_payment,
                "buyer_total_payment_vnd": buyer_total_payment,
            }
        )
        matched_total += matched_quantity
        shortfall_total += shortfall_quantity
        excess_total += excess_quantity
        evn_matched_total += evn_matched_payment
        dppa_charge_total += dppa_charge
        shortfall_payment_total += shortfall_payment
        cfd_total += buyer_cfd_payment
        buyer_total += buyer_total_payment

    total_load = sum(load_series)
    blended_cost = buyer_total / total_load if total_load else 0.0

    return {
        "model": "Ninhsim DPPA Case 2 Buyer Settlement",
        "status": "ok",
        "market_reference_price_type": settlement_inputs["market_reference_price_type"],
        "settlement_quantity_rule": settlement_inputs["settlement_quantity_rule"],
        "excess_generation_treatment": settlement_inputs["excess_generation_treatment"],
        "parameters": {
            "strike_price_vnd_per_kwh": strike,
            "dppa_adder_vnd_per_kwh": adder,
            "kpp_factor": kpp,
            "exchange_rate_vnd_per_usd": exchange_rate,
        },
        "hourly_ledger": hourly_ledger,
        "summary": {
            "matched_quantity_kwh": matched_total,
            "shortfall_quantity_kwh": shortfall_total,
            "excess_quantity_kwh": excess_total,
            "buyer_evn_matched_payment_vnd": evn_matched_total,
            "buyer_dppa_charge_vnd": dppa_charge_total,
            "buyer_shortfall_payment_vnd": shortfall_payment_total,
            "buyer_cfd_payment_vnd": cfd_total,
            "buyer_total_payment_vnd": buyer_total,
            "buyer_total_payment_usd": buyer_total / exchange_rate,
            "buyer_blended_cost_vnd_per_kwh": blended_cost,
            "buyer_blended_cost_usd_per_kwh": blended_cost / exchange_rate,
            "total_consumed_load_kwh": total_load,
            "hours_with_negative_cfd_credit": negative_cfd_hours,
        },
        "notes": list(settlement_inputs.get("notes", [])),
    }


def build_dppa_case_2_buyer_benchmark(
    physical_summary: dict,
    settlement: dict,
) -> dict:
    hourly_ledger = settlement["hourly_ledger"]
    benchmark_total = sum(
        float(entry["load_kwh"]) * float(entry["evn_retail_rate_vnd_per_kwh"])
        for entry in hourly_ledger
    )
    buyer_total = float(settlement["summary"]["buyer_total_payment_vnd"])
    total_load = float(settlement["summary"]["total_consumed_load_kwh"])
    benchmark_blended = benchmark_total / total_load if total_load else 0.0
    buyer_savings = max(0.0, benchmark_total - buyer_total)
    buyer_premium = max(0.0, buyer_total - benchmark_total)
    delta = buyer_total - benchmark_total

    return {
        "model": "Ninhsim DPPA Case 2 Buyer Benchmark",
        "status": settlement.get("status", "unknown"),
        "case_identity": physical_summary.get("case_identity", {}),
        "site_load_basis": physical_summary.get("site_load_basis", {}),
        "year_one_costs": {
            "buyer_total_payment_vnd": buyer_total,
            "benchmark_evn_total_cost_vnd": benchmark_total,
            "buyer_savings_vs_evn_vnd": buyer_savings,
            "buyer_premium_vs_evn_vnd": buyer_premium,
            "buyer_minus_benchmark_vnd": delta,
            "buyer_blended_cost_vnd_per_kwh": float(
                settlement["summary"]["buyer_blended_cost_vnd_per_kwh"]
            ),
            "benchmark_blended_cost_vnd_per_kwh": benchmark_blended,
        },
        "risk_summary": {
            "matched_quantity_kwh": float(
                settlement["summary"]["matched_quantity_kwh"]
            ),
            "shortfall_quantity_kwh": float(
                settlement["summary"]["shortfall_quantity_kwh"]
            ),
            "excess_quantity_kwh": float(settlement["summary"]["excess_quantity_kwh"]),
            "hours_with_negative_cfd_credit": int(
                settlement["summary"]["hours_with_negative_cfd_credit"]
            ),
        },
        "decision": {
            "buyer_savings_positive": buyer_savings > 0.0,
            "customer_premium_present": buyer_premium > 0.0,
            "recommended_position": (
                "buyer_savings_vs_evn"
                if buyer_savings > 0.0
                else "customer_premium_vs_evn"
            ),
        },
    }
