# Testing Strategy

## 4 Layers

| Layer | What | Speed | Files |
|---|---|---|---|
| **1: Data Validation** | Schema compliance, value bounds for all `data/vietnam/` files | <2s | `tests/julia/test_data_validation.jl`, `tests/python/test_data_validation.py` |
| **2: Unit Tests** | Every exported function, edge cases, error handling, non-destructive merge | <3s | `tests/julia/test_unit.jl`, `tests/python/test_unit.py` |
| **3: Cross-Validation** | Julia vs Python produce identical dicts (tolerance 1e-10) | <5s | `tests/cross_language/cross_validate.py`, `tests/julia/export_processed_dict.jl` |
| **4: Integration** | Scenario() construction, solver runs, regression baselines, incentive verification, API domain connectivity | ~30-60s/scenario | `tests/julia/test_integration.jl`, `tests/python/test_integration.py` |

**Baselines:** Stored in `tests/baselines/`. Auto-generated on first run; subsequent runs compare within 5% tolerance. Delete baseline file to regenerate.

## Test Runner

```powershell
# Run all layers (Layers 1-3 fast, Layer 4 slow)
.\\tests\\run_all_tests.ps1

# Skip solver-dependent tests
.\\tests\\run_all_tests.ps1 -SkipLayer4

# Layer 4 smoke tests only (Scenario construction, no solver)
.\\tests\\run_all_tests.ps1 -SmokeOnly

# Run a single layer
.\\tests\\run_all_tests.ps1 -Layer 2
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

# Run only the API domain connectivity check (fast, ~3s)
python -m pytest tests/python/test_integration.py::TestAPIIntegration::test_nlr_domain_connectivity -v
```

## Known L4 Status (as of 2026-03)

| Test | Status | Notes |
|---|---|---|
| `TestTemplateSmokeTests` (9 tests) | PASS | No API key required |
| `TestAPIIntegration::test_nlr_domain_connectivity` | PASS | Verifies `developer.nlr.gov` reachable; ~3s |
| `TestAPIIntegration::test_commercial_rooftop_api_solve` | FAIL (pre-existing) | HTTP 400 from `/job/` — payload issue, unrelated to domain migration |
| `TestAPIIntegration::test_api_vs_baseline_regression` | FAIL (pre-existing) | Same HTTP 400 root cause |
| `TestJuliaVsAPICrossCheck` | SKIP | Requires local Julia + API key together |
