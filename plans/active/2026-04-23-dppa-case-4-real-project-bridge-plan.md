---
title: "DPPA Case 4 Real-Project Decision-Grade Bridge"
date: "2026-04-23"
status: "draft"
request: "using the insights/lessons from dppa case 1 3 retrospective review to evoke plan skill for a detail multiphase md plan for a new dppa case 4"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-07-vietnam-dppa-buyer-guide.md"
---

# Plan: DPPA Case 4 Real-Project Decision-Grade Bridge

## Objective
Create a new `DPPA Case 4` workflow that turns the strongest lessons from Cases 1-3 into a decision-grade real-project bridge: reuse the Case 2 hourly synthetic-DPPA settlement architecture, preserve Case 3's site-consistency and storage-floor discipline, and move the workflow toward actual-project `8760` load, tariff, controller, and finance assumptions. This matters now because the retrospective review concluded that Case 2 is the best analytical core, Case 3 is the right realism-first direction but not yet trustworthy downstream, and the repo already has real-project notes that are specific enough to justify a clean new planning pass.

## Context Snapshot
- **Current state:** `DPPA Case 1` is a useful private-wire reference but did not validate a real PV+BESS candidate; `DPPA Case 2` is the strongest synthetic-DPPA baseline and already has a tested hourly buyer settlement engine; `DPPA Case 3` improved site consistency and storage enforcement but its downstream D-G analytics are partial or defective; `AGENTS.md` records a real-project study basis of `3.2 MWp PV`, `1 MW / 2.2 MWh BESS`, `22kV` two-part EVN tariff, `20-year` life, `20%` CIT, and `15%` PPA discount, with missing actual `8760` data still identified as the main gap.
- **Desired state:** `DPPA Case 4` becomes the repo's first explicitly decision-grade real-project bridge workflow with hard data-fidelity gates, branch-faithful `22kV` buyer settlement, controller-vs-optimizer comparison on the same candidate, separate buyer/developer outputs, robust regression coverage, and a final report that is generated only from validated, schema-checked artifacts.
- **Key repo surfaces:** `reports/2026-04-23-dppa-case-1-3-retrospective-review.md`, `reports/2026-04-21-dppa-case-3-plan-implementation-review.md`, `research/2026-04-07-vietnam-dppa-buyer-guide.md`, `src/python/reopt_pysam_vn/integration/dppa_case_2.py`, `src/python/reopt_pysam_vn/integration/dppa_case_3.py`, `src/python/reopt_pysam_vn/integration/bridge.py`, `src/julia/REoptVietnam.jl`, `scripts/julia/run_vietnam_scenario.jl`, `AGENTS.md`, `tests/python/integration/test_dppa_case_2_phase_*.py`, `tests/python/integration/test_dppa_case_3_phase_ab.py`.
- **Out of scope:** broad portfolio ranking across multiple sites, private-wire redesign of Case 1, non-DPPA tariff studies, wind/diesel/resilience additions, and publishing a final closeout based on transferred market data or unvalidated synthetic placeholders.

## Research Inputs
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` - Confirms the buyer-side synthetic DPPA payment stack must stay explicit (`EVN payment + CfD +/- generator`), which means Case 4 should build on the Case 2 hourly settlement architecture rather than on Case 1 private-wire pricing or Case 3 annual-average shortcuts.
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` - Reinforces that settlement quantity, excess-generation treatment, DPPA adder, KPP, and shortfall billing are core commercial design inputs, so Case 4 must freeze them early and keep them schema-validated through reporting.

