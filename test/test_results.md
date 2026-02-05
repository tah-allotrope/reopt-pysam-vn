# Test Results

## pv.json results
PV size: 3,162.38 kW
Lifecycle cost (LCC): $10,680,646.79 (~$10.68 million)
Annual energy produced: 5,630,515.56 kWh (~5.63 million kWh)
Utility bill (year one): $1,115,439.36 (~$1.12 million)

These values are reasonable for a commercial retail building with a ~3.2 MW solar system in California (based on the lat/long in pv.json). The lifecycle cost of ~$10.7M over 20 years aligns with the discount rate of 8.1% and the utility bill offset from solar generation.

## pv_storage.json results
**Scenario:** `test/pv_storage.json`  
**Solver:** HiGHS  
**Status:** optimal  

| Metric | Value |
|--------|-------|
| PV size (kW) | 216.67 |
| PV annual energy (kWh) | 379,271.82 |
| Storage size (kW) | 55.88 |
| Storage size (kWh) | 78.91 |
| Storage to‑load energy (kWh, year one) | 10,977.98 |
| Storage SOC min/max (%) | 0.2 / 1.0 |
| Lifecycle cost (LCC) | $12,400,367.56 |
| Utility bill (year one) | $1,681,177.91 |

**Observations**
- Storage is active and cycling SOC between 20% and 100%.
- Storage delivers ~11 MWh to load in year one.
- PV provides ~379 MWh annually.
- The optimizer selected modest storage sizing given the tariff and cost assumptions.
