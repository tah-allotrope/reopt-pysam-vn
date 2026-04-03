"""
Compatibility shim for the relocated Julia module.
Prefer `include(joinpath(REPO_ROOT, "src", "julia", "REoptVietnam.jl"))`.
"""

include(joinpath(@__DIR__, "julia", "REoptVietnam.jl"))
