from pathlib import Path
import runpy

TARGET = (
    Path(__file__).resolve().parent
    / "integration"
    / "run_ninhsim_dppa_case_1_pvwatts.py"
)
runpy.run_path(str(TARGET), run_name="__main__")
