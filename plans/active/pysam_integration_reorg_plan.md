# PySAM Integration and Repository Reorganization Plan

> Status: Draft for review - 2026-04-03
> Scope: Planning only for the next implementation phase
> Current repo: `reopt-pysam-vn` (GitHub renamed; local folder rename pending release of file lock)
> Proposed repo: `reopt-pysam-vn`

---

## 1. Why this phase exists

VIDA now needs a developer-side finance layer in addition to the existing buyer-side REopt workflow.

- REopt remains the buyer-side optimization engine for load, tariff, dispatch, and technology sizing.
- PySAM adds the missing developer-side finance stack for PPA pricing, debt service, IRR, and contract-structure modeling.
- The repository should be reorganized now so PySAM can be added without turning the Python layer into an ad hoc collection of scripts.
- The planning files should move to a root-level `plans/` location so future phase reviews are easier to access.

---

## 2. Current-state observations

The current repository is functional, but it is still organized around the original REopt-only scope.

### Current strengths

- Clear split between Julia execution and Python preprocessing.
- Existing `scripts/python/`, `tests/python/`, and `src/python/reopt_pysam_vn/reopt/preprocess.py` already give PySAM a natural Python-side entry point.
- Documentation and testing are already phase-based and disciplined.

### Current constraints for PySAM integration

- The Python code is not yet organized as a package with explicit REopt and future PySAM subdomains.
- `requirements.txt` does not yet include PySAM.
- Repository naming, README copy, and some metadata still describe a REopt-only project.
- Planning documents currently live under `plans/archive/`, which makes them less visible than they should be for active iteration.

---

## 3. Phase goals

This next phase should accomplish four things in order:

1. Rename the project from `reopt-julia-VNanalysis` to `reopt-pysam-vn` locally and on GitHub.
2. Reorganize the repository so REopt and PySAM can coexist cleanly in the Python layer.
3. Move planning artifacts to a root-level `plans/` home and define an archive convention for older plans.
4. Create the foundation for PySAM-based developer PPA modeling without changing upstream REopt or PySAM internals.

### Non-goals for this phase

- Do not replace the Julia REopt flow.
- Do not fork or modify upstream PySAM or SAM logic.
- Do not build a full Pexapark clone in one pass.
- Do not rewrite historical results artifacts unless there is a strong operational reason.

---

## 4. Proposed end-state structure

This is the recommended target structure after the reorganization and initial PySAM landing work.

```text
reopt-pysam-vn/
  AGENTS.md
  README.md
  Project.toml
  Manifest.toml
  requirements.txt
  pyproject.toml                # recommended for Python packaging
  plans/
    README.md
    active/
    archive/
  docs/
    architecture.md
    data_and_api.md
    scenarios.md
    testing.md
    pysam.md                    # new
    worklog/
      research/
  data/
  artifacts/
  reports/
  scenarios/
  scripts/
    julia/
    python/
      reopt/
      pysam/
      integration/
  src/
    julia/
      REoptVietnam.jl
    python/
      reopt_pysam_vn/
        __init__.py
        reopt/
          preprocess.py
          tariffs.py
          scenario_builder.py
        pysam/
          config.py
          single_owner.py
          ppa.py
          cashflow.py
          metrics.py
        integration/
          strike_search.py
          bridge.py
          assumptions.py
        common/
          currency.py
          time_series.py
          validation.py
  tests/
    julia/
    python/
      reopt/
      pysam/
      integration/
    cross_language/
```

### Why this structure is recommended

- It preserves the Julia project at the root where `Project.toml` already expects it.
- It keeps Python as one language domain with clear subpackages for `reopt`, `pysam`, and cross-tool `integration` logic.
- It avoids scattering PySAM logic into one-off scripts.
- It makes future packaging, imports, and testing cleaner without breaking the existing Julia-first workflow.

---

## 5. Folder and path migration plan

### Required moves

