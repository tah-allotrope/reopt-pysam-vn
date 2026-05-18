# Research Brief: Operational Decision Engine Next Steps

**Date:** 2026-05-18
**Modes run:** codebase, domain
**Depth:** standard
**Invocation context:** /research operational decision engine next steps

---

## Synthesis

The repo is ready for PHASE-01 and PHASE-02 implementation. PHASE-01's PackageCompiler sysimage approach is feasible — the key constraint is the 2GB sysimage limit, but a lean image with REopt + JuMP + HiGHS (excluding solver binaries, which load as JLL artifacts) should stay well under that threshold. The NREL API fallback path is fully wired: the V3 endpoint at `developer.nlr.gov` accepts the same scenario JSON schema as local Julia, and the old `nrel.gov` domain is being retired May 29, 2026 (the repo already migrated to `nlr.gov` in the Python preprocess module). The `bounded-opt` Julia scripts have a stale hardcoded path (`reopt-pysam-vn` vs `reopt-pysam`) that must be fixed before they can run.

PHASE-02's financial modules have CLI entry points already in place but hardcoded constants that need to be extracted. The `vn_deal_defaults_2026.json` config file already exists and is registered in `manifest.json` — it was likely created as part of an earlier phase. The key work is rewiring `equity_irr.py`, `dppa_settlement.py`, and `bess_dispatch_analysis.py` to read from it. PySAM's `Single Owner` bridge is already available if developer-side validation is needed.

**[NOTE]** The NREL API domain shutdown (May 29, 2026) is 11 days away. If local Julia solves remain blocked, priority should shift to the API fallback path. The `solve_via_api.py` script would need to use `developer.nlr.gov` (already configured in Python preprocess). The existing Python route `run_vietnam_reopt()` in `src/python/reopt_pysam_vn/reopt/preprocess.py` already submits via this API, so a solver wrapper could reuse that module directly rather than crafting raw HTTP requests.

## Codebase Survey

### Discovery

Audited the full repo structure at `C:\Users\tukum\Downloads\reopt-pysam` covering `scripts/julia/`, `scripts/python/reopt/`, `src/julia/REoptVietnam.jl`, `src/python/reopt_pysam_vn/`, `Project.toml`, `.gitignore`, `scenarios/generated/`, `artifacts/`, and `data/vietnam/`.

### Verification

- **Julia solve entry point:** `scripts/julia/run_vietnam_scenario.jl` (187 lines) accepts `--no-solve`, `--scenario`, `--output-dir`. It uses `run_vietnam_reopt()` from `REoptVietnam.jl` which adds Decree 57 export cap constraints — this is the canonical solver path.
- **`bounded-opt` scripts** (`scripts/julia/run_bounded_opt_*.jl`) have a hardcoded `REPO_ROOT = raw"C:\Users\tukum\Downloads\reopt-pysam-vn"` which mismatches the actual repo path (`reopt-pysam`). These scripts are broken for clean checkout. Source: file reading on `scripts/julia/run_bounded_opt_22kv_solve.jl` line ~10 and `run_bounded_opt_solve.jl` line ~10.
- **Financial modules** have CLI entry points but load defaults from module-level constants:
  - `equity_irr.py` lines 32-37: `TOTAL_CAPEX_USD=49_510_000.0`, `DEBT_FRACTION=0.70`, `INTEREST_RATE=0.085`, etc.
  - `dppa_settlement.py` line 22: `EXCHANGE_RATE=26_400.0`, plus `DEFAULT_STRIKE=1100.0`
  - `bess_dispatch_analysis.py` lines 30-31: `PEAK_HOURS_WEEKDAY={17..22}`, `OFFPEAK_HOURS={0..5}`, line 88: `ROUND_TRIP_EFFICIENCY=0.92`
- **`vn_deal_defaults_2026.json`** already exists in `data/vietnam/` and is registered in `manifest.json` — config-driven defaults are ready to be consumed.
- **No sysimage or build script exists.** No `.so`, `.dll`, or `build_sysimage*` found anywhere in the repo.
- **6 TOU comparison scenarios** are materialized under `scenarios/generated/tou_comparison/` but unsolved. No result JSONs exist under `artifacts/results/tou_comparison/` — only `input.json` and `resolved_regime.json` files.

