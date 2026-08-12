from obsad.motion import compare_splice


def state(**overrides):
    result = {
        "strategy": "scale_equivalent",
        "topology_family": "recursive_nested",
        "symmetry_order": 8,
        "center": [0.5, 0.5],
        "phase_degrees": 0,
        "scale": 4.0,
        "scale_velocity": 0.25,
        "palette": "violet-cyan",
        "center_motif": "aperture",
        "persistent_anchors": ["blue-orbs"],
        "motion_vector": "inward",
    }
    result.update(overrides)
    return result


def test_exact_splice_passes():
    result = compare_splice(state(), state())
    assert result["valid"] is True
    assert [check["field"] for check in result["checks"]] == [
        "topology_family", "symmetry_order", "center", "phase_degrees", "scale",
        "scale_velocity", "palette", "center_motif", "persistent_anchors", "motion_vector",
    ]


def test_center_and_circular_phase_fail_with_evidence():
    result = compare_splice(state(), state(center=[0.53, 0.5], phase_degrees=359), {"center": 0.01, "phase_degrees": 0.5})
    assert result["valid"] is False
    checks = {item["field"]: item for item in result["checks"]}
    assert checks["center"]["delta"] == 0.03
    assert checks["phase_degrees"]["delta"] == 1
