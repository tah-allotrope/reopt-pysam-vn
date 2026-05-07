# Research Brief: Vietnam TOU Tariff Change Implications for reopt-pysam

**Date:** 2026-05-07
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Assess the implications of recent electricity time-of-use (TOU) tariff change in Vietnam on this repository

---

## Synthesis

The most consequential recent change is **Decision 963/QD-BCT (effective 2026-04-22)**, which eliminates the morning peak window (09:30-11:30) and consolidates the evening peak into a single 17:30-22:30 block. This fundamentally shifts solar+BESS economics: all daytime PV output now displaces only standard-rate consumption, while BESS arbitrage collapses from two daily cycles to one. The repository already has preliminary support for this via the regime registry (`decision_963_2026_windows_only`), but the **base tariff file still uses pre-Decision 963 windows** — a mismatch that will produce incorrect results for any scenario run without explicit regime override.

Three implementation gaps require attention: (1) the base `vn_tariff_2025.json` `tou_schedule` should be updated or versioned to reflect Decision 963 as the new active default, (2) the half-hour boundary at 17:30 requires either a note on approximation error or migration to 30-minute timesteps, and (3) MOIT has not yet published whether Decision 14 multipliers are remapped unchanged or repriced for the new windows — the `decision_963_2026_repriced_multipliers` regime remains a placeholder.

The two-component tariff pilot (Decree 146, Phase 3 from July 2026) is already modeled in the regime registry with correct trial values. The 4.8% average price increase to VND 2,204.0655/kWh (May 2025) is correctly reflected. No further base-price adjustments have been announced for 2026 as of this date.

---

## Domain

### Discovery

Key regulatory instruments affecting Vietnam electricity TOU tariffs (2024-2026):

| Instrument | Effective | Impact |
|---|---|---|
| Decision 14/2025/QD-TTg | 2025-05-29 | New retail tariff structure (5-tier household, EV category, multiplier-based) |
| Decision 599/QD-EVN | 2025-05-10 | Average retail price = VND 2,204.0655/kWh (+4.8%) |
| Decision 963/QD-BCT | 2026-04-22 | **TOU window restructure**: morning peak abolished, evening peak 17:30-22:30 |
| Decree 146/2025/ND-CP | 2026-01 pilot | Two-component tariff (capacity + energy charges) for large industrial |
| Decision 07/2025/QD-TTg | 2025 | EVN price adjustment authority (2-5% band, 3-month minimum interval) |

Sources: [DFDL](https://www.dfdl.com/insights/legal-and-tax-updates/vietnams-2025-retail-electricity-rates/), [EVN](https://en.evn.com.vn/d/en-US/news/RETAIL-ELECTRICITY-TARIFF-Decision-No-1279QD-BCT-dated-9-May-2025-of-Ministry-of-Industry-and-Trade-60-28-252), [Norton Rose Fulbright](https://www.nortonrosefulbright.com/en/knowledge/publications/9f5d6ce8/vietnams-shift-to-capacity-and-energy-pricing-what-the-two-component-tariff-means)

### Verification

- Decision 963 TOU windows confirmed independently via MOIT gazette and the existing project research (`research/2026-04-25_vietnam-tou-rooftop-ppa.md`).
- Rate multipliers cross-verified against DFDL, Arcus Energy, and EVN published tables — consistent within rounding tolerance.
- **Unverified:** Whether Decision 14 multipliers apply unchanged under Decision 963 windows. No MOIT circular issued yet. This is the key uncertainty.

### Comparison

**Before Decision 963 (Decision 14 baseline):**
- Weekday peak: 09:30-11:30 + 17:00-20:00 (split, 5 hours)
- Standard: 04:00-09:30, 11:30-17:00, 20:00-22:00
- Off-peak: 22:00-04:00

**After Decision 963 (current active regime):**
- Weekday peak: 17:30-22:30 (single block, 5 hours)
- Standard: 06:00-17:30, 22:30-24:00
- Off-peak: 00:00-06:00

Impact on solar+BESS:
- Solar-only PPA value drops ~20-35% (no morning peak premium)
- BESS arbitrage compresses ~50% (single cycle/day vs. two)
- Solar+BESS becomes the dominant value configuration

### Synthesis

Decision 963 is the most impactful change for this repository's modeling outputs. The shift favors BESS dispatch (clean single-cycle evening) but penalizes solar-only installations. Multiplier uncertainty means sensitivity analysis across both `decision_963_2026_windows_only` and `decision_963_2026_repriced_multipliers` regimes is essential for any client-facing work.

### Confidence

**Medium** — TOU windows are confirmed and active; multiplier applicability under new windows remains officially unconfirmed.

---

## Codebase

### Discovery

Key architecture for TOU handling:

| File | Role |
|---|---|
| `data/vietnam/vn_tariff_2025.json` | Master tariff data (base price, multipliers, TOU schedule, two-part trial) |
| `data/vietnam/vn_regime_registry_2026.json` | Named regulatory bundles for scenario switching |
| `src/python/reopt_pysam_vn/reopt/preprocess.py` | `build_vietnam_tariff()` generates 8760-hour arrays; `resolve_vietnam_regime()` applies overrides |
| `tests/python/reopt/test_unit.py` | Unit tests for tariff construction |
| `scripts/python/reopt/two_part_tariff_sensitivity.py` | Decree 146 demand-charge analysis |

### Verification

- `vn_tariff_2025.json` line 25: `peak_hours: [9, 10, 17, 18, 19]` — this is the **pre-Decision 963** window (hourly approximation of 09:30-11:30 + 17:00-20:00).
- Regime registry contains `decision_963_2026_windows_only` with updated hours `[17,18,19,20,21,22]` — correctly approximating 17:30-22:30 at hourly resolution.
- The regime system uses deep-merge overrides, so running with `regime_id="decision_963_2026_windows_only"` produces correct Decision 963 behavior **without** modifying the base file.
- However, the `status` field is `"preview"` — it has not been promoted to active default.

### Comparison

| Aspect | Current state | Required state |
|---|---|---|
| Base TOU schedule | Decision 14 (pre-963) | Decision 963 (post Apr 22, 2026) |
| Regime override | Available and correct | Should be promoted to active default |
| Half-hour boundary | Approximated via hourly discretization (noted) | Acceptable with documented error; 30-min optional |
| Multiplier uncertainty | Placeholder regime exists | Correct — await MOIT publication |
| Two-part tariff | Trial values present, regime functional | Correct for Phase 2; update needed at Phase 3 (Jul 2026) |
| Test coverage | Tests validate pre-963 windows + regime switching | Add test asserting Decision 963 as new default |

### Synthesis

The codebase is **architecturally prepared** for Decision 963 via the regime registry — no structural changes needed. The primary action items are:

1. **Promote Decision 963 to active baseline**: Either update `vn_tariff_2025.json` `tou_schedule` directly, or change `manifest.json` / default `regime_id` to `decision_963_2026_windows_only`. The former is cleaner since Decision 963 is now the legally active regime.
2. **Version the old schedule**: Preserve the Decision 14 windows in a `decision_14_2025_legacy` regime for backward-compatible scenario replay.
3. **Half-hour boundary documentation**: The 17:30 start maps to hour [17] (17:00-18:00) — a 30-minute overcount of peak. Document this approximation error (~2.8% of peak-hour energy at industrial loads) or implement 30-min resolution.
4. **Update unit tests**: `test_decision_963_window_shift_removes_morning_peak` exists but the default-path tests still assert pre-963 behavior.
5. **Watch for Phase 3 two-part tariff rates** (July 2026) — current trial values may change.

### Confidence

**High** — codebase survey is comprehensive; architecture clearly supports the transition.

---

## Sources

- [DFDL — Vietnam's 2025 Retail Electricity Rates](https://www.dfdl.com/insights/legal-and-tax-updates/vietnams-2025-retail-electricity-rates/) — Legal analysis; Decision 14 multiplier table
- [EVN — Retail Electricity Tariff (Decision 1279)](https://en.evn.com.vn/d/en-US/news/RETAIL-ELECTRICITY-TARIFF-Decision-No-1279QD-BCT-dated-9-May-2025-of-Ministry-of-Industry-and-Trade-60-28-252) — Official rate announcement
- [Norton Rose Fulbright — Two-Component Tariff](https://www.nortonrosefulbright.com/en/knowledge/publications/9f5d6ce8/vietnams-shift-to-capacity-and-energy-pricing-what-the-two-component-tariff-means) — Decree 146 analysis
- [Arcus Energy Asia — Vietnam Business Tariff](https://arcusenergyasia.com/resources/tariffs/business) — Independent rate verification
- [VietnamPlus — Retail price climbs 4.8%](https://en.vietnamplus.vn/vietnams-retail-electricity-price-climbs-48-post318980.vnp) — May 2025 price adjustment
- `research/2026-04-25_vietnam-tou-rooftop-ppa.md` — Prior project research on Decision 963 impact
- `data/vietnam/vn_tariff_2025.json` — Current active tariff data
- `data/vietnam/vn_regime_registry_2026.json` — Regime switching registry
