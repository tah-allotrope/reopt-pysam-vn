"""
Compute leveraged equity IRR from REopt unlevered EBITDA.

REopt outputs unlevered (project-level) IRR and NPV. The Saigon18 Excel model
reports a headline 19.4% equity IRR assuming 70% debt at 8.5% over 10 years.
This script bridges the two by post-processing REopt's avoided-cost cash flows
through a standard project finance debt schedule.

Usage:
    python scripts/python/equity_irr.py \
        --reopt results/real_project/saigon18_scenario_a_results.json \
        --capex 49510000 \
        --output reports/real_project/saigon18_equity_irr.json
"""
import argparse
import json
from pathlib import Path

import numpy_financial as npf


# ---------------------------------------------------------------------------
# Constants (from plan Section 7.2 and project summary)
# ---------------------------------------------------------------------------

TOTAL_CAPEX_USD          = 49_510_000.0  # $49.51M total CAPEX
DEBT_FRACTION            = 0.70
INTEREST_RATE            = 0.085         # blended (6.5% base + 2% margin, 50% hedged)
DEBT_TENOR_YEARS         = 10
ANALYSIS_YEARS           = 20
EXCEL_EQUITY_IRR_TARGET  = 0.194         # 19.4% from Excel


# ---------------------------------------------------------------------------
# EBITDA extraction from REopt results
# ---------------------------------------------------------------------------


def extract_annual_ebitda(results: dict, analysis_years: int) -> list[float]:
    """Derive annual unlevered free cash flows (EBITDA proxy) from REopt results.

    Uses year_one_total_operating_cost_savings_before_tax as the year-1 base
    and grows it at the electricity escalation rate (default 5%) each year.
    This is the correct approach — lcc_bau - lcc_opt yields a present-value
    total, not a nominal year-1 figure, and using it as the EBITDA base
    produces a severely understated series (was causing −17.9% equity IRR).

    Returns a list of `analysis_years` annual cash flows.
    """
    fin = results.get("Financial", {})
    year1_cf = fin.get("year_one_total_operating_cost_savings_before_tax")
    if not year1_cf:
        raise ValueError(
            "Cannot determine annual cash flows: REopt results missing "
            "'Financial.year_one_total_operating_cost_savings_before_tax'. "
            "Check that the scenario solved successfully."
        )

    elec_esc = fin.get("elec_cost_escalation_rate_fraction", 0.05)
    return [year1_cf * (1 + elec_esc) ** (yr - 1) for yr in range(1, analysis_years + 1)]


# ---------------------------------------------------------------------------
# Equity IRR computation
# ---------------------------------------------------------------------------


def compute_equity_irr(
    ebitda_series: list[float],
    total_capex: float,
    debt_fraction: float = DEBT_FRACTION,
    interest_rate: float = INTEREST_RATE,
    debt_tenor_years: int = DEBT_TENOR_YEARS,
    analysis_years: int = ANALYSIS_YEARS,
) -> dict:
    """Compute levered equity IRR given REopt EBITDA and debt assumptions.

    Args:
        ebitda_series: Annual unlevered free cash flows (length = analysis_years).
        total_capex: Total project CAPEX in USD.
        debt_fraction: Fraction of CAPEX financed with debt (default 70%).
        interest_rate: Annual interest rate on debt (default 8.5%).
        debt_tenor_years: Debt repayment period in years (default 10).
        analysis_years: Project lifetime in years (default 20).

    Returns:
        dict with equity IRR, equity NPV, debt schedule, and comparison to Excel.
    """
    if len(ebitda_series) != analysis_years:
        raise ValueError(
            f"ebitda_series length {len(ebitda_series)} != analysis_years {analysis_years}"
        )

    debt   = total_capex * debt_fraction
    equity = total_capex * (1.0 - debt_fraction)

    # Constant-payment (mortgage-style) annual debt service
    annual_debt_service = float(npf.pmt(interest_rate, debt_tenor_years, -debt))

    equity_cashflows = [-equity]
    debt_schedule = []

    balance = debt
    for yr in range(1, analysis_years + 1):
        if yr <= debt_tenor_years:
            interest   = balance * interest_rate
            principal  = annual_debt_service - interest
            balance   -= principal
            ds         = annual_debt_service
        else:
            interest  = 0.0
            principal = 0.0
            ds        = 0.0

        equity_cf = ebitda_series[yr - 1] - ds
        equity_cashflows.append(equity_cf)
        debt_schedule.append({
            "year": yr,
            "ebitda": round(ebitda_series[yr - 1], 0),
            "debt_service": round(ds, 0),
            "equity_cf": round(equity_cf, 0),
            "debt_balance": round(max(balance, 0), 0),
        })

    equity_irr = float(npf.irr(equity_cashflows))
    equity_npv = float(npf.npv(0.10, equity_cashflows))  # @ 10% discount rate

    return {
        "equity_irr": round(equity_irr, 4),
        "equity_irr_pct": f"{equity_irr:.1%}",
        "equity_npv_usd": round(equity_npv, 0),
        "total_capex_usd": total_capex,
        "debt_usd": round(debt, 0),
        "equity_usd": round(equity, 0),
        "debt_fraction": debt_fraction,
        "interest_rate": interest_rate,
        "debt_tenor_years": debt_tenor_years,
        "annual_debt_service_usd": round(annual_debt_service, 0),
        "excel_equity_irr_target": EXCEL_EQUITY_IRR_TARGET,
        "delta_vs_excel": round(equity_irr - EXCEL_EQUITY_IRR_TARGET, 4),
        "debt_schedule": debt_schedule,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Compute Saigon18 leveraged equity IRR")
    parser.add_argument("--reopt", required=True, help="REopt results JSON")
    parser.add_argument(
        "--capex",
        type=float,
        default=TOTAL_CAPEX_USD,
        help=f"Total project CAPEX in USD (default: ${TOTAL_CAPEX_USD:,.0f})",
    )
    parser.add_argument(
        "--debt-fraction",
        type=float,
        default=DEBT_FRACTION,
        dest="debt_fraction",
        help=f"Debt fraction (default: {DEBT_FRACTION})",
    )
    parser.add_argument(
        "--interest-rate",
        type=float,
        default=INTEREST_RATE,
        dest="interest_rate",
        help=f"Annual interest rate (default: {INTEREST_RATE})",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=ANALYSIS_YEARS,
        help=f"Analysis years (default: {ANALYSIS_YEARS})",
    )
    parser.add_argument(
        "--output",
        default="reports/real_project/saigon18_equity_irr.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    with open(args.reopt, encoding="utf-8") as f:
        results = json.load(f)

    ebitda = extract_annual_ebitda(results, args.years)
    irr_result = compute_equity_irr(
        ebitda_series=ebitda,
        total_capex=args.capex,
        debt_fraction=args.debt_fraction,
        interest_rate=args.interest_rate,
        analysis_years=args.years,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(irr_result, f, indent=2)

    print(f"Equity IRR results saved to: {output_path}")
    print(f"  Equity IRR (REopt-derived) : {irr_result['equity_irr_pct']}")
    print(f"  Equity IRR (Excel target)  : {EXCEL_EQUITY_IRR_TARGET:.1%}")
    print(f"  Delta                       : {irr_result['delta_vs_excel']:+.1%}")
    print(f"  Equity NPV @ 10%           : ${irr_result['equity_npv_usd']:,.0f}")


if __name__ == "__main__":
    main()
