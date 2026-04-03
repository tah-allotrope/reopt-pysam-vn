# Saigon18 Vietnam Solar+BESS — REopt Integration & Validation Plan

> **Status:** Draft — March 2026
> **Author:** Allotrope Partners
> **Repo branch:** `real-project-data`
> **Purpose:** Map the Saigon18 Excel feasibility model onto REopt.jl, identify gaps, define a data pipeline, and produce a comparison report that validates or challenges the Excel outputs.

---

## 1. Project Summary (Saigon18)

The Saigon18 project is a large-scale industrial solar + BESS installation in southern Vietnam.

| Parameter | Value | Source |
|---|---|---|
| Project name | Saigon18 | Excel Dashboard |
| Location | Vietnam (south) | Excel Dashboard |
| COD | 2026-01-01 | Excel Assumption |
| Project lifetime | 20 years | Excel Assumption |
| Solar PV capacity | 40.36 MWp | Excel Assumption row 15 |
| Annual solar yield | 71.8 GWh | Excel Assumption row 18 |
| Specific energy | 1,779 kWh/kWp | Excel Assumption row 19 |
| Performance Ratio | 80.86% | Excel Assumption row 16 |
| GHI | 2,200 kWh/m²/year | Excel Assumption row 10 |
| BESS energy capacity | 66 MWh (200 units × 330 kWh) | Excel Assumption rows 22–25 |
| BESS power capacity | 20 MW (200 units × 100 kW) | Excel Assumption rows 23–26 |
| BESS duration | 3.3 hours | Excel Dashboard |
| BESS DoD | 85% (usable: 56.1 MWh) | Excel Assumption row 27 |
| Round-trip efficiency | 90.25% (95% half-cycle²) | Excel Assumption row 28 |
| BESS degradation | 3.0%/year | Excel Assumption row 29 |
| Factory annual load | 184.3 GWh/year | Excel Financial row 25 |
| Peak load | ~30.2 MW | Excel Data Input row 6 |
| Average load | ~21.0 MW | Excel Data Input row 7 |
| Connection voltage | 110 kV | Excel Assumption row 9 |
| Tariff structure | 1-component EVN (TOU) | Excel Assumption row 10 |
| Exchange rate | 26,000 VND/USD | Excel Assumption row 9 |

**Tariff rates (EVN, current as of model):**

| Period | VND/kWh | USD/MWh |
|---|---|---|
| Standard (normal hours) | 1,811 | ~69.65 |
| Peak | 3,266 | ~125.62 |
| Off-peak | 1,146 | ~44.08 |
| Capacity charge | 0 (1-component) | 0 |

**BESS operating strategy (mode 1 — energy arbitrage):**
- Charge from PV: hours 11–15 daily (solar pre-charge active)
- Discharge at peak: starts at 18:00 (end-of-day discharge)
- Demand reduction target: 20% of baseline peak
- Grid charging: disabled
- Minimum reserve SOC: 215 kWh

**Key financial outputs (Scenario 1 — Bundled Discount, 15% off EVN tariff):**

| Metric | Value |
|---|---|
| Total CAPEX | $49.51M |
| — PV cost | $30.27M (~$750/MWp) |
| — BESS cost | $13.20M (~$200/MWh) |
| — BOP | $4.84M |
| — Land acquisition | $1.20M |
| Year 1 PPA revenue | ~$5.06M |
| Equity IRR | **19.4%** |
| NPV @ 10% discount | **$22.03M** |
| Payback period | **6 years** |
| Unlevered IRR (pre-tax) | 8.95% |
| Unlevered IRR (post-tax) | 8.40% |

**Revenue scenarios modeled in Excel:**

| # | Scenario | Year 1 Revenue | Description |
|---|---|---|---|
| 1 | Bundled DPPA discount | ~$5.06M | 15% discount to EVN retail TOU (active) |
| 2 | Separate PV + BESS discount | ~$5.65M | 5% discount each to EVN TOU |
| 3 | DPPA (grid-connected) | — | Strike VND 1,800/kWh vs FMP settlement |
| 4 | All-in fixed PPA to EVN | — | Fixed $70/MWh for all generation |

---

## 2. REopt Capability Map

This section establishes which aspects of the Saigon18 model REopt can handle natively, which require workarounds, and which must be handled entirely outside REopt.

### 2.1 What REopt Can Model Natively

| Capability | REopt Parameter | Notes |
|---|---|---|
| TOU tariff (EVN 3-period) | `ElectricTariff.energy_rate_series_per_kwh` | `build_vietnam_tariff()` already generates 8760-hour TOU series from `vn_tariff_2025.json` |
| PV generation profile | `PV` block + NREL PVWatts API | Uses lat/lon to pull weather and produce 8760 PV output; or inject `production_factor_series` directly from Excel |
| BESS dispatch optimization | `ElectricStorage` block | REopt optimizes charge/discharge to minimize LCC; TOU arbitrage is the primary driver |
| Self-consumption maximization | Implicit in optimization | Battery charged by PV surplus, discharged to reduce grid imports |
| Grid export (surplus) | `ElectricTariff.wholesale_rate` | Set to Decree 57 surplus rate VND 671/kWh ($0.0254/kWh) |
| Vietnam financial defaults | `Financial` block | 20% CIT, 8% owner discount rate, 4% electricity cost escalation |
| Grid emission factor | `ElectricUtility.emissions_factor_series_lb_CO2_per_kwh` | 0.681 tCO₂e/MWh (1.50 lb CO₂/kWh) from MONRE 2024 |
| LCC (lifecycle cost) | `results["Financial"]["lcc"]` | Core REopt output |
| NPV | `results["Financial"]["npv"]` | Requires two-model BAU comparison run |
| Simple payback | `results["Financial"]["simple_payback_years"]` | Available directly |
| PV sizing bounds | `PV.min_kw`, `PV.max_kw`, `PV.existing_kw` | Fix at 40,360 kW by setting `min_kw = max_kw = 40360` |
| BESS sizing bounds | `ElectricStorage.min_kw/max_kw/min_kwh/max_kwh` | Fix or let optimize; see Phase 2 |
| CAPEX input | `PV.installed_cost_per_kw`, `ElectricStorage.installed_cost_per_kw/kwh` | Use actual project costs |
| O&M escalation | `Financial.om_cost_escalation_rate_fraction` | Set to 0.04 (4%) |
| Analysis period | `Financial.analysis_years` | Override to 20 (from default 25) |

