from pathlib import Path
import runpy

TARGET = (
    Path(__file__).resolve().parent
    / "integration"
    / "run_ninhsim_solar_storage_60pct.py"
)
runpy.run_path(str(TARGET), run_name="__main__")
