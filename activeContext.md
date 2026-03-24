# Active Context — Saigon18 REopt Integration

## Reorganization Pass — 2026-03-24

- [x] Move Layer 3 cross-validation to a dedicated `tests/cross_language/` home while preserving old entrypoints
- [x] Move plan and research docs under `docs/worklog/` with compatibility pointers from old locations
- [x] Update repository docs and test runner references to the canonical paths
- [x] Run targeted validation for the moved paths and record results

---

> Last updated: 2026-03-23 (Decree 57 hard export cap + Scenario A/C reruns)

## Current Execution Checklist

- [x] Implement Decree 57 hard export-cap support in `src/REoptVietnam.jl`
- [x] Add regression/integration coverage for the export cap
- [x] Run targeted validation for the new constraint path
- [x] Record review/results notes for this export-cap pass

---

## Project

Mapping the Saigon18 Excel feasibility model (40.36 MWp solar + 66 MWh BESS, southern Vietnam) onto REopt.jl to validate and challenge the Excel outputs (Equity IRR 19.4%, NPV $22M, 6-yr payback).

Plan: `docs/worklog/plans/saigon18_reopt_integration_plan.md`

---

## Progress by Phase

### Phase 1 — Data Extraction & Input Validation ✅ Complete

| Task | Status | Notes |
|---|---|---|
| `scripts/python/extract_excel_inputs.py` | ✅ Done | Extracts 8760 load/PV/FMP from Excel; validates row count, negatives, yield |
| `scripts/python/build_saigon18_reopt_input.py` | ✅ Done | Builds Scenario A & B JSON; applies Vietnam defaults + project overrides |
| `scripts/python/dppa_settlement.py` | ✅ Done | DPPA CfD post-processing; compute settlement from FMP + REopt dispatch |
| `scripts/python/compare_reopt_vs_excel.py` | ✅ Done | Comparison report script (delta table, 5% flag threshold) |
| `scripts/python/equity_irr.py` | ✅ Done | Levered equity IRR from REopt EBITDA + debt schedule |
| `scripts/julia/run_vietnam_scenario.jl` | ✅ Done | `--scenario <path>` flag; output path branches per mode |
| `tests/python/test_saigon18_data.py` | ✅ Done | 19/19 Layer 1 tests pass |
| `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json` | ✅ Done | 71.81 GWh PV, 184.26 GWh load, 30.2 MW peak — all checks passed |
| `scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json` | ✅ Done | Built; no-solve validation passed |
| `scenarios/case_studies/saigon18/2026-03-20_scenario-b_fixed-sizing_ppa-discount.json` | ✅ Done | Built |
| No-solve validation (`--scenario ... --no-solve`) | ✅ Done | Scenario A passes |

### Phase 2 — REopt Run & Baseline Comparison ✅ Complete

| Task | Status | Notes |
|---|---|---|
| Run Scenario A (full EVN TOU, fixed sizing) | ✅ Done | OPTIMAL |
| Run Scenario B (PPA × 0.85, fixed sizing) | ✅ Done | OPTIMAL |
| Generate comparison reports | ✅ Done | A vs Excel + B vs Excel; regenerated 2026-03-22 after key-mapping fix |
| Equity IRR (Scenario A) | ✅ Done | Corrected to 19.8% after EBITDA bug fix and rerun |

#### Scenario A Results (2026-03-20)
| Metric | REopt Result |
|---|---|
| Status | OPTIMAL |
| PV size | 40,360 kW (fixed) |
| Year-1 PV energy | 71.81 GWh |
| BESS power / capacity | 20,000 kW / 66,000 kWh (fixed) |
| LCC | $129.5M |
| NPV | $10.6M |
| CAPEX | $47.5M |
| Year-1 savings (before tax) | $5.93M |
| Year-1 savings (after tax) | $4.74M |
| Unlevered IRR | 12.6% |
| Simple payback | 7.97 yr |
| Grid purchases (year 1) | 117,705 MWh |
| PV exported to grid | 549 MWh |
| Output file | `artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json` |

