# Known Pitfalls & Workarounds

### Outage: Soft vs Hard Constraint
Default outage modeling uses a **soft penalty** (`value_of_lost_load_per_kwh = $1.00/kWh`). **Fix:** Add `"min_resil_time_steps": <hours>` to `Site` for hard constraint.

### Non-US Locations (Vietnam)
AVERT, Cambium, EASIUR lookups will warn. **Fix:** Set `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` manually.

### ElectricLoad.year Required with loads_kw
When using `loads_kw` directly, `"year"` field is **required** (e.g., `"year": 2017`).

### US Incentive Defaults (zero for Vietnam)
- `federal_itc_fraction` (0.30), `macrs_option_years` (5), `macrs_bonus_fraction` (1.0) apply by default.
- `ElectricStorage.installed_cost_constant`: $222,115 fixed cost.
- **Incentive order:** Rebates → ITC → IBI → MACRS → Bonus depreciation → Tax savings.

### Off-Grid Mode
`Settings.off_grid_flag = true`: only PV/Wind/Generator/ElectricStorage allowed; Generator+Storage required; grid export/charge forced off; operating reserves enforced.

### Decree 57 Export Cap (`max_export_fraction`) — Enforcement
`apply_decree57_export!` / `apply_decree57_export` accept `max_export_fraction=0.20` but do **NOT** enforce it as an optimization constraint. REopt has no native "max % of generation exportable" constraint — enforcement requires custom JuMP constraints (future work). Passing a non-default value emits `@warn` / `UserWarning`. The function does correctly set `can_net_meter=false`, `can_wholesale=true`, and the surplus purchase rate.

### L4 API Integration Tests Return HTTP 400
`TestAPIIntegration::test_commercial_rooftop_api_solve` and `test_api_vs_baseline_regression` both fail with `HTTP 400 Bad Request` when submitting the full optimization payload to `/job/`. This is a **pre-existing payload issue**, not caused by the `nrel.gov → nlr.gov` domain migration (connectivity is confirmed working via `test_nlr_domain_connectivity`). Investigation pending — run `python -m pytest tests/python/test_integration.py::TestAPIIntegration::test_nlr_domain_connectivity -v` to confirm the domain itself is healthy.

### Benchmark Scripts — Non-Vietnam by Design
`scripts/julia/run_colab_scenarios.jl`, `run_scenario_b_only.jl`, `run_wind_battery_hospital.jl` and all `scripts/python/run_colab_api_reference*.py`, `get_scenario_b_outage_times.py` reproduce Colab tutorial results with non-Vietnam coordinates. Do **not** add `apply_vietnam_defaults!` to these scripts.