# Phase 3 Completion + Consolidated HTML Report Plan
# Saigon18 REopt Vietnam Analysis

> **Prepared:** 2026-03-26
> **Based on:** Full review of `activeContext.md`, existing artifacts, test suite, and scenario results.
> **Goal:** Complete the remaining Phase 3 analytical work, then produce a single consolidated HTML visual report covering all four Saigon18 scenarios for review.

---

## Where Things Stand

### Already done (Phases 1 & 2 + most of Phase 3)

| What | Status |
|---|---|
| Data extraction from Excel workbook | Done |
| Scenario A — baseline EVN TOU, fixed sizing | Solved, results in `artifacts/results/saigon18/` |
| Scenario B — bundled PPA 15% discount | Solved |
| Scenario C — optimised sizing (unconstrained) | Solved 2026-03-23 |
| Equity IRR vs Excel (Scenario A: 19.8% vs 19.4%) | Done |
| Decree 57 hard export cap wired into Julia solver | Done |
| Comparison reports A/B vs Excel (markdown) | Done |
| Phase 2 HTML findings report | Done — `2026-03-23_phase2-findings.html` |

### Still open (Phase 3 remainder)

| What | Priority | Notes |
|---|---|---|
| **Scenario D — DPPA strike price contract** | HIGH | Not started — the most commercially relevant scenario |
| **Refresh comparison artifacts for A + C** | HIGH | Not regenerated after the hard export-cap reruns |
| **BESS dispatch comparison by tariff period** | HIGH | Current comparison uses total annual throughput; needs peak/standard/off-peak split to be apples-to-apples with Excel |
| `tests/python/integration/test_saigon18_integration.py` (Layer 4) | MEDIUM | Not started |
| Fixed BESS dispatch window constraints (Option B) | LOW | Only needed if you want to model the Excel control logic exactly |
| Two-part tariff sensitivity (Decree 146/2025) | LOW | Deferred — pilot not yet confirmed |

### Pending confirmations (from activeContext)

- [ ] Confirm site coordinates (currently lat=10.9577, lon=106.8426 — near HCMC)
- [ ] Confirm DPPA structure: private-wire or grid-connected (ceiling tariff differs)

---

## Phase 3 Completion Work

### Step 1 — Build and solve Scenario D (DPPA)

Scenario D uses the DPPA strike price contract instead of EVN TOU retail tariffs. The pipeline already has `dppa_settlement.py` for post-processing.

**Inputs needed:**
- `strike_price_usd_per_kwh` from the Saigon18 Excel model (~$0.069/kWh)
- `k_factor` (grid loss factor, ~1.02)
- `kpp` (voltage correction, ~1.027 for 110kV)
- FMP time series (already extracted to `data/interim/saigon18/...json`)
- DPPA structure: private-wire vs grid-connected — confirm before running

**What to do:**
1. Build `scenarios/case_studies/saigon18/YYYY-MM-DD_scenario-d_fixed-sizing_dppa.json` using `build_saigon18_reopt_input.py` with `--scenario d` flag.
2. Solve via `run_vietnam_scenario.jl --scenario <path>`.
3. Run `dppa_settlement.py` to apply DPPA CfD post-processing to REopt dispatch output.
4. Run `equity_irr.py` to compute levered equity IRR for Scenario D.
5. Run `compare_reopt_vs_excel.py --scenario "D (DPPA)"` to generate the comparison markdown.

**Expected output:** Equity IRR for DPPA scenario, NPV, and year-1 DPPA revenue figure to compare against Excel's $272K/yr DPPA revenue line.

---

### Step 2 — Refresh Scenario A and C comparison artifacts

The Scenario A and C comparison reports (`2026-03-22_scenario-a_vs_excel_comparison.md`) predate the hard export-cap reruns. The result JSON files were updated on 2026-03-23 but the reports were not regenerated.

**What to do:**
```powershell
python scripts/python/reopt/compare_reopt_vs_excel.py `
  --reopt artifacts/results/saigon18/2026-03-23_scenario-a_fixed-sizing_evntou_reopt-results.json `
  --scenario "A (fixed sizing EVN TOU)"

python scripts/python/reopt/compare_reopt_vs_excel.py `
  --reopt artifacts/results/saigon18/2026-03-23_scenario-c_optimized-sizing_reopt-results.json `
  --scenario "C (optimized sizing)"
```

Save both outputs as date-stamped markdown files in `artifacts/reports/saigon18/`.

---

### Step 3 — BESS dispatch comparison by tariff period

