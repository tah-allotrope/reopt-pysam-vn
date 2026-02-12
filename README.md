# REopt Vietnam Analysis

Techno-economic optimization for cost-optimal Solar, Wind, and Battery systems for buildings and microgrids in Vietnam using [NREL REopt.jl](https://github.com/NREL/REopt.jl).

## Tech Stack

- **Julia 1.10+** with REopt.jl v0.57.0, JuMP, HiGHS
- **Python** scripts for REopt API comparison and data prep
- **Pipeline:** `Scenario(dict)` → `REoptInputs(s)` → `run_reopt(m, inputs)` → results dict

## Project Structure

```
scenarios/          JSON scenario inputs
  colab/            Colab reference scenarios (Retail PV+Storage, Hospital Resilience)
  wind/             Wind+Battery hospital scenario
  tinh/             Vietnam site-specific scenarios
scripts/
  julia/            Julia run scripts
  python/           REopt API reference & utility scripts
notebooks/          Jupyter notebooks (Colab examples, Tinh test)
results/            Optimization outputs (JSON + markdown summaries)
```

## Quick Start

```powershell
# 1. Set API keys (or source NREL_API.env)
$env:NREL_DEVELOPER_API_KEY = "your-key"
$env:NREL_DEVELOPER_EMAIL   = "your-email"

# 2. Run a scenario (with precompilation workaround)
$env:JULIA_PKG_PRECOMPILE_AUTO = "0"
julia --project --compile=min scripts/julia/run_colab_scenarios.jl
```

## Key Scenarios

| Scenario | Input | Description |
|---|---|---|
| **A – Retail PV+Storage** | `scenarios/colab/scenario_a_retail_pv_storage.json` | Grid-tied PV optimization (Kyiv) |
| **B – Hospital Resilience** | `scenarios/colab/scenario_b_hospital_resilience.json` | 48h outage survival with PV+Storage |
| **Wind+Battery Hospital** | `scenarios/wind/wind_battery_hospital.json` | Wind + battery sizing |

## Vietnam-Specific Notes

- US incentive defaults (30% ITC, MACRS) must be **zeroed out** for non-US sites.
- Set `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` manually (AVERT/Cambium are US-only).
- When using `loads_kw`, the `ElectricLoad.year` field is **required**.
- Outage modeling is a soft constraint by default — add `Site.min_resil_time_steps` for hard constraint.

## References

- [REopt.jl GitHub](https://github.com/NREL/REopt.jl)
- [REopt API Docs](https://developer.nrel.gov/docs/energy-optimization/reopt/v2/)
- [DeepWiki – REopt.jl Internals](https://deepwiki.com/NatLabRockies/REopt.jl)