### 2.2 Partial / Workaround Required

| Capability | Gap | Workaround |
|---|---|---|
| **BESS degradation (3%/year)** | REopt uses `battery_replacement_year` (discrete replacement model, not continuous degradation) | Set `battery_replacement_year = 10` with `replace_cost_per_kwh` to approximate mid-life replacement; run separate sensitivity on post-replacement performance |
| **PPA revenue (discount to EVN tariff)** | REopt optimizes against its tariff array — it does not compute PPA revenue as a separate revenue stream | Pre-compute a modified `energy_rate_series_per_kwh` representing the PPA price = EVN tariff × (1 − 15% discount), and pass that as the tariff. REopt's avoided-cost calculation then approximates PPA savings correctly |
| **Decree 57 export cap (20%)** | `apply_decree57_export()` sets `can_wholesale=true` and surplus rate but does NOT enforce the 20% cap as a hard JuMP constraint | Add a custom JuMP constraint `sum(dvProductionToGrid[t,ts] for ts) ≤ 0.20 * sum(dvRatedProduction[t,ts] for ts)` (see Phase 3) |
| **Tax holiday (4yr exempt + 9yr 50% CIT)** | REopt uses a single static `owner_tax_rate_fraction` — no multi-year holiday schedule | Use blended effective rate: (4×0 + 9×0.05 + 7×0.10) / 20 = **0.0575** for a 20-year project (already documented in `vn_financial_defaults_2025.json`) |
| **Fixed BESS charge/discharge windows** | REopt optimizes dispatch freely; it will not respect an externally imposed "charge only 11–15h" constraint | Add custom JuMP constraints (see Phase 3) OR run REopt in unconstrained mode and note the behavioral difference in the comparison report |
| **BESS DoD constraint** | REopt respects `min_soc_fraction` and `max_soc_fraction` | Set `min_soc_fraction = 1 - 0.85 = 0.15` and `max_soc_fraction = 1.0` |
| **Round-trip efficiency** | REopt uses separate charge/discharge efficiency parameters | Set `charge_efficiency = discharge_efficiency = 0.95` (each half-cycle = 95%, consistent with Excel 90.25% round-trip) |
| **20-year project life** | REopt defaults to 25 years | Set `Financial.analysis_years = 20` (override default) |
| **Two-part tariff (capacity charge)** | Saigon18 uses 1-component tariff (no capacity charge today); future pilot uses capacity charge | Set `monthly_demand_rates = [0] * 12` for current model. Create a separate "two-part tariff" scenario for forward-looking runs using the Decree 146/2025 trial rates from `vn_tariff_2025.json` |

### 2.3 Out-of-Scope for REopt (Must Be Handled Outside)

| Feature | Why Not in REopt | External Approach |
|---|---|---|
| **DPPA / CfD revenue (Scenario 3)** | REopt does not model contract-for-difference structures against a wholesale market price | Implement DPPA settlement as a post-processing step in Python: for each hour, compute settlement = max(0, Strike − FMP) × Qm where Qm = net delivered generation. Sum over 8760 hours. Stack on top of REopt's baseline cost savings |
| **Leveraged equity IRR** | REopt computes unlevered project IRR and NPV, not levered equity IRR | Run Python DCF module: take REopt EBITDA → apply debt service schedule (70% leverage, 10yr tenor, 8.5% interest) → compute equity cash flows → compute IRR. Compare against Excel's 19.4% equity IRR |
| **Debt sizing / DSCR optimization** | REopt has no debt sizing model | Excel's GoalSeek on DSCR ≥ 1.3 must be replicated in Python: iteratively solve for max debt that satisfies DSCR constraint |
| **Forward Market Price (FMP) data** | REopt uses a fixed tariff series, not real-time wholesale prices | FMP/CFMP data is in the Excel `Data Input` sheet (8760 hourly values). Extract and use for DPPA settlement calculations |
| **VWEM participation** | REopt has no market participation model | Model as additional revenue: generator sells into spot market at FMP, with buyer receiving the CfD spread |
| **VND currency reporting** | REopt outputs USD | Post-processing: multiply all USD results by exchange rate (26,000 VND/USD) for VND reporting |
| **BESS peak shaving demand reduction target** | "20% demand reduction" is not a REopt input parameter | Model as: fix BESS power at 20 MW and allow REopt to optimize dispatch within that capacity, OR add JuMP constraint `max(load_kw) * (1 - dvStoragePower / peak_load) ≤ 0.80 * baseline_peak` — this is complex; document the approximation |
| **Scenario sensitivity table** | Multi-scenario comparison across CAPEX / tariff / degradation assumptions | Python driver script that loops across parameter combinations, calls REopt API (or runs Julia locally), and aggregates results |

---

## 3. Mapping Excel Data to REopt Inputs

### 3.1 Input Field Mapping Table

| Excel Source | Field | REopt Block.Field | Conversion | Notes |
|---|---|---|---|---|
| Assumption!B15 | Solar capacity (40,360 kWp) | `PV.min_kw` = `PV.max_kw` = 40360 | Direct | Fix size for comparison run |
| Assumption!B25 | BESS energy (66,000 kWh) | `ElectricStorage.min_kwh` = `ElectricStorage.max_kwh` = 66000 | Direct | Fix for comparison run |
| Assumption!B26 | BESS power (20,000 kW) | `ElectricStorage.min_kw` = `ElectricStorage.max_kw` = 20000 | Direct | Fix for comparison run |
| Assumption!B27 | DoD (85%) | `ElectricStorage.min_soc_fraction` = 0.15 | `1 − DoD` | |
| Assumption!B28 | Half-cycle efficiency (95%) | `ElectricStorage.charge_efficiency` = 0.95, `discharge_efficiency` = 0.95 | Direct | |
| Assumption!B41 | PV CAPEX ($750k/MWp) | `PV.installed_cost_per_kw` = 750 | Direct ($/kW = $/MWp / 1000) | |
| Assumption!B42 | BESS CAPEX ($200k/MWh) | `ElectricStorage.installed_cost_per_kwh` = 200 | Direct | |
| Assumption!O10 | Project life (20 years) | `Financial.analysis_years` = 20 | Direct | |
| Assumption!O25 | O&M Solar ($6k/MWp/year) | `PV.om_cost_per_kw` = 6 | Direct ($/kW) | |
| Assumption!O27 | O&M BESS ($2k/MWh/year) | `ElectricStorage.om_cost_per_kwh` = 2 | Direct | |
| Assumption!O34 | Opex escalation (4%) | `Financial.om_cost_escalation_rate_fraction` = 0.04 | Direct | |
| Assumption!O62 | CIT rate (20%) | `Financial.owner_tax_rate_fraction` = 0.0575 | Use blended 20yr effective rate | See tax holiday workaround |
| Assumption!O16 | Tariff structure "1-component" | `ElectricTariff.energy_rate_series_per_kwh` | Apply TOU but verify 1-component flag | 1-component = energy only, no capacity |
| Assumption!P14 | Standard tariff (VND 1,811/kWh) | TOU series standard hours | ÷ 26,000 VND/USD → $0.0696/kWh | `build_vietnam_tariff()` handles this |
| Assumption!P15 | Peak tariff (VND 3,266/kWh) | TOU series peak hours | ÷ 26,000 → $0.1256/kWh | |
| Assumption!P16 | Off-peak tariff (VND 1,146/kWh) | TOU series off-peak hours | ÷ 26,000 → $0.0441/kWh | |
| Data Input!C:C | Hourly solar profile (kW) | `PV.production_factor_series` | Divide by 40,360 → capacity factor fraction | 8760 values from PVsyst/SAM simulation |
| Data Input!D:D | Hourly load profile (kW) | `ElectricLoad.loads_kw` | Direct | Requires `ElectricLoad.year = 2024` |
| Data Input!E:E | FMP (VND/MWh) | External only (DPPA post-processing) | Not a REopt input | |
| Assumption!O30 | PPA discount (15%) | Modify `energy_rate_series_per_kwh` × 0.85 | Apply before passing to REopt | See Section 4.2 |