## Assumptions and Constraints
- **ASM-001:** `DPPA Case 4` should inherit the retrospective's central lesson: reuse Case 2's hourly settlement engine as the canonical analytical core and treat Case 3's downstream D-G scripts as reference inputs, not as the base implementation path.
- **ASM-002:** The real-project basis recorded in `AGENTS.md` is the intended starting point for Case 4 unless the user later redirects the case basis: `3.2 MWp PV`, `1 MW / 2.2 MWh BESS`, `22kV` two-part EVN tariff, `20-year` life, `20%` CIT, and `15%` PPA discount.
- **ASM-003:** Case 4 should explicitly distinguish `staging` artifacts from `decision-grade` artifacts when synthesized 8760 load data is used early and before actual project data is available.
- **ASM-004:** The base commercial anchor uses `5% below EVN` as the strike basis, with `15% below EVN` tested as a sensitivity — preserving continuity with Case 3's commercial framing.
- **ASM-005:** Case 4 runs a single fixed physical reference lane only (no bounded optimization sensitivity lane); the case is a feasibility-study replication, not an optimization-assisted sizing decision.
- **ASM-006:** Controller analysis uses a documented proxy schedule, not actual project controller windows; the proxy limitation must be recorded in source-quality metadata and report headers.
- **CON-001:** Actual project `8760` load profile is not yet available; synthesized/scaled load is permitted for staging artifacts, but decision-grade closeout is blocked until actual or explicitly approved bankable `8760` data is available.
- **CON-002:** `22kV` two-part tariff demand charges may not map natively inside REopt, so Case 4 will require a post-processing demand-charge reconciliation layer for the buyer benchmark and settlement package.
- **CON-003:** Case 3 showed that final reports can become misleading when artifact contracts drift; Case 4 must not generate a final closeout report unless flat/nested artifact shape checks and critical-field presence checks pass.
- **DEC-001:** Case 4 remains a `synthetic_financial_dppa` case, not a return to Case 1 private-wire logic.
- **DEC-002:** Hard physical requirements must be encoded as hard constraints or explicit fixed-lane assumptions; descriptive metadata alone is not sufficient.
- **DEC-003:** Buyer and developer economics remain separate surfaces until the final decision artifact, following the Case 2 pattern.
- **DEC-004:** Case 4 implementation stays in the current main workspace (`main` branch); the `real-project-data` branch is used as a reference for inputs/assumptions only, not as the primary implementation location.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Freeze Case 4 definition, fidelity gates, and shared guardrails from the retrospective | None | Case 4 plan-aligned definition, assumptions register, gap/guardrail register |
| PHASE-02 | Build the canonical Case 4 data package and artifact contracts around actual-project inputs | PHASE-01 | Input package, schema contracts, source-quality metadata, regression tests |
| PHASE-03 | Build and validate the fixed physical reference lane (single fixed lane, no bounded sensitivity) | PHASE-02 | Fixed scenario JSON, REopt result artifacts, physical summaries, Phase C tests |
| PHASE-04 | Implement hourly buyer settlement, branch-faithful benchmarking, controller realism screen, and developer finance | PHASE-03 | Buyer settlement, benchmark, contract risk, controller gap (proxy), PySAM results, REopt-vs-PySAM comparison, developer screening |
| PHASE-05 | Add release-grade validation, combined decision packaging, and durable documentation | PHASE-04 | Combined decision, final summary, final report, README/docs updates, full regression lane |

## Detailed Phases

### PHASE-01 - Freeze Case 4 Definition and Guardrails
**Goal**
Define what `DPPA Case 4` is solving, what it inherits from Cases 2 and 3, what it must not repeat from Cases 1 and 3, and what conditions must be met before any output can be labeled decision-grade.

**Tasks**
- [ ] TASK-01-01: Create a `DPPA Case 4` design note that explicitly states the intended split: Case 2 hourly settlement engine as canonical buyer core, Case 3 site consistency and storage-floor discipline as required guardrails, and actual-project data fidelity as the main new objective.
- [ ] TASK-01-02: Freeze the commercial basis as `synthetic_financial_dppa` with the `5% below EVN` base strike anchor and `15% below EVN` as a sensitivity, carrying forward matched quantity, excess treatment, DPPA adder, KPP, and shortfall rules from Case 2 unless changed consciously.
- [ ] TASK-01-03: Freeze the real-project reference package recorded in `AGENTS.md` as the base comparison case: `3.2 MWp PV`, `1 MW / 2.2 MWh BESS`, `22kV` two-part tariff, `20-year` life, `20%` CIT.
- [ ] TASK-01-04: Define a hard data-fidelity gate that separates `staging` mode (synthesized/scaled `8760` load) from `decision-grade` mode (actual or agreed bankable `8760` load + market basis). Decision-grade closeout is blocked until the gate is satisfied.
- [ ] TASK-01-05: Define release guardrails: no final report if any critical metric is null unexpectedly, if artifact schemas fail, if buyer/developer surfaces are blended prematurely, or if controller-vs-optimizer compares different physical candidates.
- [ ] TASK-01-06: Confirm implementation stays in the main workspace; the `real-project-data` branch is a reference source only, not the primary implementation location.

