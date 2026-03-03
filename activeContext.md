# REopt Vietnam Project – Active Context

## Project Overview
- **Mission:** Julia-based techno-economic optimization for Solar/Wind/Battery mixes using NREL REopt.jl.
- **Full project guidelines:** See `AGENTS.md` → `docs/` for detailed reference.

## Current Status
- **Julia:** 1.10.10, REopt v0.56.4 / JuMP / HiGHS. Version bounds in `Project.toml [compat]`.
- **API keys:** Configured via `NREL_API.env` (git-ignored). See `NREL_API.env.example`.
- **API domain:** Migrated from `developer.nrel.gov` → `developer.nlr.gov` (Mar 2026). Old domain expires May 29 2026.
- **REopt Vietnam Tool:** All 9 implementation steps complete. Full preprocessing pipeline, 4 scenario templates, 4-layer test suite, test runner, documentation.

## Implementation Steps (all complete)
1. Data layer — 5 JSON files + manifest (`data/vietnam/`)
2. Julia module — `src/REoptVietnam.jl`
3. Julia Layer 1 + Layer 2 tests
4. Python module — `src/reopt_vietnam.py`
5. Python Layer 1 + Layer 2 tests + Layer 3 cross-validation
6. 4 scenario templates in `scenarios/templates/`
7. Layer 4 integration/regression tests + baselines
8. Test runner `tests/run_all_tests.ps1`
9. Documentation (`AGENTS.md` → `docs/`, `README.md`)

## Test Suite Status (last run: Mar 2026)
| Layer | Result |
|---|---|
| L1 Julia + Python data validation | PASS |
| L2 Julia + Python unit tests | PASS |
| L3 Julia vs Python cross-validation | PASS |
| L4 Template smoke tests (9 tests) | PASS |
| L4 `test_nlr_domain_connectivity` | PASS — new domain confirmed healthy |
| L4 `test_commercial_rooftop_api_solve` | FAIL (pre-existing HTTP 400 — payload issue, not domain) |
| L4 `test_api_vs_baseline_regression` | FAIL (same root cause) |

## Key Learnings & Notes
- REopt.jl outage modeling is a **soft constraint** by default. Use `Site.min_resil_time_steps` for hard constraint.
- `ElectricStorage.installed_cost_constant` defaults to **$222,115** — Vietnam defaults override to $0.
- US federal incentives (30% ITC, 100% MACRS bonus) apply by default even for non-US sites — zeroed by preprocessing.
- Vietnam data files use `_meta` envelope for versioning; code reads only `"data"` block. Update policy data by creating new versioned file + changing `manifest.json`.
- Colab benchmark scripts reproduce non-Vietnam tutorial results — do **not** add `apply_vietnam_defaults!` to them.
- Pass `voltage_level` explicitly to preprocessing when reliable site voltage info is available.

## Reference
- Architecture, pipeline, coding standards → `docs/architecture.md`
- API base URL, data schema, DeepWiki → `docs/data_and_api.md`
- Common errors, workarounds → `docs/pitfalls.md`
- Scenario templates & usage → `docs/scenarios.md`
- Test layers, runner commands, L4 status → `docs/testing.md`
