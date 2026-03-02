# Scenario Templates

Pre-filled Vietnam scenario templates requiring only Site/Load/sizing overrides are located in `scenarios/templates/`.

| Template | Use Case | Technologies | Mode |
|---|---|---|---|
| `vn_commercial_rooftop_pv.json` | Commercial building, HCMC | PV + Storage | Grid-tied, TOU tariff |
| `vn_industrial_pv_storage.json` | Industrial facility, south | PV + Storage | Grid-tied, demand optimization |
| `vn_offgrid_microgrid.json` | Remote site, central | PV + Wind + Generator + Storage | Off-grid |
| `vn_hospital_resilience.json` | Hospital, HCMC | PV + Storage | Grid-tied, 4h outage resilience |

Each template includes a `_template` metadata block (name, description, usage, region, customer_type, voltage_level). Strip `_template` before passing to `Scenario()`.

**Usage pattern:**
```julia
d = JSON.parsefile("scenarios/templates/vn_commercial_rooftop_pv.json")
delete!(d, "_template")
# Override site-specific values
d["Site"]["latitude"] = 10.82
d["ElectricLoad"]["annual_kwh"] = 500_000
# Apply Vietnam defaults (builds TOU tariff series, etc.)
apply_vietnam_defaults!(d, vn; customer_type="commercial", region="south")
s = Scenario(d)
```