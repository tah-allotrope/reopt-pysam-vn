from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "reopt" / "build_saigon18_reopt_input.py"
runpy.run_path(str(TARGET), run_name="__main__")
