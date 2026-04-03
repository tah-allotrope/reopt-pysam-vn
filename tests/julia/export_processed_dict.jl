"""
Helper script for Layer 3 cross-validation.

Loads a minimal scenario JSON, applies Vietnam defaults via REoptVietnam.jl,
and writes the processed dict to a JSON file for comparison with Python output.

Usage:
    julia --project tests/julia/export_processed_dict.jl <input.json> <output.json> [year]

Arguments:
    input.json   — Minimal scenario JSON (same file used by Python cross-validation)
    output.json  — Path to write the processed dict
    year         — (optional) Year for tariff generation, default 2025
"""

using JSON

const REPO_ROOT = abspath(joinpath(@__DIR__, "..", ".."))
include(joinpath(REPO_ROOT, "src", "julia", "REoptVietnam.jl"))
using .REoptVietnam

function main()
    if length(ARGS) < 2
        error("Usage: julia --project tests/julia/export_processed_dict.jl <input.json> <output.json> [year]")
    end

    input_path = ARGS[1]
    output_path = ARGS[2]
    year = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : 2025

    # Load input scenario
    d = JSON.parsefile(input_path)

    # Load Vietnam data
    vn = load_vietnam_data()

    # Apply all Vietnam defaults with fixed parameters for reproducibility
    apply_vietnam_defaults!(d, vn;
        customer_type="industrial",
        voltage_level="medium_voltage_22kv_to_110kv",
        region="south",
        pv_type="rooftop",
        wind_type="onshore",
        financial_profile="standard",
        currency="USD",
        exchange_rate=26400.0,
    )

    # Rebuild tariff with fixed year for reproducibility (overwrite the one from apply_vietnam_defaults!)
    tariff_dict = build_vietnam_tariff(vn, "industrial", "medium_voltage_22kv_to_110kv";
                                        exchange_rate=26400.0, year=year)
    for (k, v) in tariff_dict
        d["ElectricTariff"][k] = v
    end

    # Write output
    open(output_path, "w") do f
        JSON.print(f, d, 2)
    end

    println("Exported processed dict to: $output_path")
end

main()
