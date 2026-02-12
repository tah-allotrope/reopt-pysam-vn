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
- **Core Engine:** REopt.jl (v0.57.0, Julia 1.10+)
- **Modeling Layer:** JuMP
- **Solver:** HiGHS (default open-source), with optional Cbc/SCIP/Xpress/CPLEX
- **Solver Limitation:** HiGHS does **not** support indicator constraints — battery degradation (`model_degradation=true`) and flexible HVAC require Xpress or CPLEX.
- **Environment Variables:** `ENV["NREL_DEVELOPER_API_KEY"]` (PVWatts, Wind Toolkit, NSRDB) and `ENV["NREL_DEVELOPER_EMAIL"]` (Cambium emissions data).

### Canonical Workflow (5 steps)
```julia
using REopt, JuMP, HiGHS, JSON

# 1. Parse JSON → Dict
d = JSON.parsefile("scenarios/my_scenario.json")

# 2. Construct validated Scenario struct (applies defaults, creates loads & techs)
s = Scenario(d)

# 3. Build REoptInputs (+ automatic BAUInputs for baseline comparison)
inputs = REoptInputs(s)

# 4. Create solver model
m = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))

# 5a. All-in-one: build + solve + extract results (single model = LCC only)
results = run_reopt(m, inputs)

# 5b. BAU comparison: pass two models for NPV/payback calculation
m1 = Model(optimizer_with_attributes(HiGHS.Optimizer))
m2 = Model(optimizer_with_attributes(HiGHS.Optimizer))
results = run_reopt([m1, m2], inputs)
```

**Key entry points (source files):**
| Function | File | Purpose |
|---|---|---|
| `Scenario(dict)` | `src/core/scenario.jl` | Validate inputs, apply defaults, create tech/load objects |
| `REoptInputs(scenario)` | `src/core/reopt_inputs.jl` | Pre-process into solver-ready matrices |
| `build_reopt!(model, inputs)` | `src/core/reopt.jl:19-87` | Add variables + constraints to JuMP model |
| `run_reopt(model, inputs)` | `src/core/reopt.jl:93-135` | All-in-one: build → optimize → extract results |
| `reopt_results(model, inputs)` | `src/results/results.jl` | Extract results dict from solved model |

### 3a. Scenario Struct Anatomy
The `Scenario` struct (immutable once constructed) aggregates all input components:

**Required:**
- `Settings` — solver tolerances, off-grid flag, time steps per hour
- `Site` — latitude, longitude, land area, min_resil_time_steps
- `ElectricLoad` — `loads_kw` array or `doe_reference_name`

**Optional Core:**
- `Financial` — analysis_years, discount rates, tax rates
- `ElectricTariff` — utility rate (URDB label or custom tiers)
- `ElectricUtility` — outage params, emissions factors, net metering limits

**Technologies (all optional):**
- `PV` — **can be an Array of Dicts** for multiple arrays (rooftop + ground, etc.)
- `Wind`, `Generator`, `CHP`, `SteamTurbine`, `CST`
- `ElectricStorage`, `HotThermalStorage`, `ColdThermalStorage`, `HighTempThermalStorage`
- `Boiler`, `ExistingBoiler`, `ElectricHeater`, `ASHP`, `GHP` (also array), `AbsorptionChiller`, `ExistingChiller`

**Loads (created automatically from input or defaults):**
- `SpaceHeatingLoad`, `DomesticHotWaterLoad`, `ProcessHeatLoad`, `CoolingLoad`, `FlexibleHVAC`

### 3b. Key Decision Variables (JuMP)
When debugging or inspecting the solved model, these are the core variable names:

| Variable | Meaning |
|---|---|
| `dvSize[t]` | Optimal capacity (kW) for tech `t` |
| `dvStorageEnergy[b]` | Storage energy capacity (kWh) for storage type `b` |
| `dvStoragePower[b]` | Storage power capacity (kW) |
| `dvRatedProduction[t,ts]` | Generation output per timestep |
| `dvDischargeFromStorage[b,ts]` | Storage discharge per timestep |
| `dvGridPurchase[ts]` | Grid electricity purchased |
| `dvGridToStorage[ts]` | Grid-to-storage charging |
| `dvProductionToGrid[t,ts]` | Export to grid |
| `dvUnservedLoad[s,tz,ts]` | Unserved load during outage scenario |
| `dvMGsize[t]` | Microgrid capacity for tech (≤ dvSize) |
| `binMGTechUsed[t]` | Binary: tech participates in microgrid |

