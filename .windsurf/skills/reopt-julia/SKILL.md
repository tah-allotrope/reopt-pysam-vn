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

### 1. Load and Construct Scenario
Scenario files are JSON-based and located in the `scenarios/` directory.
```julia
using REopt, JuMP, HiGHS, JSON

# Parse JSON → Dict
d = JSON.parsefile("scenarios/FILENAME.json")
# Modify parameters programmatically before constructing Scenario
d["Financial"]["analysis_years"] = 20

# Construct validated Scenario struct (applies defaults, creates loads & techs)
s = Scenario(d)

# Build REoptInputs (+ automatic BAUInputs for baseline comparison)
inputs = REoptInputs(s)
```

**Key entry points:**
| Function | Purpose |
|---|---|
| `Scenario(dict)` | Validate inputs, apply defaults, create tech/load objects |
| `REoptInputs(scenario)` | Pre-process into solver-ready matrices |
| `build_reopt!(model, inputs)` | Add variables + constraints to JuMP model |
| `run_reopt(model, inputs)` | All-in-one: build → optimize → extract results |
| `reopt_results(model, inputs)` | Extract results dict from solved model |

### 2. Select a Solver
- **HiGHS**: High-performance free solver. Recommended default. Does **not** support indicator constraints.
- **Cbc**: Use for general models. May be slower with binary variables.
- **Xpress/CPLEX**: Required for `model_degradation=true` (battery) and `FlexibleHVAC`. Use only if a commercial license is available.

### 3. Run Optimization
There are two primary modes of execution:

**Mode A: Single Model (No BAU)**
Use this for quick lifecycle cost (LCC) checks.
```julia
m = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
results = run_reopt(m, inputs)
```

**Mode B: BAU Comparison**
Use this for detailed BAU analysis and NPV calculations.
```julia
m1 = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
m2 = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
results = run_reopt([m1, m2], inputs)
```

### 4. Extract Results
Results are nested dicts with string keys.

**Key metrics to report:**
- **PV Size**: `results["PV"]["size_kw"]`
- **Wind Size**: `results["Wind"]["size_kw"]`
- **Storage**: `results["ElectricStorage"]["size_kw"]` (Power) and `results["ElectricStorage"]["size_kwh"]` (Capacity).
- **Financials**: `results["Financial"]["lcc"]`, `["npv"]`, `["lifecycle_capital_costs"]`, `["initial_capital_costs"]`, `["initial_capital_costs_after_incentives"]`, `["simple_payback_years"]`, `["internal_rate_of_return"]`
- **Site-level**: `results["Site"]["annual_onsite_renewable_electricity_kwh"]`, `["onsite_renewable_electricity_fraction_of_elec_load"]`, `["lifecycle_emissions_tonnes_CO2"]`
- **BAU comparison**: BAU results merged with `_bau` suffix. NPV formula: `npv = lcc_bau - lcc`.

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

## Scenario Struct Anatomy
The `Scenario` struct (immutable once constructed) aggregates all input components:

**Required:** `Settings`, `Site`, `ElectricLoad`
**Optional Core:** `Financial`, `ElectricTariff`, `ElectricUtility`
**Technologies (all optional):**
- `PV` — **can be an Array of Dicts** for multiple arrays (rooftop + ground)
- `Wind`, `Generator`, `CHP`, `SteamTurbine`, `CST`
- `ElectricStorage`, `HotThermalStorage`, `ColdThermalStorage`, `HighTempThermalStorage`
- `Boiler`, `ExistingBoiler`, `ElectricHeater`, `ASHP`, `GHP` (also array), `AbsorptionChiller`

**Loads (created automatically):** `SpaceHeatingLoad`, `DomesticHotWaterLoad`, `ProcessHeatLoad`, `CoolingLoad`, `FlexibleHVAC`

## Technology Parameter Interface
All technologies share common parameters:
- **Sizing:** `min_kw`, `max_kw`, `existing_kw`
- **Costs:** `installed_cost_per_kw`, `om_cost_per_kw`, `om_cost_per_kwh`
- **Cost Curves:** `installed_cost_per_kw` (array) + `tech_sizes_for_cost_curve` (array) for piecewise linear
- **Export:** `can_net_meter`, `can_wholesale`, `can_export_beyond_nem_limit`, `can_curtail`