### 3.2 Site Coordinates

The Excel model does not include explicit lat/lon coordinates (the project is named "Saigon18" suggesting proximity to Ho Chi Minh City). Use the following defaults until the actual site coordinates are confirmed:

```json
"Site": {
    "latitude": 10.9577,
    "longitude": 106.8426,
    "land_acres": 0.0,
    "roof_squarefeet": 0
}
```

> ⚠ **Action required:** Confirm site coordinates from the project developer. This affects the NREL PVWatts solar resource fetch. If providing `production_factor_series` directly from Excel, coordinates are only needed for weather/emissions lookups.

### 3.3 PV Production Profile Injection

Two options for PV generation profile:

**Option A — Use NREL PVWatts API (via REopt):**
REopt fetches the production factor series from NREL's NSRDB via lat/lon. Set only the system parameters:
```json
"PV": {
    "min_kw": 40360, "max_kw": 40360,
    "tilt": 10.96,
    "azimuth": 180.0,
    "module_type": 1,
    "array_type": 0,
    "dc_ac_ratio": 1.2,
    "losses": 0.14
}
```

**Option B — Inject from Excel directly (preferred for comparison fidelity):**
Extract `SimulationProfile_kW` (column B in `Data Input` sheet), divide by 40,360 kW to get capacity factor, and pass as `production_factor_series`:
```json
"PV": {
    "min_kw": 40360, "max_kw": 40360,
    "production_factor_series": [<8760 capacity factors from Excel>]
}
```
Option B is strongly preferred because it uses the same PVsyst/SAM simulation data that the Excel model uses, enabling a direct apples-to-apples comparison.

---

## 4. Data Pipeline

### 4.1 Pipeline Architecture

```
Excel File (Data Input sheet)
    │
    ├── Extract 8760 loads_kw array (column D)
    ├── Extract 8760 production_factor_series (column B ÷ 40,360)
    ├── Extract 8760 FMP values (column E) ← for DPPA post-processing only
    └── Extract financial & technical assumptions (Assumption sheet)
    │
    ▼
Python: excel_to_reopt.py
    │
    ├── Build base REopt input dict (Site, ElectricLoad, PV, ElectricStorage, Financial, ElectricTariff)
    ├── Call apply_vietnam_defaults() ← from src/python/reopt_pysam_vn/reopt/preprocess.py
    ├── Apply project-specific overrides (CAPEX, BESS sizing, analysis_years=20, etc.)
    ├── Apply PPA tariff modification (EVN TOU × 0.85 for Scenario 1)
    └── Write to scenarios/case_studies/saigon18/2026-03-xx_<scenario>.json
    │
    ▼
REopt (Julia local or API)
    │
    ├── Julia: run_vietnam_scenario.jl --scenario scenario-b_fixed-sizing_ppa-discount
    │       → artifacts/results/saigon18/2026-03-20_scenario-b_fixed-sizing_ppa-discount_reopt-results.json
    └── API: run_vietnam_reopt(d, api_key)
           → artifacts/results/saigon18/2026-03-xx_<scenario>_api-results.json
    │
    ▼
Python: compare_reopt_vs_excel.py
    │
    ├── Load REopt results JSON
    ├── Load Excel outputs (Financial sheet annual rows)
    ├── Compute DPPA settlement from FMP data + REopt dispatch
    ├── Compute leveraged equity IRR from REopt EBITDA + debt schedule
    └── Write artifacts/reports/saigon18/2026-03-xx_<report>.md + .html
```

### 4.2 Excel Extraction Script

**File:** `scripts/python/reopt/extract_excel_inputs.py`

```python
"""
Extract Saigon18 project data from Excel model for use as REopt inputs.

Usage:
    python scripts/python/reopt/extract_excel_inputs.py \
        --excel "path/to/llm 20260129 SOLAR BESS MODEL - Editing - for processing test.xlsx" \
        --output data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json
"""
import json
import argparse
from pathlib import Path
import openpyxl

def extract_saigon18_data(excel_path: str) -> dict:
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)

    # --- Data Input sheet: 8760 hourly profiles ---
    data_ws = wb["Data Input"]
    rows = list(data_ws.iter_rows(min_row=9, max_row=8768, values_only=True))
    assert len(rows) == 8760, f"Expected 8760 rows, got {len(rows)}"

    pv_kw_raw   = [r[1] or 0.0 for r in rows]  # col B: SimulationProfile_kW
    loads_kw    = [r[3] or 0.0 for r in rows]  # col D: Load_kW
    fmp         = [r[4] or 0.0 for r in rows]  # col E: FMP (VND/MWh)
    cfmp        = [r[5] or 0.0 for r in rows]  # col F: CFMP

    pv_kw_rated = 40360.0  # MWp in kW
    pv_prod_factor = [v / pv_kw_rated for v in pv_kw_raw]

    # --- Assumption sheet: key parameters ---
    assump_ws = wb["Assumption"]
    # (Row,Col) → 0-indexed. Read specific cells by iterating.
    assump_data = {}
    for row in assump_ws.iter_rows(min_row=1, max_row=70, values_only=True):
        for j, v in enumerate(row):
            pass  # populate as needed

    return {
        "loads_kw": loads_kw,
        "pv_production_factor_series": pv_prod_factor,
        "fmp_vnd_per_mwh": fmp,
        "cfmp_vnd_per_mwh": cfmp,
        "solar_kw_rated": pv_kw_rated,
        "data_year": 2024,
        "location": "Vietnam (south, HCMC area)",
        "annual_solar_gwh": sum(pv_kw_raw) / 1e6,
        "annual_load_gwh": sum(loads_kw) / 1e6,
        "peak_load_kw": max(loads_kw),
    }
```

