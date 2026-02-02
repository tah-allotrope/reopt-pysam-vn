# REopt.jl
REopt.jl is the core module of the [REopt® techno-economic decision support platform](https://www.nrel.gov/reopt/), developed by the National Renewable Energy Laboratory (NREL). REopt optimizes the sizing and dispatch of integrated energy systems for buildings, campuses, communities, microgrids, and more. REopt identifies the cost-optimal mix of generation, storage, and heating and cooling technologies to meet cost savings, resilience, emissions reductions, and energy performance goals. The open-source REopt.jl code is available on GitHub: https://github.com/NREL/REopt.jl. 

!!! note
    This REopt.jl package is used as the core model of the [REopt API](https://github.com/NREL/REopt_API) and the [REopt Web Tool](https://reopt.nrel.gov/tool). This package contains additional functionality and flexibility to run locally and customize.

## Installing
REopt evaluations for all system types except GHP (see below) can be performed using the following installation instructions from the package manager mode (`]`) of the Julia REPL:
```sh
(active_env) pkg> add REopt JuMP HiGHS
```

### Add NREL developer API key for PV, CST, and Wind
If you don't have an NREL developer network API key, [sign up here on https://developer.nrel.gov to get one (free)](https://developer.nrel.gov/signup); this is required to load PV and Wind resource profiles from PVWatts and the Wind Toolkit APIs from within REopt.jl.
Assign your API key to the expected environment variable:
```julia
ENV["NREL_DEVELOPER_API_KEY"]="your API key"
```
before running PV or Wind scenarios, and also assign your email to the expected environment variable as well before running CST scenarios: 
```julia
ENV["NREL_DEVELOPER_EMAIL"]="your contact email"
```

### Additional package loading for GHP
GHP evaluations must load in the [`GhpGhx.jl`](https://github.com/NREL/GhpGhx.jl) package separately because it has a more [restrictive license](https://github.com/NREL/GhpGhx.jl/blob/main/LICENSE.md) and is not a registered Julia package.

Install gcc via homebrew (if running on a Mac).

Add the GhpGhx.jl package to the project's dependencies from the package manager (`]`):
```sh
(active_env) pkg> add "https://github.com/NREL/GhpGhx.jl"
```

Load in the package from the script where `run_reopt()` is called:
```julia
using GhpGhx
```

## Required Packages
### Core Required Packages 
REopt.jl has three essential packages that must be installed index.md:7-11 :

REopt - The main optimization framework
JuMP - The optimization modeling layer
HiGHS - An open-source solver (or another compatible solver)
Full Dependency List 
The complete list of required packages is declared in Project.toml Project.toml:6-24 :

Core Dependencies:

JuMP - Optimization modeling Project.toml:16
MathOptInterface - Solver interface Project.toml:20
LinearAlgebra - Matrix operations Project.toml:18
Data Processing:

JSON - Input/output handling Project.toml:15
CSV - Data file handling Project.toml:8
DataFrames - Tabular data Project.toml:10
JLD - Julia data serialization Project.toml:14
External APIs:

HTTP - API calls to NREL services Project.toml:13
ArchGDAL - Geospatial operations for emissions lookups Project.toml:7
Specialized Features:

LinDistFlow - Multi-site power flow constraints Project.toml:17
CoolProp - Thermodynamic properties Project.toml:9
Roots - Root-finding for IRR calculations Project.toml:22
Requires - Conditional package loading Project.toml:21
Standard Library:

Dates, DelimitedFiles, Logging, Statistics Project.toml:11-23
These packages are imported in the main module file REopt.jl:34-57 .

### Optional Packages 
GhpGhx - Required only for ground-source heat pump (GHP) analysis index.md:24-26 . This is loaded conditionally REopt.jl:59-61 and must be installed separately from GitHub index.md:29-32 .

### Notes 
All dependencies are automatically installed when you run add REopt in Julia's package manager. The Manifest.toml file locks specific versions of all transitive dependencies for reproducibility Manifest.toml:121-210 . Version compatibility constraints are specified in the [compat] section Project.toml:26-45 .