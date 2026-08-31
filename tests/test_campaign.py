from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from obsad.campaign import SECTION_ORDER, compile_provider, load, validate_campaign

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "campaigns/calcium-nourish-the-signal"


class CampaignTest(unittest.TestCase):
    def test_campaign_cross_file_validation(self) -> None:
        self.assertEqual([], validate_campaign(CAMPAIGN, ROOT / "schemas/campaign-contract.schema.json"))

    def test_compilation_is_deterministic_and_ordered_for_all_providers(self) -> None:
        for provider in ("openai", "xai", "comfyui", "wan"):
            first = compile_provider(CAMPAIGN, provider)
            second = compile_provider(CAMPAIGN, provider)
            self.assertEqual(first, second)
            self.assertEqual([name.upper() for name in SECTION_ORDER], [s["name"] for s in first["sections"]])
            self.assertEqual(first["compiled_sha256"], second["compiled_sha256"])
            self.assertTrue(first["model"].startswith("${OBSAD_"))

    def test_constraints_and_post_typography_survive_every_adapter(self) -> None:
        forbidden = load(CAMPAIGN / "creative-contract.json")["negative_constraints"]
        for provider in ("openai", "xai", "comfyui", "wan"):
            compiled = compile_provider(CAMPAIGN, provider)
            negative = next(s["text"] for s in compiled["sections"] if s["name"] == "NEGATIVE_CONSTRAINTS")
            self.assertTrue(all(term in negative for term in forbidden))
            typography = next(s["text"] for s in compiled["sections"] if s["name"] == "TYPOGRAPHY_PLACEHOLDER")
            self.assertIn("deterministically in post", typography)

    def test_keyframe_and_isolate_lineage(self) -> None:
        keys = load(CAMPAIGN / "tasks/keyframes.yaml")["keyframes"]
        isolates = load(CAMPAIGN / "tasks/motion-isolates.yaml")["isolates"]
        self.assertEqual([f"K{i:02}" for i in range(1, 9)], [item["id"] for item in keys])
        self.assertEqual([f"M{i:02}" for i in range(1, 9)], [item["id"] for item in isolates])
        key_ids = {item["id"] for item in keys}
        self.assertTrue(all(item["start_keyframe"] in key_ids and item["end_keyframe"] in key_ids for item in isolates))

    def test_workflow_patches_resolve(self) -> None:
        workflow = load(CAMPAIGN / "workflows/wan-staged-api.json")
        patch_doc = load(CAMPAIGN / "workflows/wan-patches.yaml")
        for patch in patch_doc["patches"]:
            self.assertIn(patch["node"], workflow)
            self.assertIn(patch["input"], workflow[patch["node"]]["inputs"])

    def test_platforms_and_manifest_trace_to_contract(self) -> None:
        contract = load(CAMPAIGN / "creative-contract.json")
        tasks = load(CAMPAIGN / "tasks/channel-derivatives.yaml")["outputs"]
        manifest = load(CAMPAIGN / "outputs/final-asset-manifest.json")
        expected = {(x["id"], x["width"], x["height"]) for x in contract["platform_targets"]}
        actual = {(x["id"], x["width"], x["height"]) for x in tasks}
        self.assertEqual(expected, actual)
        self.assertEqual("../creative-contract.json", manifest["contract"])
        self.assertTrue(all(item["derives_from"] == "social_master" for item in manifest["derivatives"]))
        self.assertTrue(all(item["asset"] is None for item in manifest["derivatives"]))


    def test_keyframe_compilation_is_task_specific(self) -> None:
        first = compile_provider(CAMPAIGN, "wan", task_id="K01")
        second = compile_provider(CAMPAIGN, "wan", task_id="K02")
        self.assertNotEqual(first["compiled_sha256"], second["compiled_sha256"])
        self.assertEqual("K01", first["task"]["id"])
        self.assertEqual(314151, first["seed"])
        self.assertIn("single restrained cyan pulse", first["positive"])

    def test_schedule_and_workflow_are_connected(self) -> None:
        isolates = load(CAMPAIGN / "tasks/motion-isolates.yaml")["isolates"]
        self.assertEqual(15.0, sum(item["duration_seconds"] for item in isolates))
        workflow = load(CAMPAIGN / "workflows/wan-staged-api.json")
        self.assertEqual(["7", 0], workflow["5"]["inputs"]["latent_image"])
        self.assertEqual(["8", 0], workflow["6"]["inputs"]["images"])
        self.assertEqual(["4", 0], workflow["7"]["inputs"]["pixels"])
        self.assertEqual(["5", 0], workflow["8"]["inputs"]["samples"])

    def test_manifest_hash_and_invalid_contract_diagnostics(self) -> None:
        contract = load(CAMPAIGN / "creative-contract.json")
        manifest = load(CAMPAIGN / "outputs/final-asset-manifest.json")
        from obsad.campaign import sha256
        self.assertEqual(sha256(contract), manifest["contract_sha256"])
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "campaign"
            shutil.copytree(CAMPAIGN, copy)
            invalid = load(copy / "creative-contract.json")
            invalid.pop("qa_requirements")
            (copy / "creative-contract.json").write_text(json.dumps(invalid), encoding="utf-8")
            errors = validate_campaign(copy, ROOT / "schemas/campaign-contract.schema.json")
            self.assertTrue(errors)
            self.assertTrue(any("qa_requirements" in error for error in errors))

    def test_validation_rejects_cycles_unknown_blockers_and_stale_manifest(self) -> None:
        mutations = (
            lambda contract: contract["platform_targets"][0].update({"derives_from": "social_master"}),
            lambda contract: contract["qa_requirements"]["blocking_dimensions"].append("typo_dimension"),
            lambda contract: contract.update({"campaign_name": "Changed without manifest refresh"}),
        )
        expected = ("cyclic platform derivation", "not weighted", "contract_sha256")
        for mutate, message in zip(mutations, expected):
            with tempfile.TemporaryDirectory() as temp:
                copy = Path(temp) / "campaign"
                shutil.copytree(CAMPAIGN, copy)
                contract = load(copy / "creative-contract.json")
                mutate(contract)
                (copy / "creative-contract.json").write_text(json.dumps(contract), encoding="utf-8")
                errors = validate_campaign(copy, ROOT / "schemas/campaign-contract.schema.json")
                self.assertTrue(any(message in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
