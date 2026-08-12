from pathlib import Path

import yaml


ROOT = Path("obsad-impl")


def load(path):
    return yaml.safe_load((ROOT / path).read_text())


def test_manifest_governs_four_external_sources():
    manifest = load("fixtures/motion/mandala-videos/manifest.yaml")
    sources = manifest["sources"]
    assert [item["id"] for item in sources] == ["10006", "8586", "8594", "9040"]
    assert all(item["binary_committed"] is False for item in sources)
    assert all(item["hash_status"] == "pending_governed_ingestion" for item in sources)


def test_observations_are_separate_from_inferences():
    records = load("fixtures/motion/mandala-videos/observations.yaml")["records"]
    assert len(records) == 4
    assert all(record["observations"] and record["inferences"] for record in records)
    assert all("fact" in fact and "claim" not in fact for record in records for fact in record["observations"])
    assert all("claim" in claim and "evidence" in claim for record in records for claim in record["inferences"])


def test_prompt_pack_has_six_complete_recipes():
    pack = load("prompt-packs/motion/recursive-mandala.yaml")
    assert len(pack["recipes"]) == 6
    for recipe in pack["recipes"]:
        assert recipe["locks"] and recipe["motion"] and recipe["final_state"] and recipe["negative"]
