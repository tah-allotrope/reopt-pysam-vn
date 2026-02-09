---
name: reopt-julia
description: Use this skill to run techno-economic energy optimizations using the REopt.jl Julia package.
---

# REopt Julia Optimization

## When to Use
- When the user requires local execution of REopt instead of the web API.
- When specific solvers (Cbc, HiGHS, Xpress) are needed for complex optimizations.
- When performing Business-As-Usual (BAU) comparisons to calculate Net Present Value (NPV).

## Prerequisites
1. **Julia Installed**: The system must have Julia available.
2. **API Key**: Set the NREL Developer API key in the environment: `ENV["NREL_DEVELOPER_API_KEY"] = "YOUR_KEY"`.
3. **Environment Setup**: 
   - Navigate to the script directory.
   - Enter Julia Pkg mode (`]`) and run `activate .` followed by `instantiate`.

## Execution Workflow

### 1. Load and Modify Scenario Data
Scenario files are JSON-based and located in the `scenarios/` directory.
- Use `JSON.parsefile("scenarios/FILENAME.json")` to load data.
- Modify parameters programmatically (e.g., `data["Financial"]["analysis_years"] = 20`).

### 2. Select a Solver
- **Cbc**: Use for general models. Note: May be slower with binary variables.
- **HiGHS**: A high-performance free solver. Recommended for models with BAU cases.
- **Xpress**: Use only if a commercial license is available on the machine.

### 3. Run Optimization
There are two primary modes of execution:

**Mode A: Single Model (No BAU)**
Use this for quick lifecycle cost (LCC) checks.
```julia
m = Model(Cbc.Optimizer)
results = run_reopt(m, data)
```

**Mode B: BAU Comparison**
Use this for detailed BAU analysis and NPV calculations.
```julia
m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)
results = run_reopt([m1, m2], data)
```

### 4. Extract Results
Key metrics to report back to the user:
- **PV Size**: `results["PV"]["size_kw"]`
- **Storage**: `results["ElectricStorage"]["size_kw"]` (Power) and `results["ElectricStorage"]["size_kwh"]` (Capacity).
- **Financials**: `results["Financial"]["lcc"]` (Lifecycle Cost) and `results["Financial"]["npv"]` (Net Present Value).

## Resilience / Outage Modeling
REopt supports evaluating system performance during grid outages.

### Key Inputs
- `ElectricUtility.outage_durations`: Array of outage durations in hours, e.g., `[48]`.
- `ElectricUtility.outage_start_time_steps`: Array of 1-indexed time steps where outages begin.
- `Site.min_resil_time_steps`: Minimum consecutive time steps the system must survive without grid.

### Soft vs Hard Constraint (Critical)
By default, REopt.jl treats multiple outage modeling as a **soft constraint** with `value_of_lost_load_per_kwh = $1.00/kWh`. The optimizer may shed load if it's cheaper than building storage.

To enforce **hard** outage survival (matching REopt API behavior), add:
```json
"Site": { "min_resil_time_steps": 48 }
```

### Generating Outage Start Times
Use the REopt API `/peak_load_outage_times/` endpoint to compute seasonal peak outage start times from a load profile. See `scripts/python/get_scenario_b_outage_times.py` for an example.

## Non-US Locations
For sites outside the contiguous US:
- AVERT, Cambium, and EASIUR data lookups will fail with warnings. This is expected.
- Manually set `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` to a known grid emissions factor (e.g., `1.04` for Ukraine).
- US federal incentives (30% ITC, MACRS) still apply by default — override them if modeling a non-US financial scenario.

## Input Gotchas
- **`ElectricLoad.year` required with `loads_kw`:** When providing a raw `loads_kw` array instead of `doe_reference_name`, you must also set `"year": 2017` (or the appropriate year).
- **`loads_kw` vs `doe_reference_name`:** Both produce identical optimization results. Use `doe_reference_name` for convenience; use `loads_kw` when you have a custom profile.
- **`installed_cost_constant`:** ElectricStorage has a default fixed cost of $222,115 that applies only when a battery is selected. This can dominate small-system economics.

## API Helper Endpoints
These REopt API endpoints are useful for generating Julia inputs:
- **`/simulated_load/`** — Generate DOE reference building load profiles (GET request).
- **`/peak_load_outage_times/`** — Compute seasonal peak outage start times from a load profile (POST request).
- **Base URL:** `https://developer.nrel.gov/api/reopt/stable`

## Troubleshooting
- **Solver Speed**: If Cbc is too slow, switch to `HiGHS`.
- **Precompilation Error**: ArchGDAL causes `Method overwriting` errors. Run with: `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl`
- **Version Issues**: Ensure the package is up to date by running `Pkg.update("REopt")`.
- **Directory Errors**: Always check the working directory with `pwd()` before calling `include()` or loading JSON files.

## Output
Results should be saved to the `results/` folder in JSON format for persistence.
