# Active Context — Saigon18 REopt Integration

> Last updated: 2026-03-20

---

## Project

Mapping the Saigon18 Excel feasibility model (40.36 MWp solar + 66 MWh BESS, southern Vietnam) onto REopt.jl to validate and challenge the Excel outputs (Equity IRR 19.4%, NPV $22M, 6-yr payback).

Plan: `plans/saigon18_reopt_integration_plan.md`

---

## Progress by Phase

### Phase 1 — Data Extraction & Input Validation ✅ (scripts done, partial validation)

| Task | Status | Notes |
|---|---|---|
| `scripts/python/extract_excel_inputs.py` | ✅ Done | Extracts 8760 load/PV/FMP from Excel; validates row count, negatives, yield |
| `scripts/python/build_saigon18_reopt_input.py` | ✅ Done | Builds Scenario A & B JSON; applies Vietnam defaults + project overrides |
| `scripts/python/dppa_settlement.py` | ✅ Done | DPPA CfD post-processing; compute settlement from FMP + REopt dispatch |
| `scripts/python/compare_reopt_vs_excel.py` | ✅ Done | Comparison report script (delta table, 5% flag threshold) |
| `scripts/python/equity_irr.py` | ✅ Done | Levered equity IRR from REopt EBITDA + debt schedule |
| `scripts/julia/run_vietnam_scenario.jl` | ✅ Done | Added `--scenario <path>` flag; output path branches per mode |
| `tests/python/test_saigon18_data.py` | ✅ Done | Layer 1 data validation tests (synthetic, no Excel needed) |
| `data/real_project/saigon18_extracted.json` | ⏳ Blocked | Needs Excel file from project developer |
| `scenarios/real_project/saigon18_scenario_a.json` | ⏳ Blocked | Needs extracted JSON first |
| `scenarios/real_project/saigon18_scenario_b.json` | ⏳ Blocked | Needs extracted JSON first |
| No-solve validation (`--scenario ... --no-solve`) | ⏳ Blocked | Needs scenario JSONs |

### Phase 2 — REopt Run & Baseline Comparison ⏳ Not started

Blocked on Phase 1 Excel extraction.

| Task | Status |
|---|---|
| Run Scenario A (full EVN TOU, fixed sizing) | ⏳ Blocked |
| Run Scenario B (PPA × 0.85, fixed sizing) | ⏳ Blocked |
| Generate comparison report | ⏳ Blocked |
| `reports/real_project/saigon18_comparison_report.md` | ⏳ Blocked |

### Phase 3 — Custom Constraints & Advanced Scenarios ⏳ Not started

| Task | Status |
|---|---|
| Decree 57 20% export cap as hard JuMP constraint in `src/REoptVietnam.jl` | ⏳ Not started |
| Optional fixed BESS dispatch window constraints (Option B) | ⏳ Not started |
| Scenario C — optimized sizing (unconstrained PV + BESS) | ⏳ Blocked |
| Equity IRR validation vs Excel 19.4% | ⏳ Blocked |
| `tests/python/test_saigon18_integration.py` (Layer 4) | ⏳ Not started |

---

## Outstanding / Blockers

### Hard blocker
- **Excel file not provided.** All downstream Phase 1–3 work (extraction, scenario build, solve, comparison) is blocked until the file is shared:
  ```
  llm 20260129 SOLAR BESS MODEL - Editing - for processing test.xlsx
  ```
  → Once provided, run: `python scripts/python/extract_excel_inputs.py --excel "<path>" --output data/real_project/saigon18_extracted.json`

### Pending actions (unblocked now)
- [ ] Confirm actual site coordinates (currently defaulting to lat=10.9577, lon=106.8426 near HCMC)
- [ ] Confirm whether Saigon18 uses private-wire or grid-connected DPPA — ceiling tariff differs (VND 1,149.86/kWh vs. higher ceiling for private wire); plan uses VND 1,800/kWh strike price which may exceed the Decree 57 grid-connected ceiling
- [ ] Run `python -m pytest tests/python/test_saigon18_data.py -v` to confirm all Layer 1 tests pass

### Deferred (Phase 3)
- Decree 57 20% export cap hard JuMP constraint — currently only `can_wholesale=True` + surplus rate is set; no upper bound on export volume
- Two-part tariff (capacity charge) sensitivity scenario — Decree 146/2025 pilot started Jan 2026; relevant for Year 5+ of project life

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| PV production profile | Inject from Excel (Option B) | Apples-to-apples vs Excel; avoids NREL API dependency for comparison runs |
| BESS degradation | `battery_replacement_year=10`, `replace_cost_per_kwh=100` | REopt uses discrete replacement model; continuous 3%/yr not supported natively |
| CIT tax rate | Blended 0.0575 | 4yr exempt + 9yr 50% + 7yr full = (0+0.45+0.70)/20 effective rate |
| BESS dispatch | REopt free optimization (Phase 1–2); fixed windows optional (Phase 3) | Uncover dispatch value of optimization vs. Excel fixed schedule |
| Currency | All inputs converted VND→USD at 26,000 VND/USD | REopt outputs USD; post-process for VND reporting |

---

## Scenario Summary

| ID | Description | Tariff | Sizing |
|---|---|---|---|
| A | Baseline — REopt TOU optimization | Full EVN TOU | Fixed (40.36 MWp + 66 MWh) |
| B | Bundled PPA — 15% discount | EVN TOU × 0.85 | Fixed |
| C | Optimized sizing | Full EVN TOU | Unconstrained (up to 60 MWp / 100 MWh) |
| D | DPPA strike price contract | EVN TOU (base) + FMP post-processing | Fixed |

---

## File Map

```
scripts/python/
  extract_excel_inputs.py       ← Excel → saigon18_extracted.json
  build_saigon18_reopt_input.py ← extracted JSON → scenario A/B JSON
  dppa_settlement.py            ← DPPA CfD revenue post-processor
  compare_reopt_vs_excel.py     ← delta comparison report
  equity_irr.py                 ← levered equity IRR from REopt EBITDA

scripts/julia/
  run_vietnam_scenario.jl       ← runner; --scenario flag added

data/real_project/
  saigon18_extracted.json       ← MISSING (needs Excel)

scenarios/real_project/
  saigon18_scenario_a.json      ← MISSING (needs extracted JSON)
  saigon18_scenario_b.json      ← MISSING (needs extracted JSON)

results/real_project/           ← populated after REopt runs
reports/real_project/           ← populated after compare script

tests/python/
  test_saigon18_data.py         ← Layer 1 synthetic validation tests ✅
```
