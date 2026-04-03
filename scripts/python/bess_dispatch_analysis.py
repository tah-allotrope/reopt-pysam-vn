from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "reopt" / "bess_dispatch_analysis.py"
runpy.run_path(str(TARGET), run_name="__main__")
