# Research Brief: Practical Refinements — From Research Toolkit to Operational Decision Engine

**Date:** 2026-05-18
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Identify highest-impact practical refinements to transform reopt-pysam-vn from a research-grade toolkit into an operational decision engine for live deal evaluation at Allotrope VC. Focus areas: solve pipeline reliability, BESS economics under Decision 963, FMP trajectory for DPPA strike pricing, automated workflow orchestration, and operating project benchmarks for validation.

---

## Synthesis

The repo has mature preprocessing infrastructure (Decision 963 TOU, Decree 57 export rules, multi-regime engine) and three case studies exercised through REopt scenario materialization. However, **no actual Julia solve results exist** — the cold-start timeout blocker documented in Phase 42 means all financial delta reports show "no_results." This single gap cascades: without solve results, the PySAM bridge is untested end-to-end, financial post-processing produces placeholder outputs, and client-facing reports lack quantitative substance. The highest-impact refinement is therefore **making the solve pipeline reliable** — either via PackageCompiler sysimage (eliminates 30-60s JIT cold-start), persistent Julia worker process, or fallback to the NREL REopt API for batch runs.

Three additional refinements compound on a working solve pipeline. First, **BESS dispatch economics under Decision 963** need quantitative analysis: the single evening peak (17:30-22:30) halves arbitrage cycles vs. Decision 14's dual-peak, and the upcoming Decree 146 two-component tariff (Phase 3, July 2026) introduces demand-charge reduction as a new BESS value stream not yet modeled. Second, **workflow orchestration** is the operational bottleneck — 119 scripts in `scripts/python/` with no dependency graph, no caching, and no master pipeline; each case study requires manual sequential invocation. Third, **financial post-processing modules** (`equity_irr.py`, `dppa_settlement.py`) have hardcoded constants and no integration with each other, preventing parameterized sensitivity analysis across strike price, debt terms, and tariff regime.

For validation, the most relevant published benchmark is a 50MW Binh Thuan solar plant with 4.5 years of operational data showing 16.49% average capacity factor and a **cumulative $5.7M revenue shortfall vs. modeled projections** — a direct warning that energy yield assumptions need conservatism buffers. Vietnam FMP data is not publicly available; sensitivity analysis across VND 1,400-2,000/kWh is recommended using the DPPA buyer guide's VND 1,700/kWh as central estimate.

[NOTE] The Decree 146 two-component tariff (capacity + energy charges for large industrial, Phase 3 effective July 2026) is a near-term regulatory event that will materially change BESS and demand-side economics. The repo's `vn_regime_registry_2026.json` has placeholder trial values but needs updating when Phase 3 rates are published.

---

## Domain

### Discovery

Five domain areas were investigated with the following key sources:

1. **REopt.jl solve reliability**: NREL REopt-Analysis-Scripts Discussion #149 documents solver tuning recommendations; REopt_API Issue #77 documents Docker timeout/DimensionMismatch bug; REopt_API repo shows the production deployment pattern (Django/Celery + persistent Julia workers).
2. **BESS under Decision 963**: NREL Battery Storage Lessons report (NREL/TP-7A40-91781); Energy-Storage.News on Vietnam's BESS revenue framework (Circular 62/2025/TT-BCT); Norton Rose Fulbright Vietnam Power Sector Snapshot.
3. **Vietnam FMP trajectory**: Lexology on VCGM/VWEM circular; Norton Rose Fulbright snapshot; Baringa wholesale market report (paywalled); EVN Decision 1279 wholesale tariff.
4. **Operating benchmarks**: Oxford Academic peer-reviewed study on 50MW Binh Thuan plant (4.5 years); SolarQuarter on Vietnam BESS deployment status.
5. **Automated pipelines**: NREL REopt-API-Analysis batch patterns; PyPSA Snakemake workflow; REopt_API self-hosted Docker deployment.

### Verification