#### Scenario A Re-run with Hard Export Cap (2026-03-23)
| Metric | REopt Result |
|---|---|
| Status | OPTIMAL |
| PV size | 40,360 kW (fixed) |
| Average annual PV energy | 69.02 GWh |
| PV exported to grid | 549 MWh |
| Export fraction of PV production | 0.80% |
| BESS power / capacity | 20,000 kW / 66,000 kWh (fixed) |
| LCC | $129.5M |
| NPV | $10.55M |
| Simple payback | 7.97 yr |
| Unlevered IRR | 12.6% |
| Output file | `artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json` |

#### Scenario B Results (2026-03-20)
| Metric | REopt Result |
|---|---|
| Status | OPTIMAL |
| PV / BESS | Same fixed sizing as A |
| LCC | $118.1M |
| NPV | $0.89M |
| Simple payback | 10.2 yr |
| Output file | `artifacts/results/saigon18/2026-03-20_scenario-b_fixed-sizing_ppa-discount_reopt-results.json` |

#### Scenario C Results (2026-03-23)
| Metric | REopt Result |
|---|---|
| Status | OPTIMAL |
| PV size | 42,666 kW |
| Average annual PV energy | 57.44 GWh |
| PV exported to grid | 3,714 MWh |
| Export fraction of PV production | 6.47% |
| BESS power / capacity | 0 kW / 0 kWh |
| LCC | $128.2M |
| NPV | $11.80M |
| Simple payback | 7.52 yr |
| Unlevered IRR | 14.2% |
| Output file | `artifacts/results/saigon18/2026-03-23_scenario-c_optimized-sizing_reopt-results.json` |

#### Phase 2 Comparison: REopt vs Excel
| Metric | Excel | Scenario A | Scenario B |
|---|---|---|---|
| PV generation | 71,808 MWh | 71,808 MWh ✓ | 71,808 MWh ✓ |
| NPV | $22.0M | $10.6M (−52%) | $0.89M (−96%) |
| Payback | 6.0 yr | 8.0 yr (+33%) | 10.2 yr (+70%) |
| Year-1 revenue/savings | $5.06M | $5.93M pre-tax (+17%) | $4.98M (−1.5%) |

#### Equity IRR Re-run (2026-03-22)
| Metric | Excel | REopt-derived |
|---|---|---|
| Equity IRR | 19.4% | 19.8% |
| Delta | — | +0.4% |
| Equity NPV @ 10% | — | $24.5M |
| Output file | — | `artifacts/reports/saigon18/2026-03-22_equity-irr_summary.json` |

Reports: `artifacts/reports/saigon18/2026-03-22_scenario-a_vs_excel_comparison.md`, `artifacts/reports/saigon18/2026-03-22_scenario-b_vs_excel_comparison.md`, `artifacts/reports/saigon18/2026-03-22_equity-irr_summary.json`

### Phase 3 — Custom Constraints & Advanced Scenarios ⏳ In progress

| Task | Status |
|---|---|
| Fix `equity_irr.py` EBITDA extraction bug (see bug log) | ✅ Fixed 2026-03-22 |
| Fix `compare_reopt_vs_excel.py` energy-flow key mapping (see bug log) | ✅ Fixed 2026-03-22 |
| Re-run equity IRR validation vs Excel 19.4% | ✅ Done — 19.8% vs 19.4% (+0.4%) |
| Re-generate Scenario A/B comparison reports with corrected keys | ✅ Done |
| Add regression test for Saigon18 comparison key mapping | ✅ Done — `tests/python/test_saigon18_compare.py` |
| Decree 57 20% export cap as hard JuMP constraint in `src/REoptVietnam.jl` | ✅ Done 2026-03-23 |
| Optional fixed BESS dispatch window constraints (Option B) | ⏳ Not started |
| Scenario C — optimized sizing (unconstrained PV + BESS) | ✅ Done 2026-03-23 |
| `tests/python/test_saigon18_integration.py` (Layer 4) | ⏳ Not started |

---

## Phase 2 Bug Log — Script Fixes Applied

