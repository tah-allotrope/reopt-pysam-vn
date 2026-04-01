"""
Analyze Ninhsim REopt outputs for the bundled-CPPA customer-price target.

The study logic is:
- customer buys renewable delivery under a bundled CPPA strike
- residual unmet load remains on EVN TOU
- the maximum customer-equivalent strike is the strike that keeps the blended
  paid price equal to the current weighted EVN benchmark
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _financial_value(results: dict, key: str, default: float) -> float:
    return float(results.get("Financial", {}).get(key) or default)


def _annual_energy_kwh(tech_results: dict) -> float:
    return float(
        tech_results.get("year_one_energy_produced_kwh")
        or tech_results.get("annual_energy_produced_kwh")
        or 0.0
    )


def _pad_to_8760(series: list[float]) -> list[float]:
    if len(series) >= 8760:
        return list(series[:8760])
    return list(series) + [0.0] * (8760 - len(series))


def _sum_series(*series_list: list[float]) -> list[float]:
    padded = [_pad_to_8760(series) for series in series_list]
    return [sum(values) for values in zip(*padded)]


def load_reopt_delivery_profile(results: dict) -> list[float]:
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    storage = results.get("ElectricStorage", {})
    return _sum_series(
        pv.get("electric_to_load_series_kw", []),
        wind.get("electric_to_load_series_kw", []),
        storage.get("storage_to_load_series_kw", []),
    )


def load_grid_supply_profile(results: dict) -> list[float]:
    utility = results.get("ElectricUtility", {})
    return _pad_to_8760(utility.get("electric_to_load_series_kw", []))


def calculate_customer_bill_breakdown(results: dict, extracted: dict) -> dict:
    renewable_delivery_kw = load_reopt_delivery_profile(results)
    grid_supply_kw = load_grid_supply_profile(results)
    evn_rates_usd = _pad_to_8760(
        extracted["evn_tariff"]["tou_energy_rates_usd_per_kwh"]
    )
    load_series_kw = _pad_to_8760(extracted["loads_kw"])

    renewable_kwh = sum(max(0.0, value) for value in renewable_delivery_kw)
    grid_kwh = sum(max(0.0, value) for value in grid_supply_kw)
    total_load_kwh = sum(max(0.0, value) for value in load_series_kw)
    grid_cost_usd = sum(
        max(0.0, grid_kw) * rate for grid_kw, rate in zip(grid_supply_kw, evn_rates_usd)
    )
    benchmark_cost_usd = (
        total_load_kwh * extracted["benchmark"]["weighted_evn_price_usd_per_kwh"]
    )

    return {
        "renewable_delivered_kwh": renewable_kwh,
        "grid_supplied_kwh": grid_kwh,
        "total_load_kwh": total_load_kwh,
        "grid_cost_usd": grid_cost_usd,
        "benchmark_customer_cost_usd": benchmark_cost_usd,
    }


def calculate_customer_equivalent_strike(results: dict, extracted: dict) -> dict:
    bill = calculate_customer_bill_breakdown(results, extracted)
    renewable_kwh = bill["renewable_delivered_kwh"]
    benchmark_cost_usd = bill["benchmark_customer_cost_usd"]
    grid_cost_usd = bill["grid_cost_usd"]

    max_strike_usd = 0.0
    if renewable_kwh > 0:
        max_strike_usd = max(0.0, (benchmark_cost_usd - grid_cost_usd) / renewable_kwh)

    customer_blended_price = (
        (grid_cost_usd + renewable_kwh * max_strike_usd) / bill["total_load_kwh"]
        if bill["total_load_kwh"]
        else 0.0
    )
    exchange_rate = extracted["benchmark"]["exchange_rate_vnd_per_usd"]

    return {
        **bill,
        "max_cppa_strike_usd_per_kwh": max_strike_usd,
        "max_cppa_strike_vnd_per_kwh": max_strike_usd * exchange_rate,
        "customer_blended_price_at_max_strike_usd_per_kwh": customer_blended_price,
        "customer_blended_price_at_max_strike_vnd_per_kwh": customer_blended_price
        * exchange_rate,
        "weighted_evn_benchmark_usd_per_kwh": extracted["benchmark"][
            "weighted_evn_price_usd_per_kwh"
        ],
        "weighted_evn_benchmark_vnd_per_kwh": extracted["benchmark"][
            "weighted_evn_price_vnd_per_kwh"
        ],
    }


def calculate_multi_year_cppa_path(
    results: dict, extracted: dict, analysis_years: int | None = None
) -> list[dict]:
    pricing = calculate_customer_equivalent_strike(results, extracted)
    escalation = _financial_value(results, "elec_cost_escalation_rate_fraction", 0.05)
    years = int(
        analysis_years
        or _financial_value(results, "analysis_years", 20)
        or extracted.get("assumptions", {}).get("analysis_years", 20)
    )
    renewable_kwh = pricing["renewable_delivered_kwh"]
    grid_kwh = pricing["grid_supplied_kwh"]
    total_load_kwh = pricing["total_load_kwh"]
    year_one_grid_rate = pricing["grid_cost_usd"] / grid_kwh if grid_kwh else 0.0
    exchange_rate = extracted["benchmark"]["exchange_rate_vnd_per_usd"]

    path = []
    for year in range(1, years + 1):
        multiplier = (1.0 + escalation) ** (year - 1)
        strike_usd = pricing["max_cppa_strike_usd_per_kwh"] * multiplier
        grid_rate_usd = year_one_grid_rate * multiplier
        benchmark_usd = pricing["weighted_evn_benchmark_usd_per_kwh"] * multiplier
        blended_usd = (
            (renewable_kwh * strike_usd + grid_kwh * grid_rate_usd) / total_load_kwh
            if total_load_kwh
            else 0.0
        )
        path.append(
            {
                "year": year,
                "escalation_multiplier": multiplier,
                "renewable_delivered_kwh": renewable_kwh,
                "grid_supplied_kwh": grid_kwh,
                "cPPA_strike_usd_per_kwh": strike_usd,
                "cPPA_strike_vnd_per_kwh": strike_usd * exchange_rate,
                "residual_grid_price_usd_per_kwh": grid_rate_usd,
                "residual_grid_price_vnd_per_kwh": grid_rate_usd * exchange_rate,
                "weighted_evn_benchmark_usd_per_kwh": benchmark_usd,
                "weighted_evn_benchmark_vnd_per_kwh": benchmark_usd * exchange_rate,
                "customer_blended_price_usd_per_kwh": blended_usd,
                "customer_blended_price_vnd_per_kwh": blended_usd * exchange_rate,
            }
        )
    return path


def calculate_financial_screening_view(
    results: dict, extracted: dict, analysis_years: int | None = None
) -> list[dict]:
    path = calculate_multi_year_cppa_path(results, extracted, analysis_years)

    view = []
    for year in path:
        renewable_kwh = year["renewable_delivered_kwh"]
        grid_kwh = year["grid_supplied_kwh"]
        renewable_cost_usd = renewable_kwh * year["cPPA_strike_usd_per_kwh"]
        grid_cost_usd = grid_kwh * year["residual_grid_price_usd_per_kwh"]
        customer_total_cost_usd = renewable_cost_usd + grid_cost_usd
        benchmark_cost_usd = year["weighted_evn_benchmark_usd_per_kwh"] * (
            renewable_kwh + grid_kwh
        )

        view.append(
            {
                "year": year["year"],
                "developer_revenue_usd": renewable_cost_usd,
                "offtaker_renewable_payment_usd": renewable_cost_usd,
                "offtaker_residual_grid_cost_usd": grid_cost_usd,
                "customer_total_cost_usd": customer_total_cost_usd,
                "benchmark_evn_cost_usd": benchmark_cost_usd,
                "customer_savings_vs_evn_usd": max(
                    0.0, benchmark_cost_usd - customer_total_cost_usd
                ),
            }
        )

    return view


def _discounted_npv(entries: list[dict], key: str, discount_rate: float) -> float:
    npv = 0.0
    for entry in entries:
        year = int(entry["year"])
        npv += float(entry[key]) / ((1.0 + discount_rate) ** year)
    return npv


def build_summary(results: dict, extracted: dict) -> dict:
    pricing = calculate_customer_equivalent_strike(results, extracted)
    multi_year_cppa_path = calculate_multi_year_cppa_path(results, extracted)
    financial_screening_view = calculate_financial_screening_view(results, extracted)
    pv = results.get("PV", {})
    wind = results.get("Wind", {})
    storage = results.get("ElectricStorage", {})
    financial = results.get("Financial", {})
    owner_discount_rate = float(financial.get("owner_discount_rate_fraction") or 0.08)
    offtaker_discount_rate = float(
        financial.get("offtaker_discount_rate_fraction") or 0.10
    )

    return {
        "status": results.get("status", "unknown"),
        "pricing": pricing,
        "multi_year_cppa_path": multi_year_cppa_path,
        "financial_screening_view": financial_screening_view,
        "optimal_mix": {
            "pv_size_mw": float(pv.get("size_kw") or 0.0) / 1_000.0,
            "wind_size_mw": float(wind.get("size_kw") or 0.0) / 1_000.0,
            "bess_mw": float(storage.get("size_kw") or 0.0) / 1_000.0,
            "bess_mwh": float(storage.get("size_kwh") or 0.0) / 1_000.0,
        },
        "year_one_energy": {
            "pv_gwh": _annual_energy_kwh(pv) / 1_000_000.0,
            "wind_gwh": _annual_energy_kwh(wind) / 1_000_000.0,
            "renewable_delivered_gwh": pricing["renewable_delivered_kwh"] / 1_000_000.0,
            "grid_supplied_gwh": pricing["grid_supplied_kwh"] / 1_000_000.0,
        },
        "financial": {
            "npv_usd": float(financial.get("npv") or 0.0),
            "analysis_years": int(
                financial.get("analysis_years") or len(multi_year_cppa_path)
            ),
            "owner_discount_rate_fraction": owner_discount_rate,
            "offtaker_discount_rate_fraction": offtaker_discount_rate,
            "elec_cost_escalation_rate_fraction": float(
                financial.get("elec_cost_escalation_rate_fraction") or 0.05
            ),
            "year_one_operating_savings_before_tax_usd": float(
                financial.get("year_one_total_operating_cost_savings_before_tax") or 0.0
            ),
            "developer_revenue_npv_usd": _discounted_npv(
                financial_screening_view, "developer_revenue_usd", owner_discount_rate
            ),
            "offtaker_cost_npv_usd": _discounted_npv(
                financial_screening_view,
                "customer_total_cost_usd",
                offtaker_discount_rate,
            ),
            "benchmark_evn_cost_npv_usd": _discounted_npv(
                financial_screening_view,
                "benchmark_evn_cost_usd",
                offtaker_discount_rate,
            ),
            "offtaker_savings_npv_usd": _discounted_npv(
                financial_screening_view,
                "customer_savings_vs_evn_usd",
                offtaker_discount_rate,
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Ninhsim REopt results under bundled CPPA target pricing"
    )
    parser.add_argument(
        "--reopt",
        required=True,
        help="Path to REopt results JSON",
    )
    parser.add_argument(
        "--extracted",
        default="data/interim/ninhsim/ninhsim_extracted_inputs.json",
        help="Path to Ninhsim extracted inputs JSON",
    )
    parser.add_argument(
        "--output",
        default="artifacts/reports/ninhsim/2026-04-01_ninhsim-cppa-analysis.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    results = json.loads((REPO_ROOT / args.reopt).read_text(encoding="utf-8"))
    extracted = json.loads((REPO_ROOT / args.extracted).read_text(encoding="utf-8"))
    summary = build_summary(results, extracted)

    output_path = REPO_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Ninhsim CPPA analysis written to: {output_path}")
    print(f"  Status               : {summary['status']}")
    print(
        "  Max bundled strike   : "
        f"{summary['pricing']['max_cppa_strike_vnd_per_kwh']:.2f} VND/kWh "
        f"({summary['pricing']['max_cppa_strike_usd_per_kwh']:.6f} USD/kWh)"
    )
    print(
        "  Customer benchmark   : "
        f"{summary['pricing']['weighted_evn_benchmark_vnd_per_kwh']:.2f} VND/kWh"
    )
    print(
        "  Year-20 strike       : "
        f"{summary['multi_year_cppa_path'][-1]['cPPA_strike_vnd_per_kwh']:.2f} VND/kWh"
    )
    print(
        "  Developer NPV screen : "
        f"${summary['financial']['developer_revenue_npv_usd']:,.0f}"
    )


if __name__ == "__main__":
    main()