> **Implementation note:** Assign hardcoded row references for the Assumption sheet fields (rows 9–69 as read in this analysis). The cells are deterministic; no cell-name lookups required.

### 4.3 REopt Input Builder Script

**File:** `scripts/python/reopt/build_saigon18_reopt_input.py`

Builds scenario-specific REopt JSON from extracted data and applies Vietnam defaults. See Section 5 for scenario definitions.

```python
from src.reopt_vietnam import load_vietnam_data, apply_vietnam_defaults

PVCAPEX_USD_PER_KW    = 750.0
BESS_CAPEX_USD_PER_KW = 200.0  # power cost
BESS_CAPEX_USD_PER_KWH = 200.0 # energy cost (Excel: $200k/MWh = $200/MWh = $200/kWh)
PV_KW                 = 40_360.0
BESS_KW               = 20_000.0
BESS_KWH              = 66_000.0
ANALYSIS_YEARS        = 20
EXCHANGE_RATE         = 26_000.0  # VND/USD
CIT_BLENDED_20YR      = 0.0575   # (4*0 + 9*0.05 + 7*0.10) / 20

def build_base_scenario(extracted: dict) -> dict:
    """Build the base REopt input dict for Saigon18."""
    d = {
        "Site": {
            "latitude": 10.9577,
            "longitude": 106.8426,
        },
        "ElectricLoad": {
            "loads_kw": extracted["loads_kw"],
            "year": extracted["data_year"],  # required when loads_kw is provided
        },
        "PV": {
            "min_kw": PV_KW,
            "max_kw": PV_KW,
            "installed_cost_per_kw": PVCAPEX_USD_PER_KW,
            "om_cost_per_kw": 6.0,  # $6k/MWp = $6/kW
            "production_factor_series": extracted["pv_production_factor_series"],
            "location": "ground",
            "tilt": 10.96,
            "azimuth": 180.0,
            "dc_ac_ratio": 1.2,
            "losses": 0.14,
        },
        "ElectricStorage": {
            "min_kw": BESS_KW,
            "max_kw": BESS_KW,
            "min_kwh": BESS_KWH,
            "max_kwh": BESS_KWH,
            "installed_cost_per_kw": BESS_CAPEX_USD_PER_KW,
            "installed_cost_per_kwh": BESS_CAPEX_USD_PER_KWH,
            "installed_cost_constant": 0,          # override US $222k default
            "replace_cost_per_kw": 100.0,
            "replace_cost_per_kwh": 100.0,
            "battery_replacement_year": 10,
            "inverter_replacement_year": 10,
            "min_soc_fraction": 0.15,              # 1 - 85% DoD
            "max_soc_fraction": 1.0,
            "charge_efficiency": 0.95,
            "discharge_efficiency": 0.95,
            "om_cost_per_kwh": 2.0,               # $2k/MWh/year = $2/kWh/year
        },
        "Financial": {
            "analysis_years": ANALYSIS_YEARS,
            "owner_tax_rate_fraction": CIT_BLENDED_20YR,
            "offtaker_tax_rate_fraction": 0.20,
            "owner_discount_rate_fraction": 0.08,
            "offtaker_discount_rate_fraction": 0.10,
            "elec_cost_escalation_rate_fraction": 0.05,   # Excel: 5% EVN price escalation
            "om_cost_escalation_rate_fraction": 0.04,
        },
    }

    vn = load_vietnam_data()
    apply_vietnam_defaults(
        d, vn,
        customer_type="industrial",
        voltage_level="high_voltage_above_35kv_below_220kv",  # 110 kV connection
        region="south",
        pv_type="ground",
        apply_financials=False,   # we set Financial explicitly above
        apply_tariff=True,        # inject EVN TOU series
        apply_emissions=True,
        apply_tech_costs=False,   # we set costs explicitly above
        apply_export_rules=True,
        apply_zero_incentives=True,
    )
    return d
```

---

## 5. Scenarios

Run four parallel scenarios in REopt, mirroring the Excel scenario structure.

### Scenario A — Baseline (REopt TOU Optimization, No PPA Constraint)

**Purpose:** Pure REopt optimization against EVN TOU tariff. No PPA discount. Shows what REopt recommends vs. what Excel assumes.

**Input overrides:**
- No modifications to the standard `apply_vietnam_defaults()` tariff output
- BESS and PV sizes fixed at project values
- This is the "what would REopt do with the actual system and actual tariff?" baseline

**Expected REopt outputs to capture:**
- `results["Financial"]["lcc"]`
- `results["Financial"]["npv"]`
- `results["Financial"]["simple_payback_years"]`
- `results["PV"]["year_one_energy_produced_kwh"]`
- `results["ElectricStorage"]["year_one_to_load_series_kw"]` (8760 dispatch)
- `results["ElectricStorage"]["year_one_soc_series_fraction"]` (state of charge)

### Scenario B — PPA Bundled Discount (15% off EVN TOU)

**Purpose:** Mirror Excel Scenario 1. Adjust tariff to represent PPA price = EVN TOU × 0.85.

**Tariff modification:**
```python
tariff_series = d["ElectricTariff"]["energy_rate_series_per_kwh"]
d["ElectricTariff"]["energy_rate_series_per_kwh"] = [r * 0.85 for r in tariff_series]
```

**Financial interpretation:** REopt's NPV now measures value of avoiding the PPA price (not the full EVN tariff). The difference between Scenario A NPV and Scenario B NPV equals the annual PPA discount revenue that flows to the offtaker.

