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
12. **wind_battery_hospital.json executed** – Created `run_wind_battery_hospital.jl` and ran BAU comparison with HiGHS. Results saved to `results/wind_battery_hospital_results.json` and summarized in `results/wind_battery_hospital_results.md`.
13. **wind_battery_hospital.json cost alignment** – Added `installed_cost_per_kw: 3137` to `Wind` block to match NREL reference cost assumption. Re-ran scenario: Wind size now ~153.01 kW (matches reference ~153.03 kW), but storage still not selected (0.0 kW vs reference 7.04 kW). LCC improved to ~1.14e6 vs reference ~1.13e6. Remaining gap attributed to storage cost/incentive defaults differing between REopt.jl versions.
14. **Colab comparison plan** – Extracted two scenarios from `notebooks/google_colab_simple_examples.ipynb`: Scenario A (Retail PV+Storage, Kyiv) and Scenario B (Hospital Resilience, 48h outage). Created JSON inputs and `scripts/julia/run_colab_scenarios.jl`.
15. **Scenario A validated** – REopt.jl results match REopt API exactly (PV=49.45 kW, NPV=$36,933). Created `scripts/python/run_colab_api_reference.py` for API comparison.
16. **Scenario B investigation** – Identified major discrepancy: Julia gave PV=36 kW, no storage, NPV=+$27K vs Colab reference PV=97 kW, storage=177 kWh, NPV=-$26K.
17. **Scenario B root cause found** – Three issues identified and fixed:
    - Outage start times: Replaced hardcoded values with API-derived `[90, 3593, 5272, 6448]` via `scripts/python/get_scenario_b_outage_times.py`.
    - Load profile: Injected API-generated `loads_kw` array with `year: 2017`.
    - **Root cause:** REopt.jl uses soft outage penalty ($1/kWh VoLL) vs API hard constraint. Fixed by adding `min_resil_time_steps: 48` to `Site`.
18. **Scenario B reconciled** – With `min_resil_time_steps=48`, Julia matches API exactly: PV=77.23 kW, Storage=17.36 kW / 199.05 kWh, Capital=$210,325. ~2% NPV difference ($-162.8K vs $-166.3K) due to emissions cost calculations at non-US locations. Colab reference differs from both (older API version). Full analysis in `results/colab/comparison_report.md`.
19. **Tinh scenario extracted and run** – Extracted input dict from `notebooks/REopt_Tinh_test.ipynb` (cell 4) into `scenarios/tinh/tinh_pv_storage.json`. Created `scripts/julia/run_tinh_scenario.jl` (two-model BAU+optimal). Results: PV=22.0 kW (roof-constrained), Storage=45.91 kW / 114.38 kWh, LCC=$1,224,115, NPV=-$120,872. Notebook cell outputs are stale (from an earlier Helsinki run at $1,500/kW PV), explaining all discrepancies. Full analysis in `results/tinh/tinh_comparison_report.md`.
20. **REopt Vietnam Tool — Phase 1 (Data Layer) complete** – Created `data/vietnam/` with 5 versioned JSON data files + manifest for Vietnam-specific assumptions. Each file has a `_meta` envelope (`version`, `effective_date`, `source`, `source_url`, `last_updated`, `currency`). Manifest-driven: swap policy data by changing one line in `manifest.json`. Data covers: EVN tariffs (Decision 14/2025, TOU by customer type/voltage), tech costs (PV/Wind/Battery by region), financials (CIT 20%/10% preferential, tax holidays), grid emissions (0.681 tCO2e/MWh = 1.50 lb CO2/kWh), and Decree 57 export rules (20% cap, DPPA ceilings).

## Current Status
- **Julia:** Installed and version-confirmed (1.10.10).
- **Packages:** REopt, JuMP, and HiGHS installed manually.
- **API keys:** Configured via `NREL_API.env` file, loaded at script startup.
- **Colab Scenario A (Retail PV+Storage):** Perfect match between Julia and API. PV=49.45 kW, no storage, NPV=$36,933.
- **Colab Scenario B (Hospital Resilience 48h):** Julia matches API on all sizing/cost metrics after adding `min_resil_time_steps=48`. PV=77.23 kW, Storage=17.36 kW / 199.05 kWh, NPV=-$162,825.
- **Tinh PV+Storage (HCMC, Vietnam):** PV=22.0 kW, Storage=45.91 kW / 114.38 kWh, LCC=$1,224,115, NPV=-$120,872. Notebook outputs stale; script results are correct for current inputs.
- **Vietnam Data Layer:** Phase 1 complete — 5 versioned JSON files + manifest in `data/vietnam/`. Ready for Phase 2 (Julia module).
- **Key learning:** REopt.jl multiple outage modeling is a soft constraint by default; use `Site.min_resil_time_steps` for hard constraint.

