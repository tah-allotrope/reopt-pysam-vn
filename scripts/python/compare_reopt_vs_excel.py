"""
Compare REopt results against Saigon18 Excel model outputs.

Computes a delta table for all metrics defined in plan Section 6.1,
flags discrepancies beyond tolerance, and writes a markdown comparison report.

Usage:
    python scripts/python/compare_reopt_vs_excel.py \
        --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json \
        --extracted data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json \
        --excel "path/to/Solar BESS MODEL.xlsx" \
        --output artifacts/reports/saigon18/2026-03-22_scenario-a_vs_excel_comparison.md
"""

import argparse
import json
import warnings
from pathlib import Path


# ---------------------------------------------------------------------------
# Excel target values (from plan Section 6.1 and project summary)
# These are the "ground truth" from the Excel feasibility model.
# ---------------------------------------------------------------------------

EXCEL_TARGETS = {
    "pv_gen_mwh": {"value": 71_808.0, "tolerance": 0.01, "unit": "MWh"},
    "pv_to_load_mwh": {"value": 62_106.0, "tolerance": 0.02, "unit": "MWh"},
    "pv_to_grid_mwh": {"value": 1_087.0, "tolerance": 0.05, "unit": "MWh"},
    "bess_discharge_mwh": {
        "value": 8_591.0,
        "tolerance": 0.05,
        "unit": "MWh",
    },  # 7364+1227
    "grid_purchases_mwh": {"value": 112_454.0, "tolerance": 0.02, "unit": "MWh"},
    "npv_usd": {"value": 22_034_000.0, "tolerance": None, "unit": "USD"},
    "payback_years": {"value": 6.0, "tolerance": 1.0, "unit": "years"},
    "year1_revenue_usd": {"value": 5_056_418.0, "tolerance": None, "unit": "USD"},
}


# ---------------------------------------------------------------------------
# REopt metric extractor
# ---------------------------------------------------------------------------


def load_reopt_metrics(results: dict) -> dict:
    """Extract comparable metrics from a REopt results dict."""
    pv = results.get("PV", {})
    storage = results.get("ElectricStorage", {})
    utility = results.get("ElectricUtility", {})
    fin = results.get("Financial", {})

    pv_gen_kwh = pv.get("year_one_energy_produced_kwh") or 0
    pv_export_kwh = pv.get("annual_energy_exported_kwh") or 0
    bess_to_load_series = storage.get("storage_to_load_series_kw", [])
    bess_discharge_kwh = sum(bess_to_load_series)
    npv = fin.get("npv", 0) or 0

    return {
        "pv_gen_mwh": pv_gen_kwh / 1_000,
        "pv_to_load_mwh": (pv_gen_kwh - pv_export_kwh) / 1_000,
        "pv_to_grid_mwh": pv_export_kwh / 1_000,
        "bess_discharge_mwh": bess_discharge_kwh / 1_000,
        "grid_purchases_mwh": (utility.get("annual_energy_supplied_kwh") or 0) / 1_000,
        "npv_usd": npv,
        "payback_years": fin.get("simple_payback_years") or 0,
        "year1_revenue_usd": fin.get("year_one_total_operating_cost_savings_before_tax")
        or 0,
        "lcc": fin.get("lcc") or 0,
    }


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------


def compare_metrics(reopt_metrics: dict, excel_targets: dict) -> list[dict]:
    """Return a list of row dicts for the comparison table."""
    rows = []
    for key, target_info in excel_targets.items():
        excel_val = target_info["value"]
        reopt_val = reopt_metrics.get(key)
        unit = target_info["unit"]
        tol = target_info["tolerance"]

        if reopt_val is None:
            delta_pct = None
            status = "MISSING"
        elif excel_val == 0:
            delta_pct = None
            status = "SKIP (Excel=0)"
        else:
            delta_pct = (reopt_val - excel_val) / abs(excel_val)
            if tol is None:
                status = "INFO"
            elif unit == "years":
                status = "OK" if abs(reopt_val - excel_val) <= tol else "WARN"
            else:
                status = "OK" if abs(delta_pct) <= tol else "WARN"

        rows.append(
            {
                "metric": key,
                "unit": unit,
                "excel": excel_val,
                "reopt": reopt_val,
                "delta_pct": delta_pct,
                "tolerance": tol,
                "status": status,
            }
        )
    return rows


def _fmt(v, unit: str) -> str:
    if v is None:
        return "—"
    if unit == "years":
        return f"{v:.1f}"
    if unit == "USD":
        return f"${v:,.0f}"
    if unit == "MWh":
        return f"{v:,.0f}"
    return str(v)


def _fmt_delta(delta_pct) -> str:
    if delta_pct is None:
        return "—"
    return f"{delta_pct:+.1%}"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


DISCREPANCY_EXPLANATIONS = {
    "npv_usd": (
        "REopt NPV uses unlevered owner discount rate (8%) on unlevered cash flows. "
        "Excel uses WACC/equity IRR with 70% leverage. A direct comparison is invalid — "
        "use unlevered IRR for apples-to-apples. Run equity_irr.py for leveraged comparison."
    ),
    "payback_years": (
        "REopt simple payback is based on avoided electricity cost vs. BAU. "
        "Excel payback uses PPA revenue minus opex. Framing differs; both should be ~6 years."
    ),
    "bess_discharge_mwh": (
        "REopt optimizes dispatch timing freely (TOU arbitrage). Excel uses fixed windows "
        "(charge 11–15h, discharge from 18h). Dispatch totals may match even if timing differs."
    ),
    "pv_to_grid_mwh": (
        "REopt applies Decree 57 export cap in post-processing only (hard JuMP constraint "
        "not yet implemented). Export volume may exceed the 20% limit — see plan Phase 3."
    ),
}


