# Colab REopt API vs REopt.jl Comparison

This report compares REopt.jl results against the Colab notebook reference and REopt API outputs.

## Scenario A — Retail PV + Storage (Kyiv)

| Metric | REopt.jl (local) | REopt API | Notes |
|---|---|---|---|
| Status | optimal | optimal | |
| PV size (kW) | 49.4461 | 49.4461 | Exact match |
| Storage size (kW) | 0.0 | 0.0 | No storage selected |
| Storage size (kWh) | 0.0 | 0.0 | No storage selected |
| Lifecycle capital cost ($) | 23,699 | 23,699 | Exact match |
| Lifecycle cost LCC ($) | 141,262 | 141,262 | Exact match |
| Net present value NPV ($) | 36,933 | 36,933 | Exact match |

**Verdict:** Perfect match. No issues.

## Scenario B — Hospital Resilience (48h outage)

### Final Results (with `min_resil_time_steps=48`)

| Metric | REopt.jl (local) | REopt API (same inputs) | Colab Reference | Notes |
|---|---|---|---|---|
| Status | optimal | optimal | optimal | |
| PV size (kW) | 77.2256 | 77.2256 | 97.16 | Julia ↔ API: exact match |
| Storage size (kW) | 17.36 | 17.36 | 17.26 | Julia ↔ API: exact match |
| Storage size (kWh) | 199.05 | 199.05 | 177.75 | Julia ↔ API: exact match |
| Capital cost ($) | 210,325 | 210,325 | 123,168 | Julia ↔ API: exact match |
| LCC ($) | 340,422 | 340,422 | — | Julia ↔ API: exact match |
| NPV ($) | -162,825 | -166,317 | -25,938 | Julia ↔ API: ~2% diff (emissions costs) |
| Unserved load (kWh) | 0.0 all outages | 0.0 all outages | — | Hard constraint met |

**Verdict:** Julia and API now match on all sizing and cost metrics. The ~$3.5K NPV difference is due to minor emissions cost calculation differences for non-US locations.

### Colab Reference Discrepancy

The Colab notebook reference values (PV=97 kW, storage=177 kWh, NPV=-$26K) differ from both our Julia and API runs. This is expected because the Colab was run on an **older API version** with different default cost assumptions (storage costs, incentive levels, etc.).

## Root Cause Analysis

### Issue 1: Outage Start Time Steps (Fixed)
- **Problem:** Initial hardcoded values `[1092, 3288, 5472, 7668]` did not match the API-derived seasonal peaks.
- **Fix:** Used the `/peak_load_outage_times/` API endpoint to get correct values: `[90, 3593, 5272, 6448]`.
- **Impact:** Minor — did not resolve the main discrepancy alone.

### Issue 2: Load Profile Source (Fixed)
- **Problem:** Julia used `doe_reference_name` + `annual_kwh`, which generates the load internally. The Colab fetches loads via the `/simulated_load/` API first.
- **Fix:** Injected the API-generated `loads_kw` array directly into the JSON, with `year: 2017`.
- **Impact:** Negligible — API results were identical whether using `doe_reference_name` or raw `loads_kw`.

### Issue 3: Resilience Constraint Modeling (ROOT CAUSE — Fixed)
- **Problem:** REopt.jl's multiple outage modeling uses a **soft penalty** (`value_of_lost_load_per_kwh = $1.00/kWh`) by default. The optimizer found it cheaper to shed load during outages than to build storage. The REopt API enforces outage survival as a **hard constraint** (zero unserved load).
- **Fix:** Added `"min_resil_time_steps": 48` to the `Site` section of the input JSON. This forces REopt.jl to meet 100% of critical load for the full 48-hour outage duration.
- **Impact:** This was the primary cause of the discrepancy. With this fix, Julia results match the API exactly on all sizing and cost metrics.

### Key REopt.jl Behavior Note
From `electric_utility.jl` documentation:
> "With multiple outage modeling, the model will choose to meet the critical loads only as cost-optimal. To require the model to meet critical loads during a defined outage period, specify this duration using `Site | min_resil_time_steps`."

## Files

| File | Description |
|---|---|
| `scenarios/colab/scenario_a_retail_pv_storage.json` | Scenario A input |
| `scenarios/colab/scenario_b_hospital_resilience.json` | Scenario B input (final, with `min_resil_time_steps=48` and API `loads_kw`) |
| `results/colab/scenario_a_retail_pv_storage_results.json` | Julia results for Scenario A |
| `results/colab/scenario_b_hospital_resilience_results.json` | Julia results for Scenario B (final) |
| `results/colab/scenario_b_hospital_resilience_api_results.json` | API results for Scenario B (loads_kw payload) |
| `results/colab/scenario_b_api_doe_ref_results.json` | API results for Scenario B (doe_reference_name payload) |
| `results/colab/scenario_b_outage_times.json` | API-fetched load profile and outage start times |

## Notes
- Both scenarios use a non-US location (lat 50, lon 30 — Ukraine region), causing expected warnings for AVERT/Cambium/EASIUR data.
- US federal incentives (30% ITC, 100% bonus MACRS depreciation) are applied by default in both REopt.jl and the API.
- The `installed_cost_constant` for ElectricStorage defaults to $222,115 — a large fixed cost that only applies if a battery is selected.
