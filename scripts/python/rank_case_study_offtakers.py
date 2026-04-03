from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().parent / "integration" / "rank_case_study_offtakers.py"
runpy.run_path(str(TARGET), run_name="__main__")
