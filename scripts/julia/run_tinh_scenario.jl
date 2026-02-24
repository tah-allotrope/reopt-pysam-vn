using JSON
using JuMP
using HiGHS
using REopt
using DelimitedFiles

include(joinpath(@__DIR__, "..", "..", "src", "REoptVietnam.jl"))
using .REoptVietnam

const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))
const SCENARIO_PATH = joinpath(REPO_ROOT, "scenarios", "tinh", "tinh_pv_storage.json")
const LOAD_CSV_PATH = joinpath(REPO_ROOT, "scenarios", "tinh", "Tinh_test_load.csv")
const ENV_PATH = joinpath(REPO_ROOT, "NREL_API.env")
const RESULTS_DIR = joinpath(REPO_ROOT, "results", "tinh")

function load_nrel_env(env_path::AbstractString)
    if !isfile(env_path)
        @warn "NREL_API.env not found; PV/Wind resource lookups may fail." env_path
        return
    end
    for line in eachline(env_path)
        stripped = strip(line)
        (isempty(stripped) || startswith(stripped, "#")) && continue
        !occursin('=', stripped) && continue
        key, value = split(stripped, "=", limit=2)
        key = strip(key)
        value = strip(replace(strip(value), "\"" => ""))
        if key == "API_KEY_NAME"
            ENV["NREL_DEVELOPER_API_KEY"] = value
        elseif key == "API_KEY_EMAIL"
            ENV["NREL_DEVELOPER_EMAIL"] = value
        end
    end
end

function safe_get(dict::Dict, keys::Vector{String}, default=nothing)
    current = dict
    for key in keys
        if !(current isa Dict) || !haskey(current, key)
            return default
        end
        current = current[key]
    end
    return current
end

function load_csv_profile(csv_path::AbstractString)
    lines = readlines(csv_path)
    loads = Float64[]
    for line in lines[2:end]  # skip header
        parts = split(strip(line), ",")
        if length(parts) >= 2
            push!(loads, parse(Float64, strip(parts[2])))
        end
    end
    return loads
end

function summarize_results(results::Dict)
    status = safe_get(results, ["status"], "unknown")
    pv_kw = safe_get(results, ["PV", "size_kw"], missing)
    stor_kw = safe_get(results, ["ElectricStorage", "size_kw"], missing)
    stor_kwh = safe_get(results, ["ElectricStorage", "size_kwh"], missing)
    lcc = safe_get(results, ["Financial", "lcc"], missing)
    npv = safe_get(results, ["Financial", "npv"], missing)
    capital = safe_get(results, ["Financial", "initial_capital_costs"], missing)
    capital_after = safe_get(results, ["Financial", "initial_capital_costs_after_incentives"], missing)
    elec_bill = safe_get(results, ["Financial", "lifecycle_elecbill_after_tax"], missing)
    pv_energy = safe_get(results, ["PV", "year_one_energy_produced_kwh"], missing)
    pv_lcoe = safe_get(results, ["PV", "lcoe_per_kwh"], missing)

    println("\n" * "="^60)
    println("  TINH PV + STORAGE SCENARIO RESULTS")
    println("="^60)
    println("Status:                          ", status)
    println("PV size (kW):                    ", pv_kw)
    println("Storage size (kW):               ", stor_kw)
    println("Storage size (kWh):              ", stor_kwh)
    println("PV year-one energy (kWh):        ", pv_energy)
    println("PV LCOE (\$/kWh):                 ", pv_lcoe)
    println("Initial capital cost:            \$", capital)
    println("Capital after incentives:        \$", capital_after)
    println("Lifecycle electricity bill:      \$", elec_bill)
    println("Lifecycle cost (LCC):            \$", lcc)
    println("Net present value (NPV):         \$", npv)
    println("="^60)
end

# --- Main ---
println("Loading NREL API keys...")
load_nrel_env(ENV_PATH)

println("Reading scenario: ", SCENARIO_PATH)
data = JSON.parsefile(SCENARIO_PATH)

println("Reading load profile: ", LOAD_CSV_PATH)
loads_kw = load_csv_profile(LOAD_CSV_PATH)
println("  Loaded $(length(loads_kw)) hourly values, peak = $(maximum(loads_kw)) kW")
data["ElectricLoad"]["loads_kw"] = loads_kw

println("Applying Vietnam defaults (customer_type=commercial, region=south)...")
vn = load_vietnam_data()
apply_vietnam_defaults!(data, vn; customer_type="commercial", region="south")

println("Building models and running REopt...")
m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)
results = run_reopt([m1, m2], data)

summarize_results(results)

mkpath(RESULTS_DIR)
output_path = joinpath(RESULTS_DIR, "tinh_pv_storage_results.json")
open(output_path, "w") do io
    JSON.print(io, results, 4)
end
println("\nResults saved to: ", output_path)
