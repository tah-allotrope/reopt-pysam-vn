---
title: "Operational Decision Engine: REopt-PySAM-VN Practical Refinements"
date: "2026-05-18"
status: "draft"
request: "Transform reopt-pysam-vn from research-grade toolkit to operational decision engine for live deal evaluation at Allotrope VC"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-05-18_practical-refinements-operational-engine.md"
  - "research/2026-05-07_vietnam-tou-tariff-implications.md"
  - "research/2026-04-26_commercial-product-ideas.md"
---

# Plan: Operational Decision Engine — REopt-PySAM-VN Practical Refinements

## Objective

Transform the repo from a research toolkit with materialized-but-unsolved scenarios into an operational platform where Allotrope VC can evaluate a new Vietnam solar+BESS+DPPA deal end-to-end — from load profile to financial report — in a single automated pipeline run. The immediate blocker is that no Julia solve results exist (cold-start timeout), so all financial outputs are placeholders. This plan unblocks solves, parameterizes financial modules, wires orchestration, quantifies BESS economics under Decision 963, and adds validation baselines.

## Context Snapshot

- **Current state:** 6 TOU comparison scenarios materialized but never solved. Financial modules (`equity_irr.py`, `dppa_settlement.py`, `bess_dispatch_analysis.py`) work but have hardcoded constants and no integration. 119 Python scripts with no orchestration layer. 99 tests passing but no end-to-end financial regression test.
- **Desired state:** Julia solves complete for all 6 TOU scenarios. Financial modules parameterized via CLI/config. Master pipeline script chains materialize → solve → analyze → report. BESS economics quantified under both TOU regimes. E2E test with regression baseline.
- **Key repo surfaces:**
  - `scripts/julia/run_vietnam_scenario.jl` — Julia solve entry point
  - `src/julia/REoptVietnam.jl` — Julia preprocessing module
  - `scripts/python/reopt/equity_irr.py` — Leveraged equity IRR (hardcoded constants lines 32-37)
  - `scripts/python/reopt/dppa_settlement.py` — DPPA CfD settlement
  - `scripts/python/reopt/bess_dispatch_analysis.py` — BESS dispatch comparison (hardcoded peak hours line 30-31)
  - `scripts/run_tou_comparison.ps1` — Only orchestration script (75 lines)
  - `scenarios/generated/tou_comparison/` — 6 materialized scenarios awaiting solve
  - `Project.toml` — Julia 1.10+, REopt 0.56, HiGHS 1
- **Out of scope:** Web frontend/SaaS layer (Idea 1 from commercial brief), self-hosted REopt_API Docker deployment, Decree 146 Phase 3 implementation (rates not yet published), virtual DPPA marketplace features.

## Research Inputs

- `research/2026-05-18_practical-refinements-operational-engine.md` — Identifies PackageCompiler sysimage as best solve-pipeline fix (1-2 day effort, eliminates 30-60s JIT). Documents NREL REopt API as fallback. Confirms no public FMP data (use VND 1,400-2,000 sensitivity range). Cites 50MW Binh Thuan benchmark (16.49% CF, $5.7M revenue shortfall vs model). Notes Circular 62/2025 BESS tariff framework and single-cycle economics under Decision 963.
- `research/2026-05-07_vietnam-tou-tariff-implications.md` — Confirms Decision 963 as legally active regime. Documents half-hour boundary approximation error (~2.8% at 17:30). Notes multiplier uncertainty (MOIT has not confirmed repricing). Identifies code action items all completed in Phase 40-42.
- `research/2026-04-26_commercial-product-ideas.md` — Idea 2 (TOU Regime Engine) is partially implemented via regime registry + TOU comparison workflow. This plan completes the "run and report" gap that prevents Idea 2 from producing quantitative results. Idea 3 (Bankability Studio) depends on parameterized financial modules delivered in PHASE-02 of this plan.

## Assumptions and Constraints

