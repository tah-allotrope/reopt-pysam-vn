# REopt Vietnam Project Context & Guidelines

## 1. Project Overview
> **Mission:** Julia-based techno-economic optimization for cost-optimal energy generation (Solar, Wind, Battery) for buildings and microgrids using NREL REopt.jl.

## 2. Environment & Commands
- **Language:** Julia 1.10+ with REopt.jl v0.57.0
- **Environment:** Always use `julia --project` to activate `reopt-julia-VNanalysis`.
- **API Keys:** `NREL_API.env` file; `ENV["NREL_DEVELOPER_API_KEY"]` (PVWatts, Wind, NSRDB) and `ENV["NREL_DEVELOPER_EMAIL"]` (Cambium emissions).
- **Precompilation Workaround:** `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl`

## 3. Tech Stack
- **Core:** REopt.jl → JuMP → HiGHS (default). Optional: Cbc/SCIP/Xpress/CPLEX.
- **Pipeline:** `Scenario(dict)` → `REoptInputs(s)` → `run_reopt(m, inputs)` → results dict.
- **HiGHS limitation:** No indicator constraints — `model_degradation=true` and `FlexibleHVAC` require Xpress/CPLEX.
- **Library internals** (workflow code, struct anatomy, decision variables, tech params, results keys): see `.windsurf/skills/reopt-julia/SKILL.md`.

## 4. Coding Standards
- Prefer REopt's `handle_errors` patterns and structured warnings/errors via the custom logger.
- Validate at struct construction; enforce bounds, enum membership, and time-series length consistency.

## 5. Known Pitfalls

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

## 6. REopt API Reference
- **Base URL:** `https://developer.nrel.gov/api/reopt/stable`
- **Endpoints:** `/job/` (optimize), `/simulated_load/` (load profiles), `/peak_load_outage_times/` (outage starts)
- **Scripts:** `scripts/python/run_colab_api_reference*.py`, `get_scenario_b_outage_times.py`

## 7. Extended Reference (DeepWiki — fetch on demand)
For deep REopt.jl internals (constraint math, source files, MPC, multi-node), fetch:
→ https://deepwiki.com/NatLabRockies/REopt.jl
Key pages: `/5.1-scenario-construction`, `/5.3-technology-configuration`, `/6.2-model-building-with-build_reopt!`, `/6.3-constraint-system`, `/7-results-and-post-processing`
