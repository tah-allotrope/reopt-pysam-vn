from pathlib import Path
import runpy


SCRIPT = (
    Path(__file__).resolve().parent
    / "integration"
    / "generate_ninhsim_dppa_case_2_phase_reports.py"
)


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