**Files / Surfaces**
- `plans/active/2026-04-23-dppa-case-4-real-project-bridge-plan.md` - Canonical planning artifact for Case 4 execution.
- `reports/2026-04-23-dppa-case-1-3-retrospective-review.md` - Source of cross-case lessons and anti-patterns that must be converted into guardrails.
- `AGENTS.md` - Real-project baseline assumptions and current missing-data notes.
- `src/python/reopt_pysam_vn/integration/dppa_case_2.py` - Canonical settlement architecture to preserve.
- `src/python/reopt_pysam_vn/integration/dppa_case_3.py` - Current realism-first definition surfaces and site-consistency patterns to reuse selectively.

**Dependencies**
- None

**Exit Criteria**
- [ ] Case 4 has a frozen definition that explicitly states what is reused from Case 2, what is reused from Case 3, and what is intentionally left behind from Cases 1 and 3.
- [ ] Decision-grade gating rules are explicit and written before any new implementation phase begins.

**Phase Risks**
- **RISK-01-01:** Case 4 could become an unfocused mix of Case 2 repairs and Case 3 repairs; mitigate by freezing a single base purpose: decision-grade real-project bridge using shared validated components, not a catch-all successor case.
- **RISK-01-02:** Implementation could inadvertently live across both `main` and `real-project-data` branches; mitigate by treating `real-project-data` as reference-only from day one.

### PHASE-02 - Build the Canonical Case 4 Data Package and Contracts
**Goal**
Build the source-of-truth input package, schema contracts, provenance metadata, and fidelity labels for the actual-project workflow before any new solve or settlement logic is added.

**Tasks**
- [ ] TASK-02-01: Create a new Case 4 helper module, recommended as `src/python/reopt_pysam_vn/integration/dppa_case_4.py`, that owns Phase A/B definition surfaces, source-quality metadata, and contract schemas.
- [ ] TASK-02-02: Build an input-preparation script, recommended as `scripts/python/integration/prepare_dppa_case_4_phase_ab.py`, that assembles the Case 4 load, tariff, market, controller-window, and strike metadata into a single package under `artifacts/reports/real_project/`.
- [ ] TASK-02-03: Add a `source_quality_block` that records whether each major input is `actual_project`, `same_site_proxy`, `transferred_repo_local`, or `synthetic_staging`, and require this block in every downstream artifact.
- [ ] TASK-02-04: Build a canonical `22kV` tariff package that keeps hourly energy rates separate from demand-charge logic so later settlement and benchmark stages can reconcile demand charges explicitly instead of hiding them.
- [ ] TASK-02-05: Define the proxy controller metadata package: preferred charge/discharge windows, marked explicitly as `proxy` (not actual project), with documentation of the proxy basis and limitation recorded in source-quality metadata.
- [ ] TASK-02-06: Add regression tests for the Case 4 A/B surfaces in `tests/python/integration/test_dppa_case_4_phase_ab.py`, including source-quality tags, fidelity gate behavior, and artifact-schema validation.