> **Note:** In the Excel model, the project owner *receives* revenue from the offtaker at a 15% discount to EVN. In REopt framing, you are the offtaker: the "avoided cost" is the PPA price. To align: run REopt as the *project owner* with the PPA price as the effective electricity rate. REopt NPV = project owner's project NPV from selling at PPA rates.

### Scenario C — Optimized Sizing (Unconstrained)

**Purpose:** Let REopt optimize PV and BESS sizes from scratch given actual load profile and costs. Compare the optimizer's recommendation against the Excel model's fixed 40.36 MWp + 66 MWh assumption.

**Input change:** Remove `min_kw/max_kw` fixes for both PV and BESS; set generous upper bounds:
```json
"PV": { "max_kw": 60000 },
"ElectricStorage": { "max_kw": 30000, "max_kwh": 100000 }
```

**Key comparison question:** Does REopt recommend the same sizing as the developer chose? If not, why not?

### Scenario D — DPPA (Strike Price Contract)

**Purpose:** Approximate the DPPA revenue structure from Excel Scenario 3. This requires partial post-processing because REopt cannot model CfD directly.

**Approach:**
1. Run REopt with EVN TOU tariff (Scenario A baseline) to get BESS dispatch and generation profile
2. Extract `year_one_to_grid_series_kw` (8760 export to grid)
3. In Python post-processing, compute DPPA settlement for each hour:
   ```
   if FMP[h] > strike_price:
       settlement[h] = 0  # generator receives market price (no top-up)
   else:
       settlement[h] = (strike_price - FMP[h]) * generation_to_buyer[h]  # buyer pays top-up
   ```
4. Add settlement revenue to REopt's baseline revenue
5. Note: the DPPA ceiling tariff for ground-mounted solar with BESS in the south is VND 1,149.86/kWh (~$0.0436/kWh) per `vn_export_rules_decree57.json`. The Excel uses VND 1,800/kWh strike price — confirm this is within the MOIT-approved ceiling for the specific contract type.

---

## 6. Comparison and Validation Framework

### 6.1 Comparison Metrics

For each scenario, compare the following between REopt output and Excel model output:

**Energy metrics (Year 1):**

| Metric | Excel Output | REopt Field | Tolerance |
|---|---|---|---|
| Annual PV generation (MWh) | 71,808 MWh | `PV.year_one_energy_produced_kwh / 1000` | ±1% |
| PV energy to load (MWh) | ~62,106 MWh | `PV.year_one_to_load_kwh / 1000` | ±2% |
| PV energy exported (MWh) | 1,087 MWh | `PV.year_one_to_grid_kwh / 1000` | ±5% |
| BESS discharge to peak (MWh) | 7,364 MWh/yr | From dispatch profile, peak hours only | ±5% |
| BESS discharge to std (MWh) | 1,227 MWh/yr | From dispatch profile, standard hours only | ±5% |
| Grid purchases (MWh) | ~112,454 MWh | `ElectricUtility.year_one_energy_supplied_kwh / 1000` | ±2% |

**Financial metrics:**

| Metric | Excel Output | REopt Field | Notes |
|---|---|---|---|
| Year 1 avoided cost / revenue ($) | $5,056,418 | Derive from `(BAU LCC - Optimized LCC) / 25` ≈ NPV component | Verify alignment |
| NPV @ 10% ($) | $22,034,000 | `results["Financial"]["npv"]` | REopt uses owner discount rate; Excel uses WACC |
| Simple payback (years) | 6 years | `results["Financial"]["simple_payback_years"]` | ±1 year |
| LCC savings | Derive from baseline | `lcc_bau - lcc` | |

**BESS dispatch profile validation:**

Compare hourly BESS state-of-charge from REopt (`year_one_soc_series_fraction`) against the Excel model's simulated SOC. Key patterns to validate:
- Charge buildup during solar hours (11:00–15:00)
- Discharge during peak hours (17:00–20:00)
- Near-zero SOC at end-of-day (Excel target: 215 kWh reserve = 0.33% of 66 MWh)

### 6.2 Expected Discrepancies and Explanations

Developers should expect the following differences and understand their root causes:

**1. Dispatch pattern difference:**
REopt will optimize dispatch purely on TOU tariff economics. It will charge during off-peak (not just 11–15h) if it is cost-optimal to do so. The Excel model enforces a fixed charge window (11–15h only, no grid charging). REopt's dispatch will likely be more economically optimal than the Excel model's fixed schedule — meaning REopt's NPV may be *higher* than Excel's if the fixed dispatch schedule is suboptimal.

**2. BESS sizing:**
The Saigon18 Excel model selects 66 MWh / 20 MW BESS based on a 3.3-hour dispatch window and 20% demand reduction target. REopt's unconstrained optimization (Scenario C) may recommend a different ratio. If REopt recommends a smaller BESS, this suggests the Excel model may be over-sizing the battery relative to pure economic optimality.

**3. NPV difference:**
REopt NPV uses owner discount rate (8%) applied to unlevered cash flows. Excel NPV uses a WACC/equity IRR framework with 70% leverage. A straight comparison of NPV numbers is invalid — use unlevered IRR for apples-to-apples comparison.

**4. Revenue model difference:**
REopt does not compute PPA revenue as income; it computes avoided electricity cost as the value driver. The Excel model frames cash flows as PPA income minus operating costs. These are economically equivalent when the PPA price equals the avoided electricity rate, but the labeling differs.

**5. Degradation:**
The Excel model applies 0.5%/year system degradation and 3%/year BESS degradation, reducing annual energy output over time. REopt's degradation model uses a discrete battery replacement (at year 10) rather than continuous decay. Expect ±2–3% annual energy differences by year 10–15.

### 6.3 Automated Comparison Script

**File:** `scripts/python/reopt/compare_reopt_vs_excel.py`

```python
"""
Compare REopt results against Saigon18 Excel model outputs.

Usage:
    python scripts/python/reopt/compare_reopt_vs_excel.py \
        --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json \
        --excel "path/to/Solar BESS MODEL.xlsx" \
        --output artifacts/reports/saigon18/2026-03-22_scenario-a_vs_excel_comparison.md
"""
import json
from pathlib import Path

METRICS = [
    ("Annual PV generation (MWh)",     "pv_gen_kwh",           1000),
    ("Grid purchases (MWh)",           "grid_kwh",             1000),
    ("BESS year-1 discharge (MWh)",    "bess_discharge_kwh",   1000),
    ("Year-1 avoided cost ($)",        "avoided_cost_usd",     1),
    ("NPV ($)",                        "npv_usd",              1),
    ("Simple payback (years)",         "payback_years",        1),
]

def load_reopt_metrics(results_path: str) -> dict:
    with open(results_path) as f:
        r = json.load(f)
    return {
        "pv_gen_kwh": r.get("PV", {}).get("year_one_energy_produced_kwh", 0),
        "grid_kwh": r.get("ElectricUtility", {}).get("year_one_energy_supplied_kwh", 0),
        "bess_discharge_kwh": sum(r.get("ElectricStorage", {}).get("year_one_to_load_series_kw", [0])),
        "avoided_cost_usd": r.get("Financial", {}).get("npv", 0) / 25,  # rough annual equivalent
        "npv_usd": r.get("Financial", {}).get("npv", 0),
        "payback_years": r.get("Financial", {}).get("simple_payback_years", 0),
    }
```