**Problem:** The current comparison shows REopt annual BESS throughput as 17,956 MWh vs Excel's 8,591 MWh — a 2× gap. But these numbers measure different things. REopt counts total storage-to-load energy. Excel counts only the BESS dispatch that happens during EVN peak+standard hours. Without splitting by tariff period, the comparison is not valid.

**What to do:**
1. Extend `compare_reopt_vs_excel.py` to disaggregate REopt `storage_to_load_series_kw` (8760-hour series) by EVN tariff period (off-peak / standard / peak) using the same `tou_energy_rates_per_kwh` schedule.
2. Report:
   - REopt BESS discharge during peak hours (MWh)
   - REopt BESS discharge during standard hours (MWh)
   - REopt BESS discharge during off-peak hours (MWh)
   - Excel equivalent figures
3. Update the comparison report to use the disaggregated figures.

**Why this matters:** The BESS dispatch strategy is the core model difference between REopt (free optimisation) and Excel (fixed time-window schedule). This analysis will show whether REopt is dispatching more value from the same battery or just cycling it differently.

---

### Step 4 — Add Layer 4 integration test

`tests/python/integration/test_saigon18_integration.py` is listed as not started. It should:
- Load the canonical Scenario A and C result JSONs from `artifacts/results/saigon18/`
- Assert key KPIs are within tolerance of the locked reference values in `activeContext.md`:
  - Scenario A: NPV within 5% of $10.55M, unlevered IRR within 0.5% of 12.6%, export fraction < 1%
  - Scenario C: PV size within 5% of 42,666 kW, IRR within 0.5% of 14.2%, export fraction < 10%
- Assert equity IRR within 1% of 19.8%
- This is the regression guard so future solver/data changes don't silently shift results.

---

## Phase 4 — Consolidated HTML Visual Report

The deliverable is a single self-contained HTML file:
`artifacts/reports/saigon18/YYYY-MM-DD_saigon18-full-analysis.html`

Open it in any browser — no server needed, no dependencies.

### Report sections

---

#### Section 1 — Project Overview

- Project name: Saigon18, 40.36 MWp + 66 MWh BESS, southern Vietnam
- Site: lat=10.9577, lon=106.8426 (HCMC area)
- Excel model reference: Equity IRR 19.4%, NPV $22M, 6-yr payback
- Analysis purpose: validate and challenge the Excel outputs using NREL REopt
- Report date, methodology note

---

#### Section 2 — Scenario Comparison Dashboard (4 cards)

One card per scenario with key headline numbers:

| Scenario | Sizing | Tariff | Status |
|---|---|---|---|
| A — Baseline EVN TOU | Fixed 40.36 MWp + 66 MWh | Full EVN TOU | Solved |
| B — Bundled PPA | Fixed (same) | EVN × 0.85 | Solved |
| C — Optimised sizing | Unconstrained (REopt chose 42.67 MWp + 0 BESS) | Full EVN TOU | Solved |
| D — DPPA contract | Fixed (same as A) | DPPA CfD strike price | To be solved |

Each card shows: NPV, Payback, Unlevered IRR, status badge.

---

#### Section 3 — Financial KPIs Comparison Table

Side-by-side table: Excel vs Scenario A vs B vs C vs D

| Metric | Excel | A | B | C | D |
|---|---|---|---|---|---|
| NPV ($M) | 22.0 | 10.6 | 0.89 | 11.8 | TBD |
| Unlevered IRR | — | 12.6% | — | 14.2% | TBD |
| Equity IRR | 19.4% | 19.8% | — | TBD | TBD |
| Simple payback (yr) | 6.0 | 8.0 | 10.2 | 7.5 | TBD |
| Year-1 savings ($M) | 5.06 | 5.93 | 4.98 | TBD | TBD |

Cells coloured green (within 10% of Excel), amber (10–30% delta), red (>30% delta).

---

#### Section 4 — Energy Flow Bar Charts

Horizontal bar charts (pure CSS/SVG — no JS libraries) for:

1. **Annual PV production by scenario** — shows how optimised sizing (C) changes output
2. **PV self-consumption vs export vs curtailed** — Decree 57 compliance visible
3. **BESS dispatch by tariff period** (once Step 3 above is done) — peak / standard / off-peak breakdown
4. **Grid purchases** — REopt vs Excel baseline

---

#### Section 5 — Equity IRR Deep Dive

- Box showing Excel IRR (19.4%) vs REopt-derived IRR (19.8%) with delta badge
- Explanation of the methodology: REopt provides year-1 savings, equity IRR script builds the leveraged cash flow waterfall
- Key assumptions table: CAPEX, debt tenor, interest rate, CIT schedule, DSCR

