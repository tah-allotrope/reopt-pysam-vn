# Generator Exclusion in Vietnam Scenario Templates

**Date:** 2026-03-12
**Mode:** Repo Analysis
**Query:** Is Generator included as an input in the Vietnam scenario templates? If not, how was it disabled? Walk through scenario building, model building, and analysis.

**DeepWiki sources:** Attempted `https://deepwiki.com/NREL/REopt.jl` — page returned loading screen only (not indexed or unavailable). Verified directly against installed package source at `C:/Users/tukum/.julia/packages/REopt/4oSoY/`.

---

## Findings

### 1. Generator Presence Across the Four Templates

| Template | Generator block present? | Technologies |
|---|---|---|
| `vn_commercial_rooftop_pv.json` | **No** | PV only |
| `vn_industrial_pv_storage.json` | **No** | PV + ElectricStorage |
| `vn_hospital_resilience.json` | **No** | PV + ElectricStorage |
| `vn_offgrid_microgrid.json` | **Yes** | PV + Wind + Generator + ElectricStorage |

**Summary:** Generator is intentionally absent from the three grid-tied templates. It only appears in the off-grid microgrid template, where it is structurally required by REopt's `off_grid_flag = true` mode.

---

### 2. How REopt.jl Handles a Missing Generator Block

The exclusion mechanism lives in REopt.jl's `Scenario()` constructor (`scenario.jl`, lines 151–155):

```julia
if haskey(d, "Generator")
    generator = Generator(; dictkeys_tosymbols(d["Generator"])...)
else
    generator = Generator(; max_kw=0)       # <-- this is the key line
end
```

When no `"Generator"` key exists in the input dict, REopt automatically constructs a `Generator` struct with `max_kw=0`. This is a **hard capacity ceiling** — the optimizer can size anywhere from `min_kw=0` to `max_kw=0`, so the only feasible solution is **zero kW**. The generator variable `dvSize["Generator"]` is bounded to `[0, 0]` and the optimizer never installs or dispatches it. It's structurally present in the JuMP model but mathematically removed.

Compare this to the Wind tech, which follows the same pattern (line 148):
```julia
wind = Wind(; max_kw=0)
```

This is the canonical REopt pattern: **absent key → max_kw=0 → tech is silently excluded from sizing**.

The `Generator` struct defaults (from `generator.jl`) that apply when absent:
| Field | Default | Meaning |
|---|---|---|
| `existing_kw` | 0 | No pre-installed generator |
| `min_kw` | 0 | No minimum sizing requirement |
| **`max_kw`** | **set to 0 by Scenario()** | **Capacity ceiling = zero** |
| `only_runs_during_grid_outage` | `true` | If somehow sized, runs only during outages |
| `fuel_avail_gal` | 660.0 | (irrelevant at max_kw=0) |

---

### 3. Preprocessing Layer Behaviour (REoptVietnam.jl / reopt_vietnam.py)

The Vietnam preprocessing module (`apply_vietnam_defaults!` / `apply_vietnam_defaults`) handles Generator consistently with the "only touch what exists" principle.

**In `zero_us_incentives!`:**
```julia
if haskey(d, "Generator")
    _zero_fields!(d["Generator"], GENERATOR_INCENTIVE_FIELDS)
end
```
Incentive zeroing only runs if the `"Generator"` key is present. For the three grid-tied templates, this block is **skipped entirely**.

**In `apply_vietnam_tech_costs!`:**
```julia
if haskey(d, "Generator")
    gen_data = tc["Generator"]
    # inject diesel costs...
end
```
Same pattern — cost injection is gated on `haskey(d, "Generator")`. No cost defaults are written for Generator in grid-tied templates.

The Vietnam tech costs data file (`vn_tech_costs_2025.json`) does have a `"Generator"` section with Vietnam diesel cost parameters:
```json
"Generator": {
  "diesel": {
    "installed_cost_per_kw": 500,
    "om_cost_per_kw": 20,
    "om_cost_per_kwh": 0.01,
    "fuel_cost_per_gallon": 4.50,
    "electric_efficiency_half_load": 0.30,
    "electric_efficiency_full_load": 0.35
  }
}
```
This data is **loaded** by `load_vietnam_data()` and stored in `vn.tech_costs`, but it is **never injected** into grid-tied scenarios because the preprocessing functions check for dict key presence first.

---

### 4. The Off-Grid Exception (`vn_offgrid_microgrid.json`)

