"""
Submit Scenario B to the REopt API using the Colab-style payload:
  - ElectricLoad uses doe_reference_name + annual_kwh (NOT raw loads_kw)
  - outage_start_time_steps from the peak_load_outage_times API (48h)
This mirrors what the Colab notebook actually sends.

Benchmark: non-Vietnam coordinates (lat 50, lon 30) and US assumptions by design.
Do NOT add Vietnam preprocessing here.
"""
import json
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO_ROOT / "NREL_API.env"
RESULTS_DIR = REPO_ROOT / "results" / "colab"
RESULTS_PATH = RESULTS_DIR / "scenario_b_api_doe_ref_results.json"
API_URL = "https://developer.nrel.gov/api/reopt/stable"


def redact_sensitive_fields(payload: dict) -> dict:
    if isinstance(payload, dict):
        return {
            key: redact_sensitive_fields(value)
            for key, value in payload.items()
            if not (isinstance(key, str) and key.lower() == "api_key")
        }
    if isinstance(payload, list):
        return [redact_sensitive_fields(item) for item in payload]
    return payload


def load_api_key(env_path: Path) -> str:
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == "API_KEY_NAME":
            return value.strip().replace('"', "")
    raise ValueError("API_KEY_NAME not found")


def get_simulated_load(api_key: str) -> list:
    url = f"{API_URL}/simulated_load/?api_key={api_key}"
    params = {
        "load_type": "electric",
        "doe_reference_name": "Hospital",
        "latitude": 50,
        "longitude": 30,
        "annual_kwh": 100000,
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()["loads_kw"]


def get_outage_times(api_key: str, loads_kw: list, outage_hours: int) -> list:
    url = f"{API_URL}/peak_load_outage_times/?api_key={api_key}"
    payload = {
        "seasonal_peaks": True,
        "outage_duration": outage_hours,
        "critical_load": loads_kw,
        "start_not_center_on_peaks": False,
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["outage_start_time_steps"]


def submit_job(post: dict, api_key: str) -> str:
    r = requests.post(f"{API_URL}/job/?api_key={api_key}", json=post, timeout=60)
    r.raise_for_status()
    data = r.json()
    run_uuid = data.get("run_uuid")
    if not run_uuid:
        raise RuntimeError(f"Missing run_uuid: {data}")
    return run_uuid


def poll_results(run_uuid: str, api_key: str) -> dict:
    url = f"{API_URL}/job/{run_uuid}/results/?api_key={api_key}"
    start = time.time()
    while True:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        status = data.get("outputs", {}).get("status") or data.get("status")
        if status and status.lower() != "optimizing...":
            return data
        if time.time() - start > 1800:
            raise TimeoutError("Polling exceeded 30 min")
        time.sleep(5)


def main() -> None:
    api_key = load_api_key(ENV_PATH)
    outage_hours = 48

    # Step 1: Get load profile (same as Colab cell 23)
    loads_kw = get_simulated_load(api_key)
    print(f"Got {len(loads_kw)} load values")

    # Step 2: Get outage start times for 48h (same as Colab cell 29)
    outage_times = get_outage_times(api_key, loads_kw, outage_hours)
    print(f"Outage start time steps: {outage_times}")

    # Step 3: Build the POST exactly like the Colab notebook (cell 24 + cell 29 updates)
    post = {
        "Site": {
            "latitude": 50,
            "longitude": 30,
            "land_acres": 1,
            "roof_squarefeet": 5000,
        },
        "PV": {
            "installed_cost_per_kw": 800.0,
        },
        "ElectricStorage": {},
        "ElectricLoad": {
            "doe_reference_name": "Hospital",
            "annual_kwh": 100000,
        },
        "ElectricTariff": {
            "blended_annual_energy_rate": 0.20,
            "blended_annual_demand_rate": 5,
        },
        "ElectricUtility": {
            "emissions_factor_series_lb_CO2_per_kwh": 1.04,
            "outage_durations": [outage_hours],
            "outage_start_time_steps": outage_times,
        },
        "Financial": {
            "elec_cost_escalation_rate_fraction": 0.05,
            "offtaker_discount_rate_fraction": 0.13,
            "analysis_years": 20,
            "offtaker_tax_rate_fraction": 0.18,
            "om_cost_escalation_rate_fraction": 0.025,
        },
    }

    # Step 4: Submit and poll
    run_uuid = submit_job(post, api_key)
    print(f"Submitted job: {run_uuid}")
    results = poll_results(run_uuid, api_key)
    sanitized_results = redact_sensitive_fields(results)

    # Step 5: Save and print summary
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(sanitized_results, indent=4))
    print(f"Saved to: {RESULTS_PATH}")

    o = results.get("outputs", {})
    print(f"\nStatus: {o.get('status')}")
    print(f"PV size_kw: {o.get('PV', {}).get('size_kw')}")
    print(f"Storage size_kw: {o.get('ElectricStorage', {}).get('size_kw')}")
    print(f"Storage size_kwh: {o.get('ElectricStorage', {}).get('size_kwh')}")
    print(f"Capital: {o.get('Financial', {}).get('lifecycle_capital_costs')}")
    print(f"NPV: {o.get('Financial', {}).get('npv')}")
    print(f"LCC: {o.get('Financial', {}).get('lcc')}")


if __name__ == "__main__":
    main()
