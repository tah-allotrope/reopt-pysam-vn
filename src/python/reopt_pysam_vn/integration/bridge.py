"""Schema bridge placeholders between REopt outputs and PySAM inputs."""


def bridge_stub(reopt_results: dict) -> dict:
    return {"source": "reopt", "financial": reopt_results.get("Financial", {})}
