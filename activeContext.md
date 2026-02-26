# REopt Vietnam Project – Active Context

## Project Overview
- **Mission:** Julia-based techno-economic optimization for Solar/Wind/Battery mixes using NREL REopt.jl.
- **Full project guidelines:** See `AGENTS.md` (sections 1-12).

## Current Status
- **Julia:** 1.10.10, packages REopt v0.56.4 / JuMP / HiGHS installed. Version bounds enforced in `Project.toml [compat]`.
- **API keys:** Configured via `NREL_API.env` (git-ignored). See `NREL_API.env.example` for format.
- **REopt Vietnam Tool:** All 9 implementation steps complete. Full preprocessing pipeline (data + Julia + Python modules), 4 scenario templates, 4-layer test suite (Layers 1-3: 5/5 pass in ~15s), test runner, and documentation.

## Implementation Status (REopt Vietnam Tool)
- Step 1: Data layer — 5 JSON files + manifest (`data/vietnam/`)
- Step 2: Julia module — `src/REoptVietnam.jl`
- Step 3: Julia Layer 1 + Layer 2 tests
- Step 4: Python module — `src/reopt_vietnam.py`
- Step 5: Python Layer 1 + Layer 2 tests + Layer 3 cross-validation
- Step 6: 4 scenario templates in `scenarios/templates/`
- Step 7: Layer 4 integration/regression tests + baselines
- Step 8: Test runner `tests/run_all_tests.ps1`
- Step 9: Documentation updates (AGENTS.md, README.md)

All steps complete.

## Key Learnings & Notes
- REopt.jl multiple-outage modeling is a **soft constraint** by default (`value_of_lost_load_per_kwh = $1.00`). Use `Site.min_resil_time_steps` for hard constraint.
- `ElectricStorage.installed_cost_constant` defaults to **$222,115** — large fixed cost only if battery selected. Vietnam defaults override to $0.
- US federal incentives (30% ITC, 100% MACRS bonus) apply by default even for non-US sites — zeroed by preprocessing.
- Tinh notebook cell outputs are stale (from a Helsinki run with different PV cost); current code inputs produce different results.
- For Tinh workflows, pass `voltage_level` explicitly to preprocessing when reliable site voltage information is available to avoid tariff category assumptions.
- Vietnam data files use `_meta` envelope for versioning/audit; code reads only from `"data"` block. Update policy data by creating new versioned file + changing `manifest.json`.
- Colab benchmark scripts (`scripts/julia/run_colab_scenarios.jl`, `run_scenario_b_only.jl`, `run_wind_battery_hospital.jl` and all `scripts/python/run_colab_api_reference*.py`) reproduce non-Vietnam Colab tutorial results — do **not** add `apply_vietnam_defaults!` to them.

## Reference Tables
- **Vietnam data files & schema:** `AGENTS.md` section 8
- **Preprocessing modules & functions:** `AGENTS.md` section 9
- **Scenario templates:** `AGENTS.md` section 10
- **Testing strategy (4 layers):** `AGENTS.md` section 11
- **Test runner commands:** `AGENTS.md` section 12
- **REopt.jl library internals:** `.windsurf/skills/reopt-julia/SKILL.md`

## Recent Changes (Repo Cleanup — Feb 2026)
- **Security:** Added root `.gitignore`; removed `NREL_API.env` and all `.pyc`/`__pycache__` files from git tracking. Created `NREL_API.env.example` template. API key in git history should be rotated.
- **Documentation consolidation:** Trimmed this file from 129 → ~45 lines (removed build journal, replaced duplicate tables with cross-references). Removed 50-line Vietnam data layer duplication from `SKILL.md` (defers to `AGENTS.md`). Fixed stale "Planned Module Workflow" label in `SKILL.md`. Slimmed `README.md` (removed Colab benchmark table, condensed Vietnam notes).
- **Version correction:** Fixed REopt version in `AGENTS.md` and `README.md` from v0.57.0 → v0.56.4 (actual installed). Added `[compat]` section to `Project.toml`.
- **File cleanup:** Removed superseded `wind_battery_hospital_results.json` (kept corrected version). Moved `test_api_result_sanitization.py` from `scripts/python/` to `tests/python/`. Deleted orphaned smoke tests (`test_module_load.jl`, `test_python_smoke.py`) fully superseded by Layer 2. Fixed stale path in `results/wind/wind_battery_hospital_results.md`.
