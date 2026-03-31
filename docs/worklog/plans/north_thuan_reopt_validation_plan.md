# North Thuan Wind+Solar+BESS — REopt Validation Plan

> **Status:** Updated — 2026-03-30
> **Purpose:** Use REopt locally (Julia + HiGHS) to independently validate the staff's DPPA feasibility study for the North Thuan Wind+Solar+BESS project (Scenario 3). Replaces/augments the pure-Python `validate_north_thuan.py` financial recomputation with an optimisation-based energy dispatch and sizing check.
> **Method:** Local solver via `scripts/julia/run_vietnam_scenario.jl` + `src/REoptVietnam.jl` + HiGHS. **Not the Python API path** — see rationale below.

---

## Why Julia (Local) Over the Python API

| Factor | Julia Local (HiGHS) | Python API (NREL) |
|---|---|---|
| Solver | HiGHS — free, runs offline | NREL cloud — needs API key + internet |
| Known issues | Cold start 3–8 min (one-time) | Pre-existing HTTP 400 payload failures (see `pitfalls.md`) |
| Decree 57 export cap | **Enforced** via custom JuMP constraint in `run_vietnam_reopt([m1,m2], d)` | Not enforced — only stored in `_meta` |
| Wind support | `REoptVietnam.jl` already handles Wind block, cost injection, incentive zeroing | Same via `reopt_vietnam.py` |
| Existing runner | `scripts/julia/run_vietnam_scenario.jl` — drop-in, reads scenario JSON | Need `run_north_thuan_reopt.py` (new) |
| Result format | Identical JSON structure | Identical JSON structure |

**Use local Julia.** The API path was used for Saigon18 as a convenience but has known pre-existing failures. Local Julia gives full solver control and enforces Vietnam-specific constraints properly.

---

## Background

Phase 6 validated the staff PDF using pure Python (`numpy_financial`). It confirmed financial metrics but **never ran an energy dispatch model** — it accepted the staff's 70.05 GWh matched volume as a fixed input. REopt validation will:

1. Independently compute the hourly dispatch of Solar + Wind + BESS against the factory load.
2. Verify the staff's matched volume, self-consumption rate, and RE penetration from first principles.
3. Check whether the staff's BESS sizing (10 MW / 40 MWh) is economically optimal or undersized.
4. Produce a traceable, model-backed comparison report alongside the PDF numbers.

---

## Project Parameters (from `validate_north_thuan.py`)

| Parameter | Value | Source |
|---|---|---|
| Location | North Thuan (Ninh Thuận province) | Staff PDF |
| Lat / Lon (proxy) | 11.55°N, 108.98°E | Ninh Thuận centre — **verify** |
| Solar PV | 30 MW | PDF Scenario 3 |
| Wind | 20 MW | PDF Scenario 3 |
| BESS power | 10 MW | PDF Scenario 3 |
| BESS energy | 40 MWh (4-hr duration) | PDF Scenario 3 |
| Factory annual load | 240.90 GWh/yr | PDF |
| Factory mean demand | 27.5 MW | PDF |
| Factory peak demand | 134.1 MW | PDF |
| Solar CF | 0.194 (lat 11.7°N) | Staff assumption |
| Wind CF | 0.380 (2022 Vietnam Wind Atlas) | Staff assumption |
| DPPA strike price | $0.055/kWh | PDF |
| EVN retail ceiling | $0.07394/kWh | PDF |
| Total CAPEX | $28.50M | PDF |
| Analysis horizon | 25 years | PDF |
| Discount rate | 15% (equity hurdle) | PDF |

---

## Phase 1 — Environment & Data Preparation

**Goal:** Create the North Thuan extracted-inputs JSON that mirrors `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json`.

### 1.1 Check prerequisites

```bash
# Confirm NREL API key is set
echo $NREL_DEVELOPER_API_KEY

# Confirm reopt_vietnam module loads
python -c "from src.reopt_vietnam import load_vietnam_data; print(load_vietnam_data())"
```

### 1.2 Create the North Thuan extracted-inputs JSON

Create `data/interim/north_thuan/north_thuan_extracted_inputs.json` manually from the PDF:

```json
{
  "project": "North Thuan Wind+Solar+BESS DPPA Feasibility (Scenario 3)",
  "data_year": 2025,
  "site": {
    "latitude": 11.55,
    "longitude": 108.98,
    "region": "south",
    "note": "Ninh Thuan province proxy — confirm exact coordinates with developer"
  },
  "loads_kw": "<inject 8760-hour factory load profile here — see 1.3>",
  "assumptions": {
    "solar_mw": 30.0,
    "wind_mw": 20.0,
    "bess_mw": 10.0,
    "bess_mwh": 40.0,
    "solar_cf": 0.194,
    "wind_cf": 0.380,
    "total_capex_usd": 28500000,
    "analysis_years": 25,
    "debt_fraction": 0.70,
    "interest_rate": 0.085,
    "dppa_strike_usd_per_kwh": 0.055,
    "evn_ceiling_usd_per_kwh": 0.07394,
    "factory_annual_load_gwh": 240.90,
    "factory_mean_mw": 27.5,
    "factory_peak_mw": 134.1
  }
}
```

