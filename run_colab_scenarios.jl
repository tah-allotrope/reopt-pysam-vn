using JSON
using JuMP
using HiGHS
using REopt

const SCENARIO_A_PATH = joinpath(@__DIR__, "test", "colab", "scenario_a_retail_pv_storage.json")
const SCENARIO_B_PATH = joinpath(@__DIR__, "test", "colab", "scenario_b_hospital_resilience.json")
const ENV_PATH = joinpath(@__DIR__, "NREL_API.env")
const RESULTS_DIR = joinpath(@__DIR__, "results", "colab")

function load_nrel_env(env_path::AbstractString)
    if !isfile(env_path)
        @warn "NREL_API.env not found; PV/Wind resource lookups may fail." env_path
        return
    end

    for line in eachline(env_path)
        stripped = strip(line)
        if isempty(stripped) || startswith(stripped, "#")
            continue
        end
        if !occursin('=', stripped)
            continue
        end
        key, value = split(stripped, "=", limit=2)
        key = strip(key)
        value = strip(value)
        value = replace(value, "\"" => "")
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

function summarize_results(label::AbstractString, results::Dict{String, Any})
    status = safe_get(results, ["status"], "unknown")
    pv_size_kw = safe_get(results, ["PV", "size_kw"], missing)
    storage_size_kw = safe_get(results, ["ElectricStorage", "size_kw"], missing)
    storage_size_kwh = safe_get(results, ["ElectricStorage", "size_kwh"], missing)
    capital_cost = safe_get(results, ["Financial", "lifecycle_capital_costs"], missing)
    lcc = safe_get(results, ["Financial", "lcc"], missing)
    npv = safe_get(results, ["Financial", "npv"], missing)
    println("\n=== ", label, " ===")
    println("Status: ", status)
    println("PV size (kW): ", pv_size_kw)
    println("Storage size (kW): ", storage_size_kw)
    println("Storage size (kWh): ", storage_size_kwh)
    println("Lifecycle capital cost: ", capital_cost)
    println("Lifecycle cost (LCC): ", lcc)
    println("Net present value (NPV): ", npv)
end

function run_scenario(input_path::AbstractString, output_filename::AbstractString)
    if !isfile(input_path)
        error("Input file not found: $(input_path)")
    end
    data = JSON.parsefile(input_path)
    m1 = Model(HiGHS.Optimizer)
    m2 = Model(HiGHS.Optimizer)
    results = run_reopt([m1, m2], data)
    mkpath(RESULTS_DIR)
    output_path = joinpath(RESULTS_DIR, output_filename)
    open(output_path, "w") do io
        JSON.print(io, results, 4)
    end
    return results, output_path
end

load_nrel_env(ENV_PATH)

results_a, path_a = run_scenario(SCENARIO_A_PATH, "scenario_a_retail_pv_storage_results.json")
results_b, path_b = run_scenario(SCENARIO_B_PATH, "scenario_b_hospital_resilience_results.json")

summarize_results("Scenario A: Retail PV + Storage", results_a)
summarize_results("Scenario B: Hospital Resilience", results_b)

println("\nSaved Scenario A results to: ", path_a)
println("Saved Scenario B results to: ", path_b)
