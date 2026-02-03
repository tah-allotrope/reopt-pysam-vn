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

### Local smoke test (repo)
Use the repo-provided smoke script and input to validate your local REopt setup:

```sh
& "C:\Users\tukum\.julia\juliaup\julia-1.10.10+0.x64.w64.mingw32\bin\julia.exe" run_reopt_smoke.jl
```

Inputs and scripts:
- `test/pv.json` (sample PV scenario with current schema fields)
- `run_reopt_smoke.jl` (executes REopt with HiGHS and prints key results)

Expected output highlights (example from last run):
- Status: `optimal`
- PV size (kW): `~3162.38`
- LCC: `~1.068e7`
- Average annual PV energy (kWh): `~5.63e6`
- Year-one utility bill: `~1.115e6`

## Required Packages
### Core Required Packages 
REopt.jl has three essential packages that must be installed index.md:7-11 :

REopt - The main optimization framework
JuMP - The optimization modeling layer
HiGHS - An open-source solver (or another compatible solver)


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
All dependencies are automatically installed when you run add REopt in Julia's package manager. The Manifest.toml file locks specific versions of all transitive dependencies for reproducibility Manifest.toml:121-210 . Version compatibility constraints are specified in the [compat] section Project.toml:26-45

# REopt.jl Project Information  
  
## 1. Development Environment  
  
### Programming Language and Package Manager  
REopt.jl is written in **Julia** (version 1.0+) and uses Julia's built-in package manager for dependency management. [1-cite-0](#1-cite-0)   
  