def generate_report(
    rows: list[dict],
    reopt_metrics: dict,
    scenario_label: str,
    output_path: Path,
) -> None:
    lines = [
        f"# Saigon18 REopt vs. Excel Comparison Report",
        f"",
        f"**Scenario:** {scenario_label}",
        f"",
        f"## Energy Metrics (Year 1)",
        f"",
        f"| Metric | Unit | Excel | REopt | Delta | Tol | Status |",
        f"|---|---|---|---|---|---|---|",
    ]

    energy_keys = {
        "pv_gen_mwh",
        "pv_to_load_mwh",
        "pv_to_grid_mwh",
        "bess_discharge_mwh",
        "grid_purchases_mwh",
    }
    fin_keys = {"npv_usd", "payback_years", "year1_revenue_usd"}

    def add_rows(keys):
        for r in rows:
            if r["metric"] not in keys:
                continue
            tol_str = (
                f"±{r['tolerance']:.0%}"
                if isinstance(r["tolerance"], float) and r["tolerance"] < 1
                else (f"±{r['tolerance']:.1f} yr" if r["unit"] == "years" else "—")
            )
            lines.append(
                f"| {r['metric']} | {r['unit']} "
                f"| {_fmt(r['excel'], r['unit'])} "
                f"| {_fmt(r['reopt'], r['unit'])} "
                f"| {_fmt_delta(r['delta_pct'])} "
                f"| {tol_str} "
                f"| {r['status']} |"
            )

    add_rows(energy_keys)

    lines += [
        "",
        "## Financial Metrics",
        "",
        "| Metric | Unit | Excel | REopt | Delta | Notes | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        if r["metric"] not in fin_keys:
            continue
        note = DISCREPANCY_EXPLANATIONS.get(r["metric"], "")[:60] + (
            "…" if len(DISCREPANCY_EXPLANATIONS.get(r["metric"], "")) > 60 else ""
        )
        lines.append(
            f"| {r['metric']} | {r['unit']} "
            f"| {_fmt(r['excel'], r['unit'])} "
            f"| {_fmt(r['reopt'], r['unit'])} "
            f"| {_fmt_delta(r['delta_pct'])} "
            f"| {note} "
            f"| {r['status']} |"
        )

    # Warnings section
    warn_rows = [r for r in rows if r["status"] == "WARN"]
    if warn_rows:
        lines += ["", "## Discrepancies Requiring Investigation", ""]
        for r in warn_rows:
            exp = DISCREPANCY_EXPLANATIONS.get(
                r["metric"], "No specific explanation documented."
            )
            lines.append(f"### `{r['metric']}`")
            lines.append(
                f"- REopt: {_fmt(r['reopt'], r['unit'])}, Excel: {_fmt(r['excel'], r['unit'])}, Delta: {_fmt_delta(r['delta_pct'])}"
            )
            lines.append(f"- {exp}")
            lines.append("")

    lines += [
        "## Expected Discrepancies (per plan Section 6.2)",
        "",
        "1. **Dispatch pattern:** REopt optimizes freely vs. Excel fixed charge windows (11–15h). REopt NPV may be higher.",
        "2. **NPV comparison:** REopt uses unlevered 8% discount rate; Excel uses leveraged equity IRR. Run `equity_irr.py` for fair comparison.",
        "3. **BESS degradation:** REopt uses discrete year-10 replacement; Excel uses 3%/year continuous. Expect ±2–3% energy difference by year 10–15.",
        "4. **Revenue framing:** REopt computes avoided cost; Excel computes PPA income. Economically equivalent when PPA price = avoided rate.",
        "5. **Export cap:** Decree 57 20% cap not yet enforced as hard JuMP constraint. Export volume may be overstated.",
        "",
        "## REopt Additional Outputs",
        "",
        f"- LCC: ${reopt_metrics.get('lcc', 0):,.0f}",
        "",
        "_Generated by compare_reopt_vs_excel.py_",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Comparison report saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Compare REopt vs. Saigon18 Excel outputs"
    )
    parser.add_argument("--reopt", required=True, help="REopt results JSON file")
    parser.add_argument(
        "--extracted",
        default="data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json",
        help="Extracted Excel data JSON (for scenario context)",
    )
    parser.add_argument(
        "--scenario",
        default="A",
        help="Scenario label for the report header (default: A)",
    )
    parser.add_argument(
        "--output",
        default="artifacts/reports/saigon18/2026-03-22_scenario-a_vs_excel_comparison.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()

    with open(args.reopt, encoding="utf-8") as f:
        results = json.load(f)

    reopt_metrics = load_reopt_metrics(results)
    rows = compare_metrics(reopt_metrics, EXCEL_TARGETS)

    # Print summary to stdout
    warn_count = sum(1 for r in rows if r["status"] == "WARN")
    ok_count = sum(1 for r in rows if r["status"] == "OK")
    print(
        f"\nComparison: {ok_count} OK, {warn_count} WARN, "
        f"{sum(1 for r in rows if r['status'] == 'MISSING')} MISSING"
    )

    for r in rows:
        status_sym = {"OK": "OK", "WARN": "!", "MISSING": "?", "INFO": "i"}.get(
            r["status"], " "
        )
        print(
            f"  [{status_sym}] {r['metric']:25s}  "
            f"Excel={_fmt(r['excel'], r['unit']):>12}  "
            f"REopt={_fmt(r['reopt'], r['unit']):>12}  "
            f"delta={_fmt_delta(r['delta_pct']):>8}"
        )

    generate_report(rows, reopt_metrics, args.scenario, Path(args.output))


if __name__ == "__main__":
    main()
