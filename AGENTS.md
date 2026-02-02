# REopt Vietnam Project Context & Guidelines

## 1. Project Overview
> **Mission:** This is a Julia-based techno-economic optimization application designed to find the cost-optimal mix of energy generation (Solar, Wind, Battery) for buildings and microgrids using the NREL REopt.jl engine.

## 2. Environment & Commands
- **Language:** Julia (follow REopt.jl recommendations; assume modern Julia 1.x)
- **Package Manager:** Julia Pkg (REPL `]` mode)
- **Install Dependencies:** `pkg> add REopt JuMP HiGHS`
- **Run Analysis:** Use Julia with a minimal REopt script, e.g.:
  ```julia
  using REopt, JuMP, HiGHS
  m = Model(HiGHS.Optimizer)
  results = run_reopt(m, "path/to/inputs.json")
  ```
- **API Keys:** NREL Developer API key required for PV/Wind/CST data.
  ```julia
  ENV["NREL_DEVELOPER_API_KEY"] = "your_api_key"
  ENV["NREL_DEVELOPER_EMAIL"] = "your_email"  # for CST
  ```

## 3. Tech Stack & Key Patterns
- **Core Engine:** REopt.jl
- **Modeling Layer:** JuMP
- **Solver:** HiGHS (default open-source), with optional Cbc/SCIP/Xpress/CPLEX
- **Data Structure:** Scenario → REoptInputs → JuMP model → Results
  - Technology sets organized via `Techs` struct
  - Decision variables prefixed with `dv` (camelCase)

## 4. Coding Standards (High-Level)
- **Security:** Use environment variables for secrets (API keys). No hardcoded credentials.
- **Error Handling:** Prefer REopt’s `handle_errors` patterns and structured warnings/errors via the custom logger.
- **Input Validation:** Validate at struct construction; enforce bounds, enum membership, and time-series length consistency.
- **Formatting:** Follow REopt conventions (`m` for JuMP model, `p` for REoptInputs, `p.s` for Scenario access; constants uppercase).

## 5. Documentation Index
For deep dives into the REopt input/output schema:
- **REopt Manual:** https://github.com/NatLabRockies/REopt.jl
- **Input Schema:** https://github.com/NatLabRockies/REopt.jl (see docs/inputs and @docs sections)
