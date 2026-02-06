using REopt, JuMP, HiGHS

function load_nrel_env(env_path::AbstractString)
    if !isfile(env_path)
        println("NREL env file not found at: ", env_path)
        return
    end

    for line in eachline(env_path)
        stripped = strip(line)
        if isempty(stripped) || startswith(stripped, "#")
            continue
        end
        parts = split(stripped, "=", limit=2)
        if length(parts) != 2
            continue
        end
        key = strip(parts[1])
        value = strip(parts[2])
        value = replace(value, "\"" => "")
        if key == "API_KEY_NAME"
            ENV["NREL_DEVELOPER_API_KEY"] = value
        elseif key == "API_KEY_EMAIL"
            ENV["NREL_DEVELOPER_EMAIL"] = value
        end
    end
end

function get_nested(d, keys...)
    current = d
    for key in keys
        if current isa Dict
            current = get(current, key, missing)
        else
            return missing
        end
    end
    return current
end

function first_present(values)
    for v in values
        if v !== missing
            return v
        end
    end
    return missing
end

env_path = joinpath(@__DIR__, "NREL_API.env")
load_nrel_env(env_path)

input_path = joinpath(@__DIR__, "test", "pv_retail.json")

m = Model(HiGHS.Optimizer)
results = run_reopt(m, input_path)

status = get(results, "status", "unknown")
pv_size_kw = first_present([
    get_nested(results, "PV", "size_kw"),
    get_nested(results, "PV", "size")
])
annual_energy_kwh = first_present([
    get_nested(results, "PV", "average_annual_energy_produced_kwh"),
    get_nested(results, "PV", "annual_energy_kwh")
])
lifecycle_cost = first_present([
    get_nested(results, "Financial", "lcc"),
    get_nested(results, "Financial", "lifecycle_cost"),
    get_nested(results, "Financial", "lcc_us_dollars")
])
year_one_bill = first_present([
    get_nested(results, "ElectricTariff", "year_one_bill"),
    get_nested(results, "ElectricTariff", "year_one_bill_us_dollars")
])

println("Status: ", status)
println("PV size (kW): ", pv_size_kw)
println("PV annual energy (kWh): ", annual_energy_kwh)
println("Lifecycle cost (LCC): ", lifecycle_cost)
println("Utility bill (year one): ", year_one_bill)