---

## 7. Vietnam-Specific Gaps and Workarounds (Detail)

### 7.1 Gap 1 — DPPA Revenue Structure

**Problem:** Vietnam's DPPA under Decree 57/2025 involves a generator selling electricity to an industrial buyer at a negotiated price, with a contract-for-difference against the wholesale market (VWEM forward market price). REopt has no concept of a bilateral power purchase agreement or CfD settlement.

**Workaround:**
- Run REopt to get the optimal dispatch profile and total generation
- Extract `ElectricStorage.year_one_to_load_series_kw` and `PV.year_one_to_load_series_kw` for the buyer's consumption
- Apply DPPA settlement formula in Python post-processing using the Excel's FMP array (column E, `Data Input` sheet)
- The DPPA revenue = Σ[max(0, CDPPA − FMP[h]) × Q_delivered[h]] for each hour h
- Add this revenue to the REopt NPV calculation

**Ceiling tariff check (required before any DPPA scenario):**
Per Decree 57 and `vn_export_rules_decree57.json`, the ground-mounted solar + BESS ceiling for the south is **VND 1,149.86/kWh (~$0.0436/kWh)**. The Excel model uses VND 1,800/kWh as the strike price. This appears to exceed the Decree 57 ceiling for private wire DPPA — confirm whether the project uses a private wire or grid-connected DPPA structure, as ceiling tariffs differ.

**Implementation file:** `scripts/python/reopt/dppa_settlement.py`

```python
def compute_dppa_annual_revenue(
    q_delivered_kw: list[float],     # 8760 hourly delivered power (kW)
    fmp_vnd_per_mwh: list[float],   # 8760 hourly FMP (VND/MWh)
    strike_price_vnd_per_kwh: float, # DPPA strike price (VND/kWh)
    curtailment_pct: float = 0.02,   # 2% transmission loss (from Excel)
) -> dict:
    """Compute DPPA CfD settlement revenue for one year."""
    total_settlement_vnd = 0.0
    total_q_mwh = sum(q_delivered_kw) / 1000

    for h in range(8760):
        q_mwh = q_delivered_kw[h] * (1 - curtailment_pct) / 1000
        fmp_per_kwh = fmp_vnd_per_mwh[h] / 1000
        spread = max(0, strike_price_vnd_per_kwh - fmp_per_kwh)
        total_settlement_vnd += spread * q_mwh * 1000  # convert MWh→kWh

    return {
        "total_settlement_vnd": total_settlement_vnd,
        "total_q_mwh": total_q_mwh,
        "avg_settlement_per_kwh_vnd": total_settlement_vnd / (total_q_mwh * 1000),
    }
```

### 7.2 Gap 2 — Leveraged Equity IRR

**Problem:** REopt computes unlevered (project-level) IRR. The Excel model's headline 19.4% equity IRR assumes 70% debt leverage at 8.5% interest over a 10-year tenor.

**Workaround:** Post-process REopt unlevered EBITDA through a Python DCF model.

**Implementation file:** `scripts/python/reopt/equity_irr.py`

```python
def compute_equity_irr(
    ebitda_series: list[float],          # annual unlevered free cash flows from REopt
    total_capex: float,                  # total project CAPEX ($)
    debt_fraction: float = 0.70,
    interest_rate: float = 0.085,        # blended (6.5% base + 2% margin, 50% hedged)
    debt_tenor_years: int = 10,
    analysis_years: int = 20,
) -> float:
    """
    Compute levered equity IRR given REopt EBITDA and debt assumptions.
    Returns equity IRR as a fraction (e.g., 0.194 = 19.4%).
    """
    import numpy_financial as npf

    debt = total_capex * debt_fraction
    equity = total_capex * (1 - debt_fraction)

    # Annual debt service (constant payment mortgage-style)
    annual_debt_service = npf.pmt(interest_rate, debt_tenor_years, -debt)

    equity_cashflows = [-equity]
    for yr in range(1, analysis_years + 1):
        ds = annual_debt_service if yr <= debt_tenor_years else 0
        equity_cf = ebitda_series[yr - 1] - ds
        equity_cashflows.append(equity_cf)

    return npf.irr(equity_cashflows)
```

> **Package requirement:** Add `numpy-financial` to the project's Python dependencies.

### 7.3 Gap 3 — Decree 57 Export Cap (Hard Constraint)

**Problem:** REopt's `apply_decree57_export()` correctly sets `can_wholesale=True` and `wholesale_rate` but does NOT enforce the 20% cap as a hard optimization constraint. Any unconstrained REopt run may export more than 20% of generation.

**Workaround:** Add a custom JuMP constraint in `src/julia/REoptVietnam.jl`:

```julia
# After build_reopt!(m, inputs):
pv_tech_name = "PV"  # or iterate over all PV techs
total_gen = sum(
    m[:dvRatedProduction][pv_tech_name, ts] * inputs.time_steps_per_hour
    for ts in inputs.time_steps
)
total_export = sum(
    m[:dvProductionToGrid][pv_tech_name, ts] * inputs.time_steps_per_hour
    for ts in inputs.time_steps
)
@constraint(m, total_export ≤ 0.20 * total_gen)
```

**Status:** This is deferred work flagged in `docs/pitfalls.md`. Until implemented, document in the comparison report that export volumes from REopt may exceed the Decree 57 limit and should be capped in post-processing for revenue calculation.

### 7.4 Gap 4 — Fixed BESS Dispatch Windows

**Problem:** The Saigon18 Excel model uses a rule-based dispatch controller (charge 11–15h, discharge from 18h). REopt's optimizer will freely choose charge/discharge timing based on TOU economics.

**Workaround:** Three options (choose based on comparison objective):