### Bug 1: `equity_irr.py` — EBITDA uses discounted NPV not nominal savings ✅ FIXED (2026-03-22)

**Root cause:** `extract_annual_ebitda()` computed `lcc_bau - lcc_opt` which equals the NPV
(both LCC values are present-value lifecycle costs). It then divided this discounted total
by a nominal escalation factor sum, producing a severely understated year-1 CF (~$319K
instead of ~$5.93M). This drove equity IRR to −17.9% — a model artifact, not a real result.

**Fix applied:** `extract_annual_ebitda()` now uses
`Financial.year_one_total_operating_cost_savings_before_tax` ($5,929,979) as year-1 base,
grown at `elec_cost_escalation_rate_fraction` (default 5%) each year.

**Rerun result:** `artifacts/reports/saigon18/2026-03-22_equity-irr_summary.json` now shows
19.8% equity IRR vs Excel 19.4% (+0.4%), confirming the earlier −17.9% was a script artifact.

### Bug 2: `compare_reopt_vs_excel.py` — energy flow keys don't match REopt output ✅ FIXED (2026-03-22)

**Root cause:** Script looks for keys like `year_one_to_load_kwh`, `year_one_to_grid_kwh`,
`year_one_to_load_series_kw` (BESS) which don't exist in the results JSON. Actual keys:

| Metric | Wrong key used | Correct key | Location |
|---|---|---|---|
| PV to load | `pv.year_one_to_load_kwh` | `sum(pv.electric_to_load_series_kw)` | PV (series sum) |
| PV to grid | `pv.year_one_to_grid_kwh` | `pv.annual_energy_exported_kwh` | PV scalar |
| BESS discharge | `storage.year_one_to_load_series_kw` | sum of BESS series (not in scalar output) | ElectricStorage |
| Grid purchases | `utility.year_one_energy_supplied_kwh` | `utility.annual_energy_supplied_kwh` | ElectricUtility |
| Year-1 revenue | `npv / 25` | `fin.year_one_total_operating_cost_savings_before_tax` | Financial |

**Fix applied:** `load_reopt_metrics()` now reads the actual REopt result schema:
- PV production from `PV.year_one_energy_produced_kwh`
- PV non-export delivery as `year_one_energy_produced_kwh - annual_energy_exported_kwh`
- PV export from `PV.annual_energy_exported_kwh`
- BESS discharge from `ElectricStorage.storage_to_load_series_kw`
- Grid purchases from `ElectricUtility.annual_energy_supplied_kwh`
- Year-1 revenue from `Financial.year_one_total_operating_cost_savings_before_tax`

Added regression coverage in `tests/python/test_saigon18_compare.py` to lock this mapping.

**Actual values (Scenario A, corrected report):**
- PV to grid: 549 MWh (REopt) vs Excel 1,087 MWh — Decree 57 cap partially effective
- Grid purchases: 117,705 MWh (REopt) vs Excel 112,454 MWh — +4.7%, within range
- Year-1 savings: $5.93M (REopt) vs $5.06M (Excel) — +17%, reasonable given TOU optimization
- BESS discharge: 17,956 MWh (REopt annual storage-to-load throughput) vs Excel 8,591 MWh — large gap remains and likely needs tariff-period disaggregation for apples-to-apples comparison

---

## API Compatibility Fixes Applied (REopt.jl)

The installed REopt.jl package has a newer API than the scripts assumed. Fixed in this session:

| Old field | New field | File |
|---|---|---|
| `ElectricStorage.min_soc_fraction` | `soc_min_fraction` | `build_saigon18_reopt_input.py` |
| `ElectricStorage.max_soc_fraction` | *(removed — defaults to 1.0)* | `build_saigon18_reopt_input.py` |
| `ElectricStorage.om_cost_per_kwh` | `om_cost_fraction_of_installed_cost` | `build_saigon18_reopt_input.py` |
| `ElectricTariff.energy_rate_series_per_kwh` | `tou_energy_rates_per_kwh` | `reopt_vietnam.py` + `build_saigon18_reopt_input.py` |
| `ElectricTariff.net_metering_limit_kw` | *(removed)* | `reopt_vietnam.py` |
| `ElectricTariff.export_rate_beyond_curtailment_limit` | `export_rate_beyond_net_metering_limit` | `reopt_vietnam.py` |
| `schedule["sunday"]` key | dynamic fallback to `"sunday_and_public_holidays"` | `reopt_vietnam.py` |
| Runner script `get(String, String, String)` crash at line 126 | `status = "unknown"` default | `run_vietnam_scenario.jl` |