**Incentive fields (US defaults — zero these for Vietnam):**
- `federal_itc_fraction` (default 0.30), `federal_rebate_per_kw`
- `state_ibi_fraction`, `state_rebate_per_kw`, `utility_ibi_fraction`, `utility_rebate_per_kw`
- `macrs_option_years` (default 5), `macrs_bonus_fraction` (default 1.0)
- `production_incentive_per_kwh`, `production_incentive_max_benefit`, `production_incentive_years`

**Incentive processing order:** Rebates → ITC (on reduced basis) → IBI (% with caps) → MACRS depreciation (reduced by `macrs_itc_reduction × ITC`) → Bonus depreciation → Tax savings discounted by `owner_discount_rate_fraction`.

## Key Decision Variables (JuMP)
When debugging or inspecting the solved model:

| Variable | Meaning |
|---|---|
| `dvSize[t]` | Optimal capacity (kW) for tech `t` |
| `dvStorageEnergy[b]` | Storage energy capacity (kWh) |
| `dvStoragePower[b]` | Storage power capacity (kW) |
| `dvRatedProduction[t,ts]` | Generation output per timestep |
| `dvDischargeFromStorage[b,ts]` | Storage discharge per timestep |
| `dvGridPurchase[ts]` | Grid electricity purchased |
| `dvProductionToGrid[t,ts]` | Export to grid |
| `dvUnservedLoad[s,tz,ts]` | Unserved load during outage |
| `dvMGsize[t]` | Microgrid capacity (≤ dvSize) |
| `binMGTechUsed[t]` | Binary: tech participates in microgrid |

## Non-US Locations
For sites outside the contiguous US:
- AVERT, Cambium, and EASIUR data lookups will fail with warnings. This is expected.
- Manually set `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` to a known grid emissions factor (e.g., `1.04` for Ukraine).
- US federal incentives (30% ITC, MACRS) still apply by default — zero them for non-US financial scenarios (see Technology Parameter Interface above).
- `ENV["NREL_DEVELOPER_EMAIL"]` is required for Cambium emissions data (separate from API key).

## Input Gotchas
- **`ElectricLoad.year` required with `loads_kw`:** When providing a raw `loads_kw` array instead of `doe_reference_name`, you must also set `"year": 2017` (or the appropriate year).
- **`loads_kw` vs `doe_reference_name`:** Both produce identical optimization results. Use `doe_reference_name` for convenience; use `loads_kw` when you have a custom profile.
- **`installed_cost_constant`:** ElectricStorage has a default fixed cost of $222,115 that applies only when a battery is selected. This can dominate small-system economics.
- **PV as Array:** The `"PV"` key can be a single Dict or an Array of Dicts for multiple PV arrays (e.g., rooftop + ground-mount). This is a common gotcha.

## Off-Grid Mode
When `Settings.off_grid_flag = true`:
- Only `PV`, `Wind`, `Generator`, `ElectricStorage` are permitted — thermal techs are rejected.
- `can_net_meter`, `can_wholesale`, `can_export_beyond_nem_limit` forced to `false`.
- `can_grid_charge` (storage) forced to `false`.
- `operating_reserve_required_fraction` enforced for PV and Wind.
- Generator and Storage become **required** technologies.

## API Helper Endpoints
These REopt API endpoints are useful for generating Julia inputs:
- **`/simulated_load/`** — Generate DOE reference building load profiles (GET request).
- **`/peak_load_outage_times/`** — Compute seasonal peak outage start times from a load profile (POST request).
- **Base URL:** `https://developer.nrel.gov/api/reopt/stable`

## Troubleshooting
- **Solver Speed**: If Cbc is too slow, switch to `HiGHS`.
- **Indicator Constraints**: HiGHS does **not** support indicator constraints. `model_degradation=true` (battery) and `FlexibleHVAC` require Xpress or CPLEX.
- **Precompilation Error**: ArchGDAL causes `Method overwriting` errors. Run with: `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl`
- **Version Issues**: Ensure the package is up to date by running `Pkg.update("REopt")`.
- **Directory Errors**: Always check the working directory with `pwd()` before calling `include()` or loading JSON files.

## Output
Results should be saved to the `results/` folder in JSON format for persistence.
