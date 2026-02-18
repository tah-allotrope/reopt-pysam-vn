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

## 8. Vietnam Data Layer (`data/vietnam/`)

Versioned JSON files with Vietnam-specific assumptions, loaded by `src/REoptVietnam.jl` (Julia) and `src/reopt_vietnam.py` (Python) **before** `Scenario()`. Manifest-driven: update policy data by creating a new file + changing one line in `manifest.json`.

### Key Vietnam Values
| Parameter | Value | Source |
|---|---|---|
| Grid emission factor | 0.681 tCO2e/MWh (1.50 lb CO2/kWh) | HUST/MONRE 2024 study |
| Avg retail electricity price | VND 2,204/kWh (~$0.084/kWh) | EVN Decision 599/2025 |
| Standard CIT | 20% (10% preferential for RE) | CIT Law 2025 |
| RE tax holiday | 4yr exempt + 9yr 50% reduction | CIT Law 2025 |
| Rooftop solar export cap | 20% of generation to EVN | Decree 57/2025 |
| Surplus purchase rate | VND 671/kWh (~$0.026/kWh) | Decree 57/2025 |
| PV rooftop cost (South) | $600/kW | Market estimate 2025 |
| Battery `installed_cost_constant` | $0 (overrides US $222,115 default) | Vietnam market |

### Data Files
| Manifest Key | File | Update Trigger |
|---|---|---|
| `tariff` | `vn_tariff_2025.json` | New EVN pricing decision (~annual) |
| `tech_costs` | `vn_tech_costs_2025.json` | Market price surveys (~annual) |
| `financials` | `vn_financial_defaults_2025.json` | New CIT law or incentive decree |
| `emissions` | `vn_emissions_2024.json` | Annual MONRE/HUST study (Q1) |
| `export_rules` | `vn_export_rules_decree57.json` | New decree replacing Decree 57 |

### File Schema
Every file has `_meta` (version, effective_date, source, source_url, last_updated, currency) + `data` block. Code reads only `data`; `_meta` is for audit.
