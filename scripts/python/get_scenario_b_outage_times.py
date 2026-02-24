# Benchmark: fetches outage times for Colab Scenario B using non-Vietnam coordinates (lat 50, lon 30) by design.
# Do NOT add Vietnam preprocessing here.

import json
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO_ROOT / "NREL_API.env"
OUTPUT_PATH = REPO_ROOT / "results" / "colab" / "scenario_b_outage_times.json"
API_URL = "https://developer.nrel.gov/api/reopt/stable"

LATITUDE = 50.0
LONGITUDE = 30.0
DOE_REFERENCE_NAME = "Hospital"
ANNUAL_KWH = 100000
OUTAGE_HOURS = 48


def load_api_key(env_path: Path) -> str:
    if not env_path.exists():
        raise FileNotFoundError(f"NREL_API.env not found at {env_path}")

    api_key = None
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().replace('"', "")
        if key == "API_KEY_NAME":
            api_key = value
            break

    if not api_key:
        raise ValueError("API_KEY_NAME not found in NREL_API.env")

    return api_key


def get_simulated_load(api_key: str) -> list[float]:
    load_url = f"{API_URL}/simulated_load/?api_key={api_key}"
    params = {
        "load_type": "electric",
        "doe_reference_name": DOE_REFERENCE_NAME,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "annual_kwh": ANNUAL_KWH,
    }
    response = requests.get(load_url, params=params, verify=False, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["loads_kw"]


def get_outage_times(api_key: str, loads_kw: list[float]) -> list[int]:
    times_url = f"{API_URL}/peak_load_outage_times/?api_key={api_key}"
    payload = {
        "seasonal_peaks": True,
        "outage_duration": OUTAGE_HOURS,
        "critical_load": loads_kw,
        "start_not_center_on_peaks": False,
    }
    response = requests.post(times_url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["outage_start_time_steps"]


def main() -> None:
    api_key = load_api_key(ENV_PATH)
    loads_kw = get_simulated_load(api_key)
    outage_times = get_outage_times(api_key, loads_kw)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "doe_reference_name": DOE_REFERENCE_NAME,
        "annual_kwh": ANNUAL_KWH,
        "outage_hours": OUTAGE_HOURS,
        "outage_start_time_steps": outage_times,
        "loads_kw": loads_kw,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=4))
    print(f"Saved outage times to: {OUTPUT_PATH}")
    print("Outage start time steps:", outage_times)


if __name__ == "__main__":
    main()
