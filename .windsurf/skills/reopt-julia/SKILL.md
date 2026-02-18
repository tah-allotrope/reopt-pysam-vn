---
name: reopt-julia
description: Use this skill to run techno-economic energy optimizations using the REopt.jl Julia package.
---

# REopt.jl Library Reference

> Pitfalls, environment setup, and project rules are in `AGENTS.md`. This file covers **library internals only**.

## Execution Workflow

```julia
using REopt, JuMP, HiGHS, JSON

d = JSON.parsefile("scenarios/FILENAME.json")    # 1. Parse JSON → Dict
d["Financial"]["analysis_years"] = 20            # modify before construction
s = Scenario(d)                                  # 2. Validate + apply defaults
inputs = REoptInputs(s)                          # 3. Solver-ready matrices (+ BAUInputs)

# Mode A: Single model (LCC only)
m = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
results = run_reopt(m, inputs)

# Mode B: BAU comparison (NPV, payback)
m1 = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
m2 = Model(optimizer_with_attributes(HiGHS.Optimizer, "output_flag" => false))
results = run_reopt([m1, m2], inputs)
```

**Entry points:**
| Function | Purpose |
|---|---|
| `Scenario(dict)` | Validate inputs, apply defaults, create tech/load objects |
| `REoptInputs(scenario)` | Pre-process into solver-ready matrices |
| `build_reopt!(model, inputs)` | Add variables + constraints to JuMP model |
| `run_reopt(model, inputs)` | All-in-one: build → optimize → extract results |
| `reopt_results(model, inputs)` | Extract results dict from solved model |

**Solvers:** HiGHS (default, no indicator constraints), Cbc (slower), Xpress/CPLEX (required for `model_degradation=true` and `FlexibleHVAC`).

## Scenario Struct Anatomy

**Required:** `Settings`, `Site`, `ElectricLoad`
**Optional Core:** `Financial`, `ElectricTariff`, `ElectricUtility`
**Technologies (all optional):**
- `PV` — **can be Array of Dicts** for multiple arrays
- `Wind`, `Generator`, `CHP`, `SteamTurbine`, `CST`
- `ElectricStorage`, `HotThermalStorage`, `ColdThermalStorage`, `HighTempThermalStorage`
- `Boiler`, `ExistingBoiler`, `ElectricHeater`, `ASHP`, `GHP` (also array), `AbsorptionChiller`

**Loads (auto-created):** `SpaceHeatingLoad`, `DomesticHotWaterLoad`, `ProcessHeatLoad`, `CoolingLoad`, `FlexibleHVAC`

## Technology Parameters

**Sizing:** `min_kw`, `max_kw`, `existing_kw`
**Costs:** `installed_cost_per_kw`, `om_cost_per_kw`, `om_cost_per_kwh`
**Cost Curves:** `installed_cost_per_kw` (array) + `tech_sizes_for_cost_curve` (array) → piecewise linear
**Export:** `can_net_meter`, `can_wholesale`, `can_export_beyond_nem_limit`, `can_curtail`

**Incentive fields (zero for Vietnam):**
`federal_itc_fraction` (0.30), `federal_rebate_per_kw`, `state_ibi_fraction`, `state_rebate_per_kw`, `utility_ibi_fraction`, `utility_rebate_per_kw`, `macrs_option_years` (5), `macrs_bonus_fraction` (1.0), `production_incentive_per_kwh`, `production_incentive_max_benefit`, `production_incentive_years`

**Processing order:** Rebates → ITC (reduced basis) → IBI (% w/ caps) → MACRS (`macrs_itc_reduction × ITC`) → Bonus depreciation → Tax savings (`owner_discount_rate_fraction`).

## Results Dictionary

