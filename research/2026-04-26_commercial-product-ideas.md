---
title: "Three Commercial Product Concepts for the REopt-PySAM-VN Repo (DPPA + TOU Analysis)"
date: "2026-04-26"
modes: domain, codebase
depth: standard
invocation: "/research i want to have 3 ideas that will further develop this repo into commercial project that offtakers and developers can use for dppa and new tou analysis. each ideas will be capable of spawning multiphase plan on its own"
---

# Research Brief: Three Commercial Product Concepts for REopt-PySAM-VN

**Date:** 2026-04-26
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Identify three commercial-product directions that build on the current repo so that Vietnamese C&I offtakers and IPP/EPC developers can self-serve DPPA structuring and new-TOU (Decision 963/QĐ-BCT) impact analysis. Each idea must be large enough to spawn its own multi-phase plan.

---

## Synthesis

The repo today is a research-grade toolkit: REopt.jl + PySAM with Vietnam preprocessing (`src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/reopt/preprocess.py`), versioned policy data under `data/vietnam/`, four scenario templates, and case studies (saigon18, ninhsim, north_thuan, emivest, regina, verdant) wired through Python post-processors (`scripts/python/dppa_settlement.py`, `equity_irr.py`, `bess_dispatch_analysis.py`) into HTML reports (`generate_html_report.py`, `generate_cross_project_dashboard.py`). Two regulatory tailwinds — Decree 57/2025 enabling physical and virtual DPPAs and Decision 963/QĐ-BCT (Apr 2026) collapsing the TOU peak to a single 17:30–22:30 window ([VietnamNet](https://vietnamnet.vn/en/vietnam-adjusts-power-peak-hours-amid-rising-electricity-demand-2509795.html); [Vietnam Briefing](https://www.vietnam-briefing.com/news/vietnam-renewable-energy-decree-57.html/)) — create immediate willingness-to-pay among offtakers and developers for structured analysis tools.

Three commercial directions sit naturally on top of the existing assets, each non-overlapping in scope and large enough to drive its own multi-phase plan: (1) a **DPPA Deal Screener** SaaS layer that turns one-off case studies into a self-service buyer/developer workflow; (2) a **TOU Regime Sensitivity Engine** that productizes the policy-data + preprocessing layer into a regulatory scenario library covering Decision 963, the draft 50% surplus rule, and the two-part tariff trial; (3) a **Bankability & Settlement Studio** that promotes `dppa_settlement.py` + `equity_irr.py` into a lender-grade module with FMP/KPP/CfD simulation, Monte Carlo risk, and audit-traceable cashflow waterfalls.

The recommended sequencing is **Idea 2 first** (lowest engineering risk, highest immediate market relevance because Decision 963 just landed and offtakers need answers), then **Idea 3** (extends what is already the repo's most mature post-processing code), then **Idea 1** (builds on top of both as a customer-facing surface). All three should reuse the existing 4-layer test suite and the versioned `data/vietnam/manifest.json` discipline so commercial pricing can rest on a defensible compliance story.

[NOTE] None of these ideas requires altering REopt.jl itself; all extend the Vietnam-specific layer the repo already owns, which keeps maintenance burden bounded and IP defensible.

---

## Domain

### Discovery

Two regulatory developments anchor commercial demand. **Decree 57/2025** legalizes both physical-wire and virtual/CfD DPPAs in Vietnam, with separate ceiling tariffs, a 20% rooftop surplus-export cap, and BESS technical thresholds for incentive eligibility ([Vietnam Briefing](https://www.vietnam-briefing.com/news/vietnam-renewable-energy-decree-57.html/); [Duane Morris](https://blogs.duanemorris.com/vietnam/2026/02/26/vietnam-investing-in-solar-projects-with-dppa-and-bess-what-you-must-know/)). **Decision 963/QĐ-BCT** (22 Apr 2026) replaces the split TOU with a single 17:30–22:30 evening peak Mon–Sat ([VietnamNet](https://vietnamnet.vn/en/vietnam-adjusts-power-peak-hours-amid-rising-electricity-demand-2509795.html); prior brief `research/2026-04-25_vietnam-tou-rooftop-ppa.md`). Two further forward signals: a draft MOIT consultation raising rooftop surplus-export cap toward 50% ([B-Company](https://b-company.jp/vietnam-rooftop-solar-draft-rules-2026-selling-up-to-50-surplus-power-who-benefits-and-what-to-watch-next)) and a separate BESS capacity-style tariff in development ([Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/1d041eb0/vietnam-power-sector-snapshot)).

Buyer-side and developer-side personas differ sharply. C&I offtakers (manufacturing, data centers, F&B) want avoided-cost screening, contract-term sensitivity, and a credible bill-impact narrative. IPP/EPC developers want sizing optimization, strike-price discovery, FMP/KPP settlement risk, and a lender-credible IRR/DSCR pack ([IEEFA on DPPA decree](https://ieefa.org/resources/vietnams-direct-power-purchase-agreement-dppa-decree-could-catalyze-new-era-renewable)).

### Verification

The two regulatory anchors are triple-sourced (see prior brief, Sec. Domain Verification). Persona/needs split is consistent across the three commercial law-firm and consultancy write-ups cited above. No source provides quantitative WTP for self-service tooling — flag as inferred rather than measured.

### Comparison

Two adjacent products exist but neither is Vietnam-localized: **Aurora Solar** and **Energy Toolbase** dominate US C&I solar+storage proposal/economics tooling (general web knowledge, unverified pricing). Neither encodes EVN tariffs, Decree 57, or Decision 963. NREL's **REopt Web Tool** is free but US-centric and does not expose DPPA settlement or Vietnam-specific cost curves. The competitive gap is therefore **Vietnam regulatory fidelity + DPPA settlement math**, which is exactly what this repo already encodes.

### Synthesis

The defensible commercial wedge is regulatory-data + DPPA-settlement specialization — not a generic solar calculator. Each idea below exploits this wedge in a different way: as a sensitivity engine, as a bankability product, or as a self-serve buyer/developer surface. They compose: Idea 2 supplies the policy fabric, Idea 3 supplies the cashflow engine, Idea 1 supplies the user experience.

### Confidence

**Medium-High.** Regulatory anchors are well-sourced; commercial WTP is inferred from persona analysis rather than measured.

---

## Codebase

### Discovery

Repo structure shows three already-mature layers that each map to one commercial idea (`README.md`; `plans/active/`):

- **Policy/preprocessing layer:** `data/vietnam/{vn_tariff_2025.json, vn_export_rules_decree57.json, vn_tech_costs_2025.json, vn_financial_defaults_2025.json, vn_emissions_2024.json}`, `data/vietnam/manifest.json`, `src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/reopt/preprocess.py`. Versioned, dual-language (Julia/Python), with cross-validation tests in `tests/cross_language/`.
- **Settlement/finance layer:** `scripts/python/dppa_settlement.py`, `equity_irr.py`, `bess_dispatch_analysis.py`, `compare_reopt_vs_excel.py`, plus the ninhsim DPPA case-study ladder (`analyze_ninhsim_dppa_case_1.py`, ..._case_2, ..._case_3, …). Already exercised against real EPC-grade Excel models (saigon18, north_thuan).
- **Reporting layer:** `scripts/python/generate_html_report.py`, `generate_cross_project_dashboard.py`, `generate_ninhsim_dppa_case_1_report.py` (and phase variants). HTML output usable as client deliverables; one prior Plan (`pysam_integration_reorg_plan.md`) already defined the integration structure.

Active multi-phase plans demonstrate the team's pattern of phased delivery: `dppa_case_1_plan.md` through `dppa_case_3_plan.md`, `2026-04-23-dppa-case-4-real-project-bridge-plan.md`, and `2026-04-25-vn-tou-rts-comparison-plan.md`. The TOU comparison plan (Decision 14 vs 963) directly seeds Idea 2.

### Verification

All paths above were directly enumerated in this session (see `ls` and `Read` of `README.md`, `plans/active/`, `scripts/python/`, `data/vietnam/`). The 4-layer test suite (data validation, unit, cross-language, integration) is documented in `README.md` and runnable via `tests/run_all_tests.ps1`. No ambiguity about which assets exist.

### Comparison

The three layers are loosely coupled: preprocessing has no dependency on settlement; settlement has no dependency on the HTML reporter. This is the structural reason each commercial idea can spawn an independent multi-phase plan without entangling the others.

### Synthesis

The codebase is already arranged in three commercial-ready slices. Productization work is mostly **packaging, scenario coverage, UX, and pricing** — not core algorithmic R&D. Each idea below names the existing modules it builds on and what it adds.

### Confidence

**High.** All cited files exist in the working tree.

---

## Idea 1 — DPPA Deal Screener (offtaker + developer SaaS)

**One-line value proposition.** A self-service web app where a C&I offtaker uploads a load curve (or selects an industry archetype) and a developer enters a candidate site, and receives a full DPPA structuring report (capex/opex IRR, NPV, strike-price band, regulatory fit, sensitivity tornado) for both physical-wire and virtual/CfD models under Decree 57/2025.

**What it builds on (existing).** `scenarios/templates/vn_*.json` (4 templates), `apply_vietnam_defaults` in both languages, `scripts/python/build_*_reopt_input.py` (saigon18/ninhsim/north_thuan ingestion patterns), `generate_html_report.py`, `generate_cross_project_dashboard.py`.

**What it adds (commercial scope).**
1. Multi-tenant web frontend (auth, project workspaces, project sharing).
2. Load-curve ingestion: Excel/CSV upload + industry-archetype library (factory single-shift, factory two-shift, mall, hospital, data center) derived from the existing case studies.
3. Site-data service: lat/long → PVWatts profile via existing PySAM scaffolding; aggregator/grid voltage class lookup.
4. Scenario engine: REopt batch runner with queueing; deterministic scenario hashing for caching.
5. Output: branded PDF/HTML report, side-by-side capex vs PPA vs CfD, exportable cashflow workbook.
6. Billing, NRE/AE workflow, customer-success scaffolding.

**Multi-phase plan seed (5 phases).** P1 schema + auth + storage; P2 ingestion (load + site); P3 scenario engine + REopt queue; P4 reporting + PDF; P5 billing + tenant admin.

**Why it works.** Closest competitors (Aurora Solar, Energy Toolbase) lack EVN/Decree-57 fidelity; NREL REopt Web Tool lacks DPPA settlement. Persona clarity (offtaker vs developer) supports two-sided pricing. Highest engineering scope but highest commercial leverage.

**Risks.** Largest engineering surface; SaaS reliability and SOC-equivalent posture become required, not optional.

---

## Idea 2 — Vietnam TOU & Regulatory Scenario Engine

**One-line value proposition.** A modular "what-if" engine that lets a developer or analyst run any project under any regulatory regime — Decision 14/2025 (old TOU), Decision 963/QĐ-BCT (new TOU), draft 50% surplus rule, two-part tariff trial, BESS capacity payment — and produce a deterministic side-by-side comparison.

**What it builds on (existing).** `data/vietnam/manifest.json` versioning discipline, `vn_tariff_2025.json`, `vn_export_rules_decree57.json`, the dual-language `apply_vietnam_defaults` pipeline, the in-flight `2026-04-25-vn-tou-rts-comparison-plan.md` (Decision 14 vs 963 medium-factory comparison) which is exactly Phase-0 of this idea, and the `tests/cross_language/` parity harness.

**What it adds (commercial scope).**
1. **Regime registry:** machine-readable encoding of every Vietnam regulatory regime as a versioned JSON bundle (TOU windows, multipliers, export caps, surplus rates, BESS thresholds, ceiling tariffs). Regime IDs become first-class arguments to preprocessing.
2. **Scenario combinatorics runner:** define a project once; run it under N regimes × M assumption sets in parallel; persist results in a regime-indexed store.
3. **Comparison reports:** extend `generate_html_report.py` to produce regime-vs-regime delta tables (capacity, IRR, NPV, payback, offtaker bill, developer revenue) — the exact pattern the Decision 14 vs 963 plan already calls for.
4. **Regulatory subscription feed:** monthly update channel — when MOIT issues a new circular, ship a new versioned bundle with a changelog and a one-pager on bill/IRR impact for archetypal projects (commercial subscription product).
5. **Sensitivity primitives:** parametric sweeps on multiplier remap (ASM-002 in the TOU plan), surplus cap (20% → 50%), BESS capacity payment levels.

**Multi-phase plan seed (5 phases).** P1 regime schema + Decision 963 bundle; P2 preprocessing API extension (`tou_regime` argument across Julia/Python with parity tests); P3 combinatorics runner + result store; P4 regime-delta reporter; P5 subscription feed + changelog discipline.

**Why it works.** Directly capitalizes on the April 2026 regulatory shock. Lowest engineering risk (extends existing data/preprocessing layer). Subscription-revenue model fits the regulatory-update cadence. Foundational — Ideas 1 and 3 both consume Idea 2's regime registry.

**Risks.** Regulatory drift (MOIT issues a non-anticipated circular structure) may force schema revision; mitigate by treating the regime schema itself as versioned.

---

## Idea 3 — DPPA Bankability & Settlement Studio

**One-line value proposition.** Turn the existing `dppa_settlement.py` + `equity_irr.py` + ninhsim case-study ladder into a lender-grade settlement and risk module — CfD/FMP/KPP simulation, Monte Carlo on FMP and offtaker credit, audit-traceable cashflow waterfalls, and a lender deliverable pack (term sheet appendix, DSCR/LLCR/PLCR tables, sensitivity tornado).

**What it builds on (existing).** `scripts/python/dppa_settlement.py`, `equity_irr.py`, `bess_dispatch_analysis.py`, `analyze_ninhsim_dppa_case_1.py` through `_case_3`, `2026-04-23-dppa-case-4-real-project-bridge-plan.md` (real-project bridge work in flight), `compare_reopt_vs_excel.py`, `research/2026-04-07-vietnam-dppa-buyer-guide.md`, `research/fmp_modeling.csv`, `research/simplified_settlement.txt`.

**What it adds (commercial scope).**
1. **Settlement engine v1:** generalize `dppa_settlement.py` into a configurable engine supporting all Decree 57 product structures — physical-wire on-site PPA, virtual CfD, partial CfD with retail-tariff fallback, FMP-indexed CfD, KPP-indexed contracts.
2. **Risk layer:** Monte Carlo sampling over FMP path, retail-tariff escalation, generation P50/P90, offtaker default probability; output VaR-style risk cones around equity IRR and DSCR.
3. **Lender pack:** templated PDF/Excel pack with cashflow waterfall, DSCR/LLCR/PLCR by year, covenant test, sensitivity tornado, ASM/CON/DEC traceability table — auditable per the repo's existing `activeContext.md` discipline.
4. **Offtaker credit module:** integration hook for offtaker financial data (manual entry initially; vendor API later) feeding default-probability priors.
5. **Two-product PPA support:** energy + dispatch (capacity) split required by the BESS capacity-payment trajectory ([Norton Rose](https://www.nortonrosefulbright.com/en/knowledge/publications/1d041eb0/vietnam-power-sector-snapshot)).

**Multi-phase plan seed (5 phases).** P1 settlement-engine generalization (lift from ninhsim cases); P2 Monte Carlo risk layer; P3 lender pack templates; P4 offtaker credit module; P5 two-product (energy + capacity) PPA support.

**Why it works.** This code is already the most-iterated and most-validated against real Excel models (saigon18, north_thuan, ninhsim). Bankability deliverables command premium per-deal pricing (hours of senior analyst time saved per deal). Direct fit for IPP CFOs and project-finance lenders.

**Risks.** Lender acceptance requires audit/QA discipline; mitigate by formalizing the existing `tests/baselines/` regression baselines as the audit trail.

---

## Cross-Idea Composition

Idea 2's regime registry is consumed by Idea 1's scenario engine and by Idea 3's settlement runs. Idea 3's cashflow output is consumed by Idea 1's report layer. Practically: even if all three are pursued, P1 of Idea 2 is on the critical path for Ideas 1 and 3.

---

## Sources

- `research/2026-04-25_vietnam-tou-rooftop-ppa.md` — local prior brief; canonical Decision 14 vs 963 mapping and tariff multipliers.
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` — local prior brief; DPPA structuring vocabulary (FMP, KPP, strike, retail fallback).
- `plans/active/2026-04-25-vn-tou-rts-comparison-plan.md` — in-flight multi-phase plan; seeds Idea 2.
- `plans/active/2026-04-23-dppa-case-4-real-project-bridge-plan.md` — in-flight plan; seeds Idea 3.
- [Vietnam Briefing — Decree 57/2025 explainer](https://www.vietnam-briefing.com/news/vietnam-renewable-energy-decree-57.html/) — DPPA framework, surplus cap, BESS thresholds.
- [Duane Morris — DPPA + BESS](https://blogs.duanemorris.com/vietnam/2026/02/26/vietnam-investing-in-solar-projects-with-dppa-and-bess-what-you-must-know/) — bankability framing, offtaker credit.
- [Norton Rose Fulbright — Vietnam Power Sector Snapshot](https://www.nortonrosefulbright.com/en/knowledge/publications/1d041eb0/vietnam-power-sector-snapshot) — BESS capacity tariff in development.
- [VietnamNet — TOU peak-hour adjustment](https://vietnamnet.vn/en/vietnam-adjusts-power-peak-hours-amid-rising-electricity-demand-2509795.html) — Decision 963 windows.
- [B-Company — draft 50% surplus rule](https://b-company.jp/vietnam-rooftop-solar-draft-rules-2026-selling-up-to-50-surplus-power-who-benefits-and-what-to-watch-next) — forward regulatory signal.
- [IEEFA — DPPA decree analysis](https://ieefa.org/resources/vietnams-direct-power-purchase-agreement-dppa-decree-could-catalyze-new-era-renewable) — market-reform framing.
- [REopt.jl GitHub](https://github.com/NREL/REopt.jl) — upstream solver; not modified by any idea.
