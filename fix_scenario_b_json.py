import json
from pathlib import Path

json_path = Path("test/colab/scenario_b_hospital_resilience.json")
loads_path = Path("results/colab/scenario_b_outage_times.json")

data = json.loads(json_path.read_text())
loads_data = json.loads(loads_path.read_text())

data["ElectricLoad"] = {
    "loads_kw": loads_data["loads_kw"],
    "year": 2017
}

json_path.write_text(json.dumps(data, indent=2))
print("Updated Scenario B JSON with API loads_kw and year=2017")
