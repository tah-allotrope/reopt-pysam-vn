"""Materialize TOU comparison scenarios with hardcoded tariff stripping.

Existing case study scenarios have pre-baked 8760-hour tariff arrays that bypass
the preprocessing pipeline. This script strips those arrays so the regime-based
tariff generation (Decision 963 vs Decision 14) takes effect.
"""
from __future__ import annotations

import json
import sys
import time
from copy import deepcopy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from reopt_pysam_vn.reopt.preprocess import apply_vietnam_defaults, load_vietnam_data, resolve_vietnam_regime
from reopt_pysam_vn.reopt.regime_runner import (
    DEFAULT_ASSUMPTION_SET_DIR,
    _deep_merge,
    _read_json,
    _slugify,
    _template_context,
    _write_json,
    canonicalize_for_hash,
    load_assumption_set,
    scenario_hash,
)

COMPARISON_ROOT = REPO_ROOT / "artifacts" / "results" / "tou_comparison"
GENERATED_ROOT = REPO_ROOT / "scenarios" / "generated" / "tou_comparison"

SCENARIOS = [
    "scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json",
    "scenarios/case_studies/ninhsim/2026-04-01_ninhsim_scenario-a_baseline-evn.json",
    "scenarios/case_studies/north_thuan/north_thuan_scenario_a.json",
]
REGIMES = ["decision_963_2026_current", "decision_14_2025_legacy"]

HARDCODED_TARIFF_KEYS = [
    "tou_energy_rates_per_kwh",
    "urdb_label",
    "blended_annual_energy_rate",
    "monthly_demand_rates",
    "year1_escalator",
]


def materialize_tou_scenario(scenario_path: Path, regime_id: str) -> dict:
    """Materialize a scenario with regime-based tariff, stripping hardcoded rates."""
    vn = load_vietnam_data()
    base_scenario = _read_json(scenario_path)
    context = _template_context(base_scenario, scenario_path.stem)
    assumption_set = load_assumption_set("base", DEFAULT_ASSUMPTION_SET_DIR)

    scenario = deepcopy(base_scenario)

    # Strip hardcoded tariff arrays so preprocessing generates regime-based rates
    if "ElectricTariff" in scenario:
        for key in HARDCODED_TARIFF_KEYS:
            scenario["ElectricTariff"].pop(key, None)

    scenario = _deep_merge(scenario, assumption_set["scenario_overrides"])
    apply_vietnam_defaults(
        scenario,
        vn,
        customer_type=context["customer_type"],
        voltage_level=context["voltage_level"],
        region=context["region"],
        pv_type=context["pv_type"],
        wind_type=context["wind_type"],
        financial_profile=context["financial_profile"],
        regime_id=regime_id,
    )

    scenario_meta = scenario.setdefault("_meta", {})
    scenario_meta["source_scenario_path"] = str(scenario_path)
    scenario_meta["assumption_set_id"] = "base"
    scenario_meta["tou_comparison"] = True

    resolved_regime = resolve_vietnam_regime(vn, regime_id)
    hash_payload = {
        "scenario": scenario,
        "regime_id": regime_id,
        "assumption_set_id": "base",
        "registry_version": resolved_regime.get("registry_version"),
    }
    canonical = canonicalize_for_hash(hash_payload)
    run_hash = scenario_hash(canonical)
    scenario_meta["scenario_hash"] = run_hash

    project_slug = _slugify(context.get("project_slug", scenario_path.stem))
    generated_dir = GENERATED_ROOT / project_slug
    generated_dir.mkdir(parents=True, exist_ok=True)
    generated_path = generated_dir / f"{run_hash}_{regime_id}_base.json"

    result_dir = COMPARISON_ROOT / project_slug / run_hash
    result_dir.mkdir(parents=True, exist_ok=True)

    input_path = _write_json(result_dir / "input.json", scenario)
    resolved_regime_path = _write_json(result_dir / "resolved_regime.json", resolved_regime)
    _write_json(generated_path, scenario)

    manifest = {
        "project_slug": project_slug,
        "scenario_hash": run_hash,
        "regime_id": regime_id,
        "assumption_set_id": "base",
        "registry_version": resolved_regime.get("registry_version"),
        "source_scenario_path": str(scenario_path),
        "generated_scenario_path": str(generated_path),
        "result_dir": str(result_dir),
        "input_path": str(input_path),
        "resolved_regime_path": str(resolved_regime_path),
        "status": "materialized",
        "cache_hit": False,
        "generated_at_epoch": int(time.time()),
    }

    return {
        "project_slug": project_slug,
        "scenario_hash": run_hash,
        "regime_id": regime_id,
        "result_dir": str(result_dir),
        "manifest": manifest,
        "scenario": scenario,
    }


def main():
    manifest_entries = []
    for scenario_path_str in SCENARIOS:
        scenario_path = Path(scenario_path_str).resolve()
        scenario_slug = _slugify(scenario_path.stem)

        scenario_runs = []
        for regime_id in REGIMES:
            result = materialize_tou_scenario(scenario_path, regime_id)
            scenario_runs.append({
                "regime_id": regime_id,
                "run": {
                    "scenario_hash": result["scenario_hash"],
                    "result_dir": result["result_dir"],
                    "manifest": result["manifest"],
                },
            })
            print(f"  {scenario_slug}/{regime_id}: hash={result['scenario_hash']} status=materialized")

        manifest_entries.append({
            "scenario_slug": scenario_slug,
            "scenario_path": str(scenario_path),
            "pair": scenario_runs,
        })

    manifest_path = COMPARISON_ROOT / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_entries, indent=2), encoding="utf-8")
    print(f"\nManifest written to {manifest_path}")
    print(f"Total scenario pairs: {len(manifest_entries)}")


if __name__ == "__main__":
    main()
