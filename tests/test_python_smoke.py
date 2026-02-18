"""Quick smoke test for src/reopt_vietnam.py — verifies module loads and basic functions work."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.reopt_vietnam import (
    VNData,
    load_vietnam_data,
    convert_vnd_to_usd,
    convert_usd_to_vnd,
    build_vietnam_tariff,
    apply_vietnam_defaults,
    zero_us_incentives,
)

print("=== Loading Vietnam data ===")
vn = load_vietnam_data()
assert isinstance(vn, VNData)
print(f"  Exchange rate: {vn.exchange_rate}")
print(f"  Tariff keys: {list(vn.tariff.keys())}")
print(f"  Tech cost keys: {list(vn.tech_costs.keys())}")

print("\n=== Currency conversion ===")
assert convert_vnd_to_usd(26400, exchange_rate=26400) == 1.0
assert convert_usd_to_vnd(1.0, exchange_rate=26400) == 26400.0
print("  Round-trip OK")

print("\n=== Build tariff (industrial, medium voltage) ===")
tariff = build_vietnam_tariff(vn, "industrial", "medium_voltage_22kv_to_110kv", year=2025)
rates = tariff["energy_rate_series_per_kwh"]
assert len(rates) == 8760
print(f"  Length: {len(rates)}")
print(f"  Min: {min(rates):.6f}, Max: {max(rates):.6f}, Mean: {sum(rates)/len(rates):.6f}")

print("\n=== Full apply_vietnam_defaults ===")
d = {
    "Site": {"latitude": 10.8, "longitude": 106.6},
    "ElectricLoad": {"doe_reference_name": "Hospital", "annual_kwh": 1_000_000},
    "PV": {"max_kw": 500},
    "ElectricStorage": {"max_kw": 200, "max_kwh": 800},
}
apply_vietnam_defaults(d, vn, customer_type="industrial", region="south")

assert "Financial" in d
assert "ElectricTariff" in d
assert "ElectricUtility" in d
assert d["PV"]["installed_cost_per_kw"] == 600
assert d["PV"]["federal_itc_fraction"] == 0
assert d["PV"]["can_net_meter"] is False
assert d["ElectricStorage"]["installed_cost_constant"] == 0
assert d["ElectricStorage"]["total_itc_fraction"] == 0
assert d["Financial"]["offtaker_tax_rate_fraction"] == 0.20
ef = d["ElectricUtility"]["emissions_factor_series_lb_CO2_per_kwh"]
assert len(ef) == 8760
assert abs(ef[0] - 1.5013) < 0.001
assert abs(d["ElectricTariff"]["wholesale_rate"] - 0.0254) < 0.001
print("  All assertions passed")

print("\n=== Non-destructive test ===")
d2 = {
    "Site": {"latitude": 10.8, "longitude": 106.6},
    "ElectricLoad": {"doe_reference_name": "Hospital", "annual_kwh": 500_000},
    "PV": {"installed_cost_per_kw": 800},
}
apply_vietnam_defaults(d2, vn, region="south")
assert d2["PV"]["installed_cost_per_kw"] == 800, f"Expected 800, got {d2['PV']['installed_cost_per_kw']}"
print("  User value preserved: PV cost = 800")

print("\n=== ALL PYTHON SMOKE TESTS PASSED ===")