- **ASM-001:** Julia 1.10+ and PackageCompiler.jl are compatible with REopt.jl v0.56.4 and HiGHS. PackageCompiler sysimage build should take 5-15 minutes and produce a reusable artifact.
- **ASM-002:** NREL REopt API (v3) accepts the same scenario JSON schema used by local Julia solve. Rate limits may constrain batch validation runs but individual scenario validation is feasible.
- **ASM-003:** Decision 14 multipliers apply unchanged under Decision 963 windows (the `decision_963_2026_windows_only` regime). If MOIT publishes repriced multipliers, the `decision_963_2026_repriced_multipliers` regime placeholder in `vn_regime_registry_2026.json` should be populated.
- **ASM-004:** FMP central estimate of VND 1,700/kWh (from DPPA buyer guide) with +/-20% sensitivity range (VND 1,400-2,000) is adequate for deal screening. Baringa subscription is not available.
- **CON-001:** Julia cold-start timeout blocks all solve-dependent phases. PHASE-01 must succeed before PHASE-03, PHASE-04, or PHASE-05 can produce real results.
- **CON-002:** No BESS operational data exists from Vietnam projects — BESS economics must be derived from tariff structure analysis and general literature benchmarks.
- **DEC-001:** Decision 963 is the active default regime (`DEFAULT_REGIME_ID = "decision_963_2026_current"` in `preprocess.py:47` and `REoptVietnam.jl:58`). Decision 14 preserved as legacy.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Unblock Julia solve pipeline | None | PackageCompiler sysimage, solved TOU scenarios, first real REopt results |
| PHASE-02 | Parameterize financial modules | None (parallel with P1) | Config-driven equity_irr + dppa_settlement + sensitivity sweep CLI |
| PHASE-03 | Master orchestration pipeline | PHASE-01, PHASE-02 | Single-command case study pipeline, caching, dependency tracking |
| PHASE-04 | BESS economics under Decision 963 | PHASE-01 | Quantified single-cycle vs dual-cycle dispatch value, BESS sensitivity report |
| PHASE-05 | Validation baselines & E2E testing | PHASE-01, PHASE-02 | E2E regression test, JSON schemas for interim data, capacity factor validation |

## Detailed Phases

### PHASE-01 — Solve Pipeline Reliability

**Goal**
Eliminate the Julia JIT cold-start bottleneck and produce the first actual REopt optimization results for the 6 TOU comparison scenarios and existing case studies.

**Tasks**
- [ ] TASK-01-01: Add PackageCompiler.jl to `Project.toml` dependencies
- [ ] TASK-01-02: Create `scripts/julia/build_sysimage.jl` that builds a sysimage with REopt, HiGHS, JuMP, JSON precompiled. Include a representative precompile workload (small scenario solve) to warm all code paths.
- [ ] TASK-01-03: Create `scripts/build_sysimage.ps1` PowerShell wrapper that invokes the sysimage build and stores the artifact at `artifacts/sysimage/reopt_sysimage.dll` (Windows) or `.so` (Linux)
- [ ] TASK-01-04: Update `scripts/julia/run_vietnam_scenario.jl` to accept `--sysimage <path>` flag and document usage in docstring. Default behavior unchanged (no sysimage = standard JIT).
- [ ] TASK-01-05: Create `scripts/run_solve.ps1` — wrapper that invokes Julia with sysimage flag, accepts `--scenario` and `--output-dir` arguments, validates input exists before invoking Julia
- [ ] TASK-01-06: Wire NREL REopt API as validation fallback — create `scripts/python/reopt/solve_via_api.py` that POSTs scenario JSON to `https://developer.nrel.gov/api/reopt/v3/job`, polls for results, and writes output in the same schema as local Julia solve
- [ ] TASK-01-07: Run all 6 TOU comparison scenarios (`scenarios/generated/tou_comparison/`) through the solve pipeline. Store results in `artifacts/results/tou_comparison/`
- [ ] TASK-01-08: Re-run `scripts/python/reopt/tou_financial_delta.py` and `tou_comparison_report.py` with actual solve results to populate the financial delta CSV and HTML report
- [ ] TASK-01-09: Run existing case study scenarios (saigon18, ninhsim, north_thuan) and store results

**Files / Surfaces**
- `Project.toml` — Add PackageCompiler dependency
- `scripts/julia/build_sysimage.jl` — New: sysimage builder script
- `scripts/build_sysimage.ps1` — New: PowerShell wrapper for sysimage build
- `scripts/julia/run_vietnam_scenario.jl` — Add --sysimage flag
- `scripts/run_solve.ps1` — New: solve wrapper with sysimage support
- `scripts/python/reopt/solve_via_api.py` — New: NREL API fallback solver
- `artifacts/sysimage/` — New: sysimage artifact storage
- `artifacts/results/tou_comparison/` — Solve results for TOU scenarios
- `scenarios/generated/tou_comparison/` — Input scenarios (already materialized)