| Current path | Proposed path | Action | Notes |
|---|---|---|---|
| `plans/archive/` | `plans/archive/` | Move | Historical plans remain accessible but no longer buried under docs |
| new active planning files | `plans/active/` | Create | All future iteration plans should start here |
| `src/julia/REoptVietnam.jl` | `src/julia/REoptVietnam.jl` | Move | Keep Julia code explicit and separate from Python |
| `src/python/reopt_pysam_vn/reopt/preprocess.py` | `src/python/reopt_pysam_vn/reopt/preprocess.py` | Move/refactor | Add compatibility shim during transition |
| `scripts/python/*.py` | `scripts/python/reopt/`, `scripts/python/pysam/`, or `scripts/python/integration/` | Sort | Group scripts by engine and purpose |
| `tests/python/*.py` | `tests/python/reopt/`, `tests/python/pysam/`, `tests/python/integration/` | Sort | Mirror production structure |

### Compatibility strategy

- Add temporary import shims where needed so old script entry points do not all break at once.
- Update README, docs, and test runner references in the same phase as the moves.
- Keep historical report and artifact paths stable unless they directly block the rename or packaging work.

---

## 6. Multi-phase execution roadmap

## Phase 1 - Repository rename and planning-home cleanup

### Objective

Rename the repo and make the planning surface easy to find before deeper code movement starts.

### Tasks

- Rename the local root folder from `reopt-julia-VNanalysis` to `reopt-pysam-vn` once no active process is holding the directory open.
- Rename the GitHub repository to `reopt-pysam-vn`.
- Update the local git remote URL after the GitHub rename.
- Create root-level `plans/` with `active/` and `archive/` subfolders.
- Move existing plan files from `plans/archive/` into `plans/archive/`.
- Add a short pointer note in `docs/worklog/` so older doc links still explain where plans now live.

### Deliverables

- Renamed local repo folder.
- Renamed GitHub repo.
- New root-level planning home.
- Updated plan references in docs.

### Validation

- `git remote -v` points to the renamed GitHub repo.
- `README.md` and `AGENTS.md` reference the new project name.
- Existing archived plan files are visible under `plans/archive/`.

### Risks

- Local automation, screenshots, or generated artifacts may still embed the old repo name.
- GitHub links in historical documents may need selective updates.

---

## Phase 2 - Structural reorganization for a dual-engine repo

### Objective

Make the codebase shape reflect the fact that the project now has two engines: REopt and PySAM.

### Tasks

- Split `src/` into language-aware structure: `src/julia/` and `src/python/`.
- Convert the Python side into an importable package rooted at `src/python/reopt_pysam_vn/`.
- Move existing REopt Python preprocessing logic into the `reopt/` package namespace.
- Re-sort Python scripts into `reopt`, `pysam`, and `integration` folders.
- Re-sort Python tests to mirror the same package boundaries.
- Update imports, path assumptions, and any file readers that rely on the old layout.

### Deliverables

- Clean Python package skeleton.
- Updated script and test layout.
- Import compatibility layer for moved modules.

### Validation

- Existing REopt Python tests still pass after path updates.
- Existing Julia tests still pass after moving `REoptVietnam.jl`.
- Cross-language validation still succeeds.

### Risks

- Path-sensitive scripts may fail if they assume the old `src/python/reopt_pysam_vn/reopt/preprocess.py` location.
- Julia includes may need explicit path updates wherever `REoptVietnam.jl` is loaded.

---

## Phase 3 - Python packaging and dependency foundation

### Objective

Prepare the Python layer to support PySAM as a first-class dependency rather than a one-off addition.

### Tasks

- Add PySAM to Python dependency management after version compatibility testing.
- Introduce `pyproject.toml` for Python packaging and tooling while keeping `requirements.txt` during the transition.
- Define package entry points or lightweight CLI conventions for Python workflows.
- Add a dedicated docs page for Python environment setup, PySAM install notes, and platform caveats.
- Update tests so PySAM-dependent tests can be skipped cleanly when the dependency is unavailable.

### Deliverables

- Python packaging metadata.
- Updated dependency files.
- PySAM install documentation.

### Validation

