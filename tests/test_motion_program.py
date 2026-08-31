from __future__ import annotations

import copy
import unittest
from pathlib import Path

from obsad.motion_program import (
    SECTION_ORDER,
    build_experiment_variants,
    compile_motion_program,
    load,
    validate_motion_program,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "motion-program.schema.json"
EXAMPLE = ROOT / "examples" / "motion-programs" / "radial-relief-calibration.yaml"


class MotionProgramTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = load(EXAMPLE)

    def test_example_validates(self) -> None:
        self.assertEqual([], validate_motion_program(self.program, SCHEMA))

    def test_compilation_is_deterministic_and_ordered(self) -> None:
        for provider in ("generic", "xai", "wan", "comfyui"):
            first = compile_motion_program(self.program, provider)
            second = compile_motion_program(self.program, provider)
            self.assertEqual(first, second)
            self.assertEqual(first["compiled_sha256"], second["compiled_sha256"])
            self.assertEqual(list(SECTION_ORDER), [section["name"] for section in first["sections"]])

    def test_locked_outer_anchor_cannot_receive_fold_or_rotation(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["scenes"][0]["channels"][0]["target"] = "outer_anchor"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("locked region" in error for error in errors), errors)

    def test_loop_requires_state_closure(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["temporal"]["first_last_state_match"] = False
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("first_last_state_match" in error for error in errors), errors)

    def test_whole_object_spin_is_explicitly_prohibited(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["preservation"]["prohibited"].remove("whole_object_spin")
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("whole_object_spin" in error for error in errors), errors)

    def test_provider_payload_keeps_numeric_controls_outside_prompt_only_surface(self) -> None:
        compiled = compile_motion_program(self.program, "wan")
        self.assertIn("controls", compiled)
        self.assertEqual(14, compiled["controls"]["scenes"][0]["channels"][0]["amplitude"])
        self.assertTrue(all(stage["execution_status"] == "requires_provider_workflow_binding" for stage in compiled["stages"]))

    def test_experiment_variants_change_only_requested_parameter(self) -> None:
        variants = build_experiment_variants(self.program)
        self.assertEqual(12, len(variants))
        fold = [item for item in variants if item["experiment_id"] == "EXP-FOLD"]
        self.assertEqual([0.2, 0.4, 0.6], [item["value"] for item in fold])
        self.assertEqual(
            [0.2, 0.4, 0.6],
            [item["program"]["scenes"][1]["channels"][0]["strength"] for item in fold],
        )
        self.assertEqual(
            self.program["camera"],
            fold[0]["program"]["camera"],
            "one-factor sweep must leave unrelated control surfaces unchanged",
        )


if __name__ == "__main__":
    unittest.main()