**Dependencies**
- Julia 1.10+ installed and accessible via `julia` command
- NREL API credentials in `NREL_API.env`
- PackageCompiler.jl compatible with Julia 1.10 and REopt 0.56

**Exit Criteria**
- [ ] `artifacts/sysimage/reopt_sysimage.dll` exists and `julia --sysimage=artifacts/sysimage/reopt_sysimage.dll --project -e "using REopt; println(\"OK\")"` completes in <3 seconds
- [ ] All 6 TOU comparison scenarios produce valid results JSON with non-null Financial, PV, and ElectricStorage sections
- [ ] `tou_financial_delta.py` output CSV has numeric values (not "no_results") for IRR, NPV, payback columns
- [ ] `tou_comparison_report.py` HTML shows populated Chart.js bar charts
- [ ] `solve_via_api.py` successfully solves at least 1 scenario via NREL API and result schema matches local Julia output structure

**Phase Risks**
- **RISK-01-01:** PackageCompiler sysimage build fails with REopt.jl due to precompilation incompatibilities. **Mitigation:** Fall back to NREL API for all solves; document local solve as a future optimization. The API accepts the same JSON schema.
- **RISK-01-02:** HiGHS solve times exceed 1,200s timeout for complex scenarios (PV + BESS + TOU). **Mitigation:** Per NREL Discussion #149, increase `optimality_tolerance` to 0.01 (1% gap) or constrain min/max technology sizes to reduce binary variables.
- **RISK-01-03:** NREL API rate limits prevent batch validation of all 6 scenarios. **Mitigation:** Stagger API calls with 30s delay; prioritize 1 scenario per case study (3 total) for API validation, solve remaining locally.

### PHASE-02 — Financial Module Parameterization

**Goal**
Replace hardcoded financial constants with CLI arguments and a shared config file so that sensitivity sweeps across strike price, debt terms, and tariff regime can be run without code changes.

**Tasks**
- [ ] TASK-02-01: Create `data/vietnam/vn_deal_defaults_2026.json` — shared financial config with sections for `debt_terms` (fraction, rate, tenor), `analysis` (years, discount_rate, escalation), `dppa` (strike_vnd, delivery_factor, contract_type), `exchange_rate`. Include reasonable defaults matching current hardcoded values.
- [ ] TASK-02-02: Update `scripts/python/reopt/equity_irr.py` — add `--config` CLI arg that loads `vn_deal_defaults_2026.json`; keep existing CLI args as overrides. Remove hardcoded `TOTAL_CAPEX_USD`, `DEBT_FRACTION`, `INTEREST_RATE` module-level constants; move to `compute_equity_irr()` parameter defaults loaded from config.
- [ ] TASK-02-03: Update `scripts/python/reopt/dppa_settlement.py` — add `--config` CLI arg; replace `EXCHANGE_RATE_VND_PER_USD` hardcode (line 22) with config value; add FMP sensitivity range parameter (`--fmp-range VND_MIN VND_MAX VND_STEP`).
- [ ] TASK-02-04: Update `scripts/python/reopt/bess_dispatch_analysis.py` — replace hardcoded `PEAK_HOURS_WEEKDAY` (line 30) and `OFFPEAK_HOURS` (line 31) with values loaded from `vn_tariff_2025.json` via manifest; replace `EXCHANGE_RATE_VND_PER_USD` (line 26) with config; replace `efficiency = 0.92` (line 88) with config.
- [ ] TASK-02-05: Create `scripts/python/reopt/sensitivity_sweep.py` — given a solved scenario, sweep across: strike price (VND 800-1,400, step 50), debt fraction (60%-80%, step 5%), interest rate (7%-10%, step 0.5%), FMP (VND 1,400-2,000, step 100). Output CSV matrix of equity IRR × parameter combinations.
- [ ] TASK-02-06: Add `data/vietnam/vn_deal_defaults_2026.json` to `data/vietnam/manifest.json` registry
- [ ] TASK-02-07: Update unit tests to verify config loading and CLI override behavior

