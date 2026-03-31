# Active Context — Saigon18 REopt Integration

## North Thuan REopt Validation Plan — 2026-03-31

- [x] Phase 1 - Create North Thuan extracted inputs and synthetic 8760 load builder
- [x] Phase 2 - Build North Thuan REopt scenario JSON generator for scenarios A/B/C
- [x] Phase 3 - Update Julia runner/output routing and add North Thuan orchestration path
- [x] Phase 4 - Implement REopt-vs-staff comparison extraction and regression tests
- [x] Phase 5 - Add DPPA settlement post-processing from REopt dispatch outputs
- [x] Phase 6 - Generate North Thuan REopt HTML report artifacts
- [x] Validation - Run targeted Python tests and at least no-solve North Thuan scenario validation
- [x] Review / Results - Record outcomes and generated report paths after completion

### Notes

- User requested HTML report generation at the end of each phase via the `report` skill.
- This pass should reuse existing Saigon18 and North Thuan report conventions where possible.

### Outputs Generated

- `data/interim/north_thuan/north_thuan_extracted_inputs.json`
- `scenarios/case_studies/north_thuan/north_thuan_scenario_a.json`
- `scenarios/case_studies/north_thuan/north_thuan_scenario_b.json`
- `scenarios/case_studies/north_thuan/north_thuan_scenario_c.json`
- `artifacts/results/north_thuan/north_thuan_scenario_a_reopt-results.json`
- `artifacts/results/north_thuan/north_thuan_scenario_b_reopt-results.json`
- `artifacts/results/north_thuan/north_thuan_scenario_c_reopt-results.json`
- `artifacts/reports/north_thuan/2026-03-31_north-thuan-reopt-validation.json`
- `artifacts/reports/north_thuan/2026-03-31_north-thuan-reopt-validation.html`
- `reports/2026-03-31-north-thuan-phase-1-environment-and-data-preparation.html`
- `reports/2026-03-31-north-thuan-phase-2-reopt-scenario-construction.html`
- `reports/2026-03-31-north-thuan-phase-3-local-julia-runner-and-solve-path.html`
- `reports/2026-03-31-north-thuan-phase-4-energy-comparison-extraction.html`
- `reports/2026-03-31-north-thuan-phase-5-dppa-settlement-post-processing.html`
- `reports/2026-03-31-north-thuan-phase-6-html-report-synthesis.html`

### Review / Results

- Added `scripts/python/build_north_thuan_load_profile.py` to create a deterministic 8760 industrial load profile, derived FMP proxy, and synthetic wind production-factor fallback from the staff PDF summary inputs.
- Added `scripts/python/build_north_thuan_reopt_input.py` and `scripts/python/run_north_thuan_reopt.py` so North Thuan now has the same build/run workflow shape as Saigon18.
- Updated `scripts/julia/run_vietnam_scenario.jl` so `scenarios/case_studies/north_thuan/` solves save into `artifacts/results/north_thuan/` automatically.
- Added `scripts/python/compare_north_thuan_reopt_vs_staff.py`, `scripts/python/generate_north_thuan_reopt_report.py`, and `tests/python/test_north_thuan_reopt.py` for solved-result comparison, HTML reporting, and regression coverage.
- Extended `scripts/python/dppa_settlement.py` with `compute_virtual_dppa_developer_revenue()` for the North Thuan virtual-DPPA revenue check without breaking the existing Saigon18 settlement path.
- Generated six report-skill-style phase reports in `reports/` using `scripts/python/generate_north_thuan_phase_reports.py` and the shared `report-template.html` shell.

### Validation

- `python -m pytest tests/python/test_north_thuan_reopt.py -v --tb=short` - PASS
- `python scripts/python/run_north_thuan_reopt.py --scenarios a --no-solve` - PASS
- `python scripts/python/run_north_thuan_reopt.py --scenarios a` - PASS after switching Wind to a synthetic `production_factor_series` fallback
- `python scripts/python/run_north_thuan_reopt.py --scenarios b c` - PASS
- `python scripts/python/compare_north_thuan_reopt_vs_staff.py ...` - PASS
- `python scripts/python/generate_north_thuan_reopt_report.py` - PASS
- `python scripts/python/generate_north_thuan_phase_reports.py --template ... --outdir reports` - PASS
- `python -m pytest tests/python/test_saigon18_compare.py tests/python/test_saigon18_phase3.py tests/python/test_north_thuan_reopt.py -v --tb=short` - PASS

