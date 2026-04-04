# PySAM Integration

## Status

Phase 4 is now implemented as a real wrapper-driven `Single Owner` workflow under `src/python/reopt_pysam_vn/pysam/`.

The first canonical runnable path is the Ninhsim developer-finance pass:

- REopt result -> local bridge mapper -> PySAM `CustomGenerationProfileSingleOwner`
- Wrapper-driven Vietnam defaults for tax, discount rate, inflation, debt, and escalation
- Normalized JSON artifact written to `artifacts/reports/ninhsim/`

## Supported local environment

`nrel-pysam` does not currently install on the workstation's global Python `3.14`, so the repo now uses a local Python `3.12` virtual environment for Phase 4 work.

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
.venv\Scripts\python.exe -m ensurepip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m pip install pytest
```

The upstream package name is `nrel-pysam`.

## Phase 4 scope

- Keep Vietnam-specific logic in local wrapper modules.
- Keep upstream PySAM unmodified.
- Start with `Single Owner` as the first finance model.
- Reuse canonical repo artifacts instead of hand-entered finance assumptions.

## First runnable workflow

Run the Ninhsim Phase 4 developer-finance pass with the local supported interpreter:

```powershell
.venv\Scripts\python.exe scripts/python/integration/run_ninhsim_single_owner.py
```

Default inputs:

- `artifacts/results/ninhsim/2026-04-01_ninhsim_scenario-b_optimized-cppa_reopt-results.json`
- `scenarios/case_studies/ninhsim/2026-04-01_ninhsim_scenario-b_optimized-cppa.json`
- `artifacts/reports/ninhsim/2026-04-02_ninhsim-commercial-candidate-memo.json`

Default output:

- `artifacts/reports/ninhsim/2026-04-04_ninhsim-single-owner-finance.json`

The runner defaults to the accepted commercial recommendation from the memo artifact: `5% below ceiling`.

## Testing

PySAM tests live under `tests/python/pysam/`.

Run the Phase 4 test set with the supported interpreter:

```powershell
.venv\Scripts\python.exe -m pytest tests/python/pysam -q
```

Notes:

- Global `python -m pytest` on Python `3.14` will still skip or fail for PySAM-dependent tests because `nrel-pysam` has no wheel there.
- The new Phase 4 tests validate both the Ninhsim bridge mapping and a real local `Single Owner` execution path.
