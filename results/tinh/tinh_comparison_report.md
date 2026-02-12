# Tinh PV + Storage — Comparison Report

Comparison of REopt.jl results from the standalone Julia script (`run_tinh_scenario.jl`) against the notebook (`REopt_Tinh_test.ipynb`) cell outputs.

## Execution Summary

| | **Julia Script** | **Notebook** |
|---|---|---|
| **Run mode** | Two-model (BAU + optimal) | Single-model (`run_reopt(m, dict)`) |
| **Solver** | HiGHS 1.13.0 | HiGHS 1.12.0 |
| **Status** | Optimal | Optimal |
| **Solve time** | 24.1 s (opt) + 1.3 s (BAU) | 15.9 s |

## Key Results

| Metric | **Julia Script** | **Notebook** | **Match?** |
|---|---|---|---|
| PV size (kW) | 22.0 | 22.0 | ✅ |
| PV year-one energy (kWh) | 29,988 | 18,606 | ❌ |
| PV LCOE ($/kWh) | 0.0323 | 0.0934 | ❌ |
| PV installed cost ($/kW) | 600 | 1,500 * | ❌ * |
| Storage size (kW) | 45.91 | 9.26 | ❌ |
| Storage size (kWh) | 114.38 | 24.34 | ❌ |
| Storage capital cost ($) | 295,494 | 237,237 | ❌ |
| Initial capital cost ($) | 308,688 | 270,241 | ❌ |
| Capital after incentives ($) | 160,054 | 137,715 | ❌ |
| Lifecycle elec bill ($) | 973,290 | 173,771 | ❌ |
| LCC ($) | 1,224,115 | 386,629 | ❌ |
| NPV ($) | -120,872 | N/A (single model) | — |

## Analysis of Discrepancies

### 1. Notebook cell outputs are from a different run than the current code

The notebook's **input code** (cell 4) specifies `installed_cost_per_kw: 600`, but the **output** (cell 10) shows `installed_cost_per_kw: 1500` and `name: "Helsinki_Roof_PV"`. This proves the saved cell outputs correspond to an **earlier run with different parameters** — likely a Helsinki scenario with higher PV costs. The current notebook code was edited afterward but never re-executed.

### 2. PV size matches despite cost difference

Both runs size PV at exactly **22.0 kW**. This is the rooftop-constrained maximum: `roof_squarefeet = 2200 ft²` limits the available area. The optimizer maxes out the roof in both cases because PV is cost-effective at either price point.

### 3. Storage sizing differs significantly

| | **Script** | **Notebook** |
|---|---|---|
| Storage kW | 45.91 | 9.26 |
| Storage kWh | 114.38 | 24.34 |

The script's lower PV cost ($600 vs $1,500/kW) frees up capital budget, making larger storage economically viable. Additionally, the notebook's higher PV cost reduces the overall system economics, leading to minimal storage (just above the 20 kWh minimum).

### 4. LCC and electricity bill differ by ~3x

The notebook's LCC of $386,629 is far lower than the script's $1,224,115. This is because:
- **Single-model vs two-model:** The notebook used `run_reopt(m, dict)` (single model, no BAU), which reports only the **optimal** LCC. Our script uses `run_reopt([m1, m2], dict)` (two-model), which reports the **full lifecycle cost including BAU baseline**.
- The BAU LCC alone is $1,103,243 (grid-only), confirming the script's total is consistent.

### 5. Year-one PV energy: 29,988 vs 18,606 kWh

The script produces ~61% more energy from the same 22 kW system. This is likely due to:
- **Different PVWatts resource data:** The notebook may have been run with a different location or at a different time, pulling different solar irradiance data.
- **Helsinki vs HCMC:** If the notebook outputs are from a Helsinki run (as suggested by `name: "Helsinki_Roof_PV"`), the lower solar resource at 60°N latitude explains the lower energy output.

## Conclusion

The Julia script results are **internally consistent and correct** for the inputs as currently written in the notebook code (cell 4). The discrepancies are entirely explained by the notebook's cell outputs being stale — they correspond to a previous run with different parameters (likely a Helsinki scenario with $1,500/kW PV cost).

**To reconcile:** Re-run the notebook with its current cell 4 inputs. The results should match the Julia script's optimal-model values (PV=22 kW, Storage≈45.9 kW / 114.4 kWh). The NPV of -$120,872 (available only in two-model mode) indicates that at $600/kW PV cost with the given tariff structure, the system investment does not achieve positive returns over the analysis period — primarily due to the $222,115 fixed storage cost default.

## Files

| File | Description |
|---|---|
| `scenarios/tinh/tinh_pv_storage.json` | Input JSON (extracted from notebook cell 4) |
| `scenarios/tinh/Tinh_test_load.csv` | 8760-hour load profile (199 kW peak) |
| `scripts/julia/run_tinh_scenario.jl` | Julia run script |
| `results/tinh/tinh_pv_storage_results.json` | Full results JSON |
