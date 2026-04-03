from reopt_pysam_vn.pysam.single_owner import build_single_owner_inputs


def test_single_owner_scaffold_defaults():
    inputs = build_single_owner_inputs(system_capacity_kw=1000)

    assert inputs.system_capacity_kw == 1000
    assert inputs.analysis_years == 20
    assert inputs.debt_fraction == 0.7
