using REopt, JuMP, HiGHS

input_path = joinpath(@__DIR__, "test", "pv_storage.json")

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

function summarize_series(series)
    if series === missing || !(series isa AbstractVector)
        return missing
    end
    if isempty(series)
        return missing
    end
    return Dict(
        "min" => minimum(series),
        "max" => maximum(series),
        "sum" => sum(series)
    )
end

function fmt_financial(x)
    if x === missing || !(x isa Real)
        return "N/A"
    end
    # Round to 2 decimals and add commas
    s = string(round(x, digits=2))
    # Insert commas every three digits before the decimal
    parts = split(s, ".")
    int_part = parts[1]
    dec_part = length(parts) > 1 ? parts[2] : "00"
    # Add commas to integer part
    int_with_commas = ""
    for (i, c) in enumerate(reverse(int_part))
        if i > 1 && (i-1) % 3 == 0
            int_with_commas *= ","
        end
        int_with_commas *= c
    end
    int_with_commas = reverse(int_with_commas)
    return int_with_commas * "." * dec_part
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

if haskey(results, "ElectricStorage")
    println("--- ElectricStorage keys ---")
    for k in keys(results["ElectricStorage"])
        println(k)
    end
end

# Additional key fields using actual schema keys
annual_energy_kwh = get_nested(results, "PV", "average_annual_energy_produced_kwh")
npv = get_nested(results, "Financial", "lcc")  # Using LCC as NPV proxy since NPV key not present
utility_bill = get_nested(results, "ElectricTariff", "year_one_bill")

storage_size_kw = first_present([
    get_nested(results, "ElectricStorage", "size_kw"),
    get_nested(results, "ElectricStorage", "size")
])
storage_size_kwh = first_present([
    get_nested(results, "ElectricStorage", "size_kwh"),
    get_nested(results, "ElectricStorage", "capacity_kwh")
])
storage_year_one_discharge_kwh = first_present([
    get_nested(results, "ElectricStorage", "year_one_discharge_series_kwh"),
    get_nested(results, "ElectricStorage", "year_one_discharge_series_kw")
])
storage_year_one_charge_kwh = first_present([
    get_nested(results, "ElectricStorage", "year_one_charge_series_kwh"),
    get_nested(results, "ElectricStorage", "year_one_charge_series_kw")
])
storage_year_one_to_load_kw = get_nested(results, "ElectricStorage", "year_one_to_load_series_kw")
storage_soc_series_pct = get_nested(results, "ElectricStorage", "year_one_soc_series_pct")
storage_initial_capital_cost = get_nested(results, "ElectricStorage", "initial_capital_cost")
storage_year_one_to_grid_kw = get_nested(results, "ElectricStorage", "year_one_to_grid_series_kw")
storage_year_one_grid_to_battery_kw = get_nested(results, "ElectricStorage", "year_one_grid_to_battery_series_kw")

println("Annual energy (kWh): ", annual_energy_kwh)
println("NPV (proxy via LCC): ", npv)
println("Utility bill (year one): ", utility_bill)
println("Storage size (kW): ", storage_size_kw)
println("Storage size (kWh): ", storage_size_kwh)
println("Storage year-one discharge series (kWh or kW): ", storage_year_one_discharge_kwh)
println("Storage year-one charge series (kWh or kW): ", storage_year_one_charge_kwh)
println("Storage initial capital cost: ", storage_initial_capital_cost)
println("Storage year-one to-load series summary: ", summarize_series(storage_year_one_to_load_kw))
println("Storage SOC series summary: ", summarize_series(storage_soc_series_pct))
println("Storage year-one to-grid series summary: ", summarize_series(storage_year_one_to_grid_kw))
println("Storage year-one grid-to-battery series summary: ", summarize_series(storage_year_one_grid_to_battery_kw))

println("--- PV + Storage Summary ---")
println("Status: ", status)
println("PV size (kW): ", pv_size_kw)
println("PV annual energy (kWh): ", annual_energy_kwh)
println("Storage size (kW): ", storage_size_kw)
println("Storage size (kWh): ", storage_size_kwh)
println("Storage to-load energy (kWh, year one): ", get(summarize_series(storage_year_one_to_load_kw), "sum", missing))
println("Storage SOC min/max (%): ", get(summarize_series(storage_soc_series_pct), "min", missing), "/", get(summarize_series(storage_soc_series_pct), "max", missing))
println("Lifecycle cost (LCC): ", lifecycle_cost)
println("Utility bill (year one): ", utility_bill)
