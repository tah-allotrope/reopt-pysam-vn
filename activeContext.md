# REopt Vietnam Project – Active Context & Progress

## Project Overview
- **Mission:** Julia-based techno-economic optimization for Solar/Wind/Battery mixes using NREL REopt.jl.
- **Repo state:** Includes docs plus `test/pv.json` input and `run_reopt_smoke.jl` smoke-run script.

## Completed Steps
1. **AGENTS.md created** – Project guidelines and environment commands documented.
2. **Julia installation verified** – Julia 1.10.10 installed at `C:\Users\tukum\.julia\juliaup\julia-1.10.10+0.x64.w64.mingw32\bin\julia.exe`.
3. **Dependencies installed** – REopt, JuMP, and HiGHS installed manually by user.
4. **Setup plan drafted** – Prerequisites-only plan saved to `C:\Users\tukum\.windsurf\plans\reopt-setup-plan-c4b217.md`.
5. **NREL API keys set (session)** – Environment variables configured for the smoke run.
6. **Input schema fixes** – Updated `test/pv.json` and `test/pv_storage.json` field names to current REopt schema.
7. **Smoke runs completed** – Both `pv.json` and `pv_storage.json` executed successfully with status `optimal`.
8. **PV results validated** – Confirmed PV size, LCC, annual energy, and year-one bill are present and positive.
9. **Storage results extracted** – Added storage sizing, SOC series, and to-load metrics to output reporting.
10. **Results documented** – Updated `test/test_results.md` with both PV-only and PV+Storage scenarios.
11. **pv_retail.json executed** – Created `run_pv_retail.jl` script, fixed schema keys (`*_pct` format), removed unsupported `ElectricUtility` block, and successfully ran with HiGHS. Results documented in `test/test_results.md`.


## Current Status
- **Julia:** Installed and version-confirmed (1.10.10).
- **Packages:** REopt, JuMP, and HiGHS installed manually.
- **API keys:** Configured in the current session (not yet persisted system-wide).
- **Smoke runs:** Successful for both `pv.json` and `pv_storage.json` using HiGHS.
- **PV-only output:** Status `optimal`, PV size ≈ 3162.38 kW, LCC ≈ 1.068e7, annual energy ≈ 5.63e6 kWh, year-one bill ≈ 1.115e6.
- **PV+Storage output:** Status `optimal`, PV size ≈ 216.67 kW, Storage ≈ 55.88 kW / 78.91 kWh, LCC ≈ 1.240e7, year-one bill ≈ 1.681e6, storage SOC cycles 20-100%.
- **pv_retail.json output:** Status `optimal`, PV size ≈ 63.85 kW, LCC ≈ $273,532, annual energy ≈ 111,746 kWh, year-one bill ≈ $23,912.

## Next Immediate Steps
- Persist NREL API environment variables (system/user scope) if desired.
- Decide whether to keep or remove debug key dumps in `run_reopt_smoke.jl`.
- Swap `test/pv.json` with a real scenario input and rerun.

## Key Commands Verified
- Julia version check: `& "C:\Users\tukum\.julia\juliaup\julia-1.10.10+0.x64.w64.mingw32\bin\julia.exe" --version` → `julia version 1.10.10`

## Notes
- `test/pv.json` field updates: `federal_itc_pct`, `macrs_bonus_pct`, financial `*_pct` keys; removed `ElectricUtility.co2_from_avert` (unsupported).
- `test/pv_retail.json` fixes: Updated Financial keys to `*_pct` format (e.g., `offtaker_tax_pct`, `elec_cost_escalation_pct`), removed unsupported `ElectricUtility` block to resolve constructor errors.
- Smoke-run results (test input): PV size ≈ 3162.38 kW, LCC ≈ 1.068e7, average annual PV energy ≈ 5.63e6 kWh, year-one bill ≈ 1.115e6.
- Plan excludes input file prep and first run per user request; those will be a later phase.
- If GHP analysis is needed later, add `GhpGhx.jl` from GitHub and `using GhpGhx`.
