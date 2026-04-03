"""Smoke entry point for the initial PySAM package scaffold."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from reopt_pysam_vn.pysam.single_owner import build_single_owner_inputs  # noqa: E402


def main() -> None:
    inputs = build_single_owner_inputs(system_capacity_kw=1000)
    print(inputs)


if __name__ == "__main__":
    main()
