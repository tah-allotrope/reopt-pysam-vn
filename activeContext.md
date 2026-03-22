# Active Context — Saigon18 REopt Integration

> Last updated: 2026-03-22 (Phase 3 script fixes complete)

---

## Project

Mapping the Saigon18 Excel feasibility model (40.36 MWp solar + 66 MWh BESS, southern Vietnam) onto REopt.jl to validate and challenge the Excel outputs (Equity IRR 19.4%, NPV $22M, 6-yr payback).

Plan: `plans/saigon18_reopt_integration_plan.md`

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
| `data/real_project/saigon18_extracted.json` | ✅ Done | 71.81 GWh PV, 184.26 GWh load, 30.2 MW peak — all checks passed |
| `scenarios/real_project/saigon18_scenario_a.json` | ✅ Done | Built; no-solve validation passed |
| `scenarios/real_project/saigon18_scenario_b.json` | ✅ Done | Built |
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
| Output file | `results/real_project/saigon18_scenario_a_results.json` |

#### Scenario B Results (2026-03-20)
| Metric | REopt Result |
|---|---|
| Status | OPTIMAL |
| PV / BESS | Same fixed sizing as A |
| LCC | $118.1M |
| NPV | $0.89M |
| Simple payback | 10.2 yr |
| Output file | `results/real_project/saigon18_scenario_b_results.json` |

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
| Output file | — | `reports/real_project/saigon18_equity_irr.json` |

Reports: `reports/real_project/saigon18_scenario_a_comparison.md`, `reports/real_project/saigon18_scenario_b_comparison.md`, `reports/real_project/saigon18_equity_irr.json`

### Phase 3 — Custom Constraints & Advanced Scenarios ⏳ In progress

| Task | Status |
|---|---|
| Fix `equity_irr.py` EBITDA extraction bug (see bug log) | ✅ Fixed 2026-03-22 |
| Fix `compare_reopt_vs_excel.py` energy-flow key mapping (see bug log) | ✅ Fixed 2026-03-22 |
| Re-run equity IRR validation vs Excel 19.4% | ✅ Done — 19.8% vs 19.4% (+0.4%) |
| Re-generate Scenario A/B comparison reports with corrected keys | ✅ Done |
| Add regression test for Saigon18 comparison key mapping | ✅ Done — `tests/python/test_saigon18_compare.py` |
| Decree 57 20% export cap as hard JuMP constraint in `src/REoptVietnam.jl` | ⏳ Not started |
| Optional fixed BESS dispatch window constraints (Option B) | ⏳ Not started |
| Scenario C — optimized sizing (unconstrained PV + BESS) | ⏳ Not started |
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

**Rerun result:** `reports/real_project/saigon18_equity_irr.json` now shows
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

## Pre-existing Test Failures (not caused by this session)

These 5 tests were failing before this session due to the tariff v2025.2 restructure. Not blocking Phase 2.

| Test | Root cause |
|---|---|
| `test_unit.py::test_commercial_low_voltage` | Commercial tariff now has subcategories (tourism/EV/other) not flat voltage levels |
| `test_unit.py::test_sunday_vs_weekday_pattern` | Test directly accesses `schedule["sunday"]` key (renamed to `sunday_and_public_holidays`) |
| `test_data_validation.py::test_meta_and_data_blocks[tariff]` | Meta block has `source_urls` (plural) but test checks `source_url` |
| `test_data_validation.py::test_tou_schedule_completeness[sunday]` | Test checks for `"sunday"` key in schedule |
| `test_data_validation.py::test_commercial_multipliers` | Commercial now nested by subcategory |

---

## Next Actions

1. **Refine BESS comparison metric** — the report now uses actual REopt storage output keys, but it compares Excel's peak+standard dispatch target against total annual `storage_to_load_series_kw`. Next refinement should split REopt discharge by tariff period for apples-to-apples validation.

2. **Build and run Scenario C** (optimized sizing, Phase 3):
   ```
   julia --project=. scripts/julia/run_vietnam_scenario.jl --scenario scenarios/real_project/saigon18_scenario_c.json
   ```

3. **Add `tests/python/test_saigon18_integration.py`** for the Saigon18 real-project pipeline.

4. **Implement Decree 57 export cap as a hard JuMP constraint** in `src/REoptVietnam.jl`.

5. **Fix pre-existing test failures** (Phase 3 housekeeping — not blocking)

---

## Outstanding / Pending Confirmations

- [ ] Confirm actual site coordinates (currently lat=10.9577, lon=106.8426 near HCMC)
- [ ] Confirm whether Saigon18 uses private-wire or grid-connected DPPA — ceiling tariff differs
- [ ] Two-part tariff (capacity charge) sensitivity — Decree 146/2025 pilot Jan–Jun 2026

### Deferred (Phase 3)
- Decree 57 20% export cap hard JuMP constraint — currently only `can_wholesale=True` + surplus rate set
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
| C | Optimized sizing | Full EVN TOU | Unconstrained (up to 60 MWp / 100 MWh) | ⏳ Phase 3 |
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

data/real_project/
  20260129 SOLAR BESS MODEL - Editing - V2.xlsm  ← source Excel ✅
  saigon18_extracted.json                        ← extracted data ✅

scenarios/real_project/
  saigon18_scenario_a.json      ✅
  saigon18_scenario_b.json      ✅

results/real_project/
  saigon18_scenario_a_results.json  ✅
  saigon18_scenario_b_results.json  ✅

reports/real_project/
  saigon18_scenario_a_comparison.md  ✅
  saigon18_scenario_b_comparison.md  ✅
  saigon18_equity_irr.json          ✅
```