---

#### Section 6 — Decree 57 Compliance

- Summary: Decree 57 caps annual PV export at 20% of annual PV production
- Scenario A: export fraction 0.80% (well within cap) — green badge
- Scenario C: export fraction 6.47% — green badge
- Validation run: export fraction exactly 20.00% confirmed by Julia integration test

---

#### Section 7 — Model Comparison: Where REopt Differs from Excel

Table of the major gaps found during this analysis:

| Metric | Excel | REopt | Gap | Explanation |
|---|---|---|---|---|
| NPV | $22.0M | $10.6M | −52% | Excel uses levered DPPA/DPPA+grid hybrid; REopt uses TOU savings only |
| BESS throughput | 8,591 MWh | 17,956 MWh | +109% | REopt optimises freely; Excel follows fixed time window |
| Year-1 savings | $5.06M | $5.93M | +17% | REopt TOU optimisation captures more peak value |
| PV export | 1,087 MWh | 549 MWh | −50% | Decree 57 cap binding in Excel; REopt cap at 20% |

---

#### Section 8 — Findings and Recommendations

Plain-language interpretation:

1. **The Excel equity IRR (19.4%) is credible** — REopt confirms 19.8% using independent methodology (+0.4% delta).
2. **The Excel NPV ($22M) is overstated** — REopt's $10.6M (TOU baseline) suggests the DPPA revenue premium accounts for roughly $11M of the Excel NPV gap; this will be confirmed when Scenario D is solved.
3. **Optimised sizing (Scenario C)** would select 42.67 MWp PV with no BESS — a higher IRR (14.2% vs 12.6%) but the BESS has strategic value not captured by cost optimisation alone (resilience, peak demand management).
4. **Decree 57 export cap is not binding** for this project — export fraction is <1% in Scenario A, leaving room for more solar.
5. **Next step:** Solve Scenario D (DPPA) to close the NPV gap analysis.

---

#### Section 9 — Outstanding Items and Pending Confirmations

Checklist of open items from `activeContext.md`:
- [ ] Confirm site coordinates
- [ ] Confirm DPPA structure (private-wire vs grid-connected)
- [ ] Scenario D solve
- [ ] Two-part tariff sensitivity (Decree 146/2025 pilot)

---

### HTML report implementation approach

The report should be built by a Python script:
`scripts/python/integration/generate_html_report.py`

This script:
1. Loads all result JSONs from `artifacts/results/saigon18/`
2. Loads equity IRR summary from `artifacts/reports/saigon18/2026-03-22_equity-irr_summary.json`
3. Loads comparison markdown reports
4. Computes any derived figures (delta %, bar chart widths, badge colours)
5. Renders everything into a single self-contained HTML file using Python f-strings (no Jinja2 dependency)
6. Writes to `artifacts/reports/saigon18/YYYY-MM-DD_saigon18-full-analysis.html`

**Style:** Follow the same visual language as `2026-03-23_phase2-findings.html` — blue/green/amber/red colour scheme, cards, bar charts, tables with coloured cells, badge pills. All CSS inline. No JavaScript. Opens instantly in any browser.

---

## Execution Order

```
1. Confirm DPPA structure (private-wire vs grid-connected)   ← needs your input
2. Build Scenario D scenario JSON
3. Solve Scenario D (Julia)
4. Run DPPA settlement post-processing (Python)
5. Compute equity IRR for Scenario D
6. Refresh Scenario A + C comparison reports
7. Add BESS tariff-period disaggregation to compare script
8. Write test_saigon18_integration.py (Layer 4)
9. Run full test suite — confirm all layers pass
10. Write generate_html_report.py
11. Run it → open HTML report in browser
12. Review and iterate
```

---

## Key Reference Numbers (lock these in the report)

| Metric | Value | Source |
|---|---|---|
| Excel equity IRR | 19.4% | `data/raw/saigon18/` workbook |
| REopt equity IRR (Scenario A) | 19.8% | `2026-03-22_equity-irr_summary.json` |
| REopt NPV (Scenario A) | $10.6M | Scenario A results JSON |
| REopt NPV (Scenario B) | $0.89M | Scenario B results JSON |
| REopt NPV (Scenario C) | $11.8M | Scenario C results JSON |
| Scenario A export fraction | 0.80% | Scenario A results JSON |
| Scenario C PV size | 42,666 kW | Scenario C results JSON |
| Scenario C BESS size | 0 kW / 0 kWh | Scenario C results JSON — REopt chose no BESS |
| Decree 57 cap | 20% annual export fraction | `vn_export_rules_decree57.json` |
