from obsad.cli import compile_prompt


def test_task_without_motion_system_keeps_legacy_output():
    task = {
        "id": "legacy-task",
        "operation": "generate",
        "prompt": {
            "task": "Create the requested output.",
            "locks": ["composition"],
            "motion": ["subtle breath"],
            "camera": ["stable push-in"],
            "event": "brief light pulse",
            "final_state": "poised suspension",
            "style": ["tactile collage"],
            "avoid": ["camera shake"],
        },
        "output": {"directory": "output/legacy"},
    }
    assert compile_prompt(task) == {
        "positive": "Create the requested output. LOCK: preserve composition. MOTION: subtle breath. CAMERA: stable push-in. EVENT: brief light pulse. FINAL: poised suspension. STYLE: tactile collage.",
        "negative": "camera shake",
        "stats": {"positive_chars": 179, "negative_chars": 12, "locks": 1, "actions": 1, "styles": 1},
    }
