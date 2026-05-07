"""Create comparison manifest from materialized scenario directories."""
import json
from pathlib import Path

root = Path("artifacts/results/tou_comparison")
manifest = []
for slug_dir in sorted(root.iterdir()):
    if not slug_dir.is_dir():
        continue
    for hash_dir in sorted(slug_dir.iterdir()):
        if not hash_dir.is_dir():
            continue
        manifest_path = hash_dir / "run_manifest.json"
        if manifest_path.is_file():
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            regime_id = m.get("regime_id", "unknown")
            pair_item = {
                "regime_id": regime_id,
                "run": {
                    "scenario_hash": m.get("scenario_hash", "unknown"),
                    "result_dir": str(hash_dir),
                    "manifest": m,
                },
            }
            # Check for existing manifest entries
            found = False
            for entry in manifest:
                if entry["scenario_slug"] == slug_dir.name:
                    entry["pair"].append(pair_item)
                    found = True
                    break
            if not found:
                manifest.append({
                    "scenario_slug": slug_dir.name,
                    "scenario_path": m.get("source_scenario_path", ""),
                    "pair": [pair_item],
                })

manifest_path = root / "manifest.json"
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"Manifest written with {len(manifest)} scenario pairs")
for entry in manifest:
    regimes = [p["regime_id"] for p in entry["pair"]]
    print(f"  {entry['scenario_slug']}: {regimes}")