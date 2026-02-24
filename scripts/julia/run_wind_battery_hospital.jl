# Benchmark: US wind + battery reference scenario (Kansas coordinates, US assumptions).
# Do NOT add Vietnam preprocessing here — this scenario uses US lat/lon by design.
using JSON
using JuMP
using HiGHS
using REopt

const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))
const INPUT_PATH = joinpath(REPO_ROOT, "scenarios", "wind", "wind_battery_hospital.json")
const ENV_PATH = joinpath(REPO_ROOT, "NREL_API.env")
const RESULTS_DIR = joinpath(REPO_ROOT, "results", "wind")
const RESULTS_PATH = joinpath(RESULTS_DIR, "wind_battery_hospital_results.json")

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

load_nrel_env(ENV_PATH)

if !isfile(INPUT_PATH)
    error("Input file not found: $(INPUT_PATH)")
end

data = JSON.parsefile(INPUT_PATH)

m1 = Model(HiGHS.Optimizer)
m2 = Model(HiGHS.Optimizer)
results = run_reopt([m1, m2], data)

status = safe_get(results, ["status"], "unknown")
wind_size_kw = safe_get(results, ["Wind", "size_kw"], missing)
storage_size_kw = safe_get(results, ["ElectricStorage", "size_kw"], missing)
storage_size_kwh = safe_get(results, ["ElectricStorage", "size_kwh"], missing)
lcc = safe_get(results, ["Financial", "lcc"], missing)
npv = safe_get(results, ["Financial", "npv"], missing)
year_one_bill = safe_get(results, ["ElectricTariff", "year_one_bill"], missing)
if year_one_bill === missing
    year_one_bill = safe_get(results, ["ElectricTariff", "year_one_bill_after_tax"], missing)
end
if year_one_bill === missing
    year_one_bill = safe_get(results, ["ElectricTariff", "year_one_bill_before_tax"], missing)
end

println("Status: ", status)
println("Wind size (kW): ", wind_size_kw)
println("Storage size (kW): ", storage_size_kw)
println("Storage size (kWh): ", storage_size_kwh)
println("Lifecycle cost (LCC): ", lcc)
println("Net present value (NPV): ", npv)
println("Year-one utility bill: ", year_one_bill)

mkpath(RESULTS_DIR)
open(RESULTS_PATH, "w") do io
    JSON.print(io, results, 4)
end

println("Saved results to: ", RESULTS_PATH)
