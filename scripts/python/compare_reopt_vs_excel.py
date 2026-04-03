from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "reopt" / "compare_reopt_vs_excel.py"
runpy.run_path(str(TARGET), run_name="__main__")
