"""
Run a Vietnam scenario end-to-end using a pre-filled template.

Usage:
    julia --project --compile=min scripts/julia/run_vietnam_scenario.jl
    julia --project --compile=min scripts/julia/run_vietnam_scenario.jl --no-solve

Flags:
    --no-solve   Build and validate Scenario() but skip the HiGHS solver.
                 Useful for quick input validation without a full optimization run.

Environment (required for resource data fetch from NREL):
    NREL_DEVELOPER_API_KEY   your NREL developer API key
    NREL_DEVELOPER_EMAIL     your registered email

    Or put them in NREL_API.env at the repo root:
        API_KEY_NAME=<key>
        API_KEY_EMAIL=<email>
"""

using JSON
using JuMP
using HiGHS
using REopt

const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))
include(joinpath(REPO_ROOT, "src", "REoptVietnam.jl"))
using .REoptVietnam

const NO_SOLVE = "--no-solve" in ARGS

# ---------------------------------------------------------------------------
# Load NREL API keys from NREL_API.env if present
# ---------------------------------------------------------------------------
let env_path = joinpath(REPO_ROOT, "NREL_API.env")
    if isfile(env_path)
        for line in eachline(env_path)
            stripped = strip(line)
            (isempty(stripped) || startswith(stripped, "#")) && continue
            !occursin('=', stripped) && continue
            k, v = split(stripped, "=", limit=2)
            k = strip(k); v = strip(replace(strip(v), "\"" => ""))
            k == "API_KEY_NAME"  && (ENV["NREL_DEVELOPER_API_KEY"] = v)
            k == "API_KEY_EMAIL" && (ENV["NREL_DEVELOPER_EMAIL"]    = v)
        end
        println("API keys loaded from NREL_API.env")
    else
        @warn "NREL_API.env not found — set NREL_DEVELOPER_API_KEY and NREL_DEVELOPER_EMAIL manually."
    end
end

# ---------------------------------------------------------------------------
# Load Vietnam data and scenario template
# ---------------------------------------------------------------------------
println("\nLoading Vietnam data...")
vn = load_vietnam_data()

template = joinpath(REPO_ROOT, "scenarios", "templates", "vn_commercial_rooftop_pv.json")
println("Loading template: $template")
d = JSON.parsefile(template)

# Strip _template metadata block — REopt does not accept it
delete!(d, "_template")

# Expand scalar emissions factor to 8760 array (REopt requires array)
if haskey(d, "ElectricUtility")
    ef = get(d["ElectricUtility"], "emissions_factor_series_lb_CO2_per_kwh", nothing)
    if ef isa Number
        d["ElectricUtility"]["emissions_factor_series_lb_CO2_per_kwh"] = fill(Float64(ef), 8760)
    end
end

# ---------------------------------------------------------------------------
# Apply Vietnam preprocessing defaults
# ---------------------------------------------------------------------------
println("Applying Vietnam defaults (customer_type=commercial, region=south)...")
apply_vietnam_defaults!(d, vn;
    customer_type = "commercial",
    voltage_level = "medium_voltage_22kv_to_110kv",
    region        = "south",
)

# ---------------------------------------------------------------------------
# Construct Scenario (validates inputs — catches schema errors before solve)
# ---------------------------------------------------------------------------
println("\nConstructing Scenario()...")
s = Scenario(d)
println("Scenario() constructed successfully.")
println("  Site:     lat=$(s.site.latitude), lon=$(s.site.longitude)")
println("  Analysis: $(s.financial.analysis_years) years, discount=$(s.financial.offtaker_discount_rate_fraction)")

if NO_SOLVE
    println("\nSkipping solver (--no-solve). Done.")
else
    # -------------------------------------------------------------------------
    # Run REopt optimization with HiGHS
    # -------------------------------------------------------------------------
    println("\nRunning REopt optimization (HiGHS)...")
    m1 = Model(HiGHS.Optimizer)
    m2 = Model(HiGHS.Optimizer)
    results = run_reopt([m1, m2], d)

    status = get(get(results, "status", Dict()), "", get(results, "status", "unknown"))
    if results isa Dict && haskey(results, "status")
        status = results["status"]
    end

    println("\n--- Results ---")
    println("Status: $status")

    if haskey(results, "PV")
        pv = results["PV"]
        println("PV size:              $(get(pv, "size_kw", "N/A")) kW")
        println("PV year-1 energy:     $(get(pv, "year_one_energy_produced_kwh", "N/A")) kWh")
    end
    if haskey(results, "ElectricStorage")
        es = results["ElectricStorage"]
        println("Battery power:        $(get(es, "size_kw", "N/A")) kW")
        println("Battery capacity:     $(get(es, "size_kwh", "N/A")) kWh")
    end
    if haskey(results, "Financial")
        fin = results["Financial"]
        println("LCC:                  \$$(get(fin, "lcc", "N/A"))")
        println("NPV:                  \$$(get(fin, "npv", "N/A"))")
        println("Capital cost:         \$$(get(fin, "initial_capital_costs", "N/A"))")
        println("Capital after incent: \$$(get(fin, "initial_capital_costs_after_incentives", "N/A"))")
    end

    # Save results to results/ directory
    mkpath(joinpath(REPO_ROOT, "results"))
    out_path = joinpath(REPO_ROOT, "results", "commercial_rooftop_results.json")
    open(out_path, "w") do f
        JSON.print(f, results, 2)
    end
    println("\nResults saved to: $out_path")
end
