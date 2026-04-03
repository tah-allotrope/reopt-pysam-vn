from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "build_north_thuan_reopt_input.py"
runpy.run_path(str(TARGET), run_name="__main__")
