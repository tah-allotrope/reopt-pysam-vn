from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "generate_north_thuan_reopt_report.py"
runpy.run_path(str(TARGET), run_name="__main__")
