from pathlib import Path
import runpy

TARGET = (
    Path(__file__).resolve().parent / "integration" / "build_ninhsim_reopt_input.py"
)
MODULE = runpy.run_path(str(TARGET))
globals().update(MODULE)

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
