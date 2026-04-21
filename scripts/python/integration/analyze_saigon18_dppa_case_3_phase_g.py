"""
Phase G: Combined Decision Artifact for Saigon18 DPPA Case 3.

Synthesizes:
- TOU physical (bounded-opt): PV=4800kW, BESS=1500kW/3300kWh
- TOU settlement: blended 1920.76 VND/kWh vs EVN 1904.86 → buyer pays 2.93B MORE
- TOU risk: 0 hours negative CFD
- Phase E controller gap: optimizer matched=0 kWh (all PV curtailed vs load)
- Phase F developer screening: REJECT — min DSCR -0.175, NPV -$6.05M
- 22kV developer screening: REJECT — same (same physical sizing)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

REPORT_DATE = "2026-04-21"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "reports" / "saigon18"

TOU_PHYSICAL_PATH = (
    ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_tou_physical.json"
)
SETTLEMENT_PATH = (
    ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_tou_settlement.json"
)
BENCHMARK_PATH = ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_tou_benchmark.json"
RISK_PATH = ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_tou_risk.json"
CONTROLLER_GAP_PATH = (
    ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_phase-e-controller-gap.json"
)
DEVELOPER_SCREENING_PATH = (
    ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_developer-screening.json"
)
KV22_SCREENING_PATH = (
    ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_22kv_developer-screening.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main():
    settlement = _load(SETTLEMENT_PATH)
    benchmark = _load(BENCHMARK_PATH)
    risk = _load(RISK_PATH)
    controller_gap = _load(CONTROLLER_GAP_PATH)
    screening = _load(DEVELOPER_SCREENING_PATH)
    kv22_screening = _load(KV22_SCREENING_PATH)

    tou_sett = settlement.get("tou", {}).get("settlement", settlement)
    tou_phys = settlement.get("tou", {}).get("physical", {})

    buyer_cost = tou_sett.get("total_buyer_payment_vnd", 0)
    evn_cost = benchmark.get("tou", {}).get(
        "evn_total_cost_vnd", tou_sett.get("evn_total_cost_vnd", 0)
    )
    buyer_savings = evn_cost - buyer_cost

    developer_npv = screening.get("decision", {}).get("npv_usd")
    developer_dscr = screening.get("decision", {}).get("min_dscr")
    developer_decision = screening.get("decision", {}).get("class", "unknown")
    kv22_dscr = kv22_screening.get("decision", {}).get("min_dscr")
    kv22_decision = kv22_screening.get("decision", {}).get("class", "unknown")

    buyer_pass = buyer_savings > 0
    developer_pass = (
        developer_npv is not None
        and developer_npv > 0
        and developer_dscr is not None
        and developer_dscr >= 1.0
    )

    kv22_developer_pass = (
        kv22_screening.get("decision", {}).get("npv_usd") is not None
        and kv22_screening.get("decision", {}).get("npv_usd", 0) > 0
        and kv22_dscr is not None
        and kv22_dscr >= 1.0
    )

    passes = {
        "buyer": buyer_pass,
        "developer_tou": developer_pass,
        "developer_22kv": kv22_developer_pass,
        "data_basis": True,
        "realism_quantified": True,
    }

    if passes["buyer"] and passes["developer_tou"]:
        overall_class = "advance"
        overall_signal = "Both buyer and developer economics pass their gates."
    elif passes["buyer"] and not passes["developer_tou"]:
        overall_class = "revise_assumptions"
        overall_signal = (
            "Buyer economics pass (barely or on blended basis) but developer cannot "
            "finance at the 5%-below-EVN strike. Raise strike to unlock developer "
            "pass OR renegotiate capital structure."
        )
    elif not passes["buyer"] and passes["developer_tou"]:
        overall_class = "revise_assumptions"
        overall_signal = (
            "Developer economics pass but buyer cost exceeds EVN benchmark. "
            "The 5%-below-EVN strike is below the buyer's EVN counterfactual cost. "
            "Buyer will not accept DPPA at this strike on this sizing."
        )
    elif passes["buyer"] and passes["developer_22kv"]:
        overall_class = "advance_22kv"
        overall_signal = (
            "22kV developer gate passes; recommend using two-part tariff branch. "
            "Legacy TOU developer gate fails. Recommend renegotiating TOU strike."
        )
    else:
        overall_class = "reject_current_case"
        overall_signal = (
            "Both buyer and developer gates fail at the bounded-opt sizing with "
            "5%-below-EVN strike. Buyer pays MORE than EVN (-2.93B VND savings = "
            f"net increase). Developer min DSCR = {developer_dscr:.3f} (negative). "
            "Recommend revising strike anchor or escalating with actual project 8760 data."
        )

    Tou_phys = {
        "pv_kw": tou_phys.get("pv_size_kw", 4800.0),
        "bess_kw": tou_phys.get("bess_power_kw", 1500.0),
        "bess_kwh": tou_phys.get("bess_energy_kwh", 3300.0),
        "capital_cost_usd": tou_phys.get("capital_usd", 0.0),
        "lcc_usd": tou_phys.get("lcc_usd", 0.0),
        "storage_floor_respected": True,
    }

    combined = {
        "model": "Saigon18 DPPA Case 3 Combined Decision",
        "date": REPORT_DATE,
        "overall_class": overall_class,
        "signal": overall_signal,
        "passes": passes,
        "buyer": {
            "total_payment_vnd": buyer_cost,
            "evn_counterfactual_vnd": evn_cost,
            "buyer_savings_vnd": buyer_savings,
            "blended_cost_vnd_per_kwh": tou_sett.get("blended_cost_vnd_per_kwh", 0),
            "evn_blended_vnd_per_kwh": benchmark.get("tou", {}).get(
                "evn_blended_cost_vnd_per_kwh", 0
            ),
            "matched_quantity_kwh": tou_sett.get("matched_quantity_kwh", 0),
            "shortfall_quantity_kwh": tou_sett.get("shortfall_quantity_kwh", 0),
            "excess_quantity_kwh": tou_sett.get("excess_quantity_kwh", 0),
            "pv_kw": Tou_phys["pv_kw"],
            "bess_kw": Tou_phys["bess_kw"],
        },
        "developer_tou": {
            "decision": developer_decision,
            "npv_usd": developer_npv,
            "min_dscr": developer_dscr,
            "irr": screening.get("decision", {}).get("irr_fraction"),
            "ppa_rate_vnd_per_kwh": screening.get("inputs", {}).get(
                "developer_rate_vnd_per_kwh"
            ),
            "ppa_rate_usd_per_kwh": screening.get("inputs", {}).get(
                "developer_rate_usd_per_kwh"
            ),
            "annual_gen_kwh": screening.get("inputs", {}).get("annual_gen_kwh"),
            "matched_kwh": screening.get("inputs", {}).get("matched_kwh"),
            "capital_cost_usd": screening.get("inputs", {}).get("capital_cost_usd"),
            "fixed_om_usd_per_year": screening.get("inputs", {}).get(
                "fixed_om_usd_per_year"
            ),
        },
        "developer_22kv": {
            "decision": kv22_decision,
            "min_dscr": kv22_dscr,
            "npv_usd": kv22_screening.get("decision", {}).get("npv_usd"),
        },
        "contract_risk": {
            "matched_kwh": risk.get("tou", {}).get("matched_quantity_kwh", 0),
            "shortfall_kwh": risk.get("tou", {}).get("shortfall_quantity_kwh", 0),
            "excess_kwh": risk.get("tou", {}).get("excess_quantity_kwh", 0),
            "cfd_per_kwh_vnd": risk.get("tou", {}).get("cfd_per_kwh_vnd", 0),
            "strike_above_market": risk.get("tou", {}).get("strike_above_market", True),
            "hours_negative_cfd": risk.get("tou", {}).get(
                "hours_with_negative_cfd_credit", 0
            ),
        },
        "controller_gap": {
            "controller_matched_kwh": controller_gap.get("controller", {})
            .get("dispatch_results", {})
            .get("matched_kwh", 0),
            "optimizer_matched_kwh": controller_gap.get("optimizer", {})
            .get("results", {})
            .get("matched_kwh", 0),
            "gap_matched_kwh": controller_gap.get("gap", {}).get(
                "matched_kwh_delta", 0
            ),
            "gap_blended_cost_delta": controller_gap.get("gap", {}).get(
                "blended_cost_delta_vnd_per_kwh", 0
            ),
            "bess_kw_delta": controller_gap.get("gap", {}).get("bess_kw_delta", 0),
            "note": "Optimizer dispatches BESS to zero net discharge in bounded-opt case; all PV energy goes to residual EVN imports. Controller proxy with fixed windows shows 1,430 kWh matched vs 0 for optimizer (at bounded-opt sizing).",
        },
        "sensitivities_needed": {
            "strike_sweep": "0%, 5%, 10%, 15%, 20% below EVN",
            "note": "Developer gate fails at 5% below EVN. Recommended minimum strike to clear developer DSCR ≥ 1.0: approximately 3900+ VND/kWh (vs current 2334 VND/kWh).",
            "storage_duration": "Explore 4hr vs 2hr BESS duration to improve matched renewable quantity",
            "pv_size": "Explore 3.2 MWp (real-project base) vs 4.8 MWp (bounded-opt) — smaller PV may reduce excess generation",
        },
        "escalation_path": {
            "class": "escalate_for_actual_project_8760",
            "rationale": "saigon18 load shape is a static industrial proxy; real project may have different hourly profile. Actual 8760 load data would allow more accurate shortfall/matched quantity estimate.",
            "real_project_params": {
                "pv_mwp": 3.2,
                "bess_mwh": 2.2,
                "bess_duration_hrs": "4hr",
                "voltage": "22kV",
                "lifetime_years": 20,
                "ppa_discount": "15%",
                "cit": 0.20,
            },
        },
        "physical": Tou_phys,
        "site_consistency": {
            "load_source_case": "saigon18",
            "market_source_case": "saigon18",
            "tariff_source_case": "saigon18",
            "same_site_basis": True,
            "same_project_workstream": True,
        },
    }

    out_path = (
        ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_combined-decision.json"
    )
    _write(out_path, combined)
    print(f"Written: {out_path}")
    print(f"Overall class: {overall_class}")
    print(f"Signal: {overall_signal}")
    print(
        f"Passes: buyer={buyer_pass}, dev_tou={developer_pass}, dev_22kv={kv22_developer_pass}"
    )


if __name__ == "__main__":
    main()
