import json

from obsad.motion import canonical_motion_manifest, compile_motion_system
from test_motion_validation import valid_system


def test_structured_motion_compiles_deterministically():
    system = valid_system()
    first = compile_motion_system(system)
    second = compile_motion_system(system)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["locks"][0] == "visual center"
    assert len(first["actions"]) <= 5
    assert first["manifest"] == canonical_motion_manifest(system)


def test_compilation_expresses_topology_operator_and_splice():
    result = compile_motion_system(valid_system())
    assert "eightfold radial symmetry" in result["locks"]
    assert result["actions"][0] == "perform a center-locked recursive zoom inward"
    assert result["final_state"] == "end on a scale-equivalent registered state with matched motion continuity"
    assert "center drift" in result["negative"]
