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

### Decree 57 Export Cap (`max_export_fraction`) — Not Enforced
`apply_decree57_export!` / `apply_decree57_export` accept `max_export_fraction=0.20` but do **NOT** enforce it as an optimization constraint. REopt has no native "max % of generation exportable" constraint — enforcement requires custom JuMP constraints (future work). Passing a non-default value emits `@warn` / `UserWarning`. The function does correctly set `can_net_meter=false`, `can_wholesale=true`, and the surplus purchase rate.

### Benchmark Scripts — Non-Vietnam by Design
`scripts/julia/run_colab_scenarios.jl`, `run_scenario_b_only.jl`, `run_wind_battery_hospital.jl` and all `scripts/python/run_colab_api_reference*.py`, `get_scenario_b_outage_times.py` reproduce Colab tutorial results with non-Vietnam coordinates. Do **not** add `apply_vietnam_defaults!` to these scripts.

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

## 9. Preprocessing Modules

Dual Julia/Python modules that apply Vietnam defaults to a REopt input dict **before** `Scenario()` construction.

| Module | Language | Key Function |
|---|---|---|
| `src/REoptVietnam.jl` | Julia | `apply_vietnam_defaults!(dict, vn; customer_type, voltage_level, region)` |
| `src/reopt_vietnam.py` | Python | `apply_vietnam_defaults(dict, vn, customer_type, voltage_level, region)` |

Both modules share the same `data/vietnam/` data files and produce identical output (verified by Layer 3 cross-validation, max diff = 0.00e+00).

**Exported functions (both languages):**
- `load_vietnam_data()` - Load all data files via manifest
- `apply_vietnam_defaults!()` / `apply_vietnam_defaults()` - Full pipeline (tariff + financials + emissions + tech costs + export rules + zero incentives)
- `build_vietnam_tariff()` - Build 8760 TOU energy rate series
- `zero_us_incentives!()` / `zero_us_incentives()` - Zero all US-specific incentive fields
- `apply_vietnam_financials!()` / `apply_vietnam_financials()` - Set CIT, discount rates, analysis years
- `apply_vietnam_emissions!()` / `apply_vietnam_emissions()` - Set constant 8760 emissions series
- `apply_vietnam_tech_costs!()` / `apply_vietnam_tech_costs()` - Set PV/Wind/Battery/Generator costs by region
- `apply_decree57_export!()` / `apply_decree57_export()` - Set export rules per Decree 57
- `convert_vnd_to_usd()` / `convert_usd_to_vnd()` - Currency conversion

**Non-destructive:** User values already present in the dict are never overwritten.

## 10. Scenario Templates (`scenarios/templates/`)

Pre-filled Vietnam scenario templates requiring only Site/Load/sizing overrides.

| Template | Use Case | Technologies | Mode |
|---|---|---|---|
| `vn_commercial_rooftop_pv.json` | Commercial building, HCMC | PV + Storage | Grid-tied, TOU tariff |
| `vn_industrial_pv_storage.json` | Industrial facility, south | PV + Storage | Grid-tied, demand optimization |
| `vn_offgrid_microgrid.json` | Remote site, central | PV + Wind + Generator + Storage | Off-grid |
| `vn_hospital_resilience.json` | Hospital, HCMC | PV + Storage | Grid-tied, 4h outage resilience |

Each template includes a `_template` metadata block (name, description, usage, region, customer_type, voltage_level). Strip `_template` before passing to `Scenario()`.

**Usage pattern:**
```julia
d = JSON.parsefile("scenarios/templates/vn_commercial_rooftop_pv.json")
delete!(d, "_template")
# Override site-specific values
d["Site"]["latitude"] = 10.82
d["ElectricLoad"]["annual_kwh"] = 500_000
# Apply Vietnam defaults (builds TOU tariff series, etc.)
apply_vietnam_defaults!(d, vn; customer_type="commercial", region="south")
s = Scenario(d)
```

## 11. Testing Strategy (4 Layers)

| Layer | What | Speed | Files |
|---|---|---|---|
| **1: Data Validation** | Schema compliance, value bounds for all `data/vietnam/` files | <2s | `tests/julia/test_data_validation.jl`, `tests/python/test_data_validation.py` |
| **2: Unit Tests** | Every exported function, edge cases, error handling, non-destructive merge | <3s | `tests/julia/test_unit.jl`, `tests/python/test_unit.py` |
| **3: Cross-Validation** | Julia vs Python produce identical dicts (tolerance 1e-10) | <5s | `tests/cross_validate.py`, `tests/julia/export_processed_dict.jl` |
| **4: Integration** | Scenario() construction, solver runs, regression baselines, incentive verification | ~30-60s/scenario | `tests/julia/test_integration.jl`, `tests/python/test_integration.py` |

**Baselines:** Stored in `tests/baselines/`. Auto-generated on first run; subsequent runs compare within 5% tolerance. Delete baseline file to regenerate.

## 12. Test Runner

```powershell
# Run all layers (Layers 1-3 fast, Layer 4 slow)
.\tests\run_all_tests.ps1

# Skip solver-dependent tests
.\tests\run_all_tests.ps1 -SkipLayer4

# Layer 4 smoke tests only (Scenario construction, no solver)
.\tests\run_all_tests.ps1 -SmokeOnly

# Run a single layer
.\tests\run_all_tests.ps1 -Layer 2
```

**Julia tests directly:**
```powershell
$env:JULIA_PKG_PRECOMPILE_AUTO="0"
julia --project --compile=min tests/julia/test_unit.jl
julia --project --compile=min tests/julia/test_integration.jl --smoke-only
```

**Python tests directly:**
```powershell
python -m pytest tests/python/test_unit.py -v
python -m pytest tests/python/test_integration.py -v -k smoke
```
