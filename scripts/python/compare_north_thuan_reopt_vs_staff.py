from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "compare_north_thuan_reopt_vs_staff.py"
runpy.run_path(str(TARGET), run_name="__main__")
