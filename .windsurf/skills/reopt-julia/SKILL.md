---
name: reopt-julia
description: Use this skill to run techno-economic energy optimizations using the REopt.jl Julia package.
---

# REopt Julia Optimization

## When to Use
- When the user requires local execution of REopt instead of the web API.
- When specific solvers (Cbc, HiGHS, Xpress) are needed for complex optimizations.
- When performing Business-As-Usual (BAU) comparisons to calculate Net Present Value (NPV).

## Prerequisites
1. **Julia Installed**: The system must have Julia available.
2. **API Key**: Set the NREL Developer API key in the environment: `ENV["NREL_DEVELOPER_API_KEY"] = "YOUR_KEY"`.
3. **Environment Setup**: 
   - Navigate to the script directory.
   - Enter Julia Pkg mode (`]`) and run `activate .` followed by `instantiate`.

## Execution Workflow

### 1. Load and Modify Scenario Data
Scenario files are JSON-based and located in the `test/` directory.
- Use `JSON.parsefile("test/FILENAME.json")` to load data.
- Modify parameters programmatically (e.g., `data["Financial"]["analysis_years"] = 20`).

### 2. Select a Solver
- **Cbc**: Use for general models. Note: May be slower with binary variables.
- **HiGHS**: A high-performance free solver. Recommended for models with BAU cases.
- **Xpress**: Use only if a commercial license is available on the machine.

### 3. Run Optimization
There are two primary modes of execution:

**Mode A: Single Model (No BAU)**
Use this for quick lifecycle cost (LCC) checks.
```julia
m = Model(Cbc.Optimizer)
results = run_reopt(m, data)
```

**Mode B: BAU Comparison**
Use this for detailed BAU analysis and NPV calculations.
```julia
m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)
results = run_reopt([m1, m2], data)
```

### 4. Analyze Results
This `SKILL.md` is designed for the Julia-based version of REopt. It focuses on local execution, environment management, and solver selection (Cbc vs. HiGHS).

### Folder Structure Recommendation
```text
reopt-julia-optimization/
├── SKILL.md
├── scenarios/        # Store your .json input files here
├── results/          # Skill will output results here
└── simple_examples.jl # The script provided in your example
```

---

### File Content: `reopt-julia-optimization/SKILL.md`

```markdown
---
name: reopt-julia-optimization
description: Use this skill to run techno-economic energy optimizations using the REopt.jl Julia package. Ideal for lifecycle cost analysis and NPV calculations using local solvers like Cbc and HiGHS.
---

# REopt Julia Optimization

## When to Use
- When the user requires local execution of REopt instead of the web API.
- When specific solvers (Cbc, HiGHS, Xpress) are needed for complex optimizations.
- When performing Business-As-Usual (BAU) comparisons to calculate Net Present Value (NPV).

## Prerequisites
1. **Julia Installed**: The system must have Julia available.
2. **API Key**: Set the NREL Developer API key in the environment: `ENV["NREL_DEVELOPER_API_KEY"] = "YOUR_KEY"`.
3. **Environment Setup**: 
   - Navigate to the script directory.
   - Enter Julia Pkg mode (`]`) and run `activate .` followed by `instantiate`.

## Execution Workflow

### 1. Load and Modify Scenario Data
Scenario files are JSON-based and located in the `scenarios/` directory.
- Use `JSON.parsefile("scenarios/FILENAME.json")` to load data.
- Modify parameters programmatically (e.g., `data["Financial"]["analysis_years"] = 20`).

### 2. Select a Solver
- **Cbc**: Use for general models. Note: May be slower with binary variables.
- **HiGHS**: A high-performance free solver. Recommended for models with BAU cases.
- **Xpress**: Use only if a commercial license is available on the machine.

### 3. Run Optimization
There are two primary modes of execution:

**Mode A: Single Model (No BAU)**
Use this for quick lifecycle cost (LCC) checks.
```julia
m = Model(Cbc.Optimizer)
results = run_reopt(m, data)
```

**Mode B: Comparative Model (With BAU)**
Required to calculate **NPV**. You must provide two model objects.
```julia
m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)
results = run_reopt([m1, m2], data)
```

### 4. Extract Results
Key metrics to report back to the user:
- **PV Size**: `results["PV"]["size_kw"]`
- **Storage**: `results["ElectricStorage"]["size_kw"]` (Power) and `results["ElectricStorage"]["size_kwh"]` (Capacity).
- **Financials**: `results["Financial"]["lcc"]` (Lifecycle Cost) and `results["Financial"]["npv"]` (Net Present Value).

## Troubleshooting
- **Solver Speed**: If Cbc is too slow, suggest the user switch to the `HiGHS` solver.
- **Version Issues**: Ensure the package is up to date by running `Pkg.update("REopt")`.
- **Directory Errors**: Always check the working directory with `pwd()` before calling `include()` or loading JSON files.

## Output
Results should be saved to the `results/` folder in JSON format for persistence.

### Key differences in this Julia Skill:
1.  **Environment Management**: Unlike Python, Julia skills need to mention "Activating" and "Instantiating" the project environment.
2.  **The "Two-Model" Rule**: I highlighted that to get **NPV**, the agent must pass an array of two models `[m1, m2]`. This is a specific nuance of the Julia package that differs from the API.
3.  **Local Solvers**: This skill emphasizes choosing between `Cbc` and `HiGHS`, which is relevant for users running this on their own hardware vs. NREL's cloud.
