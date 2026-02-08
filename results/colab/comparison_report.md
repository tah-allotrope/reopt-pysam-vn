# Colab REopt API vs REopt.jl Comparison

This report compares REopt.jl results against the Colab notebook reference/API outputs.

## Scenario A — Retail PV + Storage (Kyiv)

| Metric | REopt.jl (local) | REopt API (reference) | Notes |
|---|---|---|---|
| Status | optimal | optimal | |
| PV size (kW) | 49.4461 | 49.4461 | Exact match |
| Storage size (kW) | -0.0 | 0.0 | Effectively zero (no storage selected) |
| Storage size (kWh) | -0.0 | 0.0 | Effectively zero (no storage selected) |
| Lifecycle capital cost | 23699.12 | 23699.12 | Exact match |
| Lifecycle cost (LCC) | 141261.52 | 141261.52 | Exact match |
| Net present value (NPV) | 36933.02 | 36933.02 | Exact match |

## Scenario B — Hospital Resilience (48h outage)

| Metric | REopt.jl (local) | Colab reference | Notes |
|---|---|---|---|
| Status | optimal | optimal | |
| PV size (kW) | 36.0466 | 97.16 | **Significant difference** - REopt.jl selects ~37% of Colab PV |
| Storage size (kW) | 1.0 | 17.26 | **Large difference** - REopt.jl selects minimal storage |
| Storage size (kWh) | -0.0 | 177.75 | **Large difference** - REopt.jl essentially no storage |
| Lifecycle capital cost | 17856.79 | 123167.87 | **Major difference** - REopt.jl ~7x lower capital cost |
| Net present value (NPV) | 27439.85 | -25937.56 | **Opposite signs** - REopt.jl shows positive NPV, Colab negative |

## Key Findings

### Scenario A (Retail PV + Storage)
- **Perfect match** between REopt.jl and REopt API results
- All metrics match to the decimal place
- Storage not selected in either implementation (costs don't justify it with $800/kW PV and RetailStore load)

### Scenario B (Hospital Resilience 48h)
- **Major discrepancies** between REopt.jl and Colab reference:
  - PV size: 36 kW vs 97 kW (REopt.jl much smaller)
  - Storage: 1 kW/-0 kWh vs 17 kW/178 kWh (REopt.jl minimal)
  - Capital cost: ~$18K vs ~$123K (REopt.jl much cheaper)
  - NPV: +$27K vs -$26K (opposite conclusions)

## Potential Explanations for Scenario B Differences

1. **Outage start time steps**: Hardcoded values [1092, 3288, 5472, 7668] may differ from Colab's API-computed seasonal peaks
2. **Load profile differences**: The Hospital DOE reference building load may be interpreted differently
3. **Version differences**: REopt.jl version vs. API version (0.56.2) may have different default assumptions
4. **Outage modeling**: The resilience constraints and critical load handling may differ between implementations
5. **Storage cost assumptions**: Default storage costs may differ, affecting the optimal mix

## Notes
- Scenario A reference values from `run_colab_api_reference.py` output (`scenario_a_retail_pv_storage_api_results.json`)
- Scenario B uses hardcoded outage start time steps: 1092, 3288, 5472, 7668
- Both scenarios show expected non-US location warnings (AVERT/Cambium/EASIUR unavailable)
- Scenario B requires further investigation to reconcile with Colab reference