**Files / Surfaces**
- `data/vietnam/vn_deal_defaults_2026.json` — New: shared financial config
- `data/vietnam/manifest.json` — Add deal defaults pointer
- `scripts/python/reopt/equity_irr.py` — Parameterize constants (lines 32-37)
- `scripts/python/reopt/dppa_settlement.py` — Parameterize constants (line 22), add FMP sweep
- `scripts/python/reopt/bess_dispatch_analysis.py` — Parameterize constants (lines 26, 30-31, 88)
- `scripts/python/reopt/sensitivity_sweep.py` — New: multi-parameter sweep runner
- `tests/python/reopt/test_unit.py` — Add config loading tests

**Dependencies**
- None (can run in parallel with PHASE-01)

**Exit Criteria**
- [ ] `python scripts/python/reopt/equity_irr.py --config data/vietnam/vn_deal_defaults_2026.json --reopt <results.json>` produces valid output using config values
- [ ] `python scripts/python/reopt/equity_irr.py --reopt <results.json> --capex 30000000 --debt-fraction 0.65` overrides config values correctly
- [ ] `python scripts/python/reopt/sensitivity_sweep.py --reopt <results.json> --config <config.json>` produces CSV with N×M parameter matrix
- [ ] `bess_dispatch_analysis.py` reads peak hours from `vn_tariff_2025.json` and produces correct Decision 963 period classification (peak = [17-22], no morning peak)
- [ ] All existing unit tests still pass (`pytest tests/python/reopt/test_unit.py`)

**Phase Risks**
- **RISK-02-01:** Changing default constants in `equity_irr.py` breaks existing Saigon18 comparison workflow. **Mitigation:** Config file defaults match current hardcoded values exactly; behavior is unchanged when invoked without `--config`.

### PHASE-03 — Workflow Orchestration Pipeline

**Goal**
Build a master pipeline script that runs a complete case study from scenario materialization through solve, financial analysis, and report generation with a single command. Implement caching so re-runs skip completed stages.

**Tasks**
- [ ] TASK-03-01: Create `scripts/run_pipeline.ps1` — master orchestration script accepting: `--case-study <name>` (saigon18|ninhsim|north_thuan), `--regime <id>` (decision_963_2026_current|decision_14_2025_legacy), `--config <path>`, `--skip-solve` flag, `--force` flag (ignore cache). Pipeline stages:
  1. Materialize scenario (calls `build_<case>_reopt_input.py`)
  2. Solve via Julia (calls `run_solve.ps1`, or `--skip-solve` uses existing results)
  3. Extract financial data (calls `equity_irr.py` + `dppa_settlement.py`)
  4. Run BESS dispatch analysis (calls `bess_dispatch_analysis.py`)
  5. Generate HTML report (calls appropriate report generator)
- [ ] TASK-03-02: Implement stage caching — each stage writes a `.done` marker file with input hash. Skip stage if marker exists and inputs unchanged. `--force` clears all markers.
- [ ] TASK-03-03: Create `scripts/run_pipeline_batch.ps1` — runs the pipeline for all case studies × all regimes (6 combinations). Produces cross-study comparison dashboard.
- [ ] TASK-03-04: Create stage validation gates — each stage validates output before proceeding. Fail fast with descriptive error if a stage produces invalid output (e.g., solve returns no PV results, equity_irr returns NaN).
- [ ] TASK-03-05: Add `--dry-run` flag that prints the pipeline plan (stages, inputs, outputs) without executing

**Files / Surfaces**
- `scripts/run_pipeline.ps1` — New: master single-case pipeline
- `scripts/run_pipeline_batch.ps1` — New: batch multi-case runner
- `scripts/run_solve.ps1` — From PHASE-01, used by pipeline
- `artifacts/pipeline_cache/` — New: stage completion markers

**Dependencies**
- PHASE-01 (solve pipeline must work)
- PHASE-02 (financial modules must accept `--config`)

**Exit Criteria**
- [ ] `.\scripts\run_pipeline.ps1 --case-study saigon18 --regime decision_963_2026_current --config data/vietnam/vn_deal_defaults_2026.json` completes all 5 stages and produces HTML report in `artifacts/reports/`
- [ ] Second run with same arguments completes in <10 seconds (all stages cached)
- [ ] `--force` flag causes full re-run
- [ ] `--dry-run` prints stage plan without executing
- [ ] Pipeline fails with clear error message when solve produces empty results
- [ ] `run_pipeline_batch.ps1` produces results for all 6 case×regime combinations

