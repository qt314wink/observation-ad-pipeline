from __future__ import annotations

import copy
import unittest
from pathlib import Path

from obsad.motion_program import (
    DEFAULT_SCHEMA_PATH,
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

    def test_nonnumeric_lighting_experiment_candidate_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["calibration"]["experiments"] = [
            {
                "id": "EXP-BAD-LIGHT",
                "parameter": "lighting.mineral_probe.incidence_deg",
                "values": ["wrong", 24],
                "prediction": "string controls are invalid",
            }
        ]
        with self.assertRaisesRegex(ValueError, "must match the existing int control type"):
            build_experiment_variants(invalid, SCHEMA)

    def test_unknown_motion_primitive_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["scenes"][0]["channels"][0]["primitive"] = "rotate.locla"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("primitive" in error for error in errors), errors)

    def test_non_finite_numeric_controls_are_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["scenes"][0]["duration_s"] = float("nan")
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("finite number" in error for error in errors), errors)

    def test_locked_region_cannot_move_even_if_marked_movable(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["structure"]["regions"][-1]["movable"] = True
        invalid["scenes"][0]["channels"][0]["target"] = "outer_anchor"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("locked region" in error for error in errors), errors)

    def test_packaged_schema_matches_repository_authority(self) -> None:
        self.assertEqual(load(SCHEMA), load(DEFAULT_SCHEMA_PATH))
        self.assertEqual([], validate_motion_program(self.program))

    def test_compiled_controls_include_immutable_preservation_constraints(self) -> None:
        compiled = compile_motion_program(self.program, "wan")
        self.assertEqual(self.program["preservation"], compiled["controls"]["preservation"])
        self.program["preservation"]["locks"].append("nucleus")
        self.assertNotIn("nucleus", compiled["controls"]["preservation"]["locks"])

    def test_scene_grammar_must_match_declared_topology(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["scenes"][0]["grammar"] = "portrait.anchor"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("incompatible with topology" in error for error in errors), errors)

    def test_geometry_displacement_cannot_target_locked_region(self) -> None:
        invalid = copy.deepcopy(self.program)
        channel = invalid["scenes"][0]["channels"][0]
        channel.update({"primitive": "cell.normal_displace", "target": "outer_anchor"})
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("cell.normal_displace cannot target locked region" in error for error in errors), errors)

    def test_non_string_mapping_keys_are_rejected_before_canonicalization(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["lighting"][7] = "invalid YAML key"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("string mapping keys" in error for error in errors), errors)
        with self.assertRaisesRegex(ValueError, "string mapping keys"):
            compile_motion_program(invalid)

    def test_motion_primitives_require_executable_controls(self) -> None:
        invalid = copy.deepcopy(self.program)
        del invalid["scenes"][0]["channels"][0]["amplitude"]
        del invalid["scenes"][0]["channels"][0]["unit"]
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("amplitude" in error and "unit" in error for error in errors), errors)

    def test_material_response_must_use_authoritative_vocabulary(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["materials"]["opal"]["response"] = "rigdi"
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("response" in error for error in errors), errors)

    def test_calibration_experiment_ids_must_be_unique(self) -> None:
        invalid = copy.deepcopy(self.program)
        duplicate = copy.deepcopy(invalid["calibration"]["experiments"][0])
        invalid["calibration"]["experiments"].append(duplicate)
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("experiments ids must be unique" in error for error in errors), errors)
        with self.assertRaisesRegex(ValueError, "experiments ids must be unique"):
            build_experiment_variants(invalid, SCHEMA)

    def test_explicit_empty_scene_order_is_rejected(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["temporal"]["scene_order"] = []
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("scene_order" in error for error in errors), errors)

    def test_region_and_material_target_names_must_be_disjoint(self) -> None:
        invalid = copy.deepcopy(self.program)
        invalid["materials"]["nucleus"] = copy.deepcopy(invalid["materials"]["opal"])
        errors = validate_motion_program(invalid, SCHEMA)
        self.assertTrue(any("must be disjoint" in error for error in errors), errors)

    def test_json_pointer_experiment_path_addresses_dot_containing_mapping_keys(self) -> None:
        pointer_program = copy.deepcopy(self.program)
        pointer_program["materials"]["blue.opal"] = pointer_program["materials"].pop("opal")
        for scene in pointer_program["scenes"]:
            for channel in scene["channels"]:
                if channel["target"] == "opal":
                    channel["target"] = "blue.opal"
        pointer_program["lighting"]["mineral_probe"]["mask"] = [
            "blue.opal" if material == "opal" else material
            for material in pointer_program["lighting"]["mineral_probe"]["mask"]
        ]
        pointer_program["calibration"]["experiments"] = [
            {
                "id": "EXP-DOTTED-MATERIAL",
                "parameter": "/materials/blue.opal/roughness",
                "values": [0.2, 0.4],
                "prediction": "must update the dot-containing material key only",
            }
        ]
        self.assertEqual([], validate_motion_program(pointer_program, SCHEMA))
        variants = build_experiment_variants(pointer_program, SCHEMA)
        self.assertEqual([0.2, 0.4], [variant["program"]["materials"]["blue.opal"]["roughness"] for variant in variants])


if __name__ == "__main__":
    unittest.main()