- **Option A (recommended for first run):** Let REopt optimize freely. Compare the dispatch profiles to understand whether the fixed windows are economically optimal. If REopt and Excel dispatch agree closely, the validation is stronger.
- **Option B:** Add JuMP time-of-use constraints to replicate the fixed windows. This validates the Excel model's controller logic but removes REopt's optimization benefit.
- **Option C:** Run both (A and B) and report the NPV difference as the "value of optimal dispatch vs. fixed schedule."

### 7.5 Gap 5 — VND Currency and Exchange Rate Risk

**Problem:** REopt outputs are denominated in USD. The Excel model computes revenue in VND and converts at a fixed 26,000 VND/USD rate. Exchange rate changes over 20 years are not modeled in either tool.

**Workaround:**
- All REopt inputs that are VND-denominated (tariff, surplus purchase rate) are converted to USD using `convert_vnd_to_usd()` from `src/python/reopt_pysam_vn/reopt/preprocess.py` at the fixed rate
- Report all REopt outputs in USD, then provide a VND conversion table in the comparison report
- Flag exchange rate risk as a sensitivity variable for future scenario analysis

### 7.6 Gap 6 — Two-Part Tariff (Forward-Looking)

**Problem:** Vietnam is transitioning to a two-part tariff (capacity + energy) per Decree 146/2025 and the Electricity Law 2024. The pilot runs Jan–Jun 2026. The Saigon18 model uses a 1-component tariff today, but this will change within the project's 20-year life.

**Workaround:**
- Current model: `monthly_demand_rates = [0] * 12`
- Future scenario: Use the two-part tariff trial values from `vn_tariff_2025.json`:
  - Capacity charge: 235,414 VND/kW/month (22kV–110kV)
  - Energy charge: 1,253–2,251 VND/kWh (normal/peak/off-peak ranges)
- Run a sensitivity scenario with the two-part tariff from year 5 onward to assess BESS peak-shaving NPV impact

---

## 8. Implementation Phases

### Phase 1 — Data Extraction and Input Validation (Week 1)

**Goal:** Extract all Saigon18 data from Excel, build REopt JSON inputs, validate that REopt accepts the inputs without errors.

**Tasks:**
1. Implement `scripts/python/reopt/extract_excel_inputs.py`
   - Extract 8760 load profile, 8760 PV production profile, 8760 FMP values
   - Extract financial and technical assumptions from Assumption sheet
   - Validate: 8760 rows, no negative values, solar sum matches annual yield (±1%)
   - Save to `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json`

2. Implement `scripts/python/reopt/build_saigon18_reopt_input.py`
   - Build Scenario A and Scenario B JSON inputs
   - Apply Vietnam defaults via `apply_vietnam_defaults()`
   - Apply project-specific overrides (sizing, costs, analysis years)
   - Save to `scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json` and `2026-03-20_scenario-b_fixed-sizing_ppa-discount.json`

3. Validate inputs (no-solve mode):
   ```powershell
   julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
       --scenario scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json `
       --no-solve
   ```
   Expected: `Scenario()` construction succeeds with no fatal errors. Warnings about AVERT/Cambium/EASIUR are expected for Vietnam locations.

4. Add Layer 1 data validation tests:
   ```
   tests/python/integration/test_saigon18_data.py
   ```

**Deliverables:**
- `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json`
- `scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json`
- `scenarios/case_studies/saigon18/2026-03-20_scenario-b_fixed-sizing_ppa-discount.json`
- Validation test passing

---

### Phase 2 — REopt Run and Baseline Comparison (Weeks 2–3)

**Goal:** Run REopt for Scenarios A and B, extract results, compare against Excel model outputs.

**Tasks:**
1. Run Scenario A (full EVN TOU tariff, fixed sizing) locally via Julia:
   ```powershell
   $env:JULIA_PKG_PRECOMPILE_AUTO="0"
   julia --project --compile=min scripts/julia/run_vietnam_scenario.jl `
       --scenario scenarios/case_studies/saigon18/2026-03-20_scenario-a_fixed-sizing_evntou.json
   ```
   Save results to `artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json`

2. Run Scenario B (PPA tariff × 0.85, fixed sizing)

3. Implement `scripts/python/reopt/compare_reopt_vs_excel.py`:
   - Load REopt JSON results
   - Load Excel Financial sheet outputs (programmatically via openpyxl)
   - Compute delta table for all metrics in Section 6.1
   - Flag discrepancies >5% with explanations

4. Implement `scripts/python/reopt/dppa_settlement.py`:
   - Compute DPPA annual settlement from REopt dispatch + FMP data
   - Compare against Excel DPPA sheet outputs

5. Generate comparison report:
   ```
   artifacts/reports/saigon18/2026-03-22_scenario-a_vs_excel_comparison.md
   ```

**Deliverables:**
- REopt results JSON for Scenarios A and B
- Python comparison script
- Comparison report (markdown + HTML)

---

### Phase 3 — Custom Constraints and Advanced Scenarios (Weeks 4–5)

**Goal:** Implement Vietnam-specific JuMP constraints, run optimized sizing scenario, validate equity IRR.

**Tasks:**
1. Implement Decree 57 export cap as hard JuMP constraint in `src/julia/REoptVietnam.jl`

2. Implement optional fixed dispatch window constraints (Phase 3 Option B from Section 7.4)

3. Run Scenario C (optimized sizing):
   - Remove fixed kW/kWh bounds from PV and BESS
   - Let REopt recommend optimal sizing
   - Compare recommended sizes against Excel's 40.36 MWp + 66 MWh

4. Implement `scripts/python/reopt/equity_irr.py`:
   - Extract annual avoided-cost cash flows from REopt results
   - Apply debt schedule (70% leverage, 10yr, 8.5%)
   - Compute equity IRR
   - Compare against Excel's 19.4%

5. Add Layer 4 integration test for Saigon18 scenarios:
   ```
   tests/python/integration/test_saigon18_integration.py
   ```

**Deliverables:**
- Updated `src/julia/REoptVietnam.jl` with Decree 57 hard constraint
- Scenario C results (optimized sizing)
- Equity IRR script and comparison
- Integration tests

---

### Phase 4 — Sensitivity Analysis and Reporting (Week 6)

**Goal:** Run multi-scenario sensitivity analysis and produce the final comparison report.

