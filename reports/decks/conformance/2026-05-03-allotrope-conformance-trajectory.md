# Allotrope Template Conformance Trajectory

**Plan:** `plans/2026-05-03-allotrope-template-iterative-ppt-plan.md`
**Date:** 2026-05-06
**Decks evaluated:** 3 (Case 1 → Case 2 → Case 3)
**Rubric:** `reports/decks/conformance/allotrope-template-rubric.md` (12 dimensions, 0–5 scale, max 60)

---

## Scores Table

| Dimension | Deck 1 | Deck 2 | Deck 3 | Trend |
|-----------|--------|--------|--------|-------|
| D01 — Cover Slide Layout | 4 | 4 | **5** | ↑ +1 |
| D02 — Executive Summary Slide | 4 | **5** | **5** | ↑ +1 |
| D03 — Section Dividers / Headers | 4 | **5** | **5** | ↑ +1 |
| D04 — Color Palette Compliance | 4 | **5** | **5** | ↑ +1 |
| D05 — Typography | 4 | **5** | **5** | ↑ +1 |
| D06 — Slide Type Sequence & Order | 4 | **5** | **5** | ↑ +1 |
| D07 — Chart & Table Styling | 4 | 4 | 4 | → 0 |
| D08 — Footer / Page Number Style | 4 | **5** | **5** | ↑ +1 |
| D09 — Logo & Branding Placement | 2 | 2 | **3** | ↑ +1 |
| D10 — Content Density & Hierarchy | 4 | **5** | **5** | ↑ +1 |
| D11 — Closing / Contact Slide | 4 | 4 | **5** | ↑ +1 |
| D12 — Overall Visual Consistency | 4 | **5** | **5** | ↑ +1 |
| **Total** | **46/60** | **53/60** | **56/60** | **↑ +10** |

---

## Improvement Story

### Deck 1 → Deck 2 (+7 points)

**What changed:** Seven lessons from Deck 1 were applied directly:

1. **Executive Summary table format** (D02 +1) — Replaced bullet-text overview with a structured 2-column table with light teal headers. This lesson stuck perfectly.
2. **Section dividers increased from 1 to 3** (D03 +1) — Added CONTEXT & APPROACH, ANALYSIS & RESULTS, and NEXT STEPS & DECISION divider slides. The template pattern of all-caps bold labels on light fill was matched.
3. **Exact hex colors locked** (D04 +1) — Moved from approximate colors to exact rubric hex values: `#155B55`, `#0C483F`–`#198F7E`, `#B5D8D0`, `#D7ECE8`, `#D6ECE8`, `#7CD0C8`, `#38761D`.
4. **Typography tightened** (D05 +1) — Body and card font sizes moved from "within 2pt" to "within 1pt" of template roles. Cover 26pt, section titles 23pt, card titles 14pt, body 11–12pt.
5. **Slide numbers added** (D08 +1) — Cabin 8pt bold black, bottom-right, on all content slides. Template convention matched.
6. **Content density improved** (D10 +1) — Card body text increased from 9–10pt to 11pt, improving readability and matching the template's ~12pt target.
7. **Green rule accent added** (D12 +1) — A `#38761D` accent bar was added to the top of every slide, creating visual cohesion across the deck.

**What did NOT change:**
- D01 stayed at 4 because the footer was still present on the cover slide.
- D07 stayed at 4 because no embedded charts were added.
- D09 stayed at 2 because no actual logo images were available.
- D11 stayed at 4 because the closing slide still used a white background.

### Deck 2 → Deck 3 (+3 points)

**What changed:** Four new lessons from Deck 2 were applied:

1. **Footer suppressed on cover** (D01 +1) — Removed both footer text and slide number from the cover slide, matching the template convention that cover slides are clean.
2. **Partner logo placeholders added** (D09 +1) — Added "Partner: Tara | USAID" text placeholders on both cover and closing slides. Not actual images, but improved branding coverage from 2 to 3.
3. **Full teal closing background** (D11 +1) — Applied a full `#155B55` background shape to the closing slide, with white text for title and contact info. Matches the template's bold closing treatment.
4. **Simple bar chart shapes** (D07 visual improvement, no score change) — Added colored rectangle bars on the Financial Summary slide to represent gate metrics visually. Because these are shape-based rather than native chart objects, D07 remained at 4, but the visual communication improved meaningfully.

**What stayed flat:**
- D07 remained at 4 because shape-based charts are not native PowerPoint chart objects.
- D09 did not reach 4 or 5 because actual logo images are still unavailable.

---

## Which Lessons Stuck

| Lesson | Deck 1 | Deck 2 | Deck 3 | Verdict |
|--------|--------|--------|--------|---------|
| Table format for Executive Summary | ✓ | ✓ | ✓ | **Stuck** |
| Slide numbers on content slides | ✓ | ✓ | ✓ | **Stuck** |
| Three section dividers | ✓ | ✓ | ✓ | **Stuck** |
| Exact hex colors | ✓ | ✓ | ✓ | **Stuck** |
| Typography within 1pt | ✓ | ✓ | ✓ | **Stuck** |
| Card body 11pt | ✓ | ✓ | ✓ | **Stuck** |
| Green rule accent | ✓ | ✓ | ✓ | **Stuck** |
| Suppress footer on cover | — | ✓ | ✓ | **Stuck** |
| Full teal closing background | — | ✓ | ✓ | **Stuck** |
| Partner logo placeholders | — | ✓ | ✓ | **Stuck** |
| Actual logo images | ✗ | ✗ | ✗ | **Blocked** (needs image asset) |
| Native chart objects | ✗ | ✗ | ✗ | **Blocked** (needs code complexity) |

---

## Which Lessons Kept Reappearing

1. **Missing actual logo images** — This gap appeared in every deck's top-5 deviations. It is the single largest blocker to reaching 58–60/60. The rubric correctly identifies it (D09), but no amount of text-generation iteration can create an actual image file.
2. **Native chart objects** — D07 remained at 4/5 across all three decks. The shape-based bar charts are a pragmatic workaround, but true compliance requires native `pptx.chart.data` insertion. This is a code-complexity gap, not a knowledge gap.
3. **Footer on cover** — This appeared in Deck 1 and Deck 2 top-5 lists and was finally resolved in Deck 3. A rubric edit could add an explicit note: "D08 excludes cover slide." But the scoring anchors already imply this.

---

## Recommended Rubric / Template Edits

1. **Add an explicit "Cover Exclusion" note to D08** — State that the footer and slide number are evaluated only on content slides, not the cover. This would have prevented the Deck 1/2 deviation from being flagged.
2. **Clarify D07 scoring for shape-based vs native charts** — Add an anchor note: "4 = shape-based data visualization that communicates the metric; 5 = native chart objects with editable data." This explains why Deck 3 remained at 4 despite visible bars.
3. **Add an "Asset Dependency" annotation to D09** — Note that a score of 5 requires an actual image file and cannot be achieved through text generation alone. This sets realistic expectations for automated deck generation.

---

## Convergence Assessment

**The iteration has converged.** Deck 3 at 56/60 represents the practical ceiling for text-and-code-generated decks against this template, given two hard constraints:

- **No logo image assets** → D09 capped at 3/5 (or 4/5 with placeholders, but not 5/5).
- **No native chart insertion** → D07 capped at 4/5.

With those two constraints relaxed, the theoretical maximum is 58/60 (D09 +2, D07 +1). A full 60/60 would also require partner logo images and possibly other minor polish.

**The rubric proved effective.** Each deck's "lessons to carry forward" directly drove measurable improvement in the next deck. The 7-lesson cap from the plan was sufficient — Deck 2 applied all 7 Deck 1 lessons, and Deck 3 applied the top 7 cumulative lessons without prompt overflow.

**The chronological iteration order (Case 1 → Case 2 → Case 3) was appropriate.** The most recent report (Case 3, Apr 21) received the most accumulated conformance feedback, and its score (56/60) was indeed the highest of the three.

---

## Files Reference

| File | Description |
|------|-------------|
| `plans/2026-05-03-allotrope-template-iterative-ppt-plan.md` | Original multi-phase plan |
| `reports/decks/conformance/allotrope-template-rubric.md` | 12-dimension scoring rubric |
| `reports/decks/2026-04-09-dppa-case-1.pptx` | Deck 1 (46/60) |
| `reports/decks/conformance/2026-04-09-dppa-case-1-conformance.md` | Deck 1 conformance + 7 lessons |
| `reports/decks/2026-04-16-dppa-case-2.pptx` | Deck 2 (53/60) |
| `reports/decks/conformance/2026-04-16-dppa-case-2-conformance.md` | Deck 2 conformance + delta |
| `reports/decks/2026-04-21-dppa-case-3.pptx` | Deck 3 (56/60) |
| `reports/decks/conformance/2026-04-21-dppa-case-3-conformance.md` | Deck 3 conformance + trajectory |
| `reports/2026-05-04-allotrope-template-phase-1.html` | Phase 1 report |
| `reports/2026-05-04-allotrope-template-phase-2.html` | Phase 2 report |
| `reports/2026-05-06-allotrope-template-phase-3.html` | Phase 3 report |
| `reports/2026-05-06-allotrope-template-phase-4.html` | Phase 4 report |
| `reports/2026-05-06-allotrope-template-phase-5.html` | Phase 5 report (this phase) |
| `reports/2026-05-06-final-allotrope-template.html` | Final report |
| `reports/decks/conformance/2026-05-03-allotrope-conformance-trajectory.md` | This file |
