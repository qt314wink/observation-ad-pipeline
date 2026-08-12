from pathlib import Path

import yaml

from obsad.validate_motion import validate_motion_fixture


ROOT = Path(__file__).resolve().parents[1]


def test_mandala_fixture_has_four_unique_lfs_sources_and_complete_taxonomy():
    fixture = ROOT / "fixtures/motion/mandala-reel-set.yaml"
    assert validate_motion_fixture(fixture, ROOT) == []


def test_pending_sources_cannot_claim_measured_or_observed_values(tmp_path):
    fixture = {
        "schemaVersion": "1.0.0",
        "fixtureId": "motion:test",
        "taxonomy": [
            "symmetry", "radial-topology", "phase-change", "morphing",
            "alignment", "frequency-behavior", "splice-points", "musical-synchronization"
        ],
        "sources": [{
            "id": "video:test",
            "path": "input/videos/test.mp4",
            "evidenceStatus": "pending-source-verification",
            "durationSeconds": 12.0,
            "observations": [{"dimension": "symmetry", "claim": "rotates"}],
        }],
    }
    path = tmp_path / "fixture.yaml"
    path.write_text(yaml.safe_dump(fixture), encoding="utf-8")
    errors = validate_motion_fixture(path, ROOT)
    assert any("cannot claim measured field durationSeconds" in e for e in errors)
    assert any("cannot contain observations" in e for e in errors)

