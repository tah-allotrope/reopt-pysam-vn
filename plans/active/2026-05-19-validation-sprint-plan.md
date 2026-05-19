---
title: "Operational Decision Engine — Validation Sprint"
date: "2026-05-19"
status: "ready"
request: "Validate the 5-phase operational decision engine code (commit b724384) end-to-end — fix bugs, build/test solve pipeline, run pipeline, populate regression baselines"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-05-18_practical-refinements-operational-engine.md"
  - "research/2026-05-18_operational-decision-engine-next.md"
---

# Plan: Operational Decision Engine — Validation Sprint

## Objective

The operational decision engine code was implemented in commit b724384 (22 files, +3,290 lines across all 5 phases), but the pipeline has never been run end-to-end. No actual solve results exist for the TOU comparison scenarios, the PackageCompiler sysimage has never been built, the NREL API fallback has never been tested, and regression baselines use placeholder ranges. This sprint validates everything works — fixing known bugs, producing real solve results, running the orchestration pipeline, and anchoring regression baselines to real data. The NREL API domain shutdown on May 29, 2026 (10 days away) adds urgency to validating the API fallback path.

## Context Snapshot

- **Current state:** 107 tests passing (73 unit + 34 data). All engine code exists but is untested at the integration/system level. `artifacts/sysimage/` is empty. TOU comparison results directories contain `input.json` and `resolved_regime.json` but no solve results. Bounded-opt Julia scripts have a stale hardcoded path (`reopt-pysam-vn` instead of `reopt-pysam`). Existing case study results (saigon18, ninhsim, north_thuan) are from prior manual API runs and predate the engine refactor. The E2E baseline JSON at `tests/baselines/financial_e2e_baseline.json` has wide placeholder ranges (IRR 1-40%).
- **Desired state:** At least 1 TOU comparison scenario solved via API (validating `solve_via_api.py`). Sysimage build attempted (success or documented failure). `run_pipeline.ps1` executes end-to-end for 1 case study. Regression baselines populated with real computed values (±5% tolerance). All integration tests pass. Bounded-opt path bug fixed. API fallback validated before May 29 domain shutdown.
- **Key repo surfaces:**
  - `scripts/julia/run_bounded_opt_solve.jl:8` — stale `REPO_ROOT` path
  - `scripts/julia/run_bounded_opt_22kv_solve.jl:8` — stale `REPO_ROOT` path
  - `scripts/julia/build_sysimage.jl` — sysimage builder (never run)
  - `scripts/build_sysimage.ps1` — PowerShell sysimage wrapper
  - `scripts/python/reopt/solve_via_api.py` — API fallback solver (never run)
  - `scripts/run_solve.ps1` — solve wrapper with auto-detect sysimage
  - `scripts/run_pipeline.ps1` — master orchestration pipeline (never run)
  - `tests/python/integration/test_e2e_financial.py` — E2E financial test
  - `tests/python/integration/test_capacity_factor_benchmark.py` — CF benchmark
  - `tests/baselines/financial_e2e_baseline.json` — placeholder baseline
  - `artifacts/results/tou_comparison/` — 6 scenario dirs, no solve results
  - `NREL_API.env` — API credentials file (exists)
  - `src/python/reopt_pysam_vn/reopt/preprocess.py:49` — `REOPT_API_BASE_URL = "https://developer.nlr.gov/api/reopt/stable"` (correct domain)
- **Out of scope:** Building sysimage for production use (attempt only, document outcome). Solving all 6 TOU scenarios (solve 1 pair minimum to validate). Running `run_pipeline_batch.ps1` for all 6 case×regime combinations. Decree 146 demand-charge validation.

## Research Inputs

- `research/2026-05-18_practical-refinements-operational-engine.md` — PackageCompiler sysimage recommended as primary solve fix (1-2 day effort). HiGHS default timeout 600s, max 1,200s. NREL API accepts same JSON schema as local Julia. 50MW Binh Thuan benchmark: 16.49% CF, PR declining 0.84→0.61 over 4.5 years. On Windows: avoid `filter_stdlibs` (PackageCompiler Issue #914).
- `research/2026-05-18_operational-decision-engine-next.md` — Confirms `vn_deal_defaults_2026.json` exists and is registered. NREL API domain shutdown May 29, 2026. `preprocess.py` already uses `nlr.gov`. Bounded-opt scripts have stale `REPO_ROOT`. Sysimage expected ~200-400MB (under 2GB limit). Recommends API fallback first, sysimage second.

## Assumptions and Constraints

- **ASM-001:** `NREL_API.env` contains a valid API key (file exists in repo root). The key grants access to `developer.nlr.gov` v3 API at standard rate limits (1,000 req/hr).
- **ASM-002:** Julia 1.10+ is installed and accessible via `julia` command. REopt.jl, HiGHS.jl, JuMP.jl are installable via `Pkg.instantiate()` from `Project.toml`.
- **ASM-003:** The `run_vietnam_reopt()` function in `preprocess.py` is the canonical API submission path. `solve_via_api.py` wraps it — if the wrapper fails, the underlying function can be tested directly.
- **ASM-004:** The existing case study results in `artifacts/results/saigon18/`, `ninhsim/`, `north_thuan/` are valid REopt v3 results. They can be used to validate E2E financial tests without requiring new solves.
- **CON-001:** PackageCompiler sysimage build may fail on Windows with REopt.jl due to precompilation complexity. The API fallback is the guaranteed path.
- **CON-002:** NREL API solve time is 30-300s per scenario, plus network latency. API validation should solve 1-2 scenarios only.
- **CON-003:** Julia cold-start timeout (~3-8 min per invocation without sysimage) makes sequential local solve of 6 scenarios impractical without sysimage.
- **DEC-001:** API fallback is validated first (per research recommendation). Sysimage build is attempted second as an optimization.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Fix known bugs and verify imports | None | Clean bounded-opt scripts, verified Python imports for all new modules |
| PHASE-02 | Validate API solve pipeline | PHASE-01 | At least 1 TOU scenario solved via NREL API, results JSON with PV/BESS/Financial data |
| PHASE-03 | Attempt sysimage build + run pipeline | PHASE-02 | Sysimage artifact (or documented failure), pipeline dry-run + real run for 1 case study |
| PHASE-04 | Populate baselines and run integration tests | PHASE-02 | Tight regression baselines, all integration tests green, validation report |

## Detailed Phases

### PHASE-01 — Bug Fixes and Import Validation

**Goal**
Fix the known bounded-opt path bug and verify that all 22 new files from commit b724384 have correct imports, no syntax errors, and are individually loadable.

**Tasks**
- [ ] TASK-01-01: Fix `scripts/julia/run_bounded_opt_solve.jl` line 8 — replace `const REPO_ROOT = raw"C:\Users\tukum\Downloads\reopt-pysam-vn"` with `const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))` (dynamic path, same pattern as `build_sysimage.jl:22`)
- [ ] TASK-01-02: Fix `scripts/julia/run_bounded_opt_22kv_solve.jl` line 8 — same change as TASK-01-01
- [ ] TASK-01-03: Verify Python import chain for all new modules — run each of these and confirm no ImportError:
  ```
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import solve_via_api"
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import sensitivity_sweep"
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import bess_regime_comparison"
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import decree146_demand_charge"
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import fmp_sensitivity"
  python -c "import sys; sys.path.insert(0,'scripts/python/reopt'); import generate_bess_economics_report"
  ```
- [ ] TASK-01-04: Run existing unit + data validation tests to confirm no regressions:
  ```
  python -m pytest tests/python/reopt/test_unit.py tests/python/reopt/test_data_validation.py -v
  ```
- [ ] TASK-01-05: Verify `NREL_API.env` exists and contains `API_KEY_NAME` key (do not print the actual key value):
  ```
  python -c "from pathlib import Path; lines=[l for l in Path('NREL_API.env').read_text().splitlines() if l.strip().startswith('API_KEY_NAME')]; print(f'{len(lines)} key(s) found')"
  ```

**Files / Surfaces**
- `scripts/julia/run_bounded_opt_solve.jl` — Fix hardcoded path at line 8
- `scripts/julia/run_bounded_opt_22kv_solve.jl` — Fix hardcoded path at line 8
- All new Python modules in `scripts/python/reopt/` — Import validation only

**Dependencies**
- None

**Exit Criteria**
- [ ] Both bounded-opt scripts use `@__DIR__`-based path resolution, no occurrence of `reopt-pysam-vn` in `scripts/julia/`
- [ ] All 6 new Python modules import without error
- [ ] 107 tests pass (73 unit + 34 data validation)
- [ ] `NREL_API.env` has at least 1 API key line

**Phase Risks**
- **RISK-01-01:** A new Python module may depend on an uninstalled package. **Mitigation:** Check `requirements.txt` or `pyproject.toml` for missing dependencies; install with pip.

### PHASE-02 — API Solve Pipeline Validation

**Goal**
Prove that `solve_via_api.py` can submit a scenario to the NREL API, poll for results, and produce a valid results JSON with non-null PV, ElectricStorage, and Financial sections. This validates the critical path before the May 29 domain shutdown.

**Tasks**
- [ ] TASK-02-01: Select 1 TOU comparison scenario pair for validation — use the saigon18 Decision 963 scenario as the test case:
  ```
  artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/699155b878151af0/input.json
  ```
  Verify this file contains valid REopt JSON with `ElectricLoad`, `PV`, and `Site` sections.
- [ ] TASK-02-02: Dry-run the solve wrapper to verify argument parsing:
  ```
  .\scripts\run_solve.ps1 -Scenario artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/699155b878151af0/input.json -NoSolve
  ```
- [ ] TASK-02-03: Run `solve_via_api.py` directly against the selected scenario:
  ```
  python scripts/python/reopt/solve_via_api.py --scenario artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/699155b878151af0/input.json --output-dir artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/699155b878151af0/ --no-apply-defaults
  ```
  Use `--no-apply-defaults` because the TOU comparison scenarios are already preprocessed (tariff arrays baked in by `materialize_tou_comparison.py`).
- [ ] TASK-02-04: Validate the results JSON — check that `status` is `"optimal"`, `PV.size_kw > 0`, and `Financial.npv` is numeric.
- [ ] TASK-02-05: If TASK-02-03 succeeds, solve the matching Decision 14 scenario:
  ```
  artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/a41f7a6f42f74a15/input.json
  ```
- [ ] TASK-02-06: Run `tou_financial_delta.py` to verify it now produces numeric values (not "no_results") for the solved pair.
- [ ] TASK-02-07: If solve fails with `run_vietnam_reopt()`, test the API directly:
  ```python
  import requests, json
  from pathlib import Path
  scenario = json.loads(Path("...input.json").read_text())
  scenario.pop("_meta", None)
  r = requests.post("https://developer.nlr.gov/api/reopt/stable/job?api_key=<KEY>",
                     json={"Scenario": scenario})
  print(r.status_code, r.json().get("run_uuid"))
  ```
  This isolates whether the failure is in the wrapper or the API.

**Files / Surfaces**
- `scripts/python/reopt/solve_via_api.py` — Primary validation target
- `scripts/run_solve.ps1` — Wrapper validation (dry-run)
- `src/python/reopt_pysam_vn/reopt/preprocess.py` — `run_vietnam_reopt()` underlying API call
- `artifacts/results/tou_comparison/2026-03-20-scenario-a-fixed-sizing-evntou/` — Target scenario pair
- `scripts/python/reopt/tou_financial_delta.py` — Downstream validation
- `NREL_API.env` — API credentials

**Dependencies**
- PHASE-01 (imports and API key verified)
- Network access to `developer.nlr.gov`

**Exit Criteria**
- [ ] At least 1 scenario produces `reopt-results.json` with `status: "optimal"` and `PV.size_kw > 0`
- [ ] `solve_via_api.py` completes without error (exit code 0)
- [ ] Results JSON has non-null `Financial.npv`, `Financial.lcc`, `ElectricTariff` sections
- [ ] `tou_financial_delta.py` produces CSV with numeric values for the solved scenario (not "no_results")
- [ ] API response time is recorded (expected 30-300s per solve)

**Phase Risks**
- **RISK-02-01:** API key is expired or rate-limited. **Mitigation:** Check API key status at `developer.nlr.gov/signup/`. If expired, regenerate key or use DEMO_KEY (30 req/hr, longer solve times).
- **RISK-02-02:** `run_vietnam_reopt()` in `preprocess.py` may not handle pre-processed scenarios (with baked-in tariff arrays) correctly when `apply_defaults=False`. **Mitigation:** Use `--no-apply-defaults` flag. If that codepath is untested, call the API directly via `requests.post` (TASK-02-07) as a diagnostic.
- **RISK-02-03:** Scenario JSON may use REopt v2 schema fields incompatible with v3 API. **Mitigation:** Check the API error response for schema validation errors. The TOU comparison scenarios were materialized with v3-compatible `apply_vietnam_defaults()`, so this risk is low.
- **RISK-02-04:** API solve exceeds 1,200s timeout for complex PV+BESS+TOU scenario. **Mitigation:** Per NREL Discussion #149, the API enforces a hard 1,200s limit. If hit, simplify the scenario by removing BESS or narrowing PV size range for validation purposes only.

### PHASE-03 — Sysimage Build and Pipeline Execution

**Goal**
Attempt to build the PackageCompiler sysimage for local Julia solves, then run the master orchestration pipeline (`run_pipeline.ps1`) end-to-end for 1 case study. If sysimage build fails, document the failure and proceed with API fallback.

**Tasks**
- [ ] TASK-03-01: Verify Julia environment — `julia --version` confirms 1.10+, `julia --project -e "using Pkg; Pkg.instantiate(); Pkg.status()"` shows REopt, HiGHS, JuMP, PackageCompiler installed.
- [ ] TASK-03-02: Attempt sysimage build:
  ```
  .\scripts\build_sysimage.ps1
  ```
  Expected outcome: `artifacts/sysimage/reopt_sysimage.dll` exists (5-15 min build). If it fails, record the error message and skip to TASK-03-04.
- [ ] TASK-03-03: If sysimage build succeeds, validate it:
  ```
  julia --sysimage artifacts/sysimage/reopt_sysimage.dll --project -e "using REopt; println(\"sysimage OK\")"
  ```
  Measure startup time — should be <3s (vs 30-60s without sysimage).
- [ ] TASK-03-04: Run `run_pipeline.ps1` in dry-run mode for saigon18:
  ```
  .\scripts\run_pipeline.ps1 -CaseStudy saigon18 -Regime decision_963_2026_current -Config data/vietnam/vn_deal_defaults_2026.json -DryRun
  ```
  Verify it prints all 5 stages with correct input/output paths without executing.
- [ ] TASK-03-05: Run `run_pipeline.ps1` with `--skip-solve` to test stages 3-5 using existing saigon18 results:
  ```
  .\scripts\run_pipeline.ps1 -CaseStudy saigon18 -Regime decision_963_2026_current -Config data/vietnam/vn_deal_defaults_2026.json -SkipSolve
  ```
  This validates the financial analysis → BESS dispatch → report stages without needing a new solve.
- [ ] TASK-03-06: If pipeline fails at a stage, diagnose: check `.done` marker files in `artifacts/pipeline_cache/`, inspect stage stdout/stderr, identify which script and arguments caused the failure.
- [ ] TASK-03-07: If sysimage exists, run pipeline with local solve (no --skip-solve, no --fallback) for 1 scenario. If no sysimage, run with `--fallback` (API solve).

**Files / Surfaces**
- `scripts/build_sysimage.ps1` — Sysimage build wrapper
- `scripts/julia/build_sysimage.jl` — Sysimage build script
- `artifacts/sysimage/` — Sysimage output (currently empty)
- `scripts/run_pipeline.ps1` — Master orchestration pipeline
- `artifacts/pipeline_cache/` — Stage completion markers
- `artifacts/results/saigon18/` — Existing case study results (used with --skip-solve)
- `data/vietnam/vn_deal_defaults_2026.json` — Financial config for pipeline

**Dependencies**
- PHASE-02 (API solve validated — needed for --fallback path)
- Julia 1.10+ installed
- PackageCompiler.jl in Project.toml

**Exit Criteria**
- [ ] Sysimage: either `artifacts/sysimage/reopt_sysimage.dll` exists with <3s startup OR failure is documented with error message and reason
- [ ] `run_pipeline.ps1 -DryRun` prints all 5 stages without error
- [ ] `run_pipeline.ps1 -SkipSolve` completes stages 3-5 and produces an HTML report in `artifacts/reports/`
- [ ] Second `run_pipeline.ps1 -SkipSolve` run completes in <10s (all stages cached)
- [ ] `--Force` flag clears cache and re-runs all stages

**Phase Risks**
- **RISK-03-01:** PackageCompiler build fails due to REopt.jl precompilation complexity or Windows-specific issues (Issue #914: `filter_stdlibs` bug). **Mitigation:** Set `SKIP_PRECOMPILE=true` for a minimal sysimage without precompile workload. If that also fails, document and proceed with API-only path.
- **RISK-03-02:** `run_pipeline.ps1` stage scripts may have hardcoded paths or assumptions about result JSON structure that don't match the actual solve output. **Mitigation:** Run with `--skip-solve` first (uses existing results), which isolates downstream script issues from solve issues.
- **RISK-03-03:** Existing saigon18 results may predate the parameterized financial module changes, causing `equity_irr.py --config` to fail with missing keys. **Mitigation:** Run `equity_irr.py` standalone with `--config data/vietnam/vn_deal_defaults_2026.json --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json` to isolate.

### PHASE-04 — Regression Baselines and Integration Tests

**Goal**
Replace placeholder regression baselines with values computed from real solve results, then run all integration tests to green. Produce a validation summary.

**Tasks**
- [ ] TASK-04-01: Run `equity_irr.py` with existing saigon18 results and config to get actual IRR/NPV values:
  ```
  python scripts/python/reopt/equity_irr.py --config data/vietnam/vn_deal_defaults_2026.json --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json
  ```
  Record the output IRR, NPV, and LCOE values.
- [ ] TASK-04-02: Update `tests/baselines/financial_e2e_baseline.json` — narrow the ranges from placeholder (IRR 1-40%) to actual computed values ±5%. Update `total_capex_usd` to match the scenario's actual initial capital cost.
- [ ] TASK-04-03: Run E2E financial test:
  ```
  python -m pytest tests/python/integration/test_e2e_financial.py -v
  ```
- [ ] TASK-04-04: Run capacity factor benchmark test:
  ```
  python -m pytest tests/python/integration/test_capacity_factor_benchmark.py -v
  ```
  This tests PySAM PVWatts output for Binh Thuan coordinates (14-20% CF range).
- [ ] TASK-04-05: Run `sensitivity_sweep.py` with existing saigon18 results to validate sweep output:
  ```
  python scripts/python/reopt/sensitivity_sweep.py --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json --config data/vietnam/vn_deal_defaults_2026.json --output artifacts/reports/saigon18_sensitivity.csv
  ```
- [ ] TASK-04-06: Run `fmp_sensitivity.py` with existing results to validate FMP sweep:
  ```
  python scripts/python/reopt/fmp_sensitivity.py --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json --output artifacts/reports/saigon18_fmp_sensitivity.csv
  ```
- [ ] TASK-04-07: Run full test suite including Layer 5:
  ```
  .\tests\run_all_tests.ps1 -IncludeFinancial
  ```
- [ ] TASK-04-08: Create validation summary — record in `activeContext.md`:
  - Which scenarios were solved (API vs local)
  - Sysimage build outcome (success/fail + reason)
  - Pipeline execution outcome
  - Test results (unit, data validation, E2E, CF benchmark)
  - Any remaining gaps

**Files / Surfaces**
- `tests/baselines/financial_e2e_baseline.json` — Update with real values
- `tests/python/integration/test_e2e_financial.py` — Run with real baseline
- `tests/python/integration/test_capacity_factor_benchmark.py` — Run PySAM validation
- `scripts/python/reopt/sensitivity_sweep.py` — Validate sweep output
- `scripts/python/reopt/fmp_sensitivity.py` — Validate FMP sweep output
- `artifacts/reports/` — Sweep output CSVs
- `tests/run_all_tests.ps1` — Full suite including Layer 5
- `activeContext.md` — Validation summary

**Dependencies**
- PHASE-02 (need at least 1 real solve result or existing case study results)
- PHASE-03 (pipeline execution informs validation summary)

**Exit Criteria**
- [ ] `financial_e2e_baseline.json` has IRR range narrower than ±10% (not 1-40%)
- [ ] `pytest tests/python/integration/test_e2e_financial.py` passes
- [ ] `pytest tests/python/integration/test_capacity_factor_benchmark.py` passes (CF in 14-20% for Binh Thuan)
- [ ] `sensitivity_sweep.py` produces CSV with >20 rows (parameter combinations)
- [ ] `fmp_sensitivity.py` produces CSV with 7 rows (VND 1,400-2,000 in steps of 100)
- [ ] Full test suite (`run_all_tests.ps1 -IncludeFinancial`) reports all layers green
- [ ] Validation summary recorded in `activeContext.md`

**Phase Risks**
- **RISK-04-01:** PySAM may not be installed or may require NSRDB API key for weather data download. **Mitigation:** Check `pip show nrel-pysam`; if missing, `pip install nrel-pysam`. PySAM PVWatts can use locally cached weather files — check `data/weather/` for existing TMY files.
- **RISK-04-02:** `sensitivity_sweep.py` or `fmp_sensitivity.py` may fail if the existing saigon18 results use an older schema without expected keys. **Mitigation:** Inspect the results JSON structure first; if keys differ, update the extraction functions.

## Verification Strategy

- **TEST-001:** `python -m pytest tests/python/reopt/test_unit.py tests/python/reopt/test_data_validation.py -v` — 107 tests pass (regression gate, PHASE-01)
- **TEST-002:** `python -m pytest tests/python/integration/test_e2e_financial.py -v` — E2E financial test with real baseline (PHASE-04)
- **TEST-003:** `python -m pytest tests/python/integration/test_capacity_factor_benchmark.py -v` — PVWatts CF in 14-20% for Binh Thuan (PHASE-04)
- **TEST-004:** `.\tests\run_all_tests.ps1 -IncludeFinancial` — Full test suite including Layer 5 (PHASE-04)
- **MANUAL-001:** Inspect `reopt-results.json` from API solve — confirm `status: "optimal"`, `PV.size_kw > 0`, `Financial.npv` is numeric (PHASE-02)
- **MANUAL-002:** Run `.\scripts\run_pipeline.ps1 -DryRun` — verify 5-stage plan prints correctly (PHASE-03)
- **MANUAL-003:** Open HTML report from pipeline run in browser — verify Chart.js renders with numeric data (PHASE-03)
- **DATA-001:** `grep -r "reopt-pysam-vn" scripts/julia/` returns zero matches after PHASE-01 bounded-opt fix
- **DATA-002:** `tou_financial_delta.py` output CSV has no "no_results" values for solved scenarios (PHASE-02)

## Risks and Alternatives

- **RISK-001:** Julia cold-start blocks local solve entirely and sysimage build fails. **Mitigation:** API fallback is validated first (PHASE-02). All downstream phases use API results or existing results. Local Julia solve becomes a documented future optimization.
- **RISK-002:** NREL API domain `developer.nlr.gov` is unreachable from this network. **Mitigation:** Test with `curl https://developer.nlr.gov/api/reopt/stable` first. If blocked, check VPN/proxy settings. If permanently unreachable, use existing case study results for all downstream validation.
- **RISK-003:** Existing case study results have a different JSON structure than what the new parameterized financial modules expect. **Mitigation:** Test `equity_irr.py --config --reopt` with existing results in PHASE-04 TASK-04-01 before running the full pipeline. If schema mismatch, add a normalization shim in the financial module.
- **ALT-001:** Skip sysimage build entirely and commit to API-only solve path. **Not chosen** because sysimage build is a one-time attempt with high payoff (eliminates 3-8 min cold-start per solve). The attempt costs 15 minutes; failure is graceful.
- **ALT-002:** Use existing case study results for all validation, skip API solve. **Not chosen** because the API fallback is time-sensitive (May 29 shutdown deadline) and `solve_via_api.py` has never been tested. Existing results can serve as a fallback if API validation fails.

## Grill Me

1. **Q-001:** Should the validation sprint also solve all 6 TOU comparison scenarios (3 case studies × 2 regimes), or is 1 pair (saigon18 × both regimes) sufficient?
   - **Recommended default:** Solve 1 pair (saigon18 × Decision 963 + Decision 14) to validate the pipeline. Solve remaining 4 as a follow-up once the pipeline is proven.
   - **Why this matters:** Each API solve takes 30-300s. Solving all 6 scenarios adds 3-30 minutes and risks hitting rate limits, but produces the complete TOU comparison dataset.
   - **If answered differently:** If all 6, add a TASK-02-08 to batch-solve via `solve_via_api.py` for ninhsim and north_thuan pairs after saigon18 validation. Budget 30 minutes for API solves.

2. **Q-002:** Should the sysimage artifact be committed (via Git LFS) or kept as a local build-on-setup artifact?
   - **Recommended default:** Keep as local build-on-setup. Add `artifacts/sysimage/` to `.gitignore` (already done in commit b724384). Document the build command in README.
   - **Why this matters:** Sysimage is ~200-400MB. Committing via LFS adds permanent storage cost and LFS dependency. Build-on-setup adds a one-time 5-15 min step per machine.
   - **If answered differently:** If committed via LFS, add `git lfs install && git lfs track "artifacts/sysimage/*.dll"` to PHASE-03.

## Suggested Next Step

Begin PHASE-01 immediately (bounded-opt fix + import validation, ~15 minutes). Then proceed to PHASE-02 API validation — this is the time-critical path due to the May 29 domain shutdown. PHASE-03 and PHASE-04 follow sequentially. The entire sprint should take 2-4 hours of active work (plus API solve wait times).
