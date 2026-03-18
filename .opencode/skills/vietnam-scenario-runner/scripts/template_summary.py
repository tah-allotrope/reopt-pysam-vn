#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/template_summary.py <template-json>")
        return 1

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Template not found: {path}")
        return 1

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    meta = data.get("_template")
    if not isinstance(meta, dict):
        print(f"No _template metadata found in: {path}")
        return 0

    ordered_keys = [
        "name",
        "description",
        "usage",
        "region",
        "customer_type",
        "voltage_level",
        "load_note",
    ]

    print(f"Template: {path}")
    for key in ordered_keys:
        if key in meta:
            print(f"{key}: {meta[key]}")

    extra_keys = [key for key in meta.keys() if key not in ordered_keys]
    for key in sorted(extra_keys):
        print(f"{key}: {meta[key]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