### 3c. Technology Parameter Interface
All technologies share a common parameter pattern:

**Sizing:** `min_kw`, `max_kw`, `existing_kw`
**Costs:** `installed_cost_per_kw`, `om_cost_per_kw`, `om_cost_per_kwh`
**Cost Curves:** `installed_cost_per_kw` (array) + `tech_sizes_for_cost_curve` (array) for piecewise linear
**Export:** `can_net_meter`, `can_wholesale`, `can_export_beyond_nem_limit`, `can_curtail`

**Incentive fields (US defaults — zero these for Vietnam):**
- `federal_itc_fraction` (default 0.30)
- `federal_rebate_per_kw`, `state_ibi_fraction`, `state_rebate_per_kw`
- `utility_ibi_fraction`, `utility_rebate_per_kw`
- `macrs_option_years` (default 5), `macrs_bonus_fraction` (default 1.0)
- `production_incentive_per_kwh`, `production_incentive_max_benefit`, `production_incentive_years`

**Incentive processing order:** Rebates → ITC (on reduced basis) → IBI (% with caps) → MACRS depreciation (reduced by `macrs_itc_reduction × ITC`) → Bonus depreciation → Tax savings discounted by `owner_discount_rate_fraction`.

### 3d. Results Dictionary Keys
Results are nested dicts with string keys. Key paths:

**Financial:** `results["Financial"]["lcc"]`, `["npv"]`, `["lifecycle_capital_costs"]`, `["initial_capital_costs"]`, `["initial_capital_costs_after_incentives"]`, `["simple_payback_years"]`, `["internal_rate_of_return"]`

**Site-level:** `results["Site"]["annual_onsite_renewable_electricity_kwh"]`, `["onsite_renewable_electricity_fraction_of_elec_load"]`, `["lifecycle_emissions_tonnes_CO2"]`, `["lifecycle_emissions_tonnes_NOx"]`

**Per-technology:** `results["PV"]["size_kw"]`, `results["ElectricStorage"]["size_kw"]` / `["size_kwh"]`, `results["Wind"]["size_kw"]`, `results["Generator"]["size_kw"]`

**BAU comparison:** When two models are passed, BAU results are merged with `_bau` suffix. NPV formula: `npv = lcc_bau - lcc`. Also computes `breakeven_cost_of_emissions_reduction_per_tonne_CO2`.

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

### Solver: HiGHS Indicator Constraint Limitation
HiGHS does **not** support indicator constraints. Features that require them will silently fail or error:
- `ElectricStorage.model_degradation = true` (daily SOH updates)
- `FlexibleHVAC` constraints
- **Fix:** Use Xpress or CPLEX for these features.

### Off-Grid Mode Restrictions
When `Settings.off_grid_flag = true`:
- Only `PV`, `Wind`, `Generator`, `ElectricStorage` are permitted — thermal techs are rejected.
- `can_net_meter`, `can_wholesale`, `can_export_beyond_nem_limit` forced to `false`.
- `can_grid_charge` (storage) forced to `false`.
- `operating_reserve_required_fraction` enforced for PV and Wind.
- Generator and Storage become **required** technologies.

## 6. REopt API Reference
The project also uses Python scripts to call the REopt API for validation and input generation.
- **API Base URL:** `https://developer.nrel.gov/api/reopt/stable`
- **Key Endpoints:**
  - `/job/` — Submit optimization, poll for results
  - `/simulated_load/` — Generate DOE reference building load profiles
  - `/peak_load_outage_times/` — Compute seasonal peak outage start times
- **Scripts:** `scripts/python/run_colab_api_reference.py`, `scripts/python/run_colab_api_reference_b.py`, `scripts/python/run_colab_api_reference_b_doe.py`, `scripts/python/get_scenario_b_outage_times.py`
