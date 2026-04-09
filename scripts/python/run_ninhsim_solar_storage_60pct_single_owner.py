from pathlib import Path
import runpy

TARGET = (
    Path(__file__).resolve().parent
    / "integration"
    / "run_ninhsim_solar_storage_60pct_single_owner.py"
)
runpy.run_path(str(TARGET), run_name="__main__")
