# PySAM Integration

## Status

PySAM support is scaffolded in the Python layer and will live under `src/python/reopt_pysam_vn/pysam/`.

## Installation

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

The upstream package name is `nrel-pysam`.

## Scope for the initial pass

- Keep Vietnam-specific logic in local wrapper modules.
- Keep upstream PySAM unmodified.
- Start with `Single Owner` as the first finance model.

## Testing

- PySAM tests live under `tests/python/pysam/`.
- They should skip cleanly when `PySAM` is not installed.
