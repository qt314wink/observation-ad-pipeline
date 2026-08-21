from __future__ import annotations

import copy
import unittest
from pathlib import Path

from obsad.motion_program import (
    build_experiment_variants,
    compile_motion_program,
    load,
    sha256,
    validate_motion_program,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "motion-program.schema.json"
EXAMPLE = ROOT / "examples" / "motion-programs" / "radial-relief-calibration.yaml"


class MotionProgramReviewRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = load(EXAMPLE)

    def test_compiled_controls_preserve_numeric_material_parameters(self) -> None:
        compiled = compile_motion_program(self.program, "wan")
        labradorite = compiled["controls"]["materials"]["labradorite"]
        self.assertEqual(0.82, labradorite["flash_strength"])
        self.assertEqual(22, labradorite["flash_threshold_deg"])
        self.assertEqual(0.31, labradorite["roughness"])

    def test_material_mapping_order_cannot_change_prompt_for_same_program_hash(self) -> None:
        reordered = copy.deepcopy(self.program)
        reordered["materials"] = dict(reversed(list(reordered["materials"].items())))
        self.assertEqual(sha256(self.program), sha256(reordered))
        first = compile_motion_program(self.program, "generic")
        second = compile_motion_program(reordered, "generic")
        self.assertEqual(first["positive"], second["positive"])
        self.assertEqual(first["negative"], second["negative"])
        self.assertEqual(first["compiled_sha256"], second["compiled_sha256"])

    def test_reversed_radial_bounds_are_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["structure"]["regions"][1]["radius"] = [0.76, 0.48]
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("inner<=outer" in error for error in errors), errors)

    def test_undeclared_microtexture_target_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["scenes"][0]["channels"][0]["target"] = "paper_microtexture"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("not a declared region/material target" in error for error in errors), errors)

    def test_compiled_payload_is_snapshot_not_alias_of_source_program(self) -> None:
        compiled = compile_motion_program(self.program, "wan")
        original_stage_amplitude = compiled["stages"][0]["channels"][0]["amplitude"]
        original_control_amplitude = compiled["controls"]["scenes"][0]["channels"][0]["amplitude"]
        original_material_roughness = compiled["controls"]["materials"]["wood"]["roughness"]
        original_hash = compiled["compiled_sha256"]

        self.program["scenes"][0]["channels"][0]["amplitude"] = 999
        self.program["materials"]["wood"]["roughness"] = 0.01

        self.assertEqual(original_stage_amplitude, compiled["stages"][0]["channels"][0]["amplitude"])
        self.assertEqual(original_control_amplitude, compiled["controls"]["scenes"][0]["channels"][0]["amplitude"])
        self.assertEqual(original_material_roughness, compiled["controls"]["materials"]["wood"]["roughness"])
        self.assertEqual(original_hash, compiled["compiled_sha256"])

    def test_invalid_experiment_path_is_a_bounded_value_error(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["calibration"]["experiments"] = [
            {
                "id": "EXP-BAD-PATH",
                "parameter": "scenes.99.channels.0.strength",
                "values": [0.2, 0.4],
                "prediction": "must not run",
            }
        ]
        with self.assertRaisesRegex(ValueError, "does not resolve"):
            build_experiment_variants(invalid, SCHEMA)

    def test_schema_invalid_experiment_candidate_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["calibration"]["experiments"] = [
            {
                "id": "EXP-BAD-FPS",
                "parameter": "temporal.fps",
                "values": [0, 24],
                "prediction": "zero fps is invalid",
            }
        ]
        with self.assertRaisesRegex(ValueError, "invalid motion program"):
            build_experiment_variants(invalid, SCHEMA)


if __name__ == "__main__":
    unittest.main()