## Next Immediate Steps (REopt Vietnam Tool)
- **Phase 2:** Build `src/REoptVietnam.jl` — Julia module with `load_vietnam_data()`, `apply_vietnam_defaults!()`, TOU tariff builder, currency conversion.
- **Phase 3:** Write Layer 1 (data validation) + Layer 2 (unit tests) for Julia.
- **Phase 4:** Build `src/reopt_vietnam.py` — Python mirror sharing same data files.
- **Phase 5:** Python tests + Layer 3 cross-validation (Julia ↔ Python dict equality).
- **Phase 6:** Create 4 scenario templates (commercial rooftop, industrial PV+storage, off-grid microgrid, hospital resilience).
- **Phase 7:** Layer 4 integration/regression tests + baselines.
- **Full plan:** `C:\Users\tukum\.windsurf\plans\reopt-vietnam-tool-9a40df.md`

## Key Commands Verified
- Julia version check: `& "C:\Users\tukum\.julia\juliaup\julia-1.10.10+0.x64.w64.mingw32\bin\julia.exe" --version` → `julia version 1.10.10`
- Julia with precompilation workaround: `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl`

## Colab Comparison Files
| File | Description |
|---|---|
| `notebooks/google_colab_simple_examples.ipynb` | Reference Colab notebook |
| `scenarios/colab/scenario_a_retail_pv_storage.json` | Scenario A input |
| `scenarios/colab/scenario_b_hospital_resilience.json` | Scenario B input (final) |
| `scripts/julia/run_colab_scenarios.jl` | Julia script for both scenarios |
| `scripts/julia/run_scenario_b_only.jl` | Julia script for Scenario B only |
| `scripts/python/run_colab_api_reference.py` | API reference for Scenario A |
| `scripts/python/run_colab_api_reference_b.py` | API reference for Scenario B (loads_kw) |
| `scripts/python/run_colab_api_reference_b_doe.py` | API reference for Scenario B (doe_ref) |
| `scripts/python/get_scenario_b_outage_times.py` | Fetch API load profile + outage times |
| `scripts/python/fix_scenario_b_json.py` | Update Scenario B JSON with API loads |
| `results/colab/comparison_report.md` | Full comparison analysis |

## Tinh Scenario Files
| File | Description |
|---|---|
| `scenarios/tinh/tinh_pv_storage.json` | Input JSON (from notebook cell 4) |
| `scenarios/tinh/Tinh_test_load.csv` | 8760-hour load profile (199 kW peak) |
| `scripts/julia/run_tinh_scenario.jl` | Julia run script (two-model) |
| `results/tinh/tinh_pv_storage_results.json` | Full results JSON |
| `results/tinh/tinh_comparison_report.md` | Comparison report vs notebook |

## Vietnam Data Layer Files
| File | Description |
|---|---|
| `data/vietnam/manifest.json` | Registry pointing to active version of each data file |
| `data/vietnam/vn_tariff_2025.json` | EVN Decision 14/2025 TOU tariff: peak/standard/off-peak hours, rate multipliers by customer type & voltage |
| `data/vietnam/vn_tech_costs_2025.json` | PV/Wind/Battery/Generator costs by region (North/Central/South), all US incentives pre-zeroed |
| `data/vietnam/vn_financial_defaults_2025.json` | CIT 20% standard / 10% RE preferential, tax holiday (4yr exempt + 9yr 50%), discount & escalation rates |
| `data/vietnam/vn_emissions_2024.json` | Grid emission factor 0.681 tCO2e/MWh (1.50 lb CO2/kWh), 2019–2024 historical trend |
| `data/vietnam/vn_export_rules_decree57.json` | Rooftop 20% export cap, surplus rate VND 671/kWh, DPPA ceiling tariffs by tech/region |

## Notes
- `test/pv.json` field updates: `federal_itc_pct`, `macrs_bonus_pct`, financial `*_pct` keys; removed `ElectricUtility.co2_from_avert` (unsupported).
- `test/pv_retail.json` fixes: Updated Financial keys to `*_pct` format, removed unsupported `ElectricUtility` block.
- Wind+Battery hospital results recorded in `results/wind_battery_hospital_results.md`.
- ElectricStorage `installed_cost_constant` defaults to $222,115 — large fixed cost only if battery selected.
- US federal incentives (30% ITC, 100% MACRS bonus) apply by default even for non-US sites.
- Tinh notebook cell outputs are stale (from a Helsinki run with different PV cost); current code inputs produce different results.
- Vietnam data files use `_meta` envelope for versioning/audit; code reads only from `"data"` block. Update policy data by creating new versioned file + changing `manifest.json`.
