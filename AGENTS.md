# REopt Vietnam Project Context & Guidelines

## 1. Project Overview
> **Mission:** Julia-based techno-economic optimization for cost-optimal energy generation (Solar, Wind, Battery) for buildings and microgrids in Vietnam using NREL REopt.jl.

## 2. Environment & Commands
- **Environment:** Julia 1.10+ with REopt.jl v0.56.4 (`julia --project` for interactive use).
- **Run Command:** `$env:JULIA_PKG_PRECOMPILE_AUTO="0"; julia --project --compile=min <script>.jl` (Bypasses precompilation hangs for scripts).
- **Test Command:** `.\\tests\\run_all_tests.ps1` (Runs all validation layers).

## 3. Documentation Directory
Detailed instructions have been organized into the `docs/` folder for progressive disclosure. When working on specific areas, read the relevant file:
- **[Architecture & Tech Stack](docs/architecture.md):** JuMP/HiGHS pipeline, Preprocessing modules (`src/REoptVietnam.jl` / `src/reopt_vietnam.py`), and Coding standards.
- **[Data Layer & API Reference](docs/data_and_api.md):** API keys, Vietnam JSON data schema, and DeepWiki URLs.
- **[Known Pitfalls & Workarounds](docs/pitfalls.md):** Common REopt errors, default overrides, and Decree 57 constraint limitations.
- **[Scenario Templates](docs/scenarios.md):** Pre-configured JSON templates and usage patterns.
- **[Testing Strategy](docs/testing.md):** The 4-layer validation strategy and direct test runner commands.