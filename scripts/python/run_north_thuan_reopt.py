from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "run_north_thuan_reopt.py"
runpy.run_path(str(TARGET), run_name="__main__")
