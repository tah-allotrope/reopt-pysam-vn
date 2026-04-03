"""Cash-flow helpers for future PySAM wrappers."""


def years_index(analysis_years: int) -> list[int]:
    return list(range(1, int(analysis_years) + 1))
