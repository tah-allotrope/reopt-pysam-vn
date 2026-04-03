from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "build_ninhsim_extracted_inputs.py"
runpy.run_path(str(TARGET), run_name="__main__")