- Fresh environment setup works from repo root.
- `python -m pytest` can distinguish core tests from PySAM-optional tests.
- A simple PySAM import smoke test passes.

### Risks

- PySAM wheels can be platform-sensitive.
- PySAM version drift can change model defaults between runs if versions are not pinned.

---

## Phase 4 - PySAM MVP for developer-side PPA finance

### Objective

Land the first usable PySAM workflow that turns an existing renewable project assumption set into developer finance outputs.

### Recommended MVP scope

- Start with `Single Owner` only.
- Use solar plus optional storage first.
- Focus on developer-side outputs: project IRR, equity IRR, DSCR, annual revenue, debt service, and cash flow.
- Feed Vietnam-specific assumptions through wrappers rather than hard-coding them into PySAM internals.

### Tasks

- Create a Vietnam PySAM wrapper layer under `src/python/reopt_pysam_vn/pysam/`.
- Define a normalized finance input schema that can be populated from current case-study data.
- Implement a `Single Owner` builder with explicit Vietnam defaults for tax, inflation, debt, and tariff assumptions.
- Add output normalization so PySAM results can be written into canonical JSON artifacts.
- Add unit tests for assumption mapping and output extraction.

### Deliverables

- Initial PySAM wrapper module.
- Canonical JSON output schema for developer finance results.
- First case-study runnable script.

### Validation

- A smoke case runs end-to-end with PySAM and produces repeatable outputs.
- Tests confirm Vietnam defaults are wrapper-driven and non-destructive.

### Risks

- PySAM financial models expose many inputs, so uncontrolled defaults can hide errors.
- Early financial mismatches may come from assumptions rather than code defects.

---

## Phase 5 - REopt plus PySAM bridge for strike-price discovery

### Objective

Connect buyer-side REopt outputs with developer-side PySAM outputs to support contract pricing decisions.

### Core business outcome

Find a strike price where:

- the developer clears a minimum return threshold, and
- the buyer still achieves savings or an acceptable parity condition versus EVN.

### Tasks

- Define a bridge schema between REopt outputs and PySAM finance inputs.
- Implement a pricing search routine that iterates strike price and checks both buyer and developer conditions.
- Add support for pay-as-produced as the first contract structure.
- Persist a combined decision artifact with buyer economics, developer economics, and strike recommendation.
- Add tests for monotonicity and convergence behavior in the strike search.

### Deliverables

- Bridge module.
- Strike-search workflow.
- Combined REopt plus PySAM artifact format.

### Validation

- At least one case study can produce a bounded strike recommendation.
- Search logic is deterministic under fixed assumptions.

### Risks

- If REopt and PySAM use inconsistent annualization, degradation, or escalation assumptions, strike outputs will look plausible but be structurally wrong.

---

## Phase 6 - Contract structures and Vietnam-specific risk layers

### Objective

Expand beyond simple pricing into the first layer of Vietnam DPPA risk analytics.

### Tasks

- Add contract-structure variants: pay-as-produced, baseload proxy, and Vietnam-style CfD or forward contract handling.
- Add sensitivity inputs for curtailment, wheeling fee uncertainty, EVN credit delay, and merchant spill pricing.
- Build scenario comparison outputs that summarize developer return, buyer savings, and key risk deltas.
- Add report-ready JSON structures so later HTML artifacts can visualize the tradeoffs.

### Deliverables

- Contract structure comparison module.
- Vietnam risk sensitivity framework.
- Scenario comparison artifacts.

### Validation

- Each sensitivity can be toggled independently.
- Result deltas are explainable and documented.

### Risks

- Vietnam-specific market rules may evolve before the model stabilizes.
- Too many sensitivities in the first pass can blur the core pricing signal.

---

## Phase 7 - Documentation, regression baselines, and release hardening

### Objective

Make the integrated repo understandable, testable, and maintainable after the structural changes.

### Tasks

- Update `README.md` to describe the two-engine architecture clearly.
- Update architecture, testing, and scenario docs to include PySAM.
- Add a dedicated `docs/pysam.md` page for model scope, assumptions, and known limitations.
- Extend the test runner strategy so PySAM tests have their own lane.
- Add one or more baseline outputs for the first canonical PySAM-enabled case study.
- Add migration notes for users pulling the renamed repository.