**Financial:** `results["Financial"]["lcc"]`, `["npv"]`, `["lifecycle_capital_costs"]`, `["initial_capital_costs_after_incentives"]`, `["simple_payback_years"]`, `["internal_rate_of_return"]`
**Site:** `results["Site"]["annual_onsite_renewable_electricity_kwh"]`, `["onsite_renewable_electricity_fraction_of_elec_load"]`, `["lifecycle_emissions_tonnes_CO2"]`
**Per-tech:** `results["PV"]["size_kw"]`, `results["ElectricStorage"]["size_kw"]` / `["size_kwh"]`, `results["Wind"]["size_kw"]`
**BAU:** `_bau` suffix on BAU results. `npv = lcc_bau - lcc`.

## Key Decision Variables (JuMP)

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
| `binMGTechUsed[t]` | Binary: tech in microgrid |

## Resilience Modeling

**Inputs:** `ElectricUtility.outage_durations` (hours array), `ElectricUtility.outage_start_time_steps` (1-indexed), `Site.min_resil_time_steps` (hard constraint).
**Outage start times:** Use `/peak_load_outage_times/` API endpoint. See `scripts/python/get_scenario_b_outage_times.py`.

## Input Tips
- `loads_kw` requires `"year"` field. `doe_reference_name` does not.
- `"PV"` accepts a single Dict or Array of Dicts (multiple arrays).
- `ElectricStorage.installed_cost_constant` = $222,115 default fixed cost.

## Vietnam Preprocessing Layer

REopt defaults are US-centric. For Vietnam, a preprocessing layer in `data/vietnam/` + `src/REoptVietnam.jl` (Julia) / `src/reopt_vietnam.py` (Python) injects country-specific assumptions **before** `Scenario()` is called.

### Data Layer (`data/vietnam/`)

All Vietnam-specific values live in versioned JSON files with a `_meta` envelope:

```jsonc
{
  "_meta": { "version": "2025.1", "effective_date": "...", "source": "...", "source_url": "...", "last_updated": "..." },
  "data": { ... }  // actual values used by the tool
}
```

**`manifest.json`** points to the active version of each file:

| Manifest Key | Active File | Contents |
|---|---|---|
| `tariff` | `vn_tariff_2025.json` | EVN Decision 14/2025 TOU schedule, rate multipliers by customer type & voltage |
| `tech_costs` | `vn_tech_costs_2025.json` | PV/Wind/Battery/Generator costs by region, all US incentives pre-zeroed |
| `financials` | `vn_financial_defaults_2025.json` | CIT 20%/10% preferential, tax holidays, discount & escalation rates |
| `emissions` | `vn_emissions_2024.json` | Grid emission factor 0.681 tCO2e/MWh → 1.50 lb CO2/kWh |
| `export_rules` | `vn_export_rules_decree57.json` | Rooftop 20% export cap, surplus rate, DPPA ceiling tariffs |

**Update workflow:** Create new versioned file → change one line in `manifest.json` → zero code changes.

### Planned Module Workflow (Phase 2+)

```julia
include("src/REoptVietnam.jl"); using .REoptVietnam
vn = load_vietnam_data()                    # reads manifest → loads active data files
d = JSON.parsefile("my_project.json")
apply_vietnam_defaults!(d, vn, customer_type="industrial", region="south")
results = run_reopt([Model(HiGHS.Optimizer), Model(HiGHS.Optimizer)], d)
```

### What Gets Injected

| Category | What changes |
|---|---|
| **US Incentives** | All zeroed: `federal_itc_fraction=0`, `macrs_option_years=0`, `macrs_bonus_fraction=0`, `installed_cost_constant=0` |
| **Financials** | `offtaker_tax_rate_fraction=0.20`, `offtaker_discount_rate_fraction=0.10`, VN escalation rates |
| **Tariff** | 8760-hour TOU array from EVN Decision 14 (peak/standard/off-peak × weekday/Sunday) |
| **Emissions** | `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` = 1.50 (constant 8760) |
| **Tech Costs** | VN-market PV/Wind/Battery costs by region (North/Central/South) |
| **Export Rules** | Decree 57: `can_net_meter=false`, `can_wholesale=true`, 20% export cap |

## Output
Save results to `results/` folder in JSON format.