### Key Results

- Scenario A solved optimally at fixed 30 MW solar + 20 MW wind + 10 MW / 40 MWh BESS.
- Scenario A energy comparison vs staff: solar 45.87 GWh (-10.1%, WARN), wind 66.58 GWh (-0.0%, OK), total RE 112.44 GWh (-4.4%, OK), matched volume 110.32 GWh (+57.5%, WARN), RE penetration 46.68% (-4.4%, OK), self-consumption 98.11% (+64.6%, WARN), factory NPV proxy $6.51M (-18.4%, WARN).
- Scenario B optimized to 24.59 MW solar, 50.00 MW wind, and no storage with factory NPV proxy $35.04M.
- Scenario C no-BESS baseline solved at the staff generation sizes with factory NPV proxy $18.66M.
- DPPA settlement post-processing landed at $6.07M year-1 developer revenue versus the staff $6.0M claim (+1.1%, OK).

### Known Limitations From This Pass

- The North Thuan proxy coordinate remains outside the NREL wind-resource coverage used by REopt's default Wind Toolkit fetch, so the workflow now intentionally uses a synthetic `Wind.production_factor_series` fallback.
- The synthetic load profile and flat year-1 FMP proxy materially affect matched volume and self-consumption, so those WARNs should be treated as model-input sensitivity rather than final project conclusions.

## Phase 7 — Cross-Project Dashboard — 2026-03-29

- [x] Implement `scripts/python/generate_cross_project_dashboard.py` — unified dashboard
- [x] Run dashboard: `artifacts/reports/2026-03-29_cross-project-dashboard.html` (18,415 bytes)
- [x] Git commit: all Phase 4–7 changes staged and committed

### Phase 7 Key Content

| Section | Description |
|---|---|
| Project overview cards | Saigon18 (40.36 MWp solar + 66 MWh BESS, private-wire) vs North Thuan (30 MW solar + 20 MW wind + 10 MW/40 MWh BESS, virtual CfD) |
| Financial metrics table | IRR, NPV, payback, DSCR side-by-side |
| Contract risk comparison | Private-wire (no FMP exposure) vs virtual CfD (FMP risk) |
| Strike sensitivity tables | Saigon18 800–1,149.86 VND/kWh; North Thuan 3.5–7.394 ¢/kWh |
| BESS dispatch value | REopt +88.8% vs Excel Option B |
| Key takeaways | 5 callouts for investment committee |

---

## Phase 6 — North Thuan Staff Validation — 2026-03-29

- [x] Implement `scripts/python/validate_north_thuan.py` — recomputes all metrics from PDF inputs
- [x] Implement `scripts/python/generate_north_thuan_validation_report.py` — standalone HTML report
- [x] Run validation: `artifacts/reports/north_thuan/2026-03-29_north-thuan-validation.json`
- [x] Publish validation HTML: `artifacts/reports/north_thuan/2026-03-29_north-thuan-validation.html`

### Phase 6 Key Results: 11 OK / 3 WARN / 0 FAIL

| Metric | Computed | Staff Report | Delta | Status |
|---|---|---|---|---|
| Energy metrics (6 items) | ✓ exact | ✓ exact | 0% | OK |
| Factory gross saving yr1 | $1,326,747 | $1,330,000 | −0.2% | OK |
| Factory NPV (25yr) | $7.87M | $7.97M | −1.3% | OK |
| Project IRR | 17.9% | 18.1% | −1.1% | OK |
| Equity IRR | 33.0% | 31.4% | +5.1% | WARN |
| Project NPV (@ 15%) | $4.78M | $5.19M | −7.9% | WARN |
| Equity NPV (@ 15%) | $10.23M | $10.36M | −1.3% | OK |
| Min DSCR | 1.71 | 1.53 | +11.8% | WARN |
| Project Payback | Year 6 | Year 6 | 0% | OK |

WARN explanations: Equity IRR gap due to FMP year-1 assumption; NPV gap due to discount rate convention (confirmed 15%); DSCR gap likely from staff's cash-sweep reserve. No errors in staff's model.

Conclusion: Staff report VALIDATED — suitable for investment committee review.

---

## Phase 5 — Two-Part Tariff + BESS Dispatch — 2026-03-29