The off-grid template explicitly includes `"Generator"` because REopt's `off_grid_flag = true` mode enforces it. From `docs/pitfalls.md`:

> Off-Grid Mode: `Settings.off_grid_flag = true` — only PV/Wind/Generator/ElectricStorage allowed; Generator+Storage required; grid export/charge forced off; operating reserves enforced.

The off-grid template includes:
```json
"Settings": { "off_grid_flag": true },
"Generator": {
    "installed_cost_per_kw": 500,
    "om_cost_per_kw": 20,
    "om_cost_per_kwh": 0.01,
    "fuel_cost_per_gallon": 4.50,
    "electric_efficiency_half_load": 0.30,
    "electric_efficiency_full_load": 0.35
}
```
No `max_kw` is specified here — so REopt uses its default `max_kw=1.0e6`, meaning the optimizer is free to size the generator. The preprocessing layer then injects Vietnam diesel costs via `apply_vietnam_tech_costs!` (since the `"Generator"` key now exists).

---

### 5. End-to-End Walk-Through for a Grid-Tied Template (e.g. `vn_commercial_rooftop_pv.json`)

#### Step 1 — Template Load (user code)
```julia
d = JSON.parsefile("scenarios/templates/vn_commercial_rooftop_pv.json")
delete!(d, "_template")
```
`d` contains: `Site`, `ElectricLoad`, `ElectricTariff`, `Financial`, `PV`, `ElectricUtility`.
**No `"Generator"` key.**

#### Step 2 — Vietnam Preprocessing (`apply_vietnam_defaults!`)
Called with `customer_type="commercial"`, `region="south"`.

Sub-functions run in sequence:
1. `zero_us_incentives!(d)` — zeroes PV incentive fields; `Generator` block absent → skip.
2. `apply_vietnam_financials!(d, vn)` — injects CIT (20%), discount rates, 25-year analysis.
3. `build_vietnam_tariff(...)` → injects 8760 TOU energy rate series into `d["ElectricTariff"]`.
4. `apply_vietnam_emissions!(d, vn)` → sets constant 8760 CO₂ series (1.5013 lb/kWh).
5. `apply_vietnam_tech_costs!(d, vn; region="south")` — updates PV costs; `Generator` absent → skip.
6. `apply_decree57_export!(d, vn)` — sets `net_metering_limit_kw=0`, `wholesale_rate`, PV export flags.

After this step, `d` still has **no `"Generator"` key**.

#### Step 3 — Scenario Construction (`Scenario(d)`)
REopt's `Scenario()` is called. When it processes Generator (line 151–155 of `scenario.jl`):
```julia
# "Generator" key absent → takes the else branch
generator = Generator(; max_kw=0)
```
The `Generator` struct is created with `max_kw=0`. The Scenario struct is fully valid.

#### Step 4 — REoptInputs Construction (`REoptInputs(s)`)
Builds solver matrices. For each technology, REopt checks capacity bounds. Generator has `max_kw=0`, so:
- The sizing variable `dvSize["Generator"]` is bounded `[0, 0]`.
- No generation, dispatch, or fuel constraints are added for Generator (zero-capacity tech is effectively pruned from active constraints).

#### Step 5 — JuMP Model Build (`build_reopt!(model, inputs)`)
HiGHS optimizer receives the LP/MILP. Generator dispatch variable `dvRatedProduction["Generator", ts]` is bounded by `dvSize["Generator"] * max_production_factor` = 0 × anything = 0 for all timesteps.

#### Step 6 — Solve (`run_reopt(...)`)
Optimizer solves. Generator never appears in the optimal solution. Result:
```julia
results["Generator"]["size_kw"]  # => 0.0
```

---

### 6. Why This Design Choice Was Made

The decision to exclude Generator from grid-tied templates is intentional and reflects Vietnam commercial/industrial reality:

1. **Grid-tied = no backup generator optimization needed.** Commercial and industrial buildings in Vietnam connect to the EVN grid and do not typically purchase diesel generators as part of a solar+storage system. The economic case is solar/battery peak-shaving against TOU tariffs.

2. **Hospital resilience uses battery, not generator.** The `vn_hospital_resilience.json` template uses `min_resil_time_steps=4` (4-hour hard outage constraint) satisfied by battery storage alone — no diesel generator. This reflects the preference for cleaner backup over diesel in urban hospital contexts.

3. **Absence = max_kw=0 is the correct REopt idiom.** The REopt library's own