Tariff data fix: added `"industrial"` alias block (with `high_voltage_above_35kv_below_220kv` and `medium_voltage_22kv_to_110kv` keys) to `data/vietnam/vn_tariff_2025.json` — the v2025.2 update renamed it to `"production"` but all scripts/tests still use `"industrial"`.

## Validation Status Update (2026-03-23)

The tariff v2025.2 schema drift in both Julia and Python test suites was fixed in this session.

| Validation scope | Result |
|---|---|
| `tests/python/test_data_validation.py` | PASS |
| `tests/python/test_unit.py` | PASS |
| `tests/cross_language/cross_validate.py` | PASS |
| `tests/python/test_integration.py` | PASS (1 skipped API block) |
| `tests/julia/test_data_validation.jl` | PASS |
| `tests/julia/test_unit.jl` | PASS |

Known environment noise remains on Julia startup from ArchGDAL method-overwrite precompile warnings, but it did not block scenario solves or the relevant validation passes.

---

## Next Actions

1. **Refine BESS comparison metric** — the report now uses actual REopt storage output keys, but it compares Excel's peak+standard dispatch target against total annual `storage_to_load_series_kw`. Next refinement should split REopt discharge by tariff period for apples-to-apples validation.

2. **Refresh Scenario A / Scenario C comparison artifacts** now that both were re-solved through the hard export-cap path.

3. **Add `tests/python/test_saigon18_integration.py`** for the Saigon18 real-project pipeline.

4. **Refine BESS comparison metric by tariff period** for apples-to-apples Excel vs REopt validation.

5. **Optional fixed BESS dispatch window constraints (Option B)** if comparison to the Excel control logic becomes the priority.

---

## Review / Results — 2026-03-23 Decree 57 Hard Export Cap

### What changed

- Added a Vietnam-specific solver wrapper `run_vietnam_reopt` in `src/REoptVietnam.jl` that builds the REopt JuMP model, injects a hard annual PV export cap constraint, then solves and post-processes results.
- `apply_decree57_export!` now stores `decree57_max_export_fraction` in `_meta` so scenario JSONs carry the intended cap into the Julia solve path.
- `scripts/julia/run_vietnam_scenario.jl` now uses `run_vietnam_reopt(...)` instead of plain `run_reopt(...)`, so scenario runs honor the Decree 57 cap automatically.
- Added a Julia integration test scenario that verifies annual PV exports are capped at 20% of annual PV production.
- Updated Julia/Python tariff preprocessing and validation tests for the tariff v2025.2 schema (`tou_energy_rates_per_kwh`, commercial subcategories, `sunday_and_public_holidays`, legacy voltage aliases).
- Rebuilt Scenario C and re-solved Scenario A + Scenario C through the hard export-cap runner.

### Targeted validation

- Focused synthetic Julia solve passed with `status=optimal`.
- Validation result: `annual_energy_exported_kwh = 175,200`, `annual_energy_produced_kwh = 876,000`, export fraction `= 0.2000` (exactly at the Decree 57 cap).
- Scenario A rerun passed with fixed design intact and export fraction `0.80%`, well below the 20% cap.
- Scenario C solve passed and selected `42.67 MWp PV` with `0 MW / 0 MWh BESS`; export fraction `6.47%`, also below the cap.

### Known remaining issues

- Scenario comparison/report artifacts have not yet been regenerated for Scenario A/C after the hard export-cap reruns.
- Julia startup still emits ArchGDAL precompile noise in this environment, but solves and tests complete successfully.

---

## Review / Results — 2026-03-24 Low-Risk Repository Reorganization

### What changed