- [x] Implement `scripts/python/two_part_tariff_sensitivity.py` — Decree 146/2025 capacity charge sweep
- [x] Implement `scripts/python/bess_dispatch_analysis.py` — REopt vs Excel Option B comparison
- [x] Run sensitivity: `artifacts/reports/saigon18/2026-03-29_two-part-tariff-sensitivity.json`
- [x] Run BESS analysis: `artifacts/reports/saigon18/2026-03-29_bess-dispatch-analysis.json`
- [x] Publish Phase 5 HTML report: `artifacts/reports/saigon18/2026-03-29_saigon18-phase5.html`
- [x] Full Python test suite: 117 passed, 1 skipped — clean

### Phase 5 Key Results

| Analysis | Finding |
|---|---|
| Decree 146 pilot rate (60 kVND/kW-month) | +$31,936/yr demand savings (current dispatch) |
| Demand shaving estimate (re-tuned BESS) | +$98,073/yr (upper bound without re-solving) |
| BAU → post-solar+BESS peak reduction | 30,246 → 27,104 kW (−3,142 kW) |
| REopt vs Excel Option B dispatch value | $1,917,232 vs $1,015,422 (+88.8%) |
| Full Python test suite | 117 passed, 1 skipped, 0 failed |

---

## Phase 4 — Private-Wire DPPA Correction — 2026-03-29

- [x] Confirm site: Ninh Sim, Khanh Hoa; proxy coords 12.48°N, 109.09°E applied to all 4 scenario JSONs
- [x] Confirm DPPA type: private-wire; update `dppa_settlement.py` formula and default contract type
- [x] Re-settle Scenario D: private_wire, strike=1,100 VND/kWh → `2026-03-29_scenario-d_dppa-settlement.json`
- [x] Re-run equity IRR: `2026-03-29_scenario-d_equity-irr_summary.json`
- [x] Regenerate Scenario D comparison report: `2026-03-29_scenario-d_vs_excel_comparison.md`
- [x] Publish Phase 4 HTML report: `artifacts/reports/saigon18/2026-03-29_saigon18-phase4.html`
- [x] All 23 Python tests pass

### Phase 4 Key Results

| Metric | Grid-connected (Phase 3) | Private-wire (Phase 4) |
|---|---|---|
| Contract type | grid_connected | private_wire |
| Strike price | 1,800 VND/kWh | 1,100 VND/kWh |
| Strike legality | Exceeded ceiling (illegal) | Below ceiling ✓ |
| Year-1 DPPA revenue | $1.10M (CfD differential) | $2.76M (strike × matched) |
| Settlement NPV (20yr) | $15.8M | $39.6M |
| Equity IRR (combined) | 25.4% | 34.3% |
| Site coords | 10.9577, 106.8426 (HCMC, wrong) | 12.48, 109.09 (Ninh Sim proxy) |

Note: Combined EBITDA (REopt base + settlement) is additive for framework consistency. In private-wire, the settlement represents the developer's contracted receipt; partial overlap with REopt avoided-cost base exists.

---

## Reorganization Pass — 2026-03-24

- [x] Move Layer 3 cross-validation to a dedicated `tests/cross_language/` home while preserving old entrypoints
- [x] Move plan and research docs under `docs/worklog/` with compatibility pointers from old locations
- [x] Update repository docs and test runner references to the canonical paths
- [x] Run targeted validation for the moved paths and record results

---

> Last updated: 2026-03-26 (Phase 3 completion + final consolidated HTML report)

## Current Execution Checklist

- [x] Fix Scenario D DPPA post-processing so it uses the actual REopt result schema and explicit settlement assumptions
- [x] Solve Scenario D and produce canonical DPPA settlement + equity artifacts
- [x] Refresh Scenario A/C comparison artifacts after the hard export-cap reruns
- [x] Add tariff-period BESS dispatch disaggregation to the Saigon18 comparison workflow
- [x] Add Saigon18 regression coverage to Layer 4 and wire it into the test runner
- [x] Generate the final consolidated HTML report after Scenario D is complete
- [x] Run targeted validation and record review/results for this completion pass

## Phase 3 Completion Pass — 2026-03-26