- **HiGHS solver behavior**: Confirmed via NREL Discussion #149 — HiGHS is default open-source solver, materially slower than commercial (Xpress/CPLEX), default timeout 600s, max 1,200s. Solver tuning options verified: increase `optimality_tolerance`, constrain solution space, try Cbc for certain problem types ([REopt-Analysis-Scripts #149](https://github.com/NREL/REopt-Analysis-Scripts/discussions/149)).
- **Decision 963 BESS impact**: Single evening peak halving arbitrage revenue is consistent across prior project research (`research/2026-05-07_vietnam-tou-tariff-implications.md`) and general BESS economics literature. Specific Vietnam BESS financial analysis is sparse — only one operational project (700kW/2MWh at PECC2) exists as of 2024.
- **FMP data**: No public FMP timeseries found. Baringa publishes forecasts to 2060 but behind paywall. VND 1,700/kWh central estimate from project's DPPA buyer guide is the best available proxy. **Flag: low confidence on FMP trajectory.**
- **50MW Binh Thuan benchmark**: Peer-reviewed (Oxford Academic, Clean Energy journal, 2024). Capacity factor 16.49%, performance ratio declining from 0.84 to 0.61 over 4.5 years. Revenue shortfall is documented at $5.7M cumulative ([Oxford Academic](https://academic.oup.com/ce/article/9/3/22/7945380)).
- **PackageCompiler for REopt.jl**: Not documented by NREL but feasible per Julia community practice. Expected to reduce cold-start from 30-60s to <1s. Build time 5-15 minutes.

### Comparison

| Solve Approach | Cold Start | Throughput | Complexity | Suitable For |
|---|---|---|---|---|
| **Raw Julia CLI** (current) | 30-60s per invocation | 1 scenario/run | Low | Ad-hoc single runs |
| **PackageCompiler sysimage** | <1s after build | 1 scenario/run, fast start | Medium (one-time build) | Batch local runs |
| **Persistent Julia worker** | 0s (already warm) | N scenarios/session | Medium-High | Interactive sessions |
| **NREL REopt API** | 0s (cloud) | Rate-limited, 1,200s max | Low | Validation/fallback |
| **Self-hosted REopt_API** | 0s (Docker) | Unlimited, parallel | High (Docker infra) | Production deployment |

For Allotrope's use case (periodic deal evaluation, not continuous SaaS), the **PackageCompiler sysimage** approach offers the best effort-to-impact ratio. A persistent worker or self-hosted API is premature until scenario volume justifies infrastructure.

| BESS Value Stream | Decision 14 (old) | Decision 963 (current) | Decree 146 (Jul 2026) |
|---|---|---|---|
| **TOU arbitrage cycles/day** | 2 (morning + evening) | 1 (evening only) | 1 + demand charge reduction |
| **Peak spread (VND/kWh)** | ~1,100 × 2 cycles | ~1,100 × 1 cycle | ~1,100 + capacity charge savings |
| **Solar shift value** | Moderate (morning peak captures some PV) | High (all PV generation is non-peak) | High + demand reduction |
| **Break-even (years)** | ~7-8 est. | ~12-15 est. (arbitrage only) | TBD (demand charge component unknown) |

### Synthesis

The solve pipeline bottleneck is the single highest-impact gap. PackageCompiler sysimage is the recommended first step (1-2 day effort, eliminates the cold-start blocker). The NREL REopt API should be wired as a validation fallback — the project already has NREL API credentials and the API accepts the same JSON schema. For BESS economics, the value proposition under Decision 963 shifts decisively from pure arbitrage to solar+BESS bundling (shifting daytime PV to evening peak), and the Decree 146 demand-charge component (July 2026) will be the next inflection point. FMP uncertainty is the weakest link in DPPA modeling — recommend building FMP sensitivity sweeps (VND 1,400-2,000/kWh range) into standard deal evaluation rather than point estimates.

### Confidence

**Medium-High** — Solver behavior and BESS economics are well-grounded. FMP trajectory is low-confidence due to data unavailability. Operating benchmarks are strong (peer-reviewed) but limited to solar-only (no BESS operational data from Vietnam).

---

## Codebase

### Discovery

Thorough analysis of the repository identified five structural areas with practical gaps:

**Solve pipeline** (`scripts/julia/run_vietnam_scenario.jl`, `src/julia/REoptVietnam.jl`):
- Single-entry Julia script (188 lines), uses `--compile=min` but no sysimage
- No batch/parallel solve capability — sequential HiGHS.Optimizer creation
- No error recovery or solver fallback
- Manual env var parsing for NREL API credentials

**Workflow orchestration** (`scripts/python/`, `scripts/run_tou_comparison.ps1`):
- 119 Python scripts with no dependency graph or master pipeline
- Only one PowerShell orchestration script (`run_tou_comparison.ps1`, 75 lines)
- Each case study (Saigon18, Ninhsim, North Thuan) has independent script chains
- No caching of intermediate results; re-running regenerates everything

**BESS dispatch** (`scripts/python/reopt/bess_dispatch_analysis.py`):
- 165-line module comparing REopt free dispatch vs. Excel time-locked windows
- Hardcoded exchange rate (line 26), efficiency (line 88), peak hours (lines 30-31)
- Missing: financial quantification ($/kWh savings), demand-charge modeling, degradation

**Financial post-processing** (`scripts/python/reopt/equity_irr.py`, `dppa_settlement.py`):
- Hardcoded constants: TOTAL_CAPEX_USD, DEBT_FRACTION, INTEREST_RATE in `equity_irr.py:32-37`
- No integration between equity IRR and DPPA settlement modules
- No cashflow waterfall, no sensitivity sweep, no lender-grade outputs
- No parameterization via CLI or config

**Test coverage** (`tests/`):
- 99 tests passing (65 unit + 34 data validation)
- No end-to-end test: REopt results → PySAM bridge → IRR/NPV
- No error-case testing (API unavailable, solver timeout, malformed input)
- No regression baselines for financial outputs

### Verification

- All file paths confirmed via `Glob`, `Read`, and `Grep` in the working tree.
- Hardcoded constants verified at specific line numbers in `equity_irr.py` and `bess_dispatch_analysis.py`.
- Test count verified: `run_all_tests.ps1` reports 65 unit + 34 data validation = 99 total. Cross-language test times out (Julia cold start).
- `scenarios/generated/tou_comparison/` contains 6 materialized scenarios but all financial delta columns show "no_results" — confirmed in `activeContext.md` Phase 42 notes.
- No JSON schemas exist for `data/interim/` extracted inputs — naming is inconsistent (Saigon18 has ISO date prefix, others don't).

### Comparison

| Gap | Impact on Deal Evaluation | Effort to Fix | Dependencies |
|---|---|---|---|
| **No solve results** | Blocking — all financial analysis is placeholder | 1-2 days (sysimage) | Julia, PackageCompiler |
| **No workflow orchestration** | High — 2-3 hours manual work per case study | 2-3 days (pipeline DAG) | Working solve pipeline |
| **Hardcoded financial params** | High — can't do sensitivity analysis | 1 day (parameterize) | None |
| **No E2E test** | Medium — silent regression risk | 1-2 days | Working solve pipeline |
| **No BESS financial quantification** | Medium — dispatch story incomplete | 1 day | Working solve pipeline |
| **No data validation schemas** | Medium — silent data bugs | 1 day | None |
| **No FMP sensitivity** | Medium — DPPA strikes are point estimates | 1 day | Parameterized financial modules |

### Synthesis

The codebase is architecturally sound but operationally incomplete. The critical path is:

1. **Unblock solves** → PackageCompiler sysimage or NREL API fallback
2. **Parameterize financial modules** → CLI/config for debt terms, strike price, FMP range
3. **Build orchestration layer** → master pipeline: materialize → solve → analyze → report
4. **Add BESS financial quantification** → $/kWh savings, demand-charge modeling under Decree 146
5. **Wire E2E test** → REopt results → PySAM → IRR/NPV with regression baseline

Steps 2 and 5 are independent of step 1 and can be parallelized. Step 3 depends on step 1. Step 4 depends on steps 1 and 2.

The data pipeline (`data/interim/`) needs schema standardization but is lower priority than the solve/orchestration gaps — it works correctly today, just without validation guardrails.

### Confidence

**High** — all findings verified against working tree. No ambiguity about what exists vs. what's missing.

---

## Sources

- [NREL REopt-Analysis-Scripts Discussion #149](https://github.com/NREL/REopt-Analysis-Scripts/discussions/149) — Solver tuning recommendations for HiGHS (timeout, tolerance, solver alternatives)
- [NREL REopt_API Issue #77](https://github.com/NREL/REopt_API/issues/77) — Docker timeout DimensionMismatch bug
- [NREL REopt_API Repository](https://github.com/NREL/REopt_API) — Production deployment pattern (Django/Celery/persistent Julia)
- [PackageCompiler.jl Documentation](https://julialang.github.io/PackageCompiler.jl/dev/sysimages) — Sysimage creation for eliminating JIT cold-start
- [NREL REopt-API-Analysis Repository](https://github.com/NREL/REopt-API-Analysis) — Batch scenario running patterns against REopt API
- [Oxford Academic: 50MW Vietnam Solar Plant Performance](https://academic.oup.com/ce/article/9/3/22/7945380) — 4.5-year operational data, capacity factor 16.49%, $5.7M revenue shortfall vs model
- [NREL Battery Storage Lessons from Emerging Economies](https://docs.nrel.gov/docs/fy25osti/91781.pdf) — BESS economics framework, degradation impact
- [Energy-Storage.News: Vietnam BESS Revenue Framework](https://www.energy-storage.news/vietnams-bess-breakthrough-a-turning-point-for-energy-storage-across-asean/) — Circular 62/2025 two-part BESS tariff
- [Norton Rose Fulbright: Vietnam Power Sector Snapshot](https://www.nortonrosefulbright.com/en/knowledge/publications/1d041eb0/vietnam-power-sector-snapshot) — BESS capacity tariff development, market reform timeline
- [Norton Rose Fulbright: BESS Development in Vietnam](https://www.nortonrosefulbright.com/en/knowledge/publications/7eb0008e/development-of-battery-energy-storage-systems-in-vietnam) — Regulatory framework for BESS projects
- [Baringa: Vietnam Wholesale Electricity Market Report](https://www.baringa.com/en/industries/energy-resources/power-market-projections/vietnam-wholesale-electricity-market-report/) — FMP forecasts to 2060 (paywalled)
- [Lexology: Vietnam Wholesale Electricity Market Circular](https://www.lexology.com/library/detail.aspx?g=b86c0061-c8a7-4bc5-8c26-6e0c403de2f3) — VCGM/VWEM structure, FMP = SMP + CAN
- [IEEFA: Vietnam Clean Energy Transition](https://ieefa.org/resources/boom-balance-vietnams-clean-energy-transition) — Market reform context
- `research/2026-05-07_vietnam-tou-tariff-implications.md` — Prior brief; Decision 963 code impact
- `research/2026-04-26_commercial-product-ideas.md` — Prior brief; three commercial product concepts
- `research/2026-04-07-vietnam-dppa-buyer-guide.md` — Prior brief; FMP VND 1,700/kWh working estimate
