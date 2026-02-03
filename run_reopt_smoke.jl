using REopt, JuMP, HiGHS

input_path = joinpath(@__DIR__, "test", "pv.json")

m = Model(HiGHS.Optimizer)
results = run_reopt(m, input_path)

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

status = get(results, "status", "unknown")
pv_size_kw = first_present([
    get_nested(results, "PV", "size_kw"),
    get_nested(results, "PV", "size")
])
lifecycle_cost = first_present([
    get_nested(results, "Financial", "lcc"),
    get_nested(results, "Financial", "lifecycle_cost"),
    get_nested(results, "Financial", "lcc_us_dollars")
])

println("Status: ", status)
println("PV size (kW): ", pv_size_kw)
println("Lifecycle cost: ", lifecycle_cost)

# Debug: inspect actual result keys
println("--- Top-level keys ---")
for k in keys(results)
    println(k)
end

# Inspect common nested structures
if haskey(results, "PV")
    println("--- PV keys ---")
    for k in keys(results["PV"])
        println(k)
    end
end
if haskey(results, "Financial")
    println("--- Financial keys ---")
    for k in keys(results["Financial"])
        println(k)
    end
end
if haskey(results, "ElectricTariff")
    println("--- ElectricTariff keys ---")
    for k in keys(results["ElectricTariff"])
        println(k)
    end
end

# Additional key fields using actual schema keys
annual_energy_kwh = get_nested(results, "PV", "average_annual_energy_produced_kwh")
npv = get_nested(results, "Financial", "lcc")  # Using LCC as NPV proxy since NPV key not present
utility_bill = get_nested(results, "ElectricTariff", "year_one_bill")

println("Annual energy (kWh): ", annual_energy_kwh)
println("NPV (proxy via LCC): ", npv)
println("Utility bill (year one): ", utility_bill)
