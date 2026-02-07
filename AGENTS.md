# REopt Vietnam Project Context & Guidelines

## 1. Project Overview
> **Mission:** This is a Julia-based techno-economic optimization application designed to find the cost-optimal mix of energy generation (Solar, Wind, Battery) for buildings and microgrids using the NREL REopt.jl engine.

## 2. Environment & Commands
- **Language:** Julia (follow REopt.jl recommendations; assume modern Julia 1.x) 
- **Environment** When running Julia code or using the terminal, always ensure the project environment reopt-julia-VNanalysis is active (use julia --project for all executions)
- **Run Analysis:** Use Julia with a minimal REopt script
- **API Keys:** NREL Developer API key required in the NREL_API.env file

## 3. Tech Stack & Key Patterns
- **Core Engine:** REopt.jl
- **Modeling Layer:** JuMP
- **Solver:** HiGHS (default open-source), with optional Cbc/SCIP/Xpress/CPLEX
- **Data Structure:** Scenario → REoptInputs → JuMP model → Results 

## 4. Coding Standards (High-Level)
- **Error Handling:** Prefer REopt’s `handle_errors` patterns and structured warnings/errors via the custom logger.
- **Input Validation:** Validate at struct construction; enforce bounds, enum membership, and time-series length consistency.
- **Formatting:** Follow REopt conventions  

