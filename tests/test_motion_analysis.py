from copy import deepcopy
from pathlib import Path

import yaml

from obsad.validate_motion import REQUIRED_DIMENSIONS, validate_motion_fixture


ROOT = Path(__file__).resolve().parents[1]
MANDALA_FIXTURE = ROOT / "fixtures/motion/mandala-reel-set.yaml"
EXPECTED_MANDALA_SOURCES = {
    ("video:mandala:10006", "input/videos/10006.mp4"),
    ("video:mandala:9040", "input/videos/9040.mp4"),
    ("video:mandala:8594", "input/videos/8594.mp4"),
    ("video:mandala:8586", "input/videos/8586.mp4"),
}


def _write_fixture(tmp_path, fixture):
    path = tmp_path / "fixture.yaml"
    path.write_text(yaml.safe_dump(fixture), encoding="utf-8")
    return path


def test_generic_schema_accepts_valid_governed_fixture_with_not_four_sources(tmp_path):
    fixture = yaml.safe_load(MANDALA_FIXTURE.read_text(encoding="utf-8"))
    fixture["fixtureId"] = "motion:one-source-regression"
    fixture["sources"] = [fixture["sources"][0]]

    assert validate_motion_fixture(_write_fixture(tmp_path, fixture), ROOT) == []


def test_mandala_fixture_has_exactly_its_four_canonical_unique_sources():
    assert validate_motion_fixture(MANDALA_FIXTURE, ROOT) == []
    fixture = yaml.safe_load(MANDALA_FIXTURE.read_text(encoding="utf-8"))
    actual = {(source["id"], source["path"]) for source in fixture["sources"]}

    assert len(fixture["sources"]) == 4
    assert len(actual) == 4
    assert actual == EXPECTED_MANDALA_SOURCES


def test_malformed_schema_structure_fails_before_semantic_invariants(tmp_path):
    malformed = {
        "schemaVersion": "1.0.0",
        "fixtureId": "motion:malformed",
        "taxonomy": sorted(REQUIRED_DIMENSIONS),
        "sources": {"not": "an array"},
    }

    errors = validate_motion_fixture(_write_fixture(tmp_path, malformed), ROOT)

    assert len(errors) == 1
    assert "schema validation failed" in errors[0]


def test_pending_sources_cannot_claim_measured_or_observed_values(tmp_path):
    fixture = yaml.safe_load(MANDALA_FIXTURE.read_text(encoding="utf-8"))
    fixture["fixtureId"] = "motion:pending-evidence-regression"
    fixture["sources"] = [deepcopy(fixture["sources"][0])]
    fixture["sources"][0]["durationSeconds"] = 12.0
    fixture["sources"][0]["observations"] = [
        {"dimension": "symmetry", "claim": "rotates"}
    ]

    errors = validate_motion_fixture(_write_fixture(tmp_path, fixture), ROOT)

    assert any("cannot claim measured field durationSeconds" in error for error in errors)
    assert any("cannot contain observations" in error for error in errors)