**Tasks:**
1. Implement Python driver script for scenario sweeps:
   ```
   scripts/python/run_saigon18_sensitivity.py
   ```
   Parameter ranges to sweep:
   - PPA discount: 10%, 15%, 20%
   - BESS sizing: 50 MWh / 75 MWh / 90 MWh
   - EVN tariff escalation: 3%, 5%, 7%
   - Exchange rate: 25,000 / 26,000 / 27,000 VND/USD
   - CIT profile: standard 20% vs. RE preferential (6.6% blended)

2. Two-part tariff sensitivity (Gap 6):
   - Rerun Scenario A with two-part tariff from year 5
   - Quantify BESS peak-shaving value under capacity charge regime

3. Final comparison report (`artifacts/reports/saigon18/2026-03-xx_final-report.md`):
   - Executive summary: REopt vs. Excel alignment scorecard
   - Energy performance comparison table
   - Financial metrics comparison table
   - BESS dispatch profile charts (matplotlib)
   - DPPA revenue comparison
   - Gap inventory: what REopt can/cannot validate
   - Recommendations: which Excel assumptions REopt supports, which need revision

**Deliverables:**
- Sensitivity results CSV/JSON
- Final comparison report (markdown + HTML)
- Charts

---

## 9. File and Folder Structure

```
reopt-pysam-vn/
├── data/
│   ├── vietnam/             (existing)
│   ├── raw/saigon18/
│   │   └── 2026-01-29_saigon18_excel_model_v2.xlsm
│   └── interim/saigon18/
│       └── 2026-03-20_saigon18_extracted_inputs.json   ← Phase 1 output
├── scenarios/
│   ├── templates/           (existing)
│   └── case_studies/saigon18/
│       ├── 2026-03-20_scenario-a_fixed-sizing_evntou.json      ← Phase 1 output
│       ├── 2026-03-20_scenario-b_fixed-sizing_ppa-discount.json ← Phase 1 output
│       ├── 2026-03-23_scenario-c_optimized-sizing.json         ← Phase 3 output
│       └── 2026-03-20_scenario-d_dppa-baseline.json            ← Phase 3 output
├── scripts/
│   ├── julia/               (existing)
│   └── python/
│       ├── extract_excel_inputs.py       ← Phase 1
│       ├── build_saigon18_reopt_input.py ← Phase 1
│       ├── compare_reopt_vs_excel.py     ← Phase 2
│       ├── dppa_settlement.py            ← Phase 2
│       ├── equity_irr.py                 ← Phase 3
│       └── run_saigon18_sensitivity.py   ← Phase 4
├── artifacts/
│   ├── results/saigon18/
│   │   ├── 2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json
│   │   ├── 2026-03-20_scenario-b_fixed-sizing_ppa-discount_reopt-results.json
│   │   └── 2026-03-23_scenario-c_optimized-sizing_reopt-results.json
│   └── reports/saigon18/
│       ├── 2026-03-22_scenario-a_vs_excel_comparison.md
│       ├── 2026-03-22_equity-irr_summary.json
│       └── 2026-03-xx_final-report.md
├── tests/
│   └── python/
│       ├── test_saigon18_data.py         ← Phase 1
│       └── test_saigon18_integration.py  ← Phase 3
└── plans/archive/
    └── saigon18_reopt_integration_plan.md  ← This document
```

---

## 10. Python Dependencies

Add to `requirements.txt` or project Python env:

```
openpyxl>=3.1          # Excel file reading
numpy-financial>=1.0   # IRR/NPV calculations
matplotlib>=3.8        # Dispatch profile charts
pandas>=2.0            # Tabular data handling in comparison scripts
requests>=2.31         # Already present (REopt API calls)
```

---

## 11. Open Questions and Action Items

| # | Question | Owner | Priority | Phase |
|---|---|---|---|---|
| 1 | Confirm exact site lat/lon for Saigon18 | Project developer | High | 1 |
| 2 | Confirm DPPA type: private wire or grid-connected? | Legal/BD | High | 2 |
| 3 | Confirm DPPA strike price ceiling compliance (VND 1,800/kWh vs. Decree 57 cap VND 1,149.86/kWh for south) | Legal | High | 2 |
| 4 | Clarify "1-component tariff" flag — is there any capacity/demand component hidden in the bills? | Finance | Medium | 1 |
| 5 | Obtain actual CAPEX breakdown (PV EPC quote, BESS quote) to confirm $750/MWp and $200/MWh | Finance | Medium | 1 |
| 6 | Confirm 2024 calendar used as proxy for 2026 — are there public holiday adjustments needed for TOU mapping? | Engineering | Low | 1 |
| 7 | Is grid charging (GridChargeAllowed) excluded for compliance reasons or purely economic? | Engineering | Low | 2 |
| 8 | What WACC does the Excel model use for NPV discounting? (vs. REopt's 8% owner discount rate) | Finance | Medium | 2 |
| 9 | Does the BESS replacement at year 10 assume full replacement or just battery cells? | Engineering | Medium | 3 |
| 10 | Should the comparison model Decree 146 two-part tariff from 2028 onward? | Policy | Low | 4 |

---

## 12. Key References

| Document | Location |
|---|---|
| REopt.jl internals (structs, variables, results keys) | `docs/reopt_internals.md` |
| Vietnam data files schema | `docs/data_and_api.md` |
| Known pitfalls and workarounds | `docs/pitfalls.md` |
| Vietnam scenario templates | `scenarios/templates/` |
| REopt API base URL | `https://developer.nlr.gov/api/reopt/stable` |
| EVN tariff structure (Decision 14/2025) | `data/vietnam/vn_tariff_2025.json` |
| Decree 57 DPPA rules | `data/vietnam/vn_export_rules_decree57.json` |
| Financial defaults (CIT, discount rates) | `data/vietnam/vn_financial_defaults_2025.json` |
| Tech costs by region | `data/vietnam/vn_tech_costs_2025.json` |
| Excel model (source) | `~/Downloads/temp/llm 20260129 SOLAR BESS MODEL - Editing - for processing test.xlsx` |
| Emivest model (variant) | `~/Downloads/temp/emivest_model_with_emivest_inputs.xlsx` |
| Previous comparison report (US scenarios) | `archive/colab/results/comparison_report.md` |
| REopt.jl GitHub | `https://github.com/NREL/REopt.jl` |
| Vietnam Energy context (DPPA) | ACEC/CEBI VNWS 2024 USAID V-LEEP II presentation |

---

*End of plan. Next step: begin Phase 1 data extraction. See `scripts/python/reopt/extract_excel_inputs.py`.*
