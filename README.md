# REopt Vietnam Analysis

Techno-economic optimization for cost-optimal Solar, Wind, and Battery systems for buildings and microgrids in Vietnam using [NREL REopt.jl](https://github.com/NREL/REopt.jl).

## Tech Stack

- **Julia 1.10+** with REopt.jl v0.56.4, JuMP, HiGHS
- **Python 3.10+** for REopt API, preprocessing mirror, and tests
- **Pipeline:** `Scenario(dict)` → `REoptInputs(s)` → `run_reopt(m, inputs)` → results dict

## Project Structure

```
data/vietnam/           Versioned Vietnam-specific data (tariffs, costs, emissions, export rules)
src/
  REoptVietnam.jl       Julia preprocessing module
  reopt_vietnam.py      Python preprocessing module (mirror)
scenarios/
  templates/            Pre-filled Vietnam scenario templates (4 templates)
  wind/                 Wind+Battery hospital scenario
scripts/
  julia/                Julia run scripts (Vietnam analysis)
results/                Optimization outputs (JSON + markdown summaries)
archive/
  colab/                US-benchmark reference scripts and results (archived)
tests/
  julia/                Julia tests (data validation, unit, integration)
  python/               Python tests (data validation, unit, integration)
  baselines/            Regression baselines (auto-generated)
  run_all_tests.ps1     Master test runner (all 4 layers)
  cross_validate.py     Layer 3: Julia vs Python cross-validation
docs/                   Reference documentation (architecture, data, pitfalls, testing, internals)
```

## Quick Start

```powershell
# 1. Set API keys (or put them in NREL_API.env — see NREL_API.env.example)
$env:NREL_DEVELOPER_API_KEY = "your-key"
$env:NREL_DEVELOPER_EMAIL   = "your-email"

# 2. Validate inputs (no solver — fast)
$env:JULIA_PKG_PRECOMPILE_AUTO = "0"
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --no-solve

# 3. Run full optimization (HiGHS solver, ~60s first run)
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl
```

## Vietnam Preprocessing Tool

The preprocessing tool applies Vietnam-specific defaults to any REopt input dict **before** `Scenario()` construction. Available in both Julia and Python with identical output.

### Usage (Julia)

```julia
include("src/REoptVietnam.jl")
using .REoptVietnam

vn = load_vietnam_data()
d = JSON.parsefile("scenarios/templates/vn_commercial_rooftop_pv.json")
delete!(d, "_template")
apply_vietnam_defaults!(d, vn; customer_type="commercial", region="south")
s = Scenario(d)
```

### Usage (Python)

```python
from src.reopt_vietnam import load_vietnam_data, apply_vietnam_defaults

vn = load_vietnam_data()
d = json.load(open("scenarios/templates/vn_commercial_rooftop_pv.json"))
d.pop("_template", None)
apply_vietnam_defaults(d, vn, customer_type="commercial", region="south")
```

### What it does

- Builds 8760 TOU energy rate series from EVN tariff data
- Zeros all US-specific incentives (ITC, MACRS, rebates)
- Sets Vietnam financial defaults (CIT 20%, discount rates, 25-year analysis)
- Sets grid emissions factor (0.681 tCO2e/MWh constant series)
- Applies PV/Wind/Battery/Generator costs by region (north/central/south)
- Configures Decree 57 export rules (20% cap, surplus purchase rate)
- **Non-destructive:** user values already in the dict are never overwritten

### Vietnam Data Files (`data/vietnam/`)

| File | Contents | Update Trigger |
|---|---|---|
| `vn_tariff_2025.json` | EVN TOU tariff by customer type & voltage | New EVN pricing decision |
| `vn_tech_costs_2025.json` | PV/Wind/Battery/Generator costs by region | Market price surveys |
| `vn_financial_defaults_2025.json` | CIT rates, discount rates, tax holidays | New CIT law or decree |
| `vn_emissions_2024.json` | Grid emission factor (HUST/MONRE study) | Annual MONRE study |
| `vn_export_rules_decree57.json` | Rooftop export cap, surplus rate, DPPA | New decree |

Update policy data by creating a new versioned file and changing one line in `manifest.json`.

## Scenario Templates

Pre-filled Vietnam templates in `scenarios/templates/` — override only Site/Load/sizing:

| Template | Use Case | Technologies |
|---|---|---|
| `vn_commercial_rooftop_pv.json` | Commercial building, HCMC | PV + Storage |
| `vn_industrial_pv_storage.json` | Industrial facility, south | PV + Storage |
| `vn_offgrid_microgrid.json` | Remote site, central | PV + Wind + Generator + Storage |
| `vn_hospital_resilience.json` | Hospital, HCMC (4h outage) | PV + Storage |

## Testing

4-layer test suite with a PowerShell test runner:

```powershell
.\tests\run_all_tests.ps1              # All layers (~15s for L1-3, ~60s+ for L4)
.\tests\run_all_tests.ps1 -SkipLayer4  # Fast: Layers 1-3 only
.\tests\run_all_tests.ps1 -SmokeOnly   # Layer 4 smoke tests (no solver)
.\tests\run_all_tests.ps1 -Layer 2     # Single layer only
```

| Layer | What | Speed |
|---|---|---|
| **1: Data Validation** | Schema compliance, value bounds | <2s |
| **2: Unit Tests** | All exported functions, edge cases | <3s |
| **3: Cross-Validation** | Julia vs Python identical output | <5s |
| **4: Integration** | Scenario construction, solver runs, regression baselines | ~30-60s/scenario |

## Vietnam-Specific Notes

- The preprocessing tool automatically handles all Vietnam overrides: US incentive zeroing, grid emissions, EVN tariff, tech costs, and Decree 57 export rules.
- When using `loads_kw`, the `ElectricLoad.year` field is **required**.
- Outage modeling is a soft constraint by default — add `Site.min_resil_time_steps` for hard constraint.

## References

- [REopt.jl GitHub](https://github.com/NREL/REopt.jl)
- [REopt API Docs](https://developer.nlr.gov/docs/energy-optimization/reopt/v2/)
- [DeepWiki - REopt.jl Internals](https://deepwiki.com/NatLabRockies/REopt.jl)
