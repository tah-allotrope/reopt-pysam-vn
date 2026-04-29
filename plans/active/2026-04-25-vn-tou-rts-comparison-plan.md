---
title: "Vietnam TOU Tariff Comparison — Rooftop Solar Financial Modeling (Medium Factory)"
date: "2026-04-25"
status: "draft"
request: "Use REopt and PySAM with one suitable existing load profile fitting for a medium factory in Vietnam to compare new TOU (Decision 963/QĐ-BCT, 17:30–22:30 evening peak) vs old TOU (09:30–11:30 + 17:00–20:00 split peak) tariff in financial terms (revenue, returns, savings, IRR, NPV, payback) for both offtakers and RTS project developers, given an optimized-capacity rooftop solar system with no storage, under both opex (PPA) and capex (self-ownership) models."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-25_vietnam-tou-rooftop-ppa.md"
  - "research/2026-04-07-vietnam-dppa-buyer-guide.md"
---

# Plan: Vietnam TOU Tariff Comparison — Rooftop Solar Financial Modeling (Medium Factory)

## Objective
Quantify the financial delta between Vietnam's old TOU schedule (Decision 14/2025 windows: 09:30–11:30 + 17:00–20:00 peak) and new TOU schedule (Decision 963/QĐ-BCT: 17:30–22:30 evening-only peak) on a medium factory rooftop solar (RTS) project with no storage. Produce side-by-side IRR / NPV / payback / annual savings tables for the offtaker and the developer, under both capex (self-ownership) and opex (PPA) models, so that investment committees can size the impact of the April 2026 peak-window shift on RTS deal economics.

## Context Snapshot
- **Current state:** The repo has REopt (Julia) + PySAM (Python) scaffolding, a Vietnam preprocessing tool (`src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/reopt/preprocess.py`), versioned Vietnam tariff data (`data/vietnam/vn_tariff_2025.json` encoding only the **old** Decision 14/2025 TOU windows: peak hours `[9,10,17,18,19]`), industrial PV+storage scenario template (`scenarios/templates/vn_industrial_pv_storage.json`), and three large case studies (saigon18 ~184 GWh/yr, ninhsim ~184 GWh/yr, north_thuan ~241 GWh/yr) — all utility-scale, none sized for a medium factory.
- **Desired state:** A reproducible workflow that (1) builds a medium-factory load profile (~10 GWh/yr, ~2 MW peak) by scaling the saigon18 shape, (2) runs PySAM PVWattsv8 to produce an 8760 generation series for a Binh Duong/HCMC rooftop, (3) runs REopt twice (old-TOU vs new-TOU schedule) to optimize capacity for capex ownership, (4) post-processes both sides of a PPA in Python using `dppa_settlement.py` / `equity_irr.py` patterns, and (5) emits a single HTML comparison report with old-vs-new financial tables for both stakeholders under both ownership models.
- **Key repo surfaces:**
  - `data/vietnam/vn_tariff_2025.json` — extend with a `tou_schedule_decision_963` block; bump version to `2026.1`.
  - `data/vietnam/manifest.json` — point to new tariff file version.
  - `src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/reopt/preprocess.py` — accept a `tou_regime` argument (`"decision_14_2025"` | `"decision_963_2026"`) and select hour arrays accordingly.
  - `scenarios/templates/vn_industrial_pv_storage.json` — clone to a no-storage variant for the medium factory.
  - `scripts/python/integration/build_north_thuan_load_profile.py` — pattern for synthesizing/scaling a load profile.
  - `scripts/python/pysam/run_single_owner_smoke.py` — pattern for PySAM PV simulation; `strike_price_discovery.py` — pattern for PySAM cashflow modeling.
  - `scripts/python/equity_irr.py`, `scripts/python/dppa_settlement.py` — financial post-processing primitives reused for offtaker / developer cashflows.
  - `scripts/julia/run_vietnam_scenario.jl` — execution entrypoint for REopt; existing pattern from saigon18/ninhsim runs.
  - `scripts/python/integration/generate_html_report.py` — HTML report generator pattern reused for the side-by-side output.
- **Out of scope:**
  - Battery/BESS sizing (explicit no-storage scope per request).
  - DPPA virtual/CfD modeling (this plan covers on-site behind-the-meter PPA only; the buyer-side CfD math from the DPPA buyer-guide brief is referenced for context, not modeled here).
  - Two-part tariff (capacity + energy) under Decree 146/2025 paper trial — flagged as a future sensitivity, not run.
  - North/Central Vietnam siting variants — fix the case to the south region.
  - Multipliers re-issued for Decision 963 — not yet published; treated as sensitivity, not base case.