### Comparison

| Approach | Setup Cost | Solve Speed | External Deps | Maturity |
|---|---|---|---|---|
| Local Julia w/ sysimage | 5-15 min build | <3s warm | PackageCompiler.jl | Best for repeated use |
| Local Julia cold-start | None | 3-8 min per solve | None | Current state — prohibitive |
| NREL API (nlr.gov) | API key | ~30-300s per job | Network, rate limits | Good fallback |
| Python REopt module (`preprocess.py`) | Already wired | Same as NREL API | Already imported | Path of least resistance for API fallback |

**Verdict:** The Python `preprocess.py` module already contains `run_vietnam_reopt()` that POSTs to `developer.nlr.gov/api/reopt/stable`. This is the fastest path to a working `solve_via_api.py` — wrap that existing function rather than writing raw HTTP calls. For local solves, proceed with sysimage build but add `artifacts/sysimage/` to `.gitignore` first.

### Synthesis

PHASE-01 should be split: TASK-01-06 (API fallback) first since it can reuse existing code and unblocks solves immediately. Then TASK-01-01 through TASK-01-05 (sysimage) in parallel as a performance optimization. The `bounded-opt` script path issue must be fixed. PHASE-02 is fully independent — the work is extracting constants into the existing `vn_deal_defaults_2026.json` config file and adding `--config` CLI overrides.

### Confidence

**High** — all codebase claims verified by file reads. The bounded-opt path issue and unsolved TOU scenarios are directly observed.

## Domain Landscape

### Discovery

- **PackageCompiler.jl** official docs at julialang.github.io/PackageCompiler.jl/dev/ — confirms Julia 1.10+ support, sysimage creation via `create_sysimage`, and `precompile_execution_file` for warm-up workloads.
- **NREL REopt API V3** docs at developer.nlr.gov/docs/energy-optimization/reopt/v3/ — confirms V3 accepts the same JSON schema as local REopt.jl. The domain transition from `nrel.gov` to `nlr.gov` began Mar 2, 2026; old domain stops resolving May 29, 2026.
- **HiGHS.jl** GitHub (github.com/jump-dev/HiGHS.jl) — v1.23.0 wraps HiGHS v1.14.0, automated binary installation via Julia artifacts. Thread-count issue on Windows resolved in PR #161.
- **Existing vignettes:**
  - `research/2026-05-18_practical-refinements-operational-engine.md` — Recommends PackageCompiler sysimage as best solve-pipeline fix (1-2 day effort).
  - `research/2026-05-07_vietnam-tou-tariff-implications.md` — Confirms Decision 963 active, half-hour boundary approximation error documented.
  - `research/2026-04-26_commercial-product-ideas.md` — Idea 2 (TOU Regime Engine) partially implemented; this plan completes it.

### Verification