### 1.3 Factory load profile (8760 hours)

REopt requires an 8760-hour hourly load series. Options (best-to-worst):

| Option | How | Quality |
|---|---|---|
| **A — From developer** | Ask for measured hourly interval data from the factory | Best |
| **B — Synthetic from PDF stats** | Scale a flat profile: 27.5 MW mean × 8760 hr → 240.9 GWh. Add diurnal shape (shift peak to 08:00–22:00) | Good enough for dispatch validation |
| **C — REopt flat load** | Pass `annual_kwh` to REopt and let it use its default commercial flat profile | Acceptable for sizing check only |

Create `scripts/python/build_north_thuan_load_profile.py` to produce a synthetic 8760 series from the PDF statistics (mean 27.5 MW, peak 134.1 MW). Use a scaled industrial diurnal template.

### 1.4 Wind production factor series

REopt can fetch wind production from NREL Wind Toolkit automatically using lat/lon. Alternatively, inject an 8760 synthetic CF series derived from the staff's 38% annual CF. For validation parity, **let REopt fetch from NREL** (no `production_factor_series` key in Wind block) so the result is fully independent.

---

## Phase 2 — Build REopt Scenario JSON

**Goal:** Create `scripts/python/build_north_thuan_reopt_input.py` following the same pattern as `build_saigon18_reopt_input.py`.

### Scenarios to build

| Scenario | Description | Purpose |
|---|---|---|
| **NT-A** | Fixed sizing (30 MW Solar + 20 MW Wind + 10/40 BESS), DPPA tariff | Direct mirror of staff PDF — validate matched volume and dispatch |
| **NT-B** | Optimised sizing (unconstrained) | Check whether staff's sizing is economically optimal |
| **NT-C** | Fixed sizing, no BESS | Isolate wind+solar contribution without storage |

### Key REopt input blocks for North Thuan

```python
d = {
    "Site": {
        "latitude": 11.55,
        "longitude": 108.98,
    },
    "ElectricLoad": {
        "loads_kw": loads_8760,   # from Phase 1.3
        "year": 2025,
    },
    "PV": {
        "min_kw": 30_000.0,   # fix at 30 MW for NT-A
        "max_kw": 30_000.0,
        "installed_cost_per_kw": 700.0,   # ~$700/kW typical for VN ground-mount
        "om_cost_per_kw": 8.0,
        "tilt": 11.55,        # latitude-tilt
        "azimuth": 180.0,
        "dc_ac_ratio": 1.2,
        "losses": 0.14,
        # Do NOT inject production_factor_series — let NREL PVWatts compute it
    },
    "Wind": {
        "min_kw": 20_000.0,   # fix at 20 MW for NT-A
        "max_kw": 20_000.0,
        "installed_cost_per_kw": 1_200.0,  # ~$1,200/kW onshore wind VN estimate
        "om_cost_per_kw": 25.0,
        # No production_factor_series — REopt fetches from NREL Wind Toolkit
    },
    "ElectricStorage": {
        "min_kw": 10_000.0,
        "max_kw": 10_000.0,
        "min_kwh": 40_000.0,
        "max_kwh": 40_000.0,
        "installed_cost_per_kw": 200.0,
        "installed_cost_per_kwh": 200.0,
        "installed_cost_constant": 0,
        "soc_min_fraction": 0.10,    # 90% DoD
        "charge_efficiency": 0.95,
        "discharge_efficiency": 0.95,
        "can_grid_charge": False,
    },
    "ElectricTariff": {
        # Use EVN TOU tariff from apply_vietnam_defaults()
        # For DPPA scenario: factory pays strike price for matched volume
        # Approximate: set tou_energy_rates to strike price for all hours
        # that will be matched, EVN retail for unmatched
        # Simplification: use EVN TOU rates — REopt will optimise dispatch
        # against this; matched volume can be read from pv+wind generation
    },
    "Financial": {
        "analysis_years": 25,
        "owner_tax_rate_fraction": 0.10,   # blended CIT with holiday
        "owner_discount_rate_fraction": 0.085,
        "offtaker_discount_rate_fraction": 0.10,
        "elec_cost_escalation_rate_fraction": 0.05,
        "om_cost_escalation_rate_fraction": 0.02,
    },
}

# Apply Vietnam defaults (zero US incentives, EVN TOU tariff, emissions)
apply_vietnam_defaults(d, vn, customer_type="industrial",
                       voltage_level="medium_voltage_22kv_to_110kv",
                       region="south", pv_type="ground",
                       wind_type="onshore",
                       apply_financials=False,
                       apply_tariff=True,
                       apply_emissions=True,
                       apply_tech_costs=False,
                       apply_export_rules=True,
                       apply_zero_incentives=True)
```