### Deliverables

- Updated repo docs.
- New PySAM documentation page.
- Stable baseline test coverage for the integrated path.

### Validation

- A new contributor can set up both Julia and Python environments from the docs.
- REopt-only workflows still run.
- PySAM workflows are discoverable and reproducible.

### Risks

- Documentation drift will become costly after the rename and path changes if not updated in the same pass.

---

## 7. Recommended implementation order inside the codebase

To minimize breakage, the recommended order is:

1. Create `plans/` and relocate plan files.
2. Rename local and GitHub repositories.
3. Update repo-level docs and path references.
4. Introduce Python package skeleton and compatibility shims.
5. Move scripts and tests into engine-specific folders.
6. Add PySAM dependency and smoke test.
7. Build PySAM `Single Owner` MVP.
8. Build REopt plus PySAM strike-search bridge.
9. Add risk layers and richer contract structures.

This order keeps planning, naming, and path changes ahead of the heavier modeling work.

---

## 8. Suggested acceptance criteria for the overall phase

The phase should be considered complete only when all of the following are true:

- The repository is named `reopt-pysam-vn` locally and on GitHub.
- Active plans are stored in a root-level `plans/` location.
- Existing REopt flows still run after the reorganization.
- PySAM installs in the documented Python environment.
- At least one PySAM `Single Owner` case runs end-to-end.
- A combined REopt plus PySAM strike-discovery workflow exists for one canonical case study.
- Documentation explains what remains buyer-side, developer-side, and integration-side.

---

## 9. Open questions for review

These questions are intentionally captured here so they can be reviewed asynchronously instead of interrupting the workflow.

### Q1. Should the Python layer become a proper package now?

- Recommended default: Yes.
- Reason: PySAM integration will be easier to test, import, and maintain if the Python side becomes `src/python/reopt_pysam_vn/` instead of staying script-first.
- Impact if changed: If deferred, PySAM can still be added, but path churn and import cleanup will likely happen twice.

### Q2. Should historical plans be moved or copied into the new `plans/` home?

- Recommended default: Move them into `plans/archive/` and leave a short pointer note in `docs/worklog/`.
- Reason: This satisfies the easier-access requirement while keeping one canonical home.
- Impact if changed: Copying reduces link breakage risk, but creates duplicate sources of truth.

### Q3. Should historical artifacts that contain the old repo name be rewritten?

- Recommended default: No, unless they are live operational inputs.
- Reason: Historical reports and generated artifacts should usually preserve provenance.
- Impact if changed: Rewriting old artifacts increases churn and may muddy historical traceability.

### Q4. Which PySAM finance model should be first?

- Recommended default: `Single Owner` first, then `Partnership Flip`, then `Sale Leaseback` only if required.
- Reason: `Single Owner` is the simplest path to strike-price discovery and early developer IRR checks.
- Impact if changed: Starting with more complex ownership structures will slow the MVP and increase assumption risk.

### Q5. Should the repo rename happen before or after the code moves?

- Recommended default: Before.
- Reason: It reduces duplicate documentation edits and lets the new structure be documented under the final name from the start.
- Impact if changed: If delayed, many path and naming edits will have to be touched twice.

### Q6. Should `requirements.txt` remain the primary Python environment file after PySAM is added?

- Recommended default: Keep `requirements.txt` for install convenience, but add `pyproject.toml` for packaging and test tooling.
- Reason: This is the least disruptive transition path.
- Impact if changed: A pure `pyproject.toml` flow is cleaner long-term, but is a larger environment shift in the same phase.

---

## 10. Immediate next-step recommendation

The cleanest next implementation pass is:

1. finalize the target folder layout and naming decisions in this plan,
2. execute the repository rename plus plan-folder relocation,
3. then start the Python packaging and PySAM MVP in the renamed structure.

That sequence keeps organizational churn ahead of model-building churn.
