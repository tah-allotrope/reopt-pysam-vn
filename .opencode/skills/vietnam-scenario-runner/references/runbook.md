# Vietnam Scenario Runbook

## Purpose

Provide the concrete execution pattern for running or validating Vietnam scenarios in this repository.

## Default Local Workflow

1. Start from a file in `scenarios/templates/` unless the user provided a scenario JSON.
2. Read the template's `_template` block to recover `customer_type`, `voltage_level`, and `region`.
3. Apply only the needed overrides.
4. Remove `_template` before passing the dict into REopt.
5. Expand scalar emissions factor values to an 8760 array when required.
6. Apply Vietnam defaults before `Scenario()` construction.
7. Run `Scenario()` first if the task is validation-oriented.
8. Run the solver only when requested and the scenario is already clean.

## Preferred Julia Commands

Validation only:

```powershell
$env:JULIA_PKG_PRECOMPILE_AUTO="0"
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --no-solve
```

Full solve:

```powershell
$env:JULIA_PKG_PRECOMPILE_AUTO="0"
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl
```

## Existing Julia Happy Path

The repo's default runner lives at `scripts/julia/run_vietnam_scenario.jl` and currently does the following:

1. Load API credentials from `NREL_API.env` if present.
2. Load Vietnam data from `data/vietnam/` through the manifest.
3. Load `scenarios/templates/vn_commercial_rooftop_pv.json`.
4. Remove `_template`.
5. Expand scalar emissions factor values.
6. Apply Vietnam defaults with:
   - `customer_type="commercial"`
   - `voltage_level="medium_voltage_22kv_to_110kv"`
   - `region="south"`
7. Construct `Scenario()`.
8. Optionally run `run_reopt` with HiGHS.
9. Save results to `results/commercial_rooftop_results.json`.

## Safe Override Targets

Most scenario customizations should be limited to:

- `Site.latitude`
- `Site.longitude`
- `ElectricLoad.annual_kwh`
- `ElectricLoad.loads_kw`
- `ElectricLoad.year`
- tech sizing bounds such as `max_kw` or `max_kwh`
- outage parameters in `ElectricUtility`
- resilience settings in `Site`

## Do Not Forget

- Remove `_template` before execution.
- Keep Vietnam preprocessing ahead of `Scenario()` construction.
- Preserve user-provided values; preprocessing is designed to be non-destructive.
- Keep US incentives zeroed.
- Treat `max_export_fraction` as informational unless custom JuMP constraints are added.

## Troubleshooting

### `Scenario()` fails before solve

Check for:

- missing `ElectricLoad.year` when `loads_kw` is used
- invalid block names or leftover `_template`
- malformed emissions field shape
- missing required load or site inputs

### Solve is slow on Julia startup

Cold start can take several minutes. Use `--no-solve` first to separate input-shape issues from solver runtime.

### API run is requested

The repo's documented status is:

- `developer.nlr.gov` connectivity works
- full `/job/` submission currently hits a pre-existing HTTP 400 payload issue

Prefer local Julia execution unless the user explicitly wants API debugging.