**Phase Risks**
- **RISK-03-01:** Different case studies have different script names and argument patterns (e.g., `build_saigon18_reopt_input.py` vs `build_ninhsim_reopt_input.py`). **Mitigation:** Pipeline maps case study names to their specific build scripts via a lookup table in the script.
- **RISK-03-02:** Caching hash collisions produce stale results. **Mitigation:** Hash includes: scenario JSON content hash, config file hash, and script modification timestamp.

### PHASE-04 — BESS Economics Quantification Under Decision 963

**Goal**
Produce a quantitative analysis of BESS dispatch economics under Decision 963's single evening peak vs. Decision 14's dual peak, including financial value per cycle, break-even analysis, and a sensitivity report.

**Tasks**
- [ ] TASK-04-01: Extend `bess_dispatch_analysis.py` — add `--regime` parameter that loads TOU windows from `vn_regime_registry_2026.json` instead of hardcoded hours. Produce side-by-side dispatch comparison for Decision 963 vs Decision 14.
- [ ] TASK-04-02: Add financial quantification to dispatch output — compute annual $/kWh savings from arbitrage, net revenue after round-trip efficiency loss, simple payback period given BESS capex (from `vn_tech_costs_2025.json`).
- [ ] TASK-04-03: Add degradation modeling — implement linear capacity degradation (2%/year) and compute lifetime dispatch revenue with declining capacity. Use 10-year BESS lifetime from tech costs.
- [ ] TASK-04-04: Create `scripts/python/reopt/bess_regime_comparison.py` — runs BESS dispatch under both regimes using actual solve results, produces comparison JSON with: cycles/day, annual arbitrage revenue, break-even year, NPV of BESS investment under each regime.
- [ ] TASK-04-05: Add Decree 146 demand-charge placeholder — stub module for demand-charge reduction value stream with configurable capacity charge rate (VND/kW/month). Populate with trial values from `vn_regime_registry_2026.json` `two_part_tariff` section.
- [ ] TASK-04-06: Create `scripts/python/reopt/generate_bess_economics_report.py` — HTML report with Chart.js visualizations: dispatch heatmap by hour-of-day, regime comparison bar chart, break-even sensitivity tornado, degradation curve.

**Files / Surfaces**
- `scripts/python/reopt/bess_dispatch_analysis.py` — Extend with regime parameter, financial quantification, degradation
- `scripts/python/reopt/bess_regime_comparison.py` — New: cross-regime BESS comparison
- `scripts/python/reopt/generate_bess_economics_report.py` — New: BESS economics HTML report
- `data/vietnam/vn_tech_costs_2025.json` — Read BESS capex ($/kWh) and lifetime
- `data/vietnam/vn_regime_registry_2026.json` — Read TOU windows per regime and two-part tariff trial values
- `artifacts/reports/bess_economics/` — New: BESS analysis outputs

**Dependencies**
- PHASE-01 (needs actual solve results with `ElectricStorage` dispatch series)

**Exit Criteria**
- [ ] `bess_dispatch_analysis.py --regime decision_963_2026_current` produces dispatch volumes with peak hours [17-22] (no morning peak)
- [ ] `bess_dispatch_analysis.py --regime decision_14_2025_legacy` produces dispatch volumes with peak hours [9-10, 17-19]
- [ ] `bess_regime_comparison.py` output shows Decision 963 has ~50% lower arbitrage cycles vs Decision 14
- [ ] Financial quantification includes: annual arbitrage revenue (VND and USD), simple payback (years), NPV of BESS investment at 8% discount rate
- [ ] Degradation model shows declining revenue curve over 10-year lifetime
- [ ] HTML report renders in browser with working Chart.js visualizations

**Phase Risks**
- **RISK-04-01:** Solve results may not include BESS dispatch series if BESS was not cost-optimal. **Mitigation:** Check `ElectricStorage.size_kw > 0` before running dispatch analysis; skip with informative message if BESS not selected.
- **RISK-04-02:** Demand-charge modeling requires Decree 146 Phase 3 rates not yet published (expected July 2026). **Mitigation:** Use trial values from regime registry as placeholder; mark outputs as "preliminary — awaiting Phase 3 rates".

### PHASE-05 — Validation Baselines and End-to-End Testing

