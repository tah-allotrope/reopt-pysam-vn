"""Extract financial metrics from paired TOU comparison results and compute deltas.

Reads the manifest produced by run_tou_comparison.py and emits a CSV summary with
per-scenario financial metrics under both regimes, deltas, and percentage changes.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

REGIME_NEW = "decision_963_2026_current"
REGIME_LEGACY = "decision_14_2025_legacy"

FINANCIAL_KEYS = [
    ("annual_energy_cost_usd", "annual_energy_cost"),
    ("lifecycle_cost_usd", "lifecycle_cost"),
    ("pv_capacity_kw", "pv_capacity_kw"),
    ("annual_pv_production_kwh", "annual_pv_production_kwh"),
    ("annual_grid_purchases_kwh", "annual_grid_purchases_kwh"),
    ("npv_usd", "npv"),
    ("simple_payback_years", "simple_payback_years"),
]


def extract_metrics(result_dir: Path) -> dict:
    reopt_path = result_dir / "reopt-results.json"
    if not reopt_path.is_file():
        return {"status": "no_results"}

    try:
        results = json.loads(reopt_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"status": "parse_error"}

    metrics: dict = {"status": results.get("status", "unknown")}

    if metrics["status"] != "optimal":
        return metrics

    financial = results.get("Financial", {})
    pv = results.get("PV", {})
    if isinstance(pv, list) and len(pv) > 0:
        pv = pv[0]

    metrics["annual_energy_cost_usd"] = financial.get("year_one_electric_cost", None)
    metrics["lifecycle_cost_usd"] = financial.get("lifecycle_electric_cost", None)
    metrics["npv_usd"] = financial.get("npv", None)
    metrics["simple_payback_years"] = financial.get("simple_payback", None)

    metrics["pv_capacity_kw"] = pv.get("size_kw", None)
    metrics["annual_pv_production_kwh"] = pv.get("year_one_energy_produced_kwh", None)

    elec = results.get("ElectricUtility", {})
    metrics["annual_grid_purchases_kwh"] = elec.get("year_one_energy_to_grid_kwh", None)

    return metrics


def safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return (a - b) / abs(b)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract financial deltas from TOU comparison results.")
    parser.add_argument("--manifest", default=str(REPO_ROOT / "artifacts" / "results" / "tou_comparison" / "manifest.json"),
                        help="Path to manifest.json from run_tou_comparison.py")
    parser.add_argument("--output", default=str(REPO_ROOT / "artifacts" / "reports" / "tou_comparison" / "financial_delta_summary.csv"),
                        help="Output CSV path")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_path = Path(args.output)

    if not manifest_path.is_file():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    rows = []
    for entry in manifest:
        slug = entry["scenario_slug"]
        pair = entry["pair"]

        metrics_by_regime = {}
        for item in pair:
            regime_id = item["regime_id"]
            result_dir = Path(item["run"]["result_dir"])
            metrics = extract_metrics(result_dir)
            metrics_by_regime[regime_id] = metrics

        new_m = metrics_by_regime.get(REGIME_NEW, {})
        legacy_m = metrics_by_regime.get(REGIME_LEGACY, {})

        row = {"scenario": slug}

        for csv_key, result_key in FINANCIAL_KEYS:
            new_val = new_m.get(result_key)
            legacy_val = legacy_m.get(result_key)

            row[f"{csv_key}_new"] = new_val
            row[f"{csv_key}_legacy"] = legacy_val

            if new_val is not None and legacy_val is not None:
                delta = new_val - legacy_val
                row[f"{csv_key}_delta"] = delta
                row[f"{csv_key}_pct_change"] = safe_div(new_val, legacy_val)
            else:
                row[f"{csv_key}_delta"] = None
                row[f"{csv_key}_pct_change"] = None

        row["status_new"] = new_m.get("status", "missing")
        row["status_legacy"] = legacy_m.get("status", "missing")
        rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["scenario"]
    for csv_key, _ in FINANCIAL_KEYS:
        fieldnames.extend([f"{csv_key}_new", f"{csv_key}_legacy", f"{csv_key}_delta", f"{csv_key}_pct_change"])
    fieldnames.extend(["status_new", "status_legacy"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Financial delta summary written to {output_path}")
    print(f"Scenarios processed: {len(rows)}")


if __name__ == "__main__":
    main()