"""Generate Phase C/D/E HTML report for Saigon18 DPPA Case 3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORT_DATE = "2026-04-21"

DEFAULT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "reports" / "saigon18"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_html(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load(name: str) -> dict:
    p = DEFAULT_ARTIFACT_DIR / f"{REPORT_DATE}_saigon18_dppa-case-3_{name}.json"
    if p.exists():
        return _load_json(p)
    return {}


def _vn(v: float) -> str:
    return f"{v:,.0f}"


def _vnd(v: float) -> str:
    return f"{v:,.2f}"


DEFAULT_DPPA_ADDER = 523.34
DEFAULT_KPP = 1.027263
DEFAULT_STRIKE_DISCOUNT = 0.05


def build_phase_cde_html() -> str:
    combined = _load("phase-cd-combined")
    physical = _load("tou_physical")
    settlement = _load("tou_settlement")
    benchmark = _load("tou_benchmark")
    controller_gap = _load("phase-e-controller-gap")

    strike_vnd = combined.get("strike_vnd_per_kwh", 1809.613356)
    weighted_evn = combined.get("weighted_evn_vnd_per_kwh", 1904.856164)

    pv_kw = physical.get("pv_size_kw", 0)
    bess_kw = physical.get("bess_power_kw", 0)
    bess_kwh = physical.get("bess_energy_kwh", 0)
    storage_ok = physical.get("storage_floor_respected", False)

    matched = settlement.get("matched_quantity_kwh", 0)
    shortfall = settlement.get("shortfall_quantity_kwh", 0)
    blended = settlement.get("blended_cost_vnd_per_kwh", 0)
    total_payment = settlement.get("total_buyer_payment_vnd", 0)
    savings = settlement.get("buyer_savings_vs_evn_vnd", 0)
    evn_total = benchmark.get("evn_total_cost_vnd", 0)

    controller = controller_gap.get("controller", {})
    ctrl_results = controller.get("dispatch_results", {})
    ctrl_settle = controller.get("settlement", {})
    gap = controller_gap.get("gap", {})
    interp = controller_gap.get("interpretation", "")
    optimizer_results = controller_gap.get("optimizer", {}).get("results")
    optimizer_settle = controller_gap.get("optimizer", {}).get("settlement")

    storage_alert_class = "alert-pass" if storage_ok else "alert-fail"
    storage_alert_msg = (
        "PASSED — BESS respected"
        if storage_ok
        else "FAILED — REopt collapsed to PV-only"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Phase Report :: DPPA Case 3 Phase C/D/E</title>
  <meta name="color-scheme" content="dark">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{ --bg:#0d0d0d; --panel:rgba(13,13,13,0.88); --line:rgba(0,245,255,0.26); --text:#e9f6ff; --muted:#8ea3ad; --accent:#00f5ff; --accent2:#39ff14; }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ background: radial-gradient(circle at top left, rgba(0,245,255,0.12), transparent 28%), radial-gradient(circle at 85% 12%, rgba(57,255,20,0.08), transparent 24%), linear-gradient(180deg,#050505 0%,#0d0d0d 36%,#090909 100%); color:var(--text); font-family:"Segoe UI",sans-serif; line-height:1.6; }}
    .page-shell {{ width:min(1180px,calc(100vw - 32px)); margin:0 auto; padding:32px 0 72px; }}
    .hero {{ padding:28px; margin-bottom:24px; border:1px solid var(--line); border-radius:28px; background:linear-gradient(145deg,rgba(0,245,255,0.08),transparent 28%),rgba(19,19,19,0.96)); box-shadow:0 14px 40px rgba(0,0,0,0.32); }}
    .hero-grid {{ display:grid; grid-template-columns:minmax(0,1.55fr) minmax(260px,0.85fr); gap:22px; align-items:end; }}
    .phase-title {{ font-size:clamp(2.5rem,5vw,4.7rem); line-height:0.94; letter-spacing:-0.05em; text-transform:uppercase; color:#f5feff; text-shadow:0 0 24px rgba(0,245,255,0.2); }}
    .hero-summary {{ margin:18px 0 0; max-width:60ch; color:var(--muted); font-size:0.98rem; }}
    .pill-row {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }}
    .pill {{ padding:8px 11px; border:1px solid rgba(57,255,20,0.22); border-radius:999px; background:rgba(57,255,20,0.06); color:#d9ffd0; font-size:0.8rem; }}
    .repo-tag {{ margin-top:10px; padding:8px 12px; border:1px solid rgba(0,245,255,0.24); border-radius:999px; background:rgba(0,245,255,0.08); color:var(--accent); font-size:0.82rem; }}
    .section {{ position:relative; margin-top:22px; padding:24px; border:1px solid var(--line); border-radius:22px; background:var(--panel); box-shadow:0 14px 40px rgba(0,0,0,0.32); }}
    .section-title {{ font-size:clamp(1.2rem,2vw,1.7rem); color:#f0feff; }}
    .section-index {{ color:var(--accent2); font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.18em; text-shadow:0 0 18px rgba(57,255,20,0.28); margin-bottom:14px; }}
    .metric-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-top:18px; }}
    .metric {{ padding:14px 16px; border:1px solid rgba(0,245,255,0.18); border-radius:12px; background:rgba(0,245,255,0.04); }}
    .metric-label {{ color:var(--muted); font-size:0.72rem; text-transform:uppercase; letter-spacing:0.16em; }}
    .metric-value {{ margin-top:8px; color:var(--accent2); font-size:1.2rem; font-weight:700; text-shadow:0 0 18px rgba(57,255,20,0.28); }}
    .technical-frame {{ border:1px solid rgba(255,255,255,0.08); border-radius:16px; background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01)),rgba(7,7,7,0.82); padding:18px; overflow-x:auto; }}
    .technical-frame table {{ width:100%; border-collapse:collapse; }}
    .technical-frame th,.technical-frame td {{ padding:10px; border-bottom:1px solid rgba(255,255,255,0.08); text-align:left; vertical-align:top; }}
    .technical-frame th {{ color:var(--accent2); font-size:0.76rem; text-transform:uppercase; letter-spacing:0.12em; }}
    .alert {{ padding:16px; border-radius:12px; margin-top:12px; font-size:0.9rem; }}
    .alert-warn {{ background:rgba(255,183,0,0.12); border:1px solid rgba(255,183,0,0.4); color:#ffd97a; }}
    .alert-fail {{ background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.4); color:#ff9e9e; }}
    .alert-pass {{ background:rgba(57,255,20,0.08); border:1px solid rgba(57,255,20,0.3); color:#a8ff9e; }}
    @media(max-width:900px){{ .hero-grid,.metric-grid{{grid-template-columns:1fr}} }}
  </style>
</head>
<body>
<main class="page-shell">
<section class="hero" id="phase-header">
  <div class="hero-grid">
    <div>
      <p class="section-index">Phase Report / Personal Technical Artifact</p>
      <h1 class="phase-title">DPPA Case 3 Phase C/D/E</h1>
      <p class="hero-summary">Bounded-optimization physical solve, buyer settlement under saigon18 site-consistent data, and controller-vs-optimizer dispatch gap analysis.</p>
      <div class="pill-row">
        <span class="pill">project :: REopt Vietnam</span>
        <span class="pill">date :: {REPORT_DATE}</span>
        <span class="pill">case :: DPPA Case 3</span>
        <span class="pill">base :: saigon18</span>
      </div>
      <div class="repo-tag">repo :: reopt-pysam-vn</div>
    </div>
  </div>
</section>

<section class="section" id="input-output">
  <p class="section-index">01 / Input -> Output</p>
  <h2 class="section-title">Input -> Output Summary</h2>
  <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:18px;">
    <div class="technical-frame">
      <div style="color:var(--accent);font-size:0.83rem;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;margin-bottom:12px;">Inputs</div>
      <table>
        <tr><th>Source</th><td>saigon18 extracted 8760 load + market</td></tr>
        <tr><th>Load annual</th><td>{_vn(settlement.get("annual_load_kwh", 0))} kWh</td></tr>
        <tr><th>Strike anchor</th><td>{strike_vnd:.2f} VND/kWh ({DEFAULT_STRIKE_DISCOUNT * 100:.0f}% below EVN)</td></tr>
        <tr><th>Weighted EVN</th><td>{weighted_evn:.2f} VND/kWh</td></tr>
        <tr><th>DPPA adder</th><td>{DEFAULT_DPPA_ADDER} VND/kWh</td></tr>
        <tr><th>KPP factor</th><td>{DEFAULT_KPP}</td></tr>
      </table>
    </div>
    <div class="technical-frame">
      <div style="color:var(--accent);font-size:0.83rem;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;margin-bottom:12px;">Outputs</div>
      <table>
        <tr><th>PV size</th><td>{_vn(pv_kw)} kW</td></tr>
        <tr><th>BESS</th><td>{_vn(bess_kw)} kW / {_vn(bess_kwh)} kWh</td></tr>
        <tr><th>Storage floor</th><td style="color:{"#a8ff9e" if storage_ok else "#ff9e9e"}">{storage_alert_msg}</td></tr>
        <tr><th>Matched renewable</th><td>{_vn(matched)} kWh</td></tr>
        <tr><th>Shortfall</th><td>{_vn(shortfall)} kWh</td></tr>
        <tr><th>Blended cost</th><td>{blended:.4f} VND/kWh</td></tr>
      </table>
    </div>
  </div>
</section>

<section class="section" id="logic-flow">
  <p class="section-index">02 / Logic Flow</p>
  <h2 class="section-title">Logic Flow</h2>
  <div style="display:flex;flex-direction:column;gap:8px;margin-top:18px;">
    <div style="padding:12px 16px;border:1px solid rgba(0,245,255,0.2);border-radius:12px;background:rgba(0,245,255,0.04);"><strong style="color:var(--accent)">1. Scenario build</strong> — saigon18 bounded-optimization JSON with mandatory min_kw>0 and min_kwh>0 storage floor</div>
    <div style="padding:12px 16px;border:1px solid rgba(0,245,255,0.2);border-radius:12px;background:rgba(0,245,255,0.04);"><strong style="color:var(--accent)">2. REopt solve</strong> — HiGHS optimization with bounded PV/BESS sizes; tariff = legacy TOU</div>
    <div style="padding:12px 16px;border:1px solid rgba(0,245,255,0.2);border-radius:12px;background:rgba(0,245,255,0.04);"><strong style="color:var(--accent)">3. Settlement ledger</strong> — matched=min(load,gen), shortfall=load−matched, CfD=matched×(strike−market)</div>
    <div style="padding:12px 16px;border:1px solid rgba(0,245,255,0.2);border-radius:12px;background:rgba(0,245,255,0.04);"><strong style="color:var(--accent)">4. EVN benchmark</strong> — full-load bill at weighted average EVN tariff</div>
    <div style="padding:12px 16px;border:1px solid rgba(0,245,255,0.2);border-radius:12px;background:rgba(0,245,255,0.04);"><strong style="color:var(--accent)">5. Controller proxy</strong> — Fixed 1MW BESS, solar-peak charge 10-16h, evening discharge 18-23h</div>
    <div style="padding:12px 16px;border:1px solid rgba(57,255,20,0.2);border-radius:12px;background:rgba(57,255,20,0.04);"><strong style="color:var(--accent2)">6. Gap analysis</strong> — Quantify dispatch value gap between controller and optimizer</div>
  </div>
</section>

<section class="section" id="math">
  <p class="section-index">03 / Math / Algorithm</p>
  <h2 class="section-title">Math / Algorithm Used</h2>
  <div class="technical-frame" style="margin-top:18px;">
    <table>
      <tr><th>Formula</th><th>Expression</th></tr>
      <tr><td>Matched quantity</td><td><code>min(annual_load_kwh, annual_gen_kwh)</code></td></tr>
      <tr><td>Shortfall quantity</td><td><code>max(0, annual_load_kwh − matched_kwh)</code></td></tr>
      <tr><td>EVN matched payment</td><td><code>matched_kwh × market_price × KPP ({DEFAULT_KPP})</code></td></tr>
      <tr><td>DPPA charge</td><td><code>matched_kwh × {DEFAULT_DPPA_ADDER} VND/kWh</code></td></tr>
      <tr><td>CfD payment</td><td><code>matched_kwh × (strike − market_price)</code></td></tr>
      <tr><td>Shortfall payment</td><td><code>shortfall_kwh × weighted_EVN_tariff</code></td></tr>
      <tr><td>Blended cost</td><td><code>total_payment / annual_load_kwh</code></td></tr>
    </table>
  </div>
</section>

<section class="section" id="results">
  <p class="section-index">04 / Results</p>
  <h2 class="section-title">Results &amp; Metrics</h2>
  <div class="metric-grid">
    <div class="metric"><div class="metric-label">PV Size (kW)</div><div class="metric-value">{_vn(pv_kw)}</div></div>
    <div class="metric"><div class="metric-label">BESS (kW/kWh)</div><div class="metric-value">{_vn(bess_kw)}/{_vn(bess_kwh)}</div></div>
    <div class="metric"><div class="metric-label">Matched (kWh)</div><div class="metric-value">{_vn(matched)}</div></div>
    <div class="metric"><div class="metric-label">Shortfall (kWh)</div><div class="metric-value">{_vn(shortfall)}</div></div>
    <div class="metric"><div class="metric-label">Blended Cost (VND/kWh)</div><div class="metric-value">{blended:.2f}</div></div>
    <div class="metric"><div class="metric-label">Buyer Savings (VND)</div><div class="metric-value" style="color:{"#a8ff9e" if savings > 0 else "#ff9e9e"}">{_vnd(savings)}</div></div>
  </div>
  <div class="alert {storage_alert_class}" style="margin-top:14px;"><strong>Storage floor:</strong> {storage_alert_msg}</div>
  <div class="technical-frame" style="margin-top:16px;">
    <table>
      <tr><th>Component</th><th>Value (VND)</th></tr>
      <tr><td>EVN matched payment</td><td>{_vnd(settlement.get("evn_matched_payment_vnd", 0))}</td></tr>
      <tr><td>DPPA charge</td><td>{_vnd(settlement.get("dppa_charge_vnd", 0))}</td></tr>
      <tr><td>Shortfall payment</td><td>{_vnd(settlement.get("shortfall_payment_vnd", 0))}</td></tr>
      <tr><td>CfD payment</td><td>{_vnd(settlement.get("cfd_payment_vnd", 0))}</td></tr>
      <tr><td>Total buyer payment</td><td>{_vnd(total_payment)}</td></tr>
      <tr><td>EVN total cost</td><td>{_vnd(evn_total)}</td></tr>
      <tr><td>Market reference price</td><td>{settlement.get("market_reference_price_vnd_per_kwh", 0):.6f} VND/kWh</td></tr>
      <tr><td>Strike price</td><td>{strike_vnd:.6f} VND/kWh</td></tr>
    </table>
  </div>
</section>

<section class="section" id="controller-gap">
  <p class="section-index">05 / Controller Gap</p>
  <h2 class="section-title">Controller vs Optimizer Dispatch Gap</h2>
  <div class="technical-frame" style="margin-top:18px;">
    <table>
      <tr><th>Metric</th><th>Controller</th><th>Optimizer</th><th>Gap</th></tr>
      <tr><td>BESS (kW)</td>
        <td>{_vn(ctrl_results.get("bess_kw", 0))}</td>
        <td>{_vn(optimizer_results.get("bess_kw", 0) if optimizer_results else 0)}</td>
        <td>{_vn(gap.get("bess_kw_delta", 0))}</td></tr>
      <tr><td>Matched (kWh)</td>
        <td>{_vn(ctrl_results.get("matched_kwh", 0))}</td>
        <td>{_vn(optimizer_results.get("matched_kwh", 0) if optimizer_results else 0)}</td>
        <td>{_vn(gap.get("matched_kwh_delta", 0))}</td></tr>
      <tr><td>Shortfall (kWh)</td>
        <td>{_vn(ctrl_results.get("shortfall_kwh", 0))}</td>
        <td>{_vn(optimizer_results.get("shortfall_kwh", 0) if optimizer_results else 0)}</td>
        <td>{_vn(gap.get("shortfall_kwh_delta", 0))}</td></tr>
      <tr><td>Blended cost (VND/kWh)</td>
        <td>{ctrl_settle.get("blended_cost_vnd_per_kwh", 0):.4f}</td>
        <td>{optimizer_settle.get("blended_cost_vnd_per_kwh", "—") if optimizer_settle else "—"}</td>
        <td>{gap.get("blended_cost_delta_vnd_per_kwh", 0):.4f}</td></tr>
    </table>
  </div>
  <div class="alert alert-warn" style="margin-top:14px;">{interp}</div>
</section>

<section class="section" id="errors">
  <p class="section-index">06 / Errors / Warnings</p>
  <h2 class="section-title">Errors &amp; Warnings</h2>
  <div style="margin-top:18px;">
    <div class="alert alert-warn"><strong>REopt location warnings:</strong> EASIUR, AVERT, Cambium failures expected for Vietnam coordinates outside US grid.</div>
    <div class="alert alert-warn" style="margin-top:10px;"><strong>Bounded-opt solve timed out</strong> (600s). Scenario validated pre-solve. Existing 2026-03-23 results used for Phase C/D analysis.</div>
    <div class="alert alert-fail" style="margin-top:10px;"><strong>Storage floor FAILED</strong> — BESS=0kW confirms the exact anti-regression failure Case 3 is designed to prevent with mandatory min_kw/min_kwh floor.</div>
  </div>
</section>

<section class="section" id="open-questions">
  <p class="section-index">07 / Open Questions</p>
  <h2 class="section-title">Open Questions / Next Steps</h2>
  <div class="technical-frame" style="margin-top:18px;">
    <table>
      <tr><th>Priority</th><th>Item</th></tr>
      <tr><td>HIGH</td><td>Re-run bounded-opt solve (longer timeout) to confirm BESS &gt; 0 with mandatory floor</td></tr>
      <tr><td>HIGH</td><td>Run 22kV two-part tariff branch scenario</td></tr>
      <tr><td>MEDIUM</td><td>Phase F: PySAM developer validation</td></tr>
      <tr><td>MEDIUM</td><td>Phase G: Final combined decision with recommendation class</td></tr>
      <tr><td>LOW</td><td>Strike sensitivity sweep 0-20% discount</td></tr>
    </table>
  </div>
</section>
</main>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Phase C/D/E report")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    html = build_phase_cde_html()
    out_path = args.output_dir / f"{REPORT_DATE}-dppa-case-3-phase-cde.html"
    _write_html(out_path, html)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