**Files / Surfaces**
- `src/python/reopt_pysam_vn/integration/dppa_case_4.py` - New Case 4 design, schema, and packaging helpers.
- `scripts/python/integration/prepare_dppa_case_4_phase_ab.py` - Canonical builder for A/B artifacts.
- `tests/python/integration/test_dppa_case_4_phase_ab.py` - Regression lock for source metadata, schema contracts, and quality gates.
- `artifacts/reports/real_project/` - Canonical home for Case 4 machine-readable planning and input-package artifacts.
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` - Buyer-settlement rules that must remain explicit in the contract schemas.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] A single Case 4 input package exists with load, market, tariff, controller, strike, and source-quality metadata.
- [ ] Phase A/B schemas fail if critical source-quality fields, tariff branch labels, or fidelity gates are missing.

**Phase Risks**
- **RISK-02-01:** If actual project `8760` inputs are still missing, the team may accidentally treat a staging package as final; mitigate by encoding `staging` vs `decision-grade` explicitly in the schema and in report-generation gates.

### PHASE-03 - Build and Validate the Physical Case Lanes
**Goal**
Produce the Case 4 physical scenario package in a way that supports both the real-project comparison need and the lessons learned about hard physical constraints, same-candidate comparisons, and tariff-aware solve validation.

**Tasks**
- [ ] TASK-03-01: Build a fixed reference scenario around the real-project basis (`3.2 MWp`, `1 MW / 2.2 MWh`) under `scenarios/case_studies/real_project/`, so the repo can compare REopt and the feasibility-study concept on the same named configuration.
- [ ] TASK-03-02: Ensure Case 4 uses hard storage floor constraints or fixed-size inputs so the workflow cannot silently collapse to PV-only. No bounded sensitivity lane — the fixed lane IS the reference case.
- [ ] TASK-03-03: Add no-solve validation and solve execution surfaces, recommended as `scripts/python/integration/build_dppa_case_4_phase_c.py` plus `scripts/julia/run_vietnam_scenario.jl`, and record both in the final validation trail.
- [ ] TASK-03-04: Reuse `src/julia/REoptVietnam.jl` export-cap support where applicable so Decree 57 hard export-cap behavior remains explicit in the physical solve.
- [ ] TASK-03-05: Add `tests/python/integration/test_dppa_case_4_phase_c.py` to lock fixed-lane sizing preservation, storage-floor enforcement, and scenario metadata truthfulness.

**Files / Surfaces**
- `scenarios/case_studies/real_project/` - New fixed and bounded Case 4 scenario JSONs.
- `scripts/python/integration/build_dppa_case_4_phase_c.py` - Canonical scenario and physical-summary builder for Phase C.
- `tests/python/integration/test_dppa_case_4_phase_c.py` - Regression tests for physical-lane behavior and metadata.
- `src/julia/REoptVietnam.jl` - Existing Decree 57 export-cap support that Case 4 should reuse rather than reimplement.
- `scripts/julia/run_vietnam_scenario.jl` - Existing no-solve and solve runner for scenario validation.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Case 4 has a single canonical fixed physical lane that preserves the real-project reference assumptions without a bounded sensitivity lane.
- [ ] The physical lane cannot return a silent zero-storage result.

**Phase Risks**
- **RISK-03-01:** The single fixed-lane approach means no sizing sensitivity is produced by default; document this as an intentional design choice and add it as a potential future phase rather than an omission.

### PHASE-04 - Implement Buyer Settlement, Controller Realism, and Developer Finance
**Goal**
Deliver the core Case 4 analytical package using hourly buyer settlement, branch-faithful tariff benchmarking, controller-vs-optimizer realism screens on the same candidate, and developer finance outputs that remain separate until the final decision layer.

**Tasks**
- [ ] TASK-04-01: Extract or reuse the Case 2 hourly settlement engine inside Case 4 rather than duplicating the simplified annual-average arithmetic used in Case 3.
- [ ] TASK-04-02: Build branch-faithful buyer settlement and benchmark artifacts for the `22kV` two-part tariff, including an explicit demand-charge reconciliation layer in post-processing when REopt cannot represent the full tariff natively.
- [ ] TASK-04-03: Run the base strike at `5% below EVN` and add a sensitivity branch at `15% below EVN`; produce side-by-side delta artifacts, not just branch labels without branch math.
- [ ] TASK-04-04: Implement the controller-vs-optimizer realism screen using the documented proxy schedule from Phase 2; both dispatch modes must be evaluated on the same fixed candidate, with proxy limitation explicitly recorded in source-quality metadata and the controller-gap artifact header.
- [ ] TASK-04-05: Extend the developer-side finance bridge in `src/python/reopt_pysam_vn/integration/bridge.py` so Case 4 can produce a cleaner separation between matched-buyer value, excess treatment, and developer revenue assumptions; if full synthetic-DPPA bilateral finance is still too large, the limitation must be explicit in the artifact schema.
- [ ] TASK-04-06: Publish the full set of Phase D/E/F artifacts: buyer settlement, buyer benchmark, contract risk, controller gap (proxy), PySAM results, REopt-vs-PySAM comparison, and developer screening.
- [ ] TASK-04-07: Add `tests/python/integration/test_dppa_case_4_phase_d.py`, `...phase_e.py`, and `...phase_f.py` to lock hourly settlement math, tariff-branch delta logic, controller same-candidate comparisons (on proxy), and PySAM key extraction.

**Files / Surfaces**
- `src/python/reopt_pysam_vn/integration/dppa_case_2.py` - Source of the hourly settlement logic that Case 4 should reuse or extract into shared helpers.
- `src/python/reopt_pysam_vn/integration/dppa_case_4.py` - New Case 4 commercial and reporting helpers.
- `src/python/reopt_pysam_vn/integration/bridge.py` - Case 4 finance mapping and REopt-vs-PySAM comparison surfaces.
- `scripts/python/integration/analyze_dppa_case_4_phase_d.py` - Buyer settlement, benchmark, and risk analysis.
- `scripts/python/integration/analyze_dppa_case_4_phase_e.py` - Controller-vs-optimizer realism analysis.
- `scripts/python/integration/analyze_dppa_case_4_phase_f.py` - PySAM finance, REopt-vs-PySAM comparison, and developer screening.
- `tests/python/integration/test_dppa_case_4_phase_d.py` - Buyer settlement and tariff-branch regression coverage.
- `tests/python/integration/test_dppa_case_4_phase_e.py` - Controller-gap and same-candidate comparison coverage.
- `tests/python/integration/test_dppa_case_4_phase_f.py` - PySAM output wiring and comparison coverage.

**Dependencies**
- PHASE-03

**Exit Criteria**
- [ ] The buyer-side Case 4 settlement is hourly, branch-faithful, and clearly reused from or aligned with the Case 2 engine.
- [ ] Controller-vs-optimizer compares the same physical candidate and cannot be generated from hardcoded fallback inputs.

**Phase Risks**
- **RISK-04-01:** Reusing Case 3 scripts directly may import known arithmetic and artifact-shape bugs; mitigate by reusing Case 2 logic and rebuilding Case 4 analytical scripts with test-first coverage rather than forking the broken downstream chain.

### PHASE-05 - Validate, Close Out, and Document the DPPA Case Family
**Goal**
Turn Case 4 into a release-grade workflow with explicit quality gates, stable combined-decision outputs, top-level documentation, and final reports that cannot outrun the underlying validated analytics.

**Tasks**
- [ ] TASK-05-01: Add a combined-decision artifact and final-summary artifact for Case 4 that consume only schema-validated Phase C-F artifacts and fail fast on missing or null critical metrics.
- [ ] TASK-05-02: Build a final report generator, recommended as `scripts/python/integration/generate_dppa_case_4_final_report.py`, that reads only the validated combined/final-summary artifacts and distinguishes `staging` from `decision-grade` mode in the header.
- [ ] TASK-05-03: Add a single orchestration script, recommended as `scripts/python/integration/run_dppa_case_4.py`, that runs the full Case 4 workflow in phase order while preserving separate no-solve, solve, analysis, and report steps.
- [ ] TASK-05-04: Add a final regression file, recommended as `tests/python/integration/test_dppa_case_4_phase_g.py`, for combined-decision and final-summary wiring.
- [ ] TASK-05-05: Update top-level documentation by adding a DPPA case-family overview to `README.md` and a dedicated overview page such as `docs/dppa_cases.md`, explicitly documenting the role, maturity, and canonical outputs of Cases 1-4.
- [ ] TASK-05-06: Regenerate the full validation trail and record the final Case 4 canonical surfaces, report status, and data-fidelity status in the human-facing documentation.

**Files / Surfaces**
- `scripts/python/integration/run_dppa_case_4.py` - End-to-end Case 4 execution surface.
- `scripts/python/integration/generate_dppa_case_4_final_report.py` - Final Case 4 report generator with gating logic.
- `tests/python/integration/test_dppa_case_4_phase_g.py` - Regression coverage for combined-decision and final-summary artifacts.
- `README.md` - Top-level DPPA case-family overview and canonical links.
- `docs/dppa_cases.md` - Durable documentation for purpose, maturity, and known limitations across Cases 1-4.
- `reports/` - Final Case 4 stakeholder-facing markdown or HTML report.

**Dependencies**
- PHASE-04

**Exit Criteria**
- [ ] A Case 4 final summary exists and the final report is generated only from validated combined artifacts.
- [ ] `README.md` and repo docs explain the role and current status of Cases 1-4, reducing reliance on `activeContext.md` for core understanding.

**Phase Risks**
- **RISK-05-01:** Report polish can again outrun analytical truth; mitigate by making report generation depend on explicit artifact validation and by labeling outputs `staging` when data-fidelity gates are not met.

## Verification Strategy
- **TEST-001:** Run `.venv\Scripts\python.exe -m pytest tests/python/integration/test_dppa_case_4_phase_ab.py tests/python/integration/test_dppa_case_4_phase_c.py tests/python/integration/test_dppa_case_4_phase_d.py tests/python/integration/test_dppa_case_4_phase_e.py tests/python/integration/test_dppa_case_4_phase_f.py tests/python/integration/test_dppa_case_4_phase_g.py -q` after the full implementation lands.
- **TEST-002:** Run `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --scenario scenarios/case_studies/real_project/<date>_real-project_dppa-case-4_fixed.json --no-solve` before the first solve, then run the full solve command on the same scenario. No bounded lane is in scope for Case 4.
- **TEST-003:** Run `.venv\Scripts\python.exe scripts/python/integration/run_dppa_case_4.py` to regenerate canonical artifacts end to end, then run `.\tests\run_all_tests.ps1` before treating the case as ready for closeout.
- **MANUAL-001:** Manually verify that the controller-vs-optimizer comparison uses the same physical candidate ID, size block, and tariff branch in both artifacts.
- **MANUAL-002:** Manually verify that the `22kV` buyer benchmark includes demand-charge reconciliation and that the side-by-side delta table uses real branch outputs rather than duplicated TOU values.
- **MANUAL-003:** Manually inspect the final report to confirm that no critical metric unexpectedly shows `0`, `null`, or placeholder values when the combined artifact contains a real value.
- **OBS-001:** Emit and inspect validation logs that record `source_quality_block`, artifact schema pass/fail status, and `staging` vs `decision-grade` state before any final report is published.

## Risks and Alternatives
- **RISK-001:** Actual project `8760` load data may remain unavailable long enough to stall the whole workflow; mitigation: allow a clearly labeled `staging` mode with synthesized load data, but block decision-grade closeout until actual or explicitly approved bankable data is available.
- **RISK-002:** Implementing full `22kV` demand-charge reconciliation may prove slower than expected; mitigation: build the demand-charge layer explicitly in post-processing and make the approximation scope visible in artifact metadata and report headers.
- **RISK-003:** A new Case 4 could duplicate logic already living in Case 2 and Case 3; mitigation: factor shared settlement, comparison, and validation helpers into reusable surfaces instead of copying scripts wholesale.
- **RISK-004:** The controller realism screen uses a proxy schedule, not actual project windows; mitigate by recording the proxy limitation explicitly in all controller-gap artifacts and in the `source_quality_block`.
- **ALT-001:** Repair Case 3 instead of planning a new Case 4. This was not chosen as the main path because the user explicitly requested a new Case 4 plan and the retrospective recommends carrying forward the good architecture into a cleaner, more decision-grade workflow rather than expanding a downstream chain already known to be partial or buggy.

## Grill Me
1. **Q-001:** Should `DPPA Case 4` allow a synthesized or scaled `8760` load profile for early staging artifacts, or must the case wait for actual project `8760` data before any implementation starts?
   - **Recommended default:** Allow synthesized/scaled `8760` only for `staging` mode, but forbid `decision-grade` closeout until actual or explicitly approved bankable `8760` data is available.
   - **Why this matters:** It changes whether Phase 2 and Phase 5 include a two-tier fidelity gate or a hard block on all downstream work.
   - **If answered differently:** If actual `8760` is mandatory from day one, Phase 2 becomes primarily a data-acquisition blocker and the rest of the plan should pause until the data exists.

2. **Q-002:** Should the base Case 4 strike anchor move to the real-project `15% below EVN` discount, or should it keep Case 3's `5% below EVN` anchor and only test `15%` as a sensitivity?
   - **Recommended default:** Use `15% below EVN` as the base Case 4 anchor and sweep around it (for example `5%`, `10%`, `15%`, `20%`).
   - **Why this matters:** It determines the default commercial baseline, the expected buyer/developer pass/fail story, and the shape of the strike-sensitivity artifacts.
   - **If answered differently:** If `5%` remains the base anchor, the plan should preserve a direct Case 3 continuity comparison and treat the real-project `15%` discount as a later sensitivity rather than the main base case.

3. **Q-003:** Should Case 4 run only the fixed real-project reference lane, or should it also include a bounded optimization sensitivity lane around `3.2 MWp / 1 MW / 2.2 MWh`?
   - **Recommended default:** Run the fixed reference lane first, then add a narrow bounded sensitivity lane only after the fixed lane is validated.
   - **Why this matters:** It changes Phase 3 scope, the shape of controller comparisons, and whether the case is primarily a feasibility-study replication or an optimization-assisted decision aid.
   - **If answered differently:** If fixed-only is chosen, the plan can simplify Phase 3 and reduce the risk of repeating Case 3's same-problem drift; if bounded-only is chosen, the plan needs stronger same-candidate controls and explicit comparison logic.

4. **Q-004:** Are actual project controller charge/discharge windows available for Case 4, or should the first implementation use a documented proxy schedule?
   - **Recommended default:** Use a documented proxy schedule first if actual windows are not yet available, but require the proxy to be recorded in metadata and reports as a limitation.
   - **Why this matters:** It changes how Phase 2 packages controller inputs and whether Phase 4 can claim a real controller-vs-optimizer comparison or only an approximate realism screen.
   - **If answered differently:** If actual windows are available, Phase 2 and Phase 4 should treat them as canonical source data and tighten the decision-grade interpretation of the controller-gap artifact.

5. **Q-005:** Should Case 4 implementation stay in the current main workspace, or should it be planned as work that first merges or mirrors assets from the `real-project-data` branch?
   - **Recommended default:** Implement Case 4 in the current workspace and mirror only the needed inputs/assumptions from `real-project-data`, so the case family stays discoverable in one canonical place.
   - **Why this matters:** It changes file locations, canonical artifact paths, and whether future contributors must understand cross-branch state to rerun the workflow.
   - **If answered differently:** If Case 4 must live primarily on `real-project-data`, the plan should add an explicit branch-synchronization phase and treat canonical-path management as part of the rollout.

## User Answers
- **Q-001:** Reuse (allow synthesized/scaled 8760 for staging, with fidelity gate before decision-grade closeout).
- **Q-002:** Keep Case 3's 5% below EVN anchor; test 15% as a sensitivity.
- **Q-003:** Run only the fixed real-project reference lane.
- **Q-004:** Documented proxy schedule.
- **Q-005:** Current main workspace.

## Suggested Next Step
Answer the `## Grill Me` questions, then update this plan into a final agreed baseline and begin implementation by freezing the Case 4 definition, source-quality gates, and A/B artifact contracts before writing any new downstream analysis code.
