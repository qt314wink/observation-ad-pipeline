import json
from pathlib import Path

import fastjsonschema

from obsad.motion import validate_motion_system


def valid_system():
    return {
        "topology": {
            "family": "recursive_nested",
            "center_lock": True,
            "symmetry_order": 8,
            "radial_registration": "strict",
        },
        "layers": [
            {"id": "core", "region": "center", "operator": "aperture_revelation"},
            {"id": "ring-01", "region": "ring", "index": 1, "operator": "radial_wave", "phase_offset_beats": 0.125},
        ],
        "transform": {
            "primary": "recursive_zoom",
            "direction": "inward",
            "scale_start": 1.0,
            "scale_end": 4.0,
            "morph_depth": 0.65,
            "topology_preservation": 0.95,
        },
        "audio_binding": {"timing_source": "external_markers"},
        "splice": {"strategy": "scale_equivalent", "outgoing_phase_degrees": 0, "handle_frames": 12},
        "qa": {"require_first_last_comparison": True},
    }


def test_valid_motion_system_has_no_semantic_errors():
    assert validate_motion_system(valid_system()) == []


def test_rejects_duplicate_layer_ids():
    system = valid_system()
    system["layers"][1]["id"] = "core"
    assert validate_motion_system(system) == ["motion_system.layers: layer ids must be unique"]


def test_strict_registration_requires_center_lock():
    system = valid_system()
    system["topology"]["center_lock"] = False
    assert validate_motion_system(system) == [
        "motion_system.topology.center_lock: required when radial_registration is strict"
    ]


def test_exact_loop_requires_first_last_comparison():
    system = valid_system()
    system["splice"]["strategy"] = "exact_loop_return"
    system["qa"]["require_first_last_comparison"] = False
    assert validate_motion_system(system) == [
        "motion_system.qa.require_first_last_comparison: required for exact_loop_return"
    ]


def test_measured_audio_requires_analysis_artifact():
    system = valid_system()
    system["audio_binding"] = {"timing_source": "measured_analysis"}
    assert validate_motion_system(system) == [
        "motion_system.audio_binding.analysis_artifact: required for measured_analysis"
    ]


def test_schema_rejects_out_of_range_symmetry_and_normalized_values():
    schema = json.loads(Path("obsad-impl/schemas/task.schema.json").read_text())
    validate = fastjsonschema.compile(schema)
    task = {
        "id": "mandala-test",
        "operation": "motion_spec",
        "prompt": {"task": "test", "motion": [], "style": [], "avoid": []},
        "output": {"directory": "output/test"},
        "motion_system": valid_system(),
    }
    task["motion_system"]["topology"]["symmetry_order"] = 65
    task["motion_system"]["transform"]["morph_depth"] = 1.1
    try:
        validate(task)
    except fastjsonschema.JsonSchemaException as exc:
        assert "must be smaller than or equal to" in exc.message
    else:
        raise AssertionError("schema accepted out-of-range motion values")