- Moved Layer 3 cross-validation to the canonical path `tests/cross_language/cross_validate.py` and added `tests/cross_validate.py` as a backward-compatible wrapper for direct script and pytest usage.
- Moved worklog plan and research notes into `docs/worklog/plans/` and `docs/worklog/research/` to better separate stable docs from active project process material.
- Updated `tests/run_all_tests.ps1`, `README.md`, `docs/testing.md`, and `activeContext.md` to point at the canonical paths.

### Targeted validation

- `python tests/cross_language/cross_validate.py` — PASS
- `python tests/cross_validate.py` — PASS (legacy wrapper path)
- `powershell -ExecutionPolicy Bypass -File tests\run_all_tests.ps1 -Layer 3 -JuliaTimeoutSeconds 1200` — PASS

### Compatibility notes

- The old `tests/cross_validate.py` entrypoint still works for both direct execution and pytest collection.
- Worklog material now lives only under `docs/worklog/`; the temporary redirect folders were removed in the follow-up cleanup pass.

---

## Review / Results — 2026-03-24 Case-Study Assets and Artifacts Reorganization

### What changed

- Moved the Saigon18 source workbook into `data/raw/saigon18/2026-01-29_saigon18_excel_model_v2.xlsm` and the extracted JSON into `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json`.
- Moved Saigon18 scenario JSON files into `scenarios/case_studies/saigon18/` and renamed them with dates plus descriptive scenario labels to make the work timeline easier to scan.
- Moved optimization outputs and reports into the canonical `artifacts/results/` and `artifacts/reports/` trees, with timeline-friendly filenames like `2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json`.
- Updated Python script defaults, the Julia scenario runner, `.claude/settings.local.json`, and the Saigon18 regression test to use the new canonical paths.
- Consolidated old placeholder-folder notes into `legacy/README.md` and prepared the redundant empty legacy directories for removal.
- Regenerated the canonical Scenario D JSON and refreshed the canonical comparison and equity-IRR artifacts using the renamed paths.

### Targeted validation

- `python scripts/python/build_saigon18_reopt_input.py` — PASS
- `python -m pytest tests/python/test_saigon18_data.py -v --tb=short` — PASS
- `python -m pytest tests/python/test_saigon18_compare.py -v --tb=short` — PASS
- `python scripts/python/compare_reopt_vs_excel.py --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json --scenario "A (fixed sizing EVN TOU)"` — PASS
- `python scripts/python/equity_irr.py --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json --capex 49510000` — PASS
- `JULIA_PKG_PRECOMPILE_AUTO=0 julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --scenario scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json --no-solve` — PASS

### Compatibility notes

- Legacy path guidance now lives in `legacy/README.md`, and the redundant empty placeholder folders have been removed.
- Historical artifact filenames now encode both the work date and the scenario/report purpose, which should make the sequence of the Saigon18 analysis easier to follow.

---

## Review / Results — 2026-03-24 Legacy Folder Consolidation

### What changed

- Removed the redundant empty compatibility folders under the old `data/real_project/`, `scenarios/real_project/`, `results/`, and `reports/` locations.
- Consolidated the old-to-new folder mapping into one place: `legacy/README.md`.
- Updated `README.md` and `activeContext.md` so they point to the consolidated legacy index instead of scattered placeholder README files.

### Validation

- Verified the repo root no longer contains the redundant `results/` or `reports/` placeholder trees.
- Verified no code, docs, or tests still depend on those removed folders.

---

## Review / Results — 2026-03-24 Final Root Cleanup

### What changed

- Removed the last redirect-only root folder, `plans/`, after confirming all references already pointed at `docs/worklog/plans/`.
- Confirmed `research/` had already been fully removed and no longer needed a compatibility marker.
- Kept `legacy/README.md` as the single consolidated place for old-to-new path guidance.

### Validation

- Verified the root now uses canonical folders only for active content, with no remaining redirect-only `plans/` or `research/` folders.
- Verified no remaining code or docs depend on the removed redirect folder.

---

## Review / Results — 2026-03-24 Final Polish Pass

### What changed

