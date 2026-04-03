from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "reopt" / "dppa_settlement.py"
runpy.run_path(str(TARGET), run_name="__main__")