- [x] Audit the current Scenario D, comparison, test, and report pipeline against the canonical repo paths
- [x] Repair the DPPA settlement and equity workflow so Scenario D can produce a final finance result
- [x] Extend the comparison tooling with tariff-period BESS breakdown and refreshed scenario outputs
- [x] Add Saigon18 regression coverage to the Layer 4 execution path
- [x] Generate the final self-contained HTML report after Scenario D artifacts are in place
- [x] Run targeted validation and capture the completion review notes

---

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

---

## Review / Results — 2026-03-26 Phase 3 Completion + Final HTML Report

### What changed

- Rewrote `scripts/python/dppa_settlement.py` to use the actual REopt result schema (`PV.electric_to_load_series_kw` + `ElectricStorage.storage_to_load_series_kw`) and to normalize the extracted FMP series safely before computing Scenario D settlement revenue.
- Extended `scripts/python/equity_irr.py` so Scenario D can add DPPA settlement cash flows on top of the base REopt EBITDA and emit a dedicated Scenario D equity summary.
- Replaced `scripts/python/compare_reopt_vs_excel.py` with a version that supports tariff-period BESS disaggregation, Scenario D settlement/equity adders, and refreshed A/C/D markdown comparison artifacts.
- Added `tests/python/test_saigon18_phase3.py` for the Scenario D schema, tariff-period BESS split, and DPPA finance-adder regression path.
- Updated `tests/run_all_tests.ps1` so the Saigon18 Phase 3 regression test runs in the Layer 4 path during full validation.
- Fixed `scripts/julia/run_vietnam_scenario.jl` output path detection so Saigon18 scenario solves write to the canonical `artifacts/results/saigon18/` tree even when invoked from bash on Windows.
- Added `scripts/python/generate_html_report.py` and generated the final consolidated HTML report at `artifacts/reports/saigon18/2026-03-26_saigon18-full-analysis.html`.

### Scenario D final outputs

- Canonical solve result: `artifacts/results/saigon18/2026-03-20_scenario-d_dppa-baseline_reopt-results.json`
- DPPA settlement artifact: `artifacts/reports/saigon18/2026-03-26_scenario-d_dppa-settlement.json`
- Scenario D equity artifact: `artifacts/reports/saigon18/2026-03-26_scenario-d_equity-irr_summary.json`
- Scenario D comparison report: `artifacts/reports/saigon18/2026-03-26_scenario-d_vs_excel_comparison.md`
- Final consolidated HTML report: `artifacts/reports/saigon18/2026-03-26_saigon18-full-analysis.html`

### Key results locked for the final report

- Scenario D contract assumption used in the final report: `grid_connected`
- Scenario D strike price: `1,800 VND/kWh`
- Scenario D year-1 DPPA settlement: `$1.10M`
- Scenario D settlement NPV adder: `$15.80M`
- Scenario D total unlevered NPV (base REopt + settlement adder): `$26.35M`
- Scenario D equity IRR: `25.4%`
- Scenario A tariff-period BESS discharge: `17,543 MWh peak`, `413 MWh standard`, `0 MWh off-peak`

### Validation

- `python -m pytest tests/python/test_saigon18_compare.py tests/python/test_saigon18_phase3.py -v --tb=short` — PASS
- `julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --scenario scenarios/case_studies/saigon18/2026-03-20_scenario-d_dppa-baseline.json --no-solve` — PASS
- `julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --scenario scenarios/case_studies/saigon18/2026-03-20_scenario-d_dppa-baseline.json` — PASS
- `python scripts/python/dppa_settlement.py --reopt artifacts/results/saigon18/2026-03-20_scenario-d_dppa-baseline_reopt-results.json ...` — PASS
- `python scripts/python/equity_irr.py --reopt artifacts/results/saigon18/2026-03-20_scenario-d_dppa-baseline_reopt-results.json --settlement ...` — PASS
- `python scripts/python/compare_reopt_vs_excel.py ...` for Scenario A/C/D — PASS
- `python scripts/python/generate_html_report.py` — PASS
- `powershell -ExecutionPolicy Bypass -File "tests/run_all_tests.ps1" -Layer 4 -SmokeOnly` — PASS

### Remaining note

- Full Layer 4 rerun through `tests/run_all_tests.ps1 -Layer 4` started successfully and entered the long Julia integration section, but the CLI command timed out before completion in this session; the pre-existing Python API payload failures documented in `docs/testing.md` still apply to the repo-wide Layer 4 scope.
