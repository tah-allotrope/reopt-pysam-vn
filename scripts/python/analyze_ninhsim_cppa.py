from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "analyze_ninhsim_cppa.py"
runpy.run_path(str(TARGET), run_name="__main__")
