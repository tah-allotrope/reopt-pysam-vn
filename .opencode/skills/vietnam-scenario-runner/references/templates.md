# Vietnam Scenario Templates

## Purpose

Provide a quick selection guide for the project templates in `scenarios/templates/`.

## Template Selection

### `vn_commercial_rooftop_pv.json`

- Use for commercial buildings in Ho Chi Minh City or similar grid-tied rooftop PV cases.
- Declares:
  - `customer_type="commercial"`
  - `voltage_level="medium_voltage_22kv_to_110kv"`
  - `region="south"`
- Typical overrides:
  - `Site.latitude`
  - `Site.longitude`
  - `ElectricLoad`
  - PV sizing bounds

### `vn_industrial_pv_storage.json`

- Use for industrial facilities with grid-tied PV plus storage.
- Expect demand optimization and larger load/sizing overrides.

### `vn_offgrid_microgrid.json`

- Use for remote off-grid sites.
- Expect PV, wind, generator, and storage to remain present.
- Check `Settings.off_grid_flag` and do not remove generator or storage without understanding REopt off-grid requirements.

### `vn_hospital_resilience.json`

- Use for grid-tied resilience scenarios with outage survival requirements.
- Includes `Site.min_resil_time_steps` and outage definitions in `ElectricUtility`.
- Prefer this template when the user mentions critical load coverage, outage planning, or hospital resilience.

## `_template` Metadata Fields

Common fields found in template metadata:

- `name`
- `description`
- `usage`
- `region`
- `customer_type`
- `voltage_level`
- `load_note`

Read these fields first. They provide the safest default preprocessing parameters.

## Load Notes

Templates may contain `doe_reference_name` and `annual_kwh` as placeholders.

For more realistic Vietnam studies, replace those placeholders with `loads_kw` and preserve `ElectricLoad.year`.

## Preparation Rule

Strip `_template` before `Scenario()` or API submission. Treat the metadata block as operator guidance, not executable REopt input.
