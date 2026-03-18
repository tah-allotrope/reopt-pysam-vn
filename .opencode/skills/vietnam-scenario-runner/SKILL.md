---
name: vietnam-scenario-runner
description: This skill should be used when running, validating, or adapting Vietnam REopt scenarios in this repository, especially when starting from `scenarios/templates/`, applying Vietnam defaults, choosing solve versus no-solve mode, and keeping scenario preparation consistent with the existing Julia workflow.
---

# Vietnam Scenario Runner

## Overview

Run Vietnam REopt scenarios in this repository by reusing the project's existing workflow instead of inventing a new one. Start from template metadata when available, normalize the scenario before execution, prefer the Julia runner for local solves, and surface the exact assumptions and overrides used.

## Trigger Conditions

Use this skill when asked to do any of the following in this repository:

- Run a scenario from `scenarios/templates/`
- Validate a scenario without solving
- Adapt a template to a project site, load, or sizing inputs
- Explain which Vietnam template to use
- Save scenario results in a repo-consistent way
- Diagnose why a scenario fails before or during `Scenario()` construction

## Load Supporting Material

Load `references/runbook.md` before running or editing a scenario.

Load `references/templates.md` when selecting a starting template or extracting `_template` metadata.

Use `scripts/template_summary.py <template-path>` when a quick summary of a template's `_template` block is enough and full file reading is unnecessary.

## Follow This Workflow

### 1. Determine the request type

Classify the task into one of these paths:

- `validate-only` - confirm that the scenario builds without running the solver
- `template-run` - run an existing template with minimal overrides
- `template-adapt` - modify a template with project-specific inputs before running
- `custom-json-run` - run a non-template JSON that still needs Vietnam preprocessing

Default to `validate-only` when the user asks for a quick check or when the task is likely to fail on input shape before solve.

### 2. Select the starting scenario

Prefer files in `scenarios/templates/` unless the user already supplied a project JSON.

When a template is used, read or summarize its `_template` block first to recover:

- `customer_type`
- `voltage_level`
- `region`
- usage notes and load caveats

Do not guess those values if the template already declares them.

### 3. Apply only the necessary overrides

Modify only the scenario fields needed for the request. The most common safe overrides are:

- `Site.latitude` and `Site.longitude`
- `ElectricLoad.annual_kwh` or `ElectricLoad.loads_kw`
- `ElectricLoad.year` when `loads_kw` is present
- PV, storage, wind, or generator sizing bounds
- outage settings for resilience scenarios

Preserve the repo's existing Vietnam defaults and non-destructive preprocessing behavior unless the user explicitly asks to override them.

### 4. Normalize the scenario before execution

Before passing the scenario into REopt, perform the same cleanup pattern used by the successful repo workflow:

- Remove `_template` because REopt does not accept it
- Expand scalar `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` to an 8760 array when required by the execution path
- Ensure `ElectricLoad.year` exists when using `loads_kw`

Treat these steps as mandatory preparation, not optional polish.

### 5. Apply Vietnam preprocessing

Run the Vietnam preprocessing layer before `Scenario()` construction.

Prefer the metadata already supplied by the template:

- `customer_type`
- `voltage_level`
- `region`

Use the Julia preprocessing module for local Julia runs and the Python mirror only when the task is explicitly Python-side or API-side.

### 6. Prefer the existing Julia runner

For end-to-end local execution, prefer:

```powershell
$env:JULIA_PKG_PRECOMPILE_AUTO="0"
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --no-solve
```

Remove `--no-solve` only when an actual optimization run is requested and the environment is ready.

Treat `scripts/julia/run_vietnam_scenario.jl` as the default reference implementation for the happy path in this repo.

### 7. Avoid the Python API path unless the task requires it

Use the Python API route only when the user explicitly asks for REopt API submission or when local Julia solve is not the goal.

Remember the known repo status:

- domain connectivity to `developer.nlr.gov` is healthy
- full API job submission currently has a documented pre-existing HTTP 400 payload issue

Do not silently switch from local Julia execution to API submission.

### 8. Report what was run and why

After execution or validation, report:

- starting file used
- overrides applied
- preprocessing parameters used
- whether the task stopped at `Scenario()` validation or reached a solve
- where outputs were saved
- the most relevant warnings or pitfalls encountered

Keep the report concise, but include enough detail for the run to be reproducible.

## Use Repo-Specific Defaults

Anchor decisions in the existing repository behavior:

- Prefer `scripts/julia/run_vietnam_scenario.jl` for local runs
- Prefer templates in `scenarios/templates/` as starting points
- Respect the manifest-driven Vietnam data layer in `data/vietnam/manifest.json`
- Keep the preprocessing non-destructive so user-supplied values win

## Handle Common Pitfalls

Watch for these repo-specific issues during scenario preparation:

- Outage modeling is soft by default; use `Site.min_resil_time_steps` for a hard resilience constraint
- `ElectricLoad.year` is required when `loads_kw` is used directly
- US incentive defaults must remain zeroed for Vietnam scenarios
- Decree 57 `max_export_fraction` is stored for reference and is not enforced as a hard optimization constraint
- Julia cold start can take several minutes; favor `--no-solve` first when diagnosing input issues

Load `references/runbook.md` for the exact commands and troubleshooting details.

## Keep The Skill Lean

Do not duplicate large sections of repo documentation inside the response when the relevant details are already in the support files.

Use the support files as follows:

- Use `references/runbook.md` for execution steps, prerequisites, and troubleshooting
- Use `references/templates.md` for template selection and metadata expectations
- Use `scripts/template_summary.py` to extract `_template` metadata quickly
