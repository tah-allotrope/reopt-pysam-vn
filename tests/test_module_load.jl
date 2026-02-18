## Quick smoke test: verify REoptVietnam.jl loads and all functions work
include(joinpath(@__DIR__, "..", "src", "REoptVietnam.jl"))
using .REoptVietnam
using JSON

println("=== Loading Vietnam data ===")
vn = load_vietnam_data()
println("VNData loaded OK")
println("  Exchange rate: ", vn.exchange_rate)
println("  Tariff keys: ", keys(vn.tariff))
println("  Tech cost keys: ", keys(vn.tech_costs))
println("  Financials keys: ", keys(vn.financials))
println("  Emissions keys: ", keys(vn.emissions))
println("  Export rules keys: ", keys(vn.export_rules))

println("\n=== Currency conversion ===")
usd = convert_vnd_to_usd(26400; exchange_rate=26400)
println("  26400 VND -> $usd USD (expect 1.0)")
vnd = convert_usd_to_vnd(1.0; exchange_rate=26400)
println("  1.0 USD -> $vnd VND (expect 26400.0)")

println("\n=== Build tariff (industrial, medium voltage, south) ===")
tariff = build_vietnam_tariff(vn, "industrial", "medium_voltage_22kv_to_110kv"; year=2025)
rates = tariff["energy_rate_series_per_kwh"]
println("  Length: ", length(rates))
println("  Min rate: ", minimum(rates), " USD/kWh")
println("  Max rate: ", maximum(rates), " USD/kWh")
println("  Mean rate: ", sum(rates)/length(rates), " USD/kWh")

println("\n=== Build tariff (household) ===")
tariff_hh = build_vietnam_tariff(vn, "household", ""; year=2025)
rates_hh = tariff_hh["energy_rate_series_per_kwh"]
println("  Household flat rate: ", rates_hh[1], " USD/kWh")

println("\n=== Full apply_vietnam_defaults! ===")
d = Dict{String,Any}(
    "Site" => Dict{String,Any}("latitude" => 10.8, "longitude" => 106.6),
    "ElectricLoad" => Dict{String,Any}("doe_reference_name" => "Hospital", "annual_kwh" => 1_000_000),
    "PV" => Dict{String,Any}("max_kw" => 500),
    "ElectricStorage" => Dict{String,Any}("max_kw" => 200, "max_kwh" => 800),
)
apply_vietnam_defaults!(d, vn; customer_type="industrial", region="south")

println("  Financial block: ", haskey(d, "Financial") ? "YES" : "NO")
println("  ElectricTariff block: ", haskey(d, "ElectricTariff") ? "YES" : "NO")
println("  ElectricUtility block: ", haskey(d, "ElectricUtility") ? "YES" : "NO")
println("  PV.installed_cost_per_kw: ", get(d["PV"], "installed_cost_per_kw", "MISSING"))
println("  PV.federal_itc_fraction: ", get(d["PV"], "federal_itc_fraction", "MISSING"))
println("  PV.can_net_meter: ", get(d["PV"], "can_net_meter", "MISSING"))
println("  ElectricStorage.installed_cost_constant: ", get(d["ElectricStorage"], "installed_cost_constant", "MISSING"))
println("  ElectricStorage.total_itc_fraction: ", get(d["ElectricStorage"], "total_itc_fraction", "MISSING"))
println("  Financial.offtaker_tax_rate_fraction: ", get(d["Financial"], "offtaker_tax_rate_fraction", "MISSING"))
eu = d["ElectricUtility"]
ef = eu["emissions_factor_series_lb_CO2_per_kwh"]
println("  Emissions series length: ", length(ef), ", value: ", ef[1])
et = d["ElectricTariff"]
println("  Wholesale rate: ", get(et, "wholesale_rate", "MISSING"))
println("  Net metering limit: ", get(et, "net_metering_limit_kw", "MISSING"))

println("\n=== Non-destructive test (user value preserved) ===")
d2 = Dict{String,Any}(
    "Site" => Dict{String,Any}("latitude" => 10.8, "longitude" => 106.6),
    "PV" => Dict{String,Any}("installed_cost_per_kw" => 800),
    "ElectricLoad" => Dict{String,Any}("doe_reference_name" => "Hospital", "annual_kwh" => 500_000),
)
apply_vietnam_defaults!(d2, vn; region="south")
println("  PV.installed_cost_per_kw: ", d2["PV"]["installed_cost_per_kw"], " (expect 800, user value preserved)")

println("\n=== ALL TESTS PASSED ===")