## Research Inputs
- `research/2026-04-25_vietnam-tou-rooftop-ppa.md` — Provides the canonical old vs new TOU windows (old: peak 09:30–11:30 + 17:00–20:00; new: peak 17:30–22:30, off-peak 00:00–06:00, Sundays peak-exempt), Decision 14/2025 multiplier tables (production medium-voltage 22–110 kV: peak 1.57, standard 0.86, off-peak 0.56), average retail price baseline VND 2,204.0655/kWh, and the structural finding that **no PV output reaches the new evening peak window** at Vietnam latitudes — driving the expectation of a 5–15% optimal capacity decrease and ~20–35% offtaker avoided-cost compression under the new TOU. This brief is the primary tariff-input source and frames the expected sign and magnitude of every result the plan produces.
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` — Used only for context on PPA structuring vocabulary (strike price, FMP, KPP, retail tariff fallback) and to confirm that the on-site/private-wire PPA modeled here is **not** the same as a Decree 57 grid-connected DPPA. The plan's PPA model uses a single behind-the-meter strike price; CfD settlement is excluded by scope.

## Assumptions and Constraints
- **ASM-001:** The medium factory is a ~10 GWh/yr industrial site at Binh Duong (10.9577°N, 106.8426°E), single-shift weekday-heavy, connected at medium voltage 22 kV (Decision 14/2025 production category, `medium_voltage_above_1kv_to_35kv` multipliers: peak 1.57, std 0.86, off-peak 0.56).
- **ASM-002:** Decision 14/2025 retail multipliers remain in force under both TOU schedules (i.e., MOIT remaps existing multipliers onto the new windows). The TOU **windows** change; the **multipliers** do not. Flag explicitly in the report and add ASM-002b sensitivity (re-issued multipliers per VietnamSolar.vn hint: peak 80–100% > normal, 2.5–3× off-peak).
- **ASM-003:** PPA price is fixed in real terms with a 1.5% annual escalation, expressed in VND/kWh, signed at financial close. Base case PPA strike: 1,800 VND/kWh — within Decree 57 ceiling range for ground-mounted no-storage solar (1,012–1,382.7 VND/kWh wholesale) plus on-site delivery premium. Validated as an assumption in Grill Me.
- **ASM-004:** No surplus export to grid (no-storage system sized to remain ≤ load year-round); curtailment is the disposition for any midday over-generation. Aligns with Decree 57 self-consumption on-site PPA model.
- **ASM-005:** Analysis horizon 25 years; offtaker discount rate 10%; developer/owner discount rate 8%; CIT 20%; O&M escalation 3%; retail-tariff escalation 4% — match `vn_industrial_pv_storage.json` defaults.
- **ASM-006:** PV installed cost 600 USD/kW × 26,400 VND/USD = ~15,840,000 VND/kW; O&M 8 USD/kW-yr; degradation 0.5%/yr; DC/AC ratio 1.2; tilt 11°, azimuth 180°, losses 14%. Match `vn_industrial_pv_storage.json` defaults.
- **CON-001:** REopt's hourly TOU discretization approximates 30-min boundaries (09:30, 11:30, 17:30, 22:30) by full-hour buckets; this plan accepts the existing tariff JSON's documented approximation and notes a 30-min sensitivity is out of scope.
- **CON-002:** Decree 57 caps rooftop solar surplus export to EVN at 20% of generation — but ASM-004 holds the design no-export, so this cap does not bind.
- **CON-003:** Solver is HiGHS via REopt.jl 0.56.4; 8760 timestep solve must complete in under ~2 minutes per scenario on the developer machine, matching saigon18 baseline runtime.
- **DEC-001:** Storage is excluded by request — only PV, no ElectricStorage block in REopt scenario JSON.
- **DEC-002:** Capacity is REopt-optimized under each TOU regime (not pre-fixed). Comparing the optimizer's chosen kW_DC across regimes is itself one of the headline findings.
- **DEC-003:** Both ownership models share the same physical system size and generation profile (PySAM output is regime-independent). Capex vs PPA differs only in cashflow allocation (post-processing).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Build medium-factory load profile and freeze inputs | None | `data/interim/vn_med_factory/load_profile_8760.json`, `vn_med_factory_inputs.json` |
| PHASE-02 | Encode Decision 963 TOU schedule and extend preprocessing tool | PHASE-01 | `data/vietnam/vn_tariff_2026.json` (v2026.1), updated `REoptVietnam.jl` and `preprocess.py`, unit tests |
| PHASE-03 | Generate PySAM 8760 PV production series for the site | PHASE-01 | `data/interim/vn_med_factory/pv_production_8760.csv`, sizing curve, validation plot |
| PHASE-04 | Run REopt twice (old TOU, new TOU) to optimize PV capacity (capex view) | PHASE-02, PHASE-03 | `artifacts/results/vn_med_factory/{old_tou,new_tou}_capex_reopt-results.json` |
| PHASE-05 | Build offtaker and developer cashflow models for capex and PPA, both regimes | PHASE-04 | `artifacts/reports/vn_med_factory/financial_summary.csv`, `cashflow_*.csv` |
| PHASE-06 | Run sensitivity sweep and emit HTML comparison report | PHASE-05 | `artifacts/reports/vn_med_factory/tou_comparison_report.html` |

## Detailed Phases

### PHASE-01 - Medium-factory load profile and input freeze
**Goal**
Produce a 8760 hourly kW load series and the canonical input dict for a ~10 GWh/yr Vietnamese medium factory, derived by scaling the saigon18 shape so the realism of an actual Vietnam industrial load is preserved.

**Tasks**
- [ ] TASK-01-01: Create `scripts/python/integration/build_vn_med_factory_load.py` modeled on `build_north_thuan_load_profile.py`. Read `data/interim/saigon18/2026-03-20_saigon18_extracted_inputs.json["loads_kw"]` (8760 array, ~21 MW avg / 30 MW peak / 184 GWh/yr) and scale uniformly by `target_annual_kwh / source_annual_kwh` with `target_annual_kwh = 10_000_000` (10 GWh).
- [ ] TASK-01-02: Validate the scaled profile shape: peak ≈ 1.6 MW, avg ≈ 1.14 MW, load factor ≈ 0.65–0.75. Write `data/interim/vn_med_factory/load_profile_8760.json` with `{"loads_kw": [...], "year": 2025, "source": "saigon18 scaled to 10 GWh/yr"}`.
- [ ] TASK-01-03: Clone `scenarios/templates/vn_industrial_pv_storage.json` to `scenarios/templates/vn_med_factory_pv_only.json`. Remove the `ElectricStorage` block. Set `Site.roof_squarefeet = 32000` (~3,000 m² — sized to host ~2 MW DC at 6.7 m²/kW), `ElectricLoad.year = 2025`, replace `doe_reference_name` + `annual_kwh` with `loads_kw` from PHASE-01-02. Set `Site.latitude = 10.9577`, `Site.longitude = 106.8426` (Binh Duong industrial corridor). Set `PV.max_kw = 2500` to allow optimizer headroom; `PV.min_kw = 0`.
- [ ] TASK-01-04: Write `data/interim/vn_med_factory/vn_med_factory_inputs.json` capturing the canonical sizing assumptions: customer_type=`industrial`, voltage=`medium_voltage_22kv_to_110kv`, region=`south`, financial defaults from ASM-005 / ASM-006.

**Files / Surfaces**
- `scripts/python/integration/build_vn_med_factory_load.py` — new builder script.
- `scenarios/templates/vn_med_factory_pv_only.json` — new no-storage template.
- `data/interim/vn_med_factory/` — new directory for medium-factory artifacts.

**Dependencies**
- None.

**Exit Criteria**
- [ ] Load profile JSON loads cleanly into `numpy.array` length 8760.
- [ ] Annual sum within ±0.1% of 10,000,000 kWh; peak between 1.4–1.8 MW; min positive (no zeros that would imply outage).
- [ ] Cloned template passes `apply_vietnam_defaults` without error using `customer_type="industrial"`.

**Phase Risks**
- **RISK-01-01:** Saigon18 shape may be more weekday-cyclic than a typical medium factory. Mitigation: report the load factor and weekday/weekend split in the output JSON's metadata; if outlier, also produce a smoothed 1-hr rolling variant for sensitivity.

### PHASE-02 - Decision 963 TOU schedule and preprocessing extension
**Goal**
Encode the new TOU windows in versioned tariff data and let both Julia and Python preprocessing tools select between regimes via a `tou_regime` argument.

**Tasks**
- [ ] TASK-02-01: Create `data/vietnam/vn_tariff_2026.json` (v`2026.1`) by copying `vn_tariff_2025.json` and adding a `tou_schedule_decision_963` block under `data.tou_schedule`. Map Decision 963 windows to hour arrays: weekday `peak_hours = [17,18,19,20,21,22]` (covers 17:30–22:30 with the documented half-hour discretization caveat), `standard_hours = [6,7,8,9,10,11,12,13,14,15,16,23]`, `offpeak_hours = [0,1,2,3,4,5]`. Sunday/holiday: `peak_hours = []`, `standard_hours = [6..23]`, `offpeak_hours = [0..5]`.
- [ ] TASK-02-02: Keep the existing Decision 14/2025 schedule under a clearly named key (`tou_schedule_decision_14_2025`) and rename the `tou_schedule` top-level key to a default pointer that selects one of the two; preserve backward compatibility by aliasing the legacy `tou_schedule` to `tou_schedule_decision_14_2025`.
- [ ] TASK-02-03: Update `data/vietnam/manifest.json` to reference `vn_tariff_2026.json` for the `tariff` slot.
- [ ] TASK-02-04: Add a `tou_regime` keyword argument (default `"decision_14_2025"`) to `apply_vietnam_defaults` in both `src/julia/REoptVietnam.jl` and `src/python/reopt_pysam_vn/reopt/preprocess.py`. The function selects the matching hour arrays before building the 8760 `tou_energy_rates_per_kwh` series.
- [ ] TASK-02-05: Add unit tests: `tests/python/reopt/test_tou_regimes.py` and `tests/julia/test_tou_regimes.jl` verifying that (a) `decision_14_2025` produces peak-rate hours at 9,10,17,18,19; (b) `decision_963_2026` produces peak-rate hours at 17,18,19,20,21,22; (c) both regimes agree on multipliers (Decision 14 multipliers held constant per ASM-002); (d) Sundays show no peak in either regime.
- [ ] TASK-02-06: Cross-validate Julia vs Python output for one full 8760 series under each regime in `tests/cross_language/`.

**Files / Surfaces**
- `data/vietnam/vn_tariff_2026.json` — new versioned tariff with both TOU schedules.
- `data/vietnam/manifest.json` — bump tariff pointer.
- `src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/reopt/preprocess.py` — add `tou_regime` kwarg.
- `tests/python/reopt/test_tou_regimes.py`, `tests/julia/test_tou_regimes.jl`, `tests/cross_language/test_tou_regimes_cross.py` — new tests.

**Dependencies**
- PHASE-01 (template references the regime indirectly via `apply_vietnam_defaults`).

**Exit Criteria**
- [ ] All four layers of the test suite pass: `.\tests\run_all_tests.ps1` green.
- [ ] Spot-check: `apply_vietnam_defaults(d, vn; customer_type="industrial", tou_regime="decision_963_2026")` produces a `tou_energy_rates_per_kwh` series whose hour-of-day average over weekdays peaks at 18:00–22:00 (1.57× base) and is flat-low at 00:00–06:00 (0.56× base).
- [ ] No regression on existing saigon18 / ninhsim baselines (those continue to use `decision_14_2025`).

**Phase Risks**
- **RISK-02-01:** Hourly discretization of 17:30 and 22:30 boundaries shifts ±30 min of value into peak in the model vs reality. Mitigation: document the bias direction (model slightly **over**states new-peak revenue because hour 17 is fully tagged peak when only its second half is) and state in the report that magnitudes are directional, not transactional.

### PHASE-03 - PySAM PV production simulation
**Goal**
Generate an 8760 hourly AC kW production series per kW DC for the site, using PySAM PVWattsv8 with NREL NSRDB / TMY data, so the same generation profile can be reused across all REopt and post-processing runs.

**Tasks**
- [ ] TASK-03-01: Create `scripts/python/pysam/run_vn_med_factory_pvwatts.py` modeled on `run_single_owner_smoke.py`. Use the NREL Developer API with the keys in `NREL_API.env` to fetch a TMY/PSM3 file for (10.9577, 106.8426) and cache to `data/interim/pysam_resources/vn_binh_duong_psm3.csv`.
- [ ] TASK-03-02: Configure PVWattsv8: `system_capacity = 1.0 kW DC` (unit normalized — REopt scales by its sized kW), `module_type = 1` (premium), `array_type = 1` (fixed roof mount), `tilt = 11`, `azimuth = 180`, `losses = 14`, `dc_ac_ratio = 1.2`, `gcr = 0.4`, `inv_eff = 96`. Match the REopt template values from PHASE-01-03.
- [ ] TASK-03-03: Run the simulation and persist the 8760 hourly AC output to `data/interim/vn_med_factory/pv_production_8760.csv` with columns `[hour_of_year, ac_kw_per_kw_dc]`. Persist the annual specific yield (kWh/kWp/yr) — expected ~1,400–1,550 for southern Vietnam — to `pv_production_metadata.json`.
- [ ] TASK-03-04: Sanity-check generation alignment vs TOU: compute the % of annual generation that falls in `decision_14_2025` peak hours vs `decision_963_2026` peak hours. Expected: ~10–15% under old TOU (morning peak captures midday ramp), ~0% under new TOU (peak starts at 17:30, post-dusk year-round at 11°N). This single number quantifies the structural finding from the research brief and goes into the report.
- [ ] TASK-03-05: Optional: produce a side-by-side hourly heatmap (8760 reshaped 24×365) overlaying old and new peak windows on the generation profile. Save as `artifacts/reports/vn_med_factory/pv_tou_overlay.png`.

**Files / Surfaces**
- `scripts/python/pysam/run_vn_med_factory_pvwatts.py` — new runner.
- `data/interim/vn_med_factory/pv_production_8760.csv` — production series.
- `data/interim/vn_med_factory/pv_production_metadata.json` — yield, % in each regime's peak.
- `data/interim/pysam_resources/vn_binh_duong_psm3.csv` — cached weather file.
- `artifacts/reports/vn_med_factory/pv_tou_overlay.png` — diagnostic plot.

**Dependencies**
- PHASE-01 (site lat/lon and design parameters frozen).

**Exit Criteria**
- [ ] Annual specific yield within 1,300–1,600 kWh/kWp (sanity bound for southern Vietnam fixed-tilt rooftop).
- [ ] PySAM run completes in under 60s.
- [ ] % of annual generation in new-TOU peak hours documented as <2% (research brief prediction).

**Phase Risks**
- **RISK-03-01:** NREL NSRDB coverage at 10.9577°N may force a fallback to the next-nearest station; document the actual coordinates used and any difference.

### PHASE-04 - REopt capacity optimization (capex view) under both TOU regimes
**Goal**
Run REopt twice with identical inputs except the TOU regime, letting the optimizer pick PV capacity. The "capex view" is the canonical REopt output where the offtaker is also the system owner; the resulting capacity and dispatch are then reused unchanged for the PPA case in PHASE-05.

**Tasks**
- [ ] TASK-04-01: Build `scenarios/case_studies/vn_med_factory/2026-04-25_old_tou_capex.json` and `2026-04-25_new_tou_capex.json` from the PHASE-01 template. Each scenario sets the appropriate `tou_regime` flag passed through `apply_vietnam_defaults`. Confirm `ElectricLoad.loads_kw` is wired from `data/interim/vn_med_factory/load_profile_8760.json`.
- [ ] TASK-04-02: Execute `scripts/julia/run_vietnam_scenario.jl --scenario <path>` for each of the two scenarios. Outputs land in `artifacts/results/vn_med_factory/{old_tou,new_tou}_capex_reopt-results.json`.
- [ ] TASK-04-03: Extract from each result: optimal `PV.size_kw_dc` and `size_kw_ac`, year-1 generation kWh, year-1 grid imports kWh by TOU bucket (peak/std/offpeak), year-1 utility bill VND, year-1 utility bill savings VND, capex VND, NPV VND, simple payback years, IRR.
- [ ] TASK-04-04: Build a `compare_tou.py` post-processing script under `scripts/python/integration/` that loads both result files and produces `artifacts/reports/vn_med_factory/capex_comparison.csv` with one row per metric and columns `[old_tou, new_tou, delta_abs, delta_pct]`.
- [ ] TASK-04-05: Validate the structural prediction: optimal kW_DC under new TOU should be **lower** than under old TOU by 5–15% (research brief). If this does not hold, pause and review whether multipliers under ASM-002 created an unexpected incentive — this is the first sanity gate.

**Files / Surfaces**
- `scenarios/case_studies/vn_med_factory/` — new scenario directory.
- `artifacts/results/vn_med_factory/` — REopt output directory.
- `scripts/python/integration/compare_tou.py` — new comparison utility.
- `artifacts/reports/vn_med_factory/capex_comparison.csv` — one of the two headline tables.

**Dependencies**
- PHASE-02 (TOU regimes must be selectable), PHASE-03 (production data implicit via REopt's PVWatts call — REopt fetches its own NSRDB by default; cross-check yield against PHASE-03's PySAM yield to within 3% to flag any divergence).

**Exit Criteria**
- [ ] Both scenarios solve to optimal status (no infeasible / time-limit returns).
- [ ] Optimal kW_DC differs between regimes (non-trivial sensitivity); if they're identical, investigate.
- [ ] `capex_comparison.csv` populated with all eight metrics enumerated in TASK-04-03.

**Phase Risks**
- **RISK-04-01:** REopt's internal PVWatts may diverge from PHASE-03's PySAM yield because of resource-file or model differences. Mitigation: log both yields, accept up to 3% divergence, document the chosen authoritative source for downstream PPA cashflows (use REopt's dispatch for the bill calculation; use PySAM's series for the developer revenue sanity check).
- **RISK-04-02:** Without storage, REopt may oversize PV and rely on `can_curtail = true` to drop midday excess. Confirm year-1 curtailment is non-negative and report it; high curtailment under new TOU is itself a finding.

### PHASE-05 - Offtaker and developer cashflow models (capex + PPA, both regimes)
**Goal**
Convert REopt outputs into four-by-two financial cases (capex/PPA × old/new TOU) for both stakeholders and produce a single comparison CSV.

**Tasks**
- [ ] TASK-05-01: Create `scripts/python/integration/build_vn_med_factory_financials.py` reusing the structure of `equity_irr.py` and `dppa_settlement.py`. For **capex/self-ownership**: offtaker pays year-0 capex, receives 25 years of bill savings (from REopt), pays O&M (3%/yr escalation). Compute offtaker NPV @ 10%, IRR, simple/discounted payback. Developer side: N/A.
- [ ] TASK-05-02: For **opex/PPA**: developer pays year-0 capex, receives 25 years of `PPA_price × generation` (1.5%/yr escalation per ASM-003), pays O&M (3%/yr), pays CIT 20% on net income. Compute developer NPV @ 8%, IRR, levelized cost of energy (LCOE), and post-tax cashflow series. Offtaker side: pays `PPA_price × generation` plus residual grid import bill (from REopt's grid-import series); offtaker savings = (counterfactual all-grid retail bill) − (PPA payments + residual grid bill). Compute offtaker NPV of savings @ 10% and effective blended VND/kWh.
- [ ] TASK-05-03: Run all four × two cases and emit `artifacts/reports/vn_med_factory/financial_summary.csv` with columns: `[scenario, ownership, tou_regime, year1_revenue_or_savings_vnd, year1_om_vnd, lifetime_npv_vnd, irr_pct, payback_years, lcoe_vnd_per_kwh]`. Also emit per-case 25-year cashflow CSVs (`cashflow_<scenario>.csv`) for traceability.
- [ ] TASK-05-04: Cross-check capex-mode offtaker IRR against REopt's own reported IRR/NPV (if available) — they should agree within 1% absolute IRR; deviations indicate a missed cost line.
- [ ] TASK-05-05: Compute the headline deltas and write them to `artifacts/reports/vn_med_factory/headline_deltas.json`:
  - Δ Offtaker year-1 savings (capex): new vs old TOU
  - Δ Offtaker year-1 savings (PPA): new vs old TOU
  - Δ Developer IRR (PPA): new vs old TOU
  - Δ Optimal kW_DC: new vs old TOU
  - Δ Effective LCOE for PPA: new vs old TOU

**Files / Surfaces**
- `scripts/python/integration/build_vn_med_factory_financials.py` — new financial post-processor.
- `artifacts/reports/vn_med_factory/financial_summary.csv` — primary output.
- `artifacts/reports/vn_med_factory/cashflow_*.csv` — eight per-case cashflows.
- `artifacts/reports/vn_med_factory/headline_deltas.json` — five-number summary.

**Dependencies**
- PHASE-04 (REopt sizing + dispatch + bill outputs).

**Exit Criteria**
- [ ] All eight cases produce non-NaN IRR and NPV values.
- [ ] Capex-mode offtaker IRR matches REopt's reported IRR within 1pp.
- [ ] Developer LCOE under PPA mode is below the assumed strike price (1,800 VND/kWh) under old TOU; check if it remains below under new TOU — this determines whether the PPA strike needs repricing.
- [ ] Headline deltas align with research-brief direction: developer IRR drops, offtaker savings drop, optimal kW falls under new TOU.

**Phase Risks**
- **RISK-05-01:** Counterfactual bill (all-grid) must use the same TOU regime as the with-PV bill — comparing old-TOU counterfactual vs new-TOU with-PV would conflate window change with policy change. The script must run **two separate counterfactuals**, one per regime, and only compare savings within the same regime. Build a clear test for this.

### PHASE-06 - Sensitivity sweep and HTML comparison report
**Goal**
Surface the result-sensitivity to the two largest open assumptions (multiplier re-issuance, PPA strike price) and emit a single self-contained HTML report.

**Tasks**
- [ ] TASK-06-01: Add a multiplier-sensitivity scenario set: under `tou_regime = decision_963_2026`, run a second REopt with multipliers shifted to (peak 1.85, std 0.92, off-peak 0.45) — encoding VietnamSolar.vn's "80–100% above normal, 2.5–3× off-peak" hint. Compare against the ASM-002 base case to show the spread between "windows-only" and "windows + repriced multipliers" interpretations.
- [ ] TASK-06-02: Add a PPA strike-price sweep at 1,500 / 1,800 / 2,100 VND/kWh under both TOU regimes; report developer IRR and offtaker savings at each. Identifies the regime-specific break-even strike.
- [ ] TASK-06-03: Extend `scripts/python/integration/generate_html_report.py` (or fork to `generate_vn_med_factory_tou_report.py`) to render `artifacts/reports/vn_med_factory/tou_comparison_report.html` with: (a) executive summary headline-deltas table, (b) PV TOU-overlay plot from PHASE-03, (c) capex comparison table, (d) PPA developer + offtaker tables, (e) sensitivity charts for TASK-06-01 and TASK-06-02, (f) caveats (ASM-002 status, hourly-discretization bias, no-storage-by-design).
- [ ] TASK-06-04: Final review pass: ensure all VND figures are presented in millions or billions for readability, all percentages are signed (Δ positive/negative), and every chart has a source caption pointing back to the originating CSV.

**Files / Surfaces**
- `scripts/python/integration/generate_vn_med_factory_tou_report.py` — new report generator (or extension of the shared one).
- `artifacts/reports/vn_med_factory/tou_comparison_report.html` — primary deliverable.
- `artifacts/reports/vn_med_factory/sensitivity_*.csv` — supporting tables.

**Dependencies**
- PHASE-05 (financial summary), PHASE-03 (TOU-overlay plot).

**Exit Criteria**
- [ ] HTML opens cleanly in a browser, all images embedded or relatively linked, no broken references.
- [ ] Both sensitivity findings narrated in plain English: multiplier-reissue effect (likely larger than windows alone) and strike-break-even (where PPA stops working).
- [ ] Caveats section explicitly states: (i) ASM-002 is unverified pending next MOIT circular, (ii) hourly discretization, (iii) no-storage-by-scope, (iv) on-site PPA only (not Decree 57 grid-DPPA).

**Phase Risks**
- **RISK-06-01:** Sensitivity multiplier values are inferred from a Vietnamese-language industry blog (VietnamSolar.vn), not an MOIT circular. Mitigation: present as a sensitivity, never as a base case, and label in-report as "illustrative pending official tariff reissue."

## Verification Strategy
- **TEST-001:** `.\tests\run_all_tests.ps1` (Layers 1–4) must pass after PHASE-02; specifically the new `test_tou_regimes.*` files must enforce the hour-array bindings for both regimes and the cross-language identity.
- **TEST-002:** Custom regression check in `tests/python/integration/test_vn_med_factory_smoke.py` that runs PHASE-04 and PHASE-05 end-to-end on a 1-week subset and asserts: optimal kW under new ≤ optimal kW under old; offtaker savings under new ≤ offtaker savings under old (capex mode); developer IRR under new ≤ developer IRR under old (PPA mode at fixed strike).
- **MANUAL-001:** Visual check of the PV-TOU overlay plot from PHASE-03: confirm zero PV output in the 17:30–22:30 band year-round.
- **MANUAL-002:** Open the HTML report and verify every headline-delta sign matches the research-brief expectation. Any reversal must be diagnosed before sign-off.
- **OBS-001:** Capture solver runtime, optimality status, and curtailment fraction in the result JSON metadata for both REopt runs; flag if curtailment exceeds 10% of generation under new TOU (would indicate PV is sized too aggressively despite the optimizer's nominal "optimal" status — possibly due to `can_curtail = true` masking economic curtailment).

## Risks and Alternatives
- **RISK-001:** ASM-002 (multipliers held constant) is the single biggest unverified input. If MOIT issues a revised tariff schedule for the new windows before publication, the base-case results become stale. Mitigation: keep PHASE-06 sensitivity infrastructure ready to swap in revised multipliers in <1 hour.
- **RISK-002:** Scaling saigon18 to 10 GWh/yr preserves shape but not necessarily the TOU-aligned consumption pattern of a "typical" medium factory (a single-shift factory ending at 17:00 is the best case under new TOU; a two-shift one extending past 22:30 is the worst). The scaled saigon18 shape is multi-shift / continuous, biasing the result toward the bad case for new TOU. Mitigation: run a single-shift sensitivity (load zeroed 17:30–06:00) in PHASE-06 if time permits, or at minimum flag the bias in the report.
- **RISK-003:** REopt's `can_wholesale = true` in the existing template would let surplus go to grid at zero or low value, distorting capex-mode IRR. Set `can_wholesale = false` in the new template per ASM-004; verify in PHASE-04.
- **ALT-001:** Use REopt's native third-party-ownership mode (`Financial.third_party_ownership = true`) instead of post-processing the PPA cashflows in Python. Rejected because the project's existing financial primitives (`equity_irr.py`, `dppa_settlement.py`) are better tested and produce the per-stakeholder breakouts the brief requires; REopt's TPO output bundles offtaker and developer into a single LCOE which obscures the comparison the user needs.
- **ALT-002:** Use the saigon18 case study at full scale. Rejected because saigon18 is a 184 GWh/yr utility-scale industrial, mismatched to the "medium factory" framing.
- **ALT-003:** Use a 30-min timestep solve to handle the 17:30 / 22:30 boundaries precisely. Rejected because it doubles solver runtime and the research brief already accepts the directional finding under hourly discretization.

## Grill Me
1. **Q-001: PPA strike price assumption.** ASM-003 sets the on-site PPA strike at 1,800 VND/kWh with 1.5% escalation. Real medium-factory rooftop PPAs in Vietnam in 2025–2026 cluster between 1,400–2,000 VND/kWh year-1 depending on credit and tenor.
   - **Recommended default:** 1,800 VND/kWh year-1 with 1.5%/yr escalation, plus a sensitivity sweep at 1,500 / 1,800 / 2,100 in PHASE-06.
   - **Why this matters:** Determines the absolute level of developer IRR and offtaker savings; the **delta** between regimes is roughly strike-invariant, but the question of whether the PPA still pencils under the new TOU at a given strike depends on this.
   - **If answered differently:** A lower strike (e.g., 1,500) would make the offtaker indifferent under new TOU but compress developer IRR below typical hurdle (10–12%), turning the headline finding into "PPA market repricing required."
2. **Q-002: Hard ceiling on PV size.** TASK-01-03 sets `PV.max_kw = 2500` based on roof area. A medium factory roof is typically 1,500–4,000 m², equivalent to ~225–600 kW DC at 6.7 m²/kW.
   - **Recommended default:** Set `PV.max_kw = 1500` and `Site.roof_squarefeet ≈ 100,000` (≈ 9,290 m² — a generous medium-factory roof) so the optimizer can pick a meaningful capacity rather than be roof-area-bound. Alternatively, fix `PV.size_kw = 1000` and skip optimization — but this loses the "optimized capacity" feature the request asked for.
   - **Why this matters:** If the roof is the binding constraint, the optimizer's TOU-driven capacity reduction (the headline finding) is masked.
   - **If answered differently:** A genuinely small roof (e.g., 2,000 m² → ~300 kW max) means the system is roof-constrained, capacity is identical under both regimes, and the headline becomes purely a revenue/savings comparison rather than a capacity comparison.
3. **Q-003: Voltage class.** ASM-001 sets medium voltage 22 kV (`medium_voltage_above_1kv_to_35kv`). Some medium factories sit at low voltage (≤1 kV) where peak multiplier is 1.68 vs 1.57.
   - **Recommended default:** Medium voltage 22 kV (most common for ≥1 MW factories in Vietnam industrial parks).
   - **Why this matters:** Low-voltage multipliers are ~7% higher peak / 8% higher standard, which proportionally amplifies all financial metrics but doesn't change directional findings.
   - **If answered differently:** Run as a side sensitivity in PHASE-06 if user prefers low-voltage framing.
4. **Q-004: Currency presentation.** Should the report present results in VND, USD (at 26,400 VND/USD), or both?
   - **Recommended default:** Both — VND as primary (matches tariff inputs), USD in a secondary column for international audiences.
   - **Why this matters:** Choice of unit affects readability and the perceived materiality of small differences.
   - **If answered differently:** USD-only would require persisting the FX assumption and a year-by-year FX path if more rigor is wanted.
5. **Q-005: Whether to include the Decree 57 surplus-export pathway as an alternative case.** ASM-004 holds no-export. Some medium factories with low Sunday load may economically prefer to export at the prior-year average market price.
   - **Recommended default:** Hold no-export base case; do not run an export sensitivity in this plan (out of scope per Out-of-Scope list).
   - **Why this matters:** Including export would partially restore the value lost by removing the morning peak (because surplus export is paid at a market reference, not at the peak retail rate).
   - **If answered differently:** Add a PHASE-06 sensitivity that allows up to 20% surplus export at the Decree 57 cap (1,012–1,382.7 VND/kWh) and report the impact on developer IRR and optimal capacity.
