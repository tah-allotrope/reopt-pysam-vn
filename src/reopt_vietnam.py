"""Compatibility shim for legacy imports.

Prefer importing from `reopt_pysam_vn.reopt.preprocess`.
"""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_SRC = REPO_ROOT / "src" / "python"
if str(PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(PYTHON_SRC))

from reopt_pysam_vn.reopt.preprocess import *  # noqa: F401,F403
