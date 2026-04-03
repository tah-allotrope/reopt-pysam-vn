"""Strike-search scaffolding for REopt plus PySAM workflows."""


def bounded_midpoint(lower: float, upper: float) -> float:
    return (float(lower) + float(upper)) / 2.0
