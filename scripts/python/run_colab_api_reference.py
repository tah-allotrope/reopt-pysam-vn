# Benchmark: reproduces Google Colab tutorial Scenario A via REopt API (non-Vietnam coordinates, US assumptions).
# Do NOT add Vietnam preprocessing here — this scenario uses lat/lon outside Vietnam by design.

import json
import os
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = REPO_ROOT / "NREL_API.env"
SCENARIO_A_PATH = REPO_ROOT / "scenarios" / "colab" / "scenario_a_retail_pv_storage.json"
RESULTS_DIR = REPO_ROOT / "results" / "colab"
RESULTS_PATH = RESULTS_DIR / "scenario_a_retail_pv_storage_api_results.json"
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


def load_post_payload(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Scenario input not found at {path}")
    return json.loads(path.read_text())


def submit_job(post_payload: dict, api_key: str) -> str:
    response = requests.post(
        f"{API_URL}/job/?api_key={api_key}",
        json=post_payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    run_uuid = data.get("run_uuid")
    if not run_uuid:
        raise RuntimeError(f"Missing run_uuid in response: {data}")
    return run_uuid


def poll_results(run_uuid: str, api_key: str, poll_seconds: int = 5, max_wait_seconds: int = 1800) -> dict:
    results_url = f"{API_URL}/job/{run_uuid}/results/?api_key={api_key}"
    start_time = time.time()
    while True:
        response = requests.get(results_url, timeout=60)
        response.raise_for_status()
        data = response.json()
        status = data.get("outputs", {}).get("status") or data.get("status")
        if status and status.lower() != "optimizing...":
            return data
        if time.time() - start_time > max_wait_seconds:
            raise TimeoutError("API results polling exceeded max wait time")
        time.sleep(poll_seconds)


def main() -> None:
    api_key = load_api_key(ENV_PATH)
    post_payload = load_post_payload(SCENARIO_A_PATH)
    run_uuid = submit_job(post_payload, api_key)
    results = poll_results(run_uuid, api_key)
    sanitized_results = redact_sensitive_fields(results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(sanitized_results, indent=4))
    print(f"Saved API results to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