**Goal**
Add regression baselines for financial outputs, JSON schemas for intermediate data, FMP sensitivity analysis, and validate energy yield assumptions against the 50MW Binh Thuan benchmark.

**Tasks**
- [ ] TASK-05-01: Create E2E test in `tests/python/integration/test_e2e_financial.py` — loads a solved REopt result → runs PySAM bridge → runs equity_irr → runs dppa_settlement → asserts IRR, NPV, settlement values within expected ranges. Store expected values in `tests/baselines/financial_e2e_baseline.json`.
- [ ] TASK-05-02: Create JSON schemas for `data/interim/` extracted inputs — `data/schemas/extracted_inputs.schema.json` defining required fields: load_series, pv_production_factor, fmp series, site metadata. Add validation step to `extract_excel_inputs.py`.
- [ ] TASK-05-03: Standardize `data/interim/` naming — rename `ninhsim_extracted_inputs.json` to `2026-04-01_ninhsim_extracted_inputs.json` and `north_thuan_extracted_inputs.json` to `2026-04-01_north_thuan_extracted_inputs.json` (use original extraction dates from git log). Update all scripts referencing these paths.
- [ ] TASK-05-04: Create `scripts/python/reopt/fmp_sensitivity.py` — sweep FMP from VND 1,400 to VND 2,000 in VND 100 steps. For each FMP level, compute: DPPA settlement revenue, offtaker avoided cost, developer IRR. Output CSV matrix and tornado chart data.
- [ ] TASK-05-05: Create `tests/python/integration/test_capacity_factor_benchmark.py` — validate that PySAM PVWatts output for southern Vietnam coordinates (Binh Thuan: 11.09°N, 108.15°E) produces capacity factor in range 14-20%, consistent with the 50MW Binh Thuan benchmark (16.49% over 4.5 years). Apply 5% conservatism buffer per the research finding of $5.7M revenue shortfall vs model.
- [ ] TASK-05-06: Add financial regression baselines — after PHASE-01 solves produce real results, snapshot equity IRR, DPPA settlement, and BESS dispatch values into `tests/baselines/` as regression anchors. Test asserts future runs stay within ±2% of baseline.
- [ ] TASK-05-07: Update `tests/run_all_tests.ps1` — add Layer 5 (financial E2E) as optional layer, invokable via `--Layer 5` or `--IncludeFinancial`

**Files / Surfaces**
- `tests/python/integration/test_e2e_financial.py` — New: end-to-end financial test
- `tests/python/integration/test_capacity_factor_benchmark.py` — New: energy yield validation
- `tests/baselines/financial_e2e_baseline.json` — New: regression baseline for financial outputs
- `data/schemas/extracted_inputs.schema.json` — New: JSON schema for interim data
- `scripts/python/reopt/fmp_sensitivity.py` — New: FMP sweep analysis
- `data/interim/ninhsim/` — Rename file for consistency
- `data/interim/north_thuan/` — Rename file for consistency
- `tests/run_all_tests.ps1` — Add Layer 5

**Dependencies**
- PHASE-01 (needs actual solve results for E2E test and baselines)
- PHASE-02 (needs parameterized financial modules for sensitivity sweep)

**Exit Criteria**
- [ ] `pytest tests/python/integration/test_e2e_financial.py` passes with real solve results
- [ ] `python -c "import jsonschema; ..."` validates all 3 extracted input JSONs against schema
- [ ] `fmp_sensitivity.py` produces CSV with 7 rows (VND 1,400 to 2,000) × financial metrics
- [ ] Capacity factor benchmark test passes with southern Vietnam coordinates
- [ ] `.\tests\run_all_tests.ps1 --Layer 5` runs financial E2E without error
- [ ] Financial regression baselines exist for all 3 case studies

