from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "reopt" / "extract_excel_inputs.py"
runpy.run_path(str(TARGET), run_name="__main__")