- **PackageCompiler 2GB limit (Issue #1019):** Confirmed open. The risk is sysimage exceeding 2GB triggering segfault. With only REopt + JuMP + HiGHS + JSON + ArchGDAL (5 packages) the sysimage should be ~200-400MB, well under 2GB. Solver binaries (HiGHS C++ library) ship as JLL artifacts, not compiled into the sysimage. Source: github.com/JuliaLang/PackageCompiler.jl/issues/1019.
- **NREL API domain shutdown May 29, 2026:** Confirmed at developer.nlr.gov/docs/nlr-domain-transition/. The repo already uses `nlr.gov` in `preprocess.py`. API keys are unchanged.
- **HiGHS Windows thread issue:** Resolved. The fix (`Highs_resetGlobalScheduler(1)` before setting threads) is documented in the HiGHS.jl README.
- **REopt.jl + HiGHS compatibility:** REopt.jl v0.56.4 depends on JuMP v1 and HiGHS v1 (confirmed in `Project.toml`). This is the recommended solver stack per REopt docs.

### Comparison

**Sysimage vs API approach for PHASE-01:**

| Criterion | Sysimage | API |
|---|---|---|
| Setup time | 5-15 min build | ~5 min (API key config) |
| Cold solve | <3s | ~30-300s + network |
| Batch 6 scenarios | <30s | ~3-30 min (sequential, rate limits) |
| Offline capable | Yes | No |
| Operational complexity | One-time build | Ongoing API key management |
| Expiry/retirement | None | Domain shutdown May 29 (already migrated) |

**Verdict:** Both approachs in PHASE-01 are correct. The API should be the first path (unblocks immediately), sysimage is the optimization for repeated local use.

### Synthesis

PHASE-01 has a time-sensitive dependency: the old `nrel.gov` domain stops resolving in 11 days. The repo already migrated `preprocess.py` to `nlr.gov`, so the API fallback script (`solve_via_api.py`) should use the `nlr.gov` endpoint from the start. The sysimage build has no external time pressure and can proceed in parallel.

PHASE-02's config file (`vn_deal_defaults_2026.json`) already exists — this is a pleasant surprise. The work is 2-3 edits per financial module to replace module-level constants with `--config` loading. The `bess_dispatch_analysis.py` change is slightly larger because it needs to load TOU windows from the tariff JSON via manifest rather than from hardcoded hour sets.

### Confidence

**High** — all claims about PackageCompiler, NREL API lifecycle, and HiGHS compatibility are verified against official sources. The domain shutdown date is from official transition docs.

## Sources
- [PackageCompiler.jl Documentation](https://julialang.github.io/PackageCompiler.jl/dev/) — Official docs; sysimage creation, precompile_execution_file, platform-specific notes
- [PackageCompiler.jl Issue #1019 - 2GB sysimage limit](https://github.com/JuliaLang/PackageCompiler.jl/issues/1019) — Open issue; risk of segfault with oversized sysimages
- [PackageCompiler.jl Issue #914 - Windows filter_stdlibs bug](https://github.com/JuliaLang/PackageCompiler.jl/issues/914) — Confirmed bug on Julia 1.10 Windows; mitigation: avoid filter_stdlibs
- [NREL/REopt API V3 Documentation](https://developer.nlr.gov/docs/energy-optimization/reopt/v3/) — Official API docs; schema compatibility, endpoint
- [NLR Domain Transition](https://developer.nlr.gov/docs/nlr-domain-transition/) — Shutdown schedule; old domain ceases May 29, 2026
- [NREL API Rate Limits](https://developer.nlr.gov/docs/rate-limits) — Tiered limits; 1,000 req/hr standard, 30/hr for DEMO_KEY
- [HiGHS.jl GitHub](https://github.com/jump-dev/HiGHS.jl) — Solver wrapper; Windows thread fix PR #161
- [REopt.jl Examples](https://natlabrockies.github.io/REopt.jl/dev/reopt/examples/) — Recommended solver configuration; HiGHS preferred open-source solver
- [REopt v0.59.0 Release Notes](https://github.com/NatLabRockies/REopt.jl/releases/tag/v0.59.0) — SOC series feature; useful for operational decision engine
- `research/2026-05-18_practical-refinements-operational-engine.md` — Prior research; sysimage as best solve-pipeline fix (local repo)
- `research/2026-05-07_vietnam-tou-tariff-implications.md` — Decision 963 active regime confirmation (local repo)
- `research/2026-04-26_commercial-product-ideas.md` — Idea 2/3 status; TOU Regime Engine partial implementation (local repo)
- `scripts/julia/run_vietnam_scenario.jl` — Julia solve entry point (local repo)
- `scripts/julia/run_bounded_opt_22kv_solve.jl` — Stale hardcoded path observation (local repo)
- `scripts/python/reopt/equity_irr.py`, `dppa_settlement.py`, `bess_dispatch_analysis.py` — Hardcoded constants audit (local repo)
- `data/vietnam/vn_deal_defaults_2026.json` — Already-existing deal defaults config (local repo)
- `data/vietnam/manifest.json` — Confirms `deal_defaults` key registered (local repo)
- `scenarios/generated/tou_comparison/` — 6 materialized but unsolved scenarios (local repo)
