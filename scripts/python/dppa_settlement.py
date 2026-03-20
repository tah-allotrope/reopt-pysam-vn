"""
Compute DPPA (Direct Power Purchase Agreement) CfD settlement revenue.

Vietnam's Decree 57/2025 DPPA involves a CfD structure:
- Generator sells to industrial buyer at a negotiated strike price
- Settlement = max(0, Strike - FMP) × Q_delivered per hour
  (buyer pays top-up when market price is below strike)

Usage:
    python scripts/python/dppa_settlement.py \
        --extracted data/real_project/saigon18_extracted.json \
        --reopt results/real_project/saigon18_scenario_d_results.json \
        --strike-vnd 1800 \
        --output reports/real_project/saigon18_dppa_settlement.json
"""
import argparse
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

EXCHANGE_RATE_VND_PER_USD = 26_000.0  # Project assumption
DECREE57_SOUTH_CEILING_VND_PER_KWH = 1_149.86  # ground-mounted solar+BESS, south


def compute_dppa_annual_revenue(
    q_delivered_kw: list[float],
    fmp_vnd_per_mwh: list[float],
    strike_price_vnd_per_kwh: float,
    curtailment_fraction: float = 0.02,
) -> dict:
    """Compute DPPA CfD settlement revenue for one year.

    Args:
        q_delivered_kw: 8760 hourly delivered power to buyer (kW).
        fmp_vnd_per_mwh: 8760 hourly Forward Market Price (VND/MWh).
        strike_price_vnd_per_kwh: DPPA strike price (VND/kWh).
        curtailment_fraction: Transmission / line loss fraction (default 2%).

    Returns:
        dict with total settlement, volumes, and per-kWh averages.
    """
    if len(q_delivered_kw) != 8760:
        raise ValueError(f"q_delivered_kw must have 8760 values, got {len(q_delivered_kw)}")
    if len(fmp_vnd_per_mwh) != 8760:
        raise ValueError(f"fmp_vnd_per_mwh must have 8760 values, got {len(fmp_vnd_per_mwh)}")

    # Check ceiling tariff compliance
    if strike_price_vnd_per_kwh > DECREE57_SOUTH_CEILING_VND_PER_KWH:
        import warnings
        warnings.warn(
            f"Strike price {strike_price_vnd_per_kwh:.2f} VND/kWh exceeds Decree 57 "
            f"south ceiling {DECREE57_SOUTH_CEILING_VND_PER_KWH:.2f} VND/kWh. "
            "Confirm whether project uses private-wire or grid-connected DPPA structure "
            "(ceiling tariffs differ). See plan Open Question #2.",
            stacklevel=2,
        )

    total_settlement_vnd = 0.0
    total_q_kwh          = 0.0
    hours_with_settlement = 0

    for h in range(8760):
        q_kw  = q_delivered_kw[h] * (1.0 - curtailment_fraction)
        q_kwh = q_kw  # 1-hour resolution: kW × 1h = kWh

        fmp_per_kwh = fmp_vnd_per_mwh[h] / 1_000.0
        spread = max(0.0, strike_price_vnd_per_kwh - fmp_per_kwh)

        settlement_h = spread * q_kwh
        total_settlement_vnd += settlement_h
        total_q_kwh          += q_kwh
        if settlement_h > 0:
            hours_with_settlement += 1

    avg_settlement_vnd_per_kwh = (
        total_settlement_vnd / total_q_kwh if total_q_kwh > 0 else 0.0
    )

    return {
        "strike_price_vnd_per_kwh": strike_price_vnd_per_kwh,
        "total_settlement_vnd": round(total_settlement_vnd, 0),
        "total_settlement_usd": round(total_settlement_vnd / EXCHANGE_RATE_VND_PER_USD, 2),
        "total_q_kwh": round(total_q_kwh, 0),
        "total_q_mwh": round(total_q_kwh / 1_000, 2),
        "avg_settlement_vnd_per_kwh": round(avg_settlement_vnd_per_kwh, 4),
        "hours_with_settlement": hours_with_settlement,
        "curtailment_fraction": curtailment_fraction,
        "decree57_ceiling_vnd_per_kwh": DECREE57_SOUTH_CEILING_VND_PER_KWH,
        "exceeds_ceiling": strike_price_vnd_per_kwh > DECREE57_SOUTH_CEILING_VND_PER_KWH,
    }


def load_reopt_delivery_profile(results: dict) -> list[float]:
    """Extract net energy delivered to load from REopt results (8760 kW).

    Combines PV-to-load + BESS-to-load as the gross delivered quantity.
    If the result fields are missing, returns zeros.
    """
    pv_to_load   = results.get("PV", {}).get("year_one_to_load_series_kw", [])
    bess_to_load = results.get("ElectricStorage", {}).get("year_one_to_load_series_kw", [])

    if not pv_to_load and not bess_to_load:
        import warnings
        warnings.warn(
            "REopt results missing PV.year_one_to_load_series_kw and "
            "ElectricStorage.year_one_to_load_series_kw — returning zero delivery profile."
        )
        return [0.0] * 8760

    n = max(len(pv_to_load), len(bess_to_load))
    pv_to_load   = list(pv_to_load)   + [0.0] * (n - len(pv_to_load))
    bess_to_load = list(bess_to_load) + [0.0] * (n - len(bess_to_load))

    return [pv_to_load[i] + bess_to_load[i] for i in range(n)]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Compute Saigon18 DPPA settlement revenue")
    parser.add_argument(
        "--extracted",
        default="data/real_project/saigon18_extracted.json",
        help="Extracted Excel data JSON (contains fmp_vnd_per_mwh)",
    )
    parser.add_argument(
        "--reopt",
        required=True,
        help="REopt results JSON (Scenario D)",
    )
    parser.add_argument(
        "--strike-vnd",
        type=float,
        default=1_800.0,
        dest="strike_vnd",
        help="DPPA strike price in VND/kWh (default: 1800)",
    )
    parser.add_argument(
        "--curtailment",
        type=float,
        default=0.02,
        help="Transmission loss fraction (default: 0.02 = 2%%)",
    )
    parser.add_argument(
        "--output",
        default="reports/real_project/saigon18_dppa_settlement.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    with open(args.extracted, encoding="utf-8") as f:
        extracted = json.load(f)
    with open(args.reopt, encoding="utf-8") as f:
        results = json.load(f)

    fmp = extracted["fmp_vnd_per_mwh"]
    q_delivered = load_reopt_delivery_profile(results)

    settlement = compute_dppa_annual_revenue(
        q_delivered_kw=q_delivered,
        fmp_vnd_per_mwh=fmp,
        strike_price_vnd_per_kwh=args.strike_vnd,
        curtailment_fraction=args.curtailment,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(settlement, f, indent=2)

    print(f"DPPA settlement results saved to: {output_path}")
    print(f"  Strike price  : {settlement['strike_price_vnd_per_kwh']:,.0f} VND/kWh")
    print(f"  Total delivery: {settlement['total_q_mwh']:,.0f} MWh/year")
    print(f"  Settlement VND: {settlement['total_settlement_vnd']:,.0f}")
    print(f"  Settlement USD: ${settlement['total_settlement_usd']:,.0f}")
    if settlement["exceeds_ceiling"]:
        print(
            f"  WARNING: Strike exceeds Decree 57 south ceiling "
            f"({DECREE57_SOUTH_CEILING_VND_PER_KWH} VND/kWh)"
        )


if __name__ == "__main__":
    main()