- Expanded `.gitignore` to cover local Python quality/test artifacts like `.ruff_cache/`, `.hypothesis/`, and coverage outputs.
- Updated `README.md` quick-start guidance to use the canonical `artifacts/`, `data/raw`, `data/interim`, and `scenarios/case_studies` paths.
- Added a dedicated Saigon18 workflow section to `README.md` so the current case-study process is discoverable from the repo entry point.
- Standardized the default example output filename in `scripts/julia/run_vietnam_scenario.jl` to `commercial-rooftop_reopt-results.json` for better naming consistency.

### Validation

- Verified README examples point only at current canonical paths.
- Verified the final root structure remains clean after the polish updates.

---

## Outstanding / Pending Confirmations

- [ ] Confirm actual site coordinates (currently lat=10.9577, lon=106.8426 near HCMC)
- [ ] Confirm whether Saigon18 uses private-wire or grid-connected DPPA — ceiling tariff differs
- [ ] Two-part tariff (capacity charge) sensitivity — Decree 146/2025 pilot Jan–Jun 2026

### Deferred (Phase 3)
- Two-part tariff sensitivity scenario

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| PV production profile | Inject from Excel (Option B) | Apples-to-apples vs Excel; avoids NREL API dependency |
| BESS degradation | `battery_replacement_year=10`, `replace_cost_per_kwh=100` | REopt uses discrete replacement model |
| CIT tax rate | Blended 0.0575 | 4yr exempt + 9yr 50% + 7yr full |
| BESS dispatch | REopt free optimization (Phase 1–2) | Uncover dispatch value vs Excel fixed schedule |
| Currency | VND→USD at 26,400 VND/USD | REopt outputs USD |
| Customer type | `"industrial"` / `high_voltage_above_35kv_below_220kv` (110kV) | Manufacturing park, 110kV grid connection |

---

## Scenario Summary

| ID | Description | Tariff | Sizing | Status |
|---|---|---|---|---|
| A | Baseline — REopt TOU optimization | Full EVN TOU (Decision 14) | Fixed (40.36 MWp + 66 MWh) | ✅ OPTIMAL |
| B | Bundled PPA — 15% discount | EVN TOU × 0.85 | Fixed | ✅ OPTIMAL |
| C | Optimized sizing | Full EVN TOU | Unconstrained (up to 60 MWp / 100 MWh) | ✅ OPTIMAL |
| D | DPPA strike price contract | EVN TOU (base) + FMP post-processing | Fixed | ⏳ Phase 3 |

---

## File Map

```
scripts/python/
  extract_excel_inputs.py       ← Excel → saigon18_extracted.json
  build_saigon18_reopt_input.py ← extracted JSON → scenario A/B JSON
  dppa_settlement.py            ← DPPA CfD revenue post-processor
  compare_reopt_vs_excel.py     ← corrected REopt-vs-Excel delta report
  equity_irr.py                 ← levered equity IRR from REopt EBITDA

scripts/julia/
  run_vietnam_scenario.jl       ← runner; --scenario flag

tests/python/
  test_saigon18_data.py         ← Layer 1 data validation ✅
  test_saigon18_compare.py      ← comparison key-mapping regression ✅

data/raw/saigon18/
  2026-01-29_saigon18_excel_model_v2.xlsm             ← source Excel ✅

data/interim/saigon18/
  2026-03-20_saigon18_extracted_inputs.json           ← extracted data ✅

scenarios/case_studies/saigon18/
  2026-03-20_scenario-a_fixed-sizing_evntou.json         ✅
  2026-03-20_scenario-b_fixed-sizing_ppa-discount.json   ✅
  2026-03-23_scenario-c_optimized-sizing.json            ✅

artifacts/results/saigon18/
  2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json        ✅
  2026-03-20_scenario-b_fixed-sizing_ppa-discount_reopt-results.json  ✅

artifacts/reports/saigon18/
  2026-03-22_scenario-a_vs_excel_comparison.md  ✅
  2026-03-22_scenario-b_vs_excel_comparison.md  ✅
  2026-03-22_equity-irr_summary.json            ✅
```