### Important note on DPPA tariff modelling

REopt does not natively model a DPPA CfD structure. For validation purposes, model it as:
- **Offtaker tariff = DPPA strike price ($0.055/kWh flat)** for all hours (the factory's effective cost from the developer).
- REopt will then optimise Solar+Wind+BESS dispatch to maximise LCC savings against this flat rate.
- Post-process: extract `PV.year_one_energy_produced_kwh` + `Wind.year_one_energy_produced_kwh` and compute matched volume as `min(total_generation, factory_load)` per hour.

---

## Phase 3 — Run REopt Locally (Julia + HiGHS)

**Goal:** Run each scenario through the existing Julia runner. No new script needed — `scripts/julia/run_vietnam_scenario.jl` already handles this.

```powershell
# First run — cold start takes 3–8 min for Julia precompilation. Subsequent runs: ~30–60s.
# Run from repo root.

# NT-A: fixed sizing, DPPA tariff
$env:JULIA_PKG_PRECOMPILE_AUTO="0"
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
    --scenario scenarios/case_studies/north_thuan/north_thuan_scenario_a.json

# NT-B: optimised sizing
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
    --scenario scenarios/case_studies/north_thuan/north_thuan_scenario_b.json

# NT-C: no BESS baseline
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
    --scenario scenarios/case_studies/north_thuan/north_thuan_scenario_c.json
```

The runner auto-detects the `north_thuan` path and saves results to `artifacts/results/north_thuan/`.

**Validate inputs first (no solver — fast):**
```powershell
julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
    --scenario scenarios/case_studies/north_thuan/north_thuan_scenario_a.json --no-solve
```

**Output files:**
- `artifacts/results/north_thuan/north_thuan_scenario_a_reopt-results.json`
- `artifacts/results/north_thuan/north_thuan_scenario_b_reopt-results.json`
- `artifacts/results/north_thuan/north_thuan_scenario_c_reopt-results.json`

> Note: `run_vietnam_scenario.jl` currently auto-routes to `saigon18` subdir when it detects that path marker. Add a `north_thuan` branch to the path routing logic (lines 156–162 of the script), or set `out_dir` explicitly.

---

## Phase 4 — Extract & Compare Energy Metrics

**Goal:** Parse REopt results and compare against staff PDF claims using the same compare_result() pattern from `validate_north_thuan.py`.

Create `scripts/python/compare_north_thuan_reopt_vs_staff.py`:

### Key REopt result paths to extract

```python
# From results dict (NT-A)
pv_gen_kwh_yr1     = results["PV"]["year_one_energy_produced_kwh"]
wind_gen_kwh_yr1   = results["Wind"]["year_one_energy_produced_kwh"]
bess_to_load_kwh   = results["ElectricStorage"]["year_one_to_load_kwh"]
grid_to_load_kwh   = results["ElectricUtility"]["year_one_energy_supplied_kwh"]

# Compute derived metrics
total_re_gen_kwh   = pv_gen_kwh_yr1 + wind_gen_kwh_yr1
factory_load_kwh   = sum(loads_8760)  # 240,900 MWh = 240,900,000 kWh
re_penetration_pct = total_re_gen_kwh / factory_load_kwh * 100

# Matched volume approximation:
# REopt dispatches RE to load first, then BESS, then grid.
# matched_kwh ≈ total_re_gen_kwh - curtailment - export_to_grid
matched_kwh = (
    results["PV"].get("year_one_to_load_kwh", 0)
    + results["Wind"].get("year_one_to_load_kwh", 0)
    + bess_to_load_kwh
)
self_consumption_pct = matched_kwh / total_re_gen_kwh * 100
```

### Comparison table to produce

| Metric | Staff PDF | REopt NT-A | Delta | Status |
|---|---|---|---|---|
| Solar GWh yr-1 | 51.0 | `pv_gen_kwh_yr1 / 1e6` | % | OK/WARN |
| Wind GWh yr-1 | 66.6 | `wind_gen_kwh_yr1 / 1e6` | % | OK/WARN |
| Total RE GWh yr-1 | 117.56 | computed | % | OK/WARN |
| Matched GWh yr-1 | 70.05 | computed | % | OK/WARN |
| RE penetration % | 48.8% | computed | % | OK/WARN |
| Self-consumption % | 59.6% | computed | % | OK/WARN |
| NPV (LCC saving) | $7.97M (factory) | `Financial.npv_usd` | % | OK/WARN |

Use the same tolerance thresholds: >5% delta = WARN.

---

## Phase 5 — DPPA Settlement Post-Processing

**Goal:** Feed REopt's hourly dispatch into the existing `dppa_settlement.py` module to verify the developer's revenue and compare to staff's financial model.

```python
# Extract hourly dispatch vectors from REopt results
pv_to_load_8760    = results["PV"]["year_one_to_load_series_kw"]
wind_to_load_8760  = results["Wind"]["year_one_to_load_series_kw"]
bess_to_load_8760  = results["ElectricStorage"]["year_one_to_load_series_kw"]
grid_to_load_8760  = results["ElectricUtility"]["year_one_energy_to_load_series_kw"]

# Hourly matched volume = RE served to load (excl. grid)
hourly_matched_kw = [
    pv + wind + bess
    for pv, wind, bess in zip(pv_to_load_8760, wind_to_load_8760, bess_to_load_8760)
]

# Pass to dppa_settlement.py with:
# - strike_price = 0.055 USD/kWh
# - contract_type = "private_wire"
# - fmp_series = FMP annual mean (or hourly if available)
```

Compare the resulting `developer_revenue_yr1_usd` against the staff's $6.0M year-1 revenue claim.

---

## Phase 6 — Generate Comparison Report

**Goal:** Produce a self-contained HTML report (`/report` skill compatible) with side-by-side comparison of REopt vs PDF.

Create `scripts/python/generate_north_thuan_reopt_report.py` following the same pattern as `generate_north_thuan_validation_report.py`. The report should include:

1. **Executive summary** — overall validation verdict (OK / WARN / FAIL counts)
2. **Energy dispatch comparison** — staff vs REopt, table + bar chart
3. **Sizing sensitivity** — NT-B optimised sizing vs NT-A fixed sizing
4. **DPPA revenue check** — REopt dispatch → settlement revenue vs staff $6.0M yr-1
5. **Financial metrics** — NPV, IRR cross-check (REopt LCC NPV vs staff's DCF)
6. **Methodology notes** — how REopt DPPA was approximated, limitations

Output: `artifacts/reports/north_thuan/YYYY-MM-DD_north-thuan-reopt-validation.html`

---

## File Map (all new files to create)

```
data/interim/north_thuan/
  north_thuan_extracted_inputs.json          # Phase 1

scripts/python/
  build_north_thuan_load_profile.py          # Phase 1.3
  build_north_thuan_reopt_input.py           # Phase 2
  run_north_thuan_reopt.py                   # Phase 3
  compare_north_thuan_reopt_vs_staff.py      # Phase 4 + 5
  generate_north_thuan_reopt_report.py       # Phase 6

scenarios/case_studies/north_thuan/
  north_thuan_scenario_a.json               # fixed sizing, DPPA tariff
  north_thuan_scenario_b.json               # optimised sizing
  north_thuan_scenario_c.json               # no BESS baseline

artifacts/results/north_thuan/
  reopt_nt-a_results.json
  reopt_nt-b_results.json
  reopt_nt-c_results.json

artifacts/reports/north_thuan/
  YYYY-MM-DD_north-thuan-reopt-validation.json
  YYYY-MM-DD_north-thuan-reopt-validation.html
```

---

## Known Limitations & Caveats

| Issue | Impact | Mitigation |
|---|---|---|
| REopt has no native DPPA CfD model | Revenue calc is approximate | Post-process with `dppa_settlement.py` as Phase 5 |
| Wind production from NREL Wind Toolkit (US-calibrated) | CF may differ from Vietnam Wind Atlas | Compare NREL CF vs staff's 38% — flag if >5% delta |
| Factory load profile is synthetic | Dispatch timings may not match reality | Use Option A (developer data) if available |
| REopt `Financial` block uses LCC framing, not equity IRR | Can't directly compare equity IRR | Use `equity_irr.py` post-processing as for Saigon18 |
| 25-year REopt runs are slower via API | ~5–10 min per scenario | Run overnight or reduce to 20yr for quick check |

---

## Success Criteria

- [ ] REopt matched volume within ±10% of staff's 70.05 GWh
- [ ] REopt solar/wind GWh within ±10% of staff claims (51.0 / 66.6 GWh)
- [ ] NT-B optimised sizing ≥ or ≤ staff fixed sizing (either result is informative)
- [ ] DPPA developer revenue yr-1 within ±15% of staff's $6.0M
- [ ] HTML report generated and readable standalone