### Dependencies  
The project has the following key dependencies:  
- **JuMP** (versions 0.21-1.x): Optimization modeling framework [1-cite-1](#1-cite-1)   
- **MathOptInterface** (versions 0.9-1.x): Mathematical optimization interface [1-cite-2](#1-cite-2)   
- **LinDistFlow**: For power flow modeling [1-cite-3](#1-cite-3)   
- **ArchGDAL**, **CoolProp**, **CSV**, **DataFrames**, **HTTP**, **JSON**: Data handling and API interactions [1-cite-4](#1-cite-4)   
- **JLD**, **Roots**, **Statistics**: Mathematical operations [1-cite-5](#1-cite-5)   
  
### Installation  
Install REopt.jl and required solvers using the Julia package manager: [1-cite-6](#1-cite-6)   
  
### How to Run Analysis  
A basic REopt optimization requires three lines of code with a solver (HiGHS recommended for open-source): [1-cite-7](#1-cite-7)   
  
The input file format can be JSON, Dict, Scenario struct, or REoptInputs struct. [1-cite-8](#1-cite-8)   
  
For Business-as-Usual comparisons, provide two JuMP models: [1-cite-9](#1-cite-9)   
  
### Supported Solvers  
REopt.jl has been tested with:  
- **HiGHS** (preferred open-source)  
- **Xpress** (commercial)  
- **Cbc**, **SCIP** (open-source)  
- **CPLEX** (commercial)  
  
The solver must support Linear Programming (LP) for basic scenarios or Mixed Integer Linear Programming (MILP) for scenarios with outages and/or generators. [1-cite-10](#1-cite-10)   
  
### API Key Requirements  
An **NREL Developer API key** is required for PV, Wind, and CST resource data. Sign up at https://developer.nrel.gov/signup and set the environment variable: [1-cite-11](#1-cite-11)   
  
For CST scenarios, also set your email address as an environment variable: [1-cite-12](#1-cite-12)   
  
### Special Requirements for GHP  
GHP (Ground Heat Pump) evaluations require the separate GhpGhx.jl package, which has a more restrictive license. [1-cite-13](#1-cite-13)   
  
## 2. Technical Architecture  
  
### High-Level Design  
REopt consists of four major components:  
1. **Scenario** - defined by user inputs and defaults  
2. **REoptInputs** - converts Scenario into mathematical program values  
3. **REopt Model** - JuMP model with constraints and objective function  
4. **Results** - derived from optimal solution [1-cite-14](#1-cite-14)   
  
### Data Structures  
  
#### Core Type Hierarchy  
Abstract types define the technology and storage hierarchies: [1-cite-15](#1-cite-15)   
  
#### Techs Structure  
The `Techs` struct contains index sets for organizing technologies into categories (all, elec, pv, gen, heating, cooling, fuel_burning, etc.) used to define model constraints and decision variables: [1-cite-16](#1-cite-16)   
  
#### REoptInputs Structure  
`REoptInputs` is parametrized by scenario type and contains 69 fields including:  
- Technology sets (`techs::Techs`)  
- Production factors and levelization factors  
- Size constraints (min_sizes, max_sizes, existing_sizes)  
- Cost parameters (cap_cost_slope)  
- Load profiles (heating_loads_kw, electric loads)  
- Present worth factors (pwf_e, pwf_om, pwf_fuel)  
  
The constructor transforms the Scenario by calling setup functions for technologies, present worth factors, and other parameters. [1-cite-17](#1-cite-17)   
  
### Modeling Layer  
  
#### JuMP Mathematical Model  
The optimization model is built via the `build_reopt!` method, which:  
1. Adds decision variables (dvSize, dvRatedProduction, dvStoredEnergy, dvCurtail, etc.)  
2. Adds constraint groups from various modules  
3. Defines the objective function [1-cite-18](#1-cite-18)   
  
Decision variables follow the `dv` prefix convention with camel case naming. [1-cite-19](#1-cite-19)   
  
#### Constraint Organization  
Constraints are organized by domain in separate files under `src/constraints/`:  
- Storage constraints  
- Load balance constraints    
- Tech constraints  
- Electric utility constraints  
- Generator constraints  
- Thermal tech constraints  
- CHP constraints  
- Operating reserve constraints  
- Battery degradation  
- Outage constraints  
- Emissions constraints  
- Renewable energy constraints [1-cite-20](#1-cite-20)   
  
#### Objective Function  
The objective minimizes lifecycle costs including:  
- Capital costs (technology and storage)  
- Fixed and variable O&M costs (tax deductible)  
- Fuel costs (tax deductible)  
- Utility bills (tax deductible)  
- CHP standby charges  
- Off-grid additional costs  
- Climate costs (optional)  
- Health costs (optional)  
- Battery degradation costs  
  
Minus:  
- Production incentives (taxable)  
- Avoided capital expenditures  
- Battery residual value [1-cite-21](#1-cite-21)   
  
The model is solved using `optimize!(m)` and results are extracted via `reopt_results(m, p)`. [1-cite-22](#1-cite-22)   
  
### Solver Interface  
REopt uses JuMP as an abstraction layer, allowing compatibility with multiple solvers. Indicator constraints are only compatible with specific solvers (CPLEX, Xpress). [1-cite-23](#1-cite-23)   
  
### Key Design Patterns  
  
#### Data Flow Pipeline  
User inputs flow through: Dict/JSON → Scenario constructor → REoptInputs constructor → JuMP model building → Optimization → Results extraction [1-cite-24](#1-cite-24)   
  
#### Multi-Scenario Parallel Execution  
REopt can run optimal and BAU scenarios in parallel using threads: [1-cite-25](#1-cite-25)   
  
#### Technology Extensibility  
The architecture supports adding new technologies by:  
1. Defining mathematical model constraints  
2. Creating input structures with defaults  
3. Mapping inputs to model coefficients  
4. Creating results adapter functions  
5. Adding tests [1-cite-26](#1-cite-26)   
  
#### Module Organization  
The codebase is organized into functional modules:  
- `src/core/`: Central code for scenarios, inputs, and model building  
- `src/constraints/`: Mathematical model constraints by domain  
- `src/results/`: Post-processing and result extraction  
- `src/mpc/`: Model Predictive Control implementation  
- `src/outagesim/`: Outage simulation and resilience metrics  
- `src/lindistflow/`: LinDistFlow power flow model integration [1-cite-27](#1-cite-27)   
  
## 3. Coding Standards  
  
### Error Handling System  
  
#### Custom Logger  
REopt implements a custom `REoptLogger` that captures warnings and errors (≥ `@warn` level) during execution in a dictionary structure. The logger distinguishes between file sources and organizes messages hierarchically. [1-cite-28](#1-cite-28)   
  
The logger handles both standard logging to console (≥ `@info`) and structured error collection for returning to users. [1-cite-29](#1-cite-29)   
  
#### Error Response Format  
The `handle_errors` functions create standardized results dictionaries with:  
- Status set to "error"  
- Messages containing warnings and errors arrays  
- Optional stacktrace for unhandled exceptions [1-cite-30](#1-cite-30)   
  
#### Try-Catch Wrappers  
Main entry points (REoptInputs, run_reopt) wrap execution in try-catch blocks that call `handle_errors()` to format error responses, distinguishing between handled errors (validation failures) and unhandled exceptions. [1-cite-31](#1-cite-31)   
  
### Input Validation  
  
#### Validation Approach  
REopt performs extensive input validation throughout the codebase using the `throw(@error(...))` pattern for invalid inputs. Validation happens at struct construction time, preventing invalid data from entering the optimization model.  
  
#### Type Conversion and Sanitization  
The codebase includes utility functions for input sanitization, including type conversion and the `dictkeys_tosymbols` function that converts string keys to symbols. [1-cite-32](#1-cite-32)   
  
#### Validation Categories  
Input validation includes:  
- **Coordinate bounds**: Latitude in [-90, 90), longitude in [-180, 180)  
- **Enum/categorical validation**: Valid values checked against predefined sets (load types, sectors, fuel types, prime movers)  
- **Array length consistency**: Time series arrays must match expected lengths (8760 hours, 12 months)  
- **Bounds checking**: Values like addressable_load_fraction must be in [0.0, 1.0]  
- **Logical constraints**: min_fraction ≤ max_fraction validations  
- **Required field validation**: Errors when required inputs are missing  
- **Cost curve parameter consistency**: Validation for segmented cost curves  
  
### Security Considerations  
The codebase uses environment variables for sensitive information like API keys rather than hardcoding them. [1-cite-33](#1-cite-33)   
  
### Code Formatting  
The codebase follows these conventions:  
- Decision variables use `dv` prefix with camel case (e.g., dvSize, dvRatedProduction)  
- Parameter structures use `p` variable name for REoptInputs instances  
- JuMP models use `m` variable name  
- Scenario access through `p.s`  
- Dynamic variable names for multinode models use Symbol notation [1-cite-34](#1-cite-34)   
  
Constants are defined in uppercase: [1-cite-35](#1-cite-35)   
  
## 4. Documentation Resources  
  
### User Manual  
The main documentation is organized in the `docs/` directory with sections for:  
- **Installation and setup**: Getting started guide  
- **Examples**: Basic and advanced usage patterns  
- **Inputs**: Comprehensive input documentation  
- **Outputs**: Results structure documentation  
- **Developer guide**: Architecture and extension guides [1-cite-36](#1-cite-36)   
  
### Hosting Documentation Locally  
Documentation can be hosted locally using Julia's Documenter.jl or LiveServer.jl: [1-cite-37](#1-cite-37)   
  
### Input Schema Documentation  
Each input structure is documented with `@docs` macros covering:  
- **Settings**: Optimization settings and flags  
- **Site**: Location and site-specific parameters  
- **ElectricLoad**: Load profiles and characteristics  
- **ElectricTariff**: Utility rate structures  
- **Financial**: Economic parameters  
- **Technologies**: PV, Wind, Storage, Generator, CHP, Boiler, GHP, Steam Turbine, ASHP, CST, etc.  
- **Thermal Loads**: Heating and cooling load specifications [1-cite-38](#1-cite-38)   
  
Minimum JSON input requirements include Site coordinates, ElectricLoad specification, and ElectricTariff information: [1-cite-39](#1-cite-39)   
  
### API/Results Documentation  
Results documentation is organized by component, with `@docs` macros for each output function:  
- Financial results and BAU comparisons  
- Technology-specific outputs (PV, Wind, Storage, Generator, etc.)  
- Load results  
- Utility and tariff results  
- Outage resilience metrics [1-cite-40](#1-cite-40)   
  
### Developer Documentation  
Developer resources include:  
- **Design Concepts**: High-level architecture overview  
- **File Organization**: Codebase structure explanation  
- **Adding Technologies**: Step-by-step guide for extensions  
- **Input System**: How inputs flow through the system [1-cite-41](#1-cite-41)   
  
### Test Scenarios  
Example JSON input files are available in the `test/scenarios/` directory covering various technology combinations and use cases. [1-cite-42](#1-cite-42)   
  
## Notes  
  
- REopt.jl is the core module of the REopt® techno-economic decision support platform developed by NREL for optimizing integrated energy systems. [1-cite-43](#1-cite-43)   
  
- The current version is 0.56.4 with multiple authors from NREL. [1-cite-44](#1-cite-44)   
  
- The package uses Julia's multiple dispatch and type system extensively for extensibility and performance.  
  
- REopt.jl is used as the core model for both the REopt API and REopt Web Tool, but contains additional functionality for local execution. [1-cite-45](#1-cite-45)   
  
- The project follows semantic versioning and maintains a detailed CHANGELOG. [1-cite-46](#1-cite-46)