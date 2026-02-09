using JSON
using JuMP
using HiGHS
using REopt

const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))
const SCENARIO_B_PATH = joinpath(REPO_ROOT, "scenarios", "colab", "scenario_b_hospital_resilience.json")
const ENV_PATH = joinpath(REPO_ROOT, "NREL_API.env")
const RESULTS_DIR = joinpath(REPO_ROOT, "results", "colab")

function load_nrel_env(env_path::AbstractString)
    if !isfile(env_path)
        @warn "NREL_API.env not found; PV/Wind resource lookups may fail." env_path
        return
    end
    for line in eachline(env_path)
        stripped = strip(line)
        if isempty(stripped) || startswith(stripped, "#") || !occursin('=', stripped)
            continue
        end
        key, value = split(stripped, "=", limit=2)
        key = strip(key)
        value = replace(strip(value), "\"" => "")
        if key == "API_KEY_NAME"
            ENV["NREL_DEVELOPER_API_KEY"] = value
        elseif key == "API_KEY_EMAIL"
            ENV["NREL_DEVELOPER_EMAIL"] = value
        end
    end
end

load_nrel_env(ENV_PATH)

println("Loading Scenario B input...")
data = JSON.parsefile(SCENARIO_B_PATH)

println("Building models...")
m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)

println("Running REopt...")
results = run_reopt([m1, m2], data)

mkpath(RESULTS_DIR)
output_path = joinpath(RESULTS_DIR, "scenario_b_hospital_resilience_results.json")
open(output_path, "w") do io
    JSON.print(io, results, 4)
end

println("\n=== Scenario B: Hospital Resilience (min_resil=48) ===")
println("Status: ", get(results, "status", "unknown"))
pv = get(results, "PV", Dict())
println("PV size (kW): ", get(pv, "size_kw", "N/A"))
es = get(results, "ElectricStorage", Dict())
println("Storage size (kW): ", get(es, "size_kw", "N/A"))
println("Storage size (kWh): ", get(es, "size_kwh", "N/A"))
fin = get(results, "Financial", Dict())
println("Capital cost: ", get(fin, "lifecycle_capital_costs", "N/A"))
println("LCC: ", get(fin, "lcc", "N/A"))
println("NPV: ", get(fin, "npv", "N/A"))
outages = get(results, "Outages", Dict())
println("Unserved load (kWh): ", get(outages, "unserved_load_per_outage_kwh", "N/A"))
println("\nSaved to: ", output_path)
