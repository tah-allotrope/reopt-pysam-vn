# REopt Vietnam Project Context & Guidelines

## 1. Project Overview
> **Mission:** This is a Julia-based techno-economic optimization application designed to find the cost-optimal mix of energy generation (Solar, Wind, Battery) for buildings and microgrids using the NREL REopt.jl engine.

## 2. Environment & Commands
- **Language:** Julia (follow REopt.jl recommendations; assume modern Julia 1.x) 
- **Environment** When running Julia code or using the terminal, always ensure the project environment reopt-julia-VNanalysis is active (use julia --project for all executions)
- **Run Analysis:** Use Julia with a minimal REopt script
- **API Keys:** NREL Developer API key required in the NREL_API.env file
- **Precompilation Workaround:** ArchGDAL causes a precompilation error. Run Julia with:
  ```
  $env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl
  ```

## 3. Tech Stack & Key Patterns
- **Core Engine:** REopt.jl
- **Modeling Layer:** JuMP
- **Solver:** HiGHS (default open-source), with optional Cbc/SCIP/Xpress/CPLEX
- **Data Structure:** Scenario → REoptInputs → JuMP model → Results 

## 4. Coding Standards (High-Level)
- **Error Handling:** Prefer REopt’s `handle_errors` patterns and structured warnings/errors via the custom logger.
- **Input Validation:** Validate at struct construction; enforce bounds, enum membership, and time-series length consistency.
- **Formatting:** Follow REopt conventions  

## 5. Known Pitfalls

### Resilience: Soft vs Hard Outage Constraint
REopt.jl's multiple outage modeling (`outage_start_time_steps` + `outage_durations`) uses a **soft penalty** by default (`value_of_lost_load_per_kwh = $1.00/kWh`). The optimizer may shed load during outages if it's cheaper than building storage. The REopt API enforces outage survival as a **hard constraint**.
- **Fix:** Add `"min_resil_time_steps": <outage_hours>` to the `Site` section to force 100% critical load survival.

### Non-US Locations
For sites outside the contiguous US (e.g., Vietnam, Ukraine), expect warnings for AVERT, Cambium, and EASIUR data lookups.
- **Fix:** Manually set `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` to a known grid emissions factor.

### ElectricLoad.year Required with loads_kw
When providing `loads_kw` directly (instead of `doe_reference_name`), the field `ElectricLoad.year` is **required** (e.g., `"year": 2017`).

### Default Cost Assumptions
- **ElectricStorage `installed_cost_constant`:** $222,115 fixed cost (only if battery is selected).
- **Federal ITC:** 30% for both PV (`federal_itc_fraction`) and storage (`total_itc_fraction`).
- **MACRS:** 5-year schedule with 100% bonus depreciation by default.
- These US-specific incentives apply by default even for non-US sites.

## 6. REopt API Reference
The project also uses Python scripts to call the REopt API for validation and input generation.
- **API Base URL:** `https://developer.nrel.gov/api/reopt/stable`
- **Key Endpoints:**
  - `/job/` — Submit optimization, poll for results
  - `/simulated_load/` — Generate DOE reference building load profiles
  - `/peak_load_outage_times/` — Compute seasonal peak outage start times
- **Scripts:** `scripts/python/run_colab_api_reference.py`, `scripts/python/run_colab_api_reference_b.py`, `scripts/python/run_colab_api_reference_b_doe.py`, `scripts/python/get_scenario_b_outage_times.py`