**Phase Risks**
- **RISK-05-01:** Renaming `data/interim/` files breaks scripts across the repo. **Mitigation:** Use `grep -r` to find all references before renaming; update all paths in a single commit. Run full test suite after rename.
- **RISK-05-02:** PySAM capacity factor for Binh Thuan coordinates may not match benchmark if using different weather year or module assumptions. **Mitigation:** Use NSRDB TMY data for Binh Thuan; accept 14-20% range (wider than benchmark's 12.8-19.5% observed range) to account for module/weather variation.

## Verification Strategy

- **TEST-001:** `pytest tests/python/reopt/test_unit.py -v` — all 65+ unit tests pass after each phase (regression gate)
- **TEST-002:** `pytest tests/python/reopt/test_data_validation.py -v` — all 34 data validation tests pass (data integrity gate)
- **TEST-003:** `pytest tests/python/integration/test_e2e_financial.py -v` — E2E financial pipeline produces results within ±2% of baseline (PHASE-05)
- **TEST-004:** `pytest tests/python/integration/test_capacity_factor_benchmark.py -v` — PVWatts CF in 14-20% range for southern Vietnam (PHASE-05)
- **MANUAL-001:** Open `tou_comparison_report.py` HTML output in browser — verify Chart.js bar charts render with numeric data (not "no_results") (PHASE-01)
- **MANUAL-002:** Open BESS economics HTML report in browser — verify dispatch heatmap, regime comparison, and break-even charts render correctly (PHASE-04)
- **MANUAL-003:** Run `.\scripts\run_pipeline.ps1 --case-study saigon18 --dry-run` — verify pipeline prints all 5 stages with correct input/output paths (PHASE-03)

## Risks and Alternatives

- **RISK-001:** Julia PackageCompiler sysimage fails to build with REopt.jl. **Mitigation:** NREL REopt API is wired as a complete fallback in TASK-01-06. If local solve is unreliable, all scenarios can be solved via API. Trade-off: API has rate limits and 1,200s max solve time.
- **RISK-002:** NREL API v3 schema differences from local Julia solve output. **Mitigation:** `solve_via_api.py` includes a schema normalization step that maps API output keys to the same structure as local Julia output. Test with at least 1 scenario during PHASE-01.
- **RISK-003:** Sensitivity sweep combinatorics (strike × debt × rate × FMP) may produce >1,000 rows, making results hard to interpret. **Mitigation:** `sensitivity_sweep.py` includes a `--top-n` flag showing only the N most impactful parameter combinations by IRR delta.
- **ALT-001:** Self-hosted REopt_API Docker deployment instead of PackageCompiler sysimage. **Not chosen** because Docker infrastructure is overkill for Allotrope's periodic deal evaluation use case. Sysimage solves the cold-start problem with minimal operational complexity.
- **ALT-002:** Replace Julia solve entirely with NREL API calls. **Not chosen** because API rate limits and external dependency make it unsuitable as the primary pipeline. API is better positioned as a validation fallback.

## Grill Me

1. **Q-001:** Should the sysimage be committed to git (large binary, ~200-500MB) or built as part of a setup step?
   - **Recommended default:** Build as a setup step (`scripts/build_sysimage.ps1`), add `artifacts/sysimage/` to `.gitignore`. Document the one-time build in README.
   - **Why this matters:** Committing a 500MB binary bloats the repo permanently. Building on setup adds a one-time 5-15 minute step.
   - **If answered differently:** If committed, use Git LFS. Adds LFS dependency but eliminates the setup step for new machines.

2. **Q-002:** Should the NREL API fallback be the primary solve method instead of local Julia?
   - **Recommended default:** Local Julia with sysimage as primary, NREL API as validation/fallback only.
   - **Why this matters:** If Julia environment setup proves too fragile across machines, switching to API-primary eliminates the Julia dependency entirely at the cost of external dependency and rate limits.
   - **If answered differently:** If API-primary, remove PHASE-01 tasks 01-05 (sysimage) and make `solve_via_api.py` the sole solver. Simplifies setup but adds network dependency and solve-time uncertainty.

3. **Q-003:** What is the target number of case studies for the pipeline? Should it handle arbitrary new projects beyond the current 3 (saigon18, ninhsim, north_thuan)?
   - **Recommended default:** Support the 3 existing case studies with a documented pattern for adding new ones. Don't build generic ingestion yet.
   - **Why this matters:** Generic ingestion (Excel upload → auto-extract → pipeline) is the Idea 1 SaaS scope. Premature generalization adds 2-3 days of engineering without immediate deal-evaluation value.
   - **If answered differently:** If generic, add a PHASE-03 task for a `register_case_study.py` script that maps an arbitrary extracted-input JSON to the pipeline.

## Suggested Next Step

Answer the Grill Me questions (or accept defaults), then begin PHASE-01 and PHASE-02 in parallel. PHASE-01 is on the critical path for all subsequent phases. PHASE-02 is independent and can be completed while sysimage build and solve runs are in progress.
