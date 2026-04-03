"""Contract-level helpers for PySAM-backed PPA workflows."""


def strike_price_series(base_price, years):
    return [float(base_price)] * int(years)
