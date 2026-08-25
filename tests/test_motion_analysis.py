from copy import deepcopy
from pathlib import Path

import yaml

import obsad.validate_motion as motion_validation
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


def _validator():
    validator = getattr(motion_validation, "validate_motion_reference", None)
    assert callable(validator), "validate_motion_reference must be exposed by obsad.validate_motion"
    return validator


def _base_reference():
    provenance = {"kind": "model-derived-observation", "sourceRef": "AN01"}
    return {
        "schemaVersion": "1.0.0",
        "referenceId": "video:reference:test",
        "source": {
            "kind": "external-video",
            "title": "Test reference",
            "creator": "Test creator",
            "platform": "youtube",
            "canonicalUrl": "https://www.youtube.com/watch?v=test",
            "rightsStatus": "reference-analysis-only",
            "mediaMeasurementStatus": "unmeasured",
        },
        "analysisRuns": [{
            "id": "AN01",
            "provider": "test-analyzer",
            "status": "completed",
            "coverage": "one imported scene",
        }],
        "directorVocabulary": [{
            "term": "stiff",
            "scope": "reference",
            "provenance": {"kind": "director-provided", "sourceRef": "working-session"},
            "verificationStatus": "imported-unverified",
        }],
        "paperFoldEvidence": {
            "classification": "origami-like",
            "structuralEvidenceRefs": [],
        },
        "scenes": [{
            "id": "S01",
            "temporalSpan": {"start": "0:00", "end": "0:01", "provenanceRef": "AN01"},
            "visualSummary": "A book opens.",
            "audioSummary": "Paper sound.",
            "camera": "static close-up",
            "lightColor": "warm",
            "environment": "table",
            "actorsObjects": ["book"],
            "interaction": "cover moves",
            "provenance": provenance,
            "movementEvents": [{
                "id": "EV01",
                "actor": "book",
                "part": "cover",
                "action": "opens",
                "structuralMechanisms": ["hinge"],
                "materialBehavior": {
                    "rigidity": "rigid",
                    "surfaceStretch": "none-visible",
                    "facePlanarity": "preserved",
                    "articulationLocality": "edge/crease-localized",
                    "thicknessBehavior": "constant-looking",
                    "collisionContact": "none-visible",
                },
                "movementQuality": {
                    "flow": "bound",
                    "time": "sustained",
                    "space": "direct",
                    "weight": "light",
                    "continuity": "segmented",
                    "stiffness": "stiff",
                },
                "manner": {
                    "leadPart": "cover edge",
                    "followParts": ["cover face"],
                    "coordination": "leader-follower",
                    "cadence": "staggered",
                    "transitionCharacter": ["ease", "settle"],
                    "phaseSequence": ["edge lifts", "cover rotates", "cover settles"],
                    "microMannerisms": [],
                    "directorPhrase": "A restrained hinge-led opening that settles rather than snaps.",
                },
                "spatialPath": {"family": "hinge-arc", "direction": "upward"},
                "timing": {"apparentTempo": "slow", "hold": "brief"},
                "provenance": provenance,
            }],
        }],
        "observations": [{
            "id": "OBS01",
            "scope": "scene",
            "category": "motion",
            "statement": "The book cover opens.",
            "provenance": provenance,
            "confidence": 0.9,
            "verificationStatus": "imported-unverified",
            "sceneRef": "S01",
        }],
        "interpretations": [{
            "id": "INF01",
            "label": "representation-boundary-breach",
            "statement": "The source plane may act as a retained boundary while depth emerges.",
            "evidence": ["OBS01"],
            "confidence": 0.6,
            "status": "candidate",
            "falsifier": "The apparent boundary disappears before depth becomes legible.",
            "usefulness": "Distinguishes a breach mechanism from an unconstrained morph.",
        }],
        "directorControls": [{
            "id": "CTRL01",
            "label": "Panel rigidity",
            "question": "How stiff should the movement feel?",
            "targetFields": ["scenes.S01.movementEvents.EV01.movementQuality.stiffness"],
            "valueType": "enum",
            "allowedValues": ["soft", "supple", "firm", "stiff", "rigid"],
            "defaultValue": "stiff",
            "locked": False,
            "whatYouWillSee": "Higher values preserve flatter, less rubbery moving regions.",
            "tooLowLooksLike": "The object behaves like cloth or rubber.",
            "tooHighLooksLike": "The motion becomes mechanically frozen.",
            "evidence": ["OBS01"],
            "confidence": 0.5,
            "basis": "inference-backed",
        }],
        "candidatePrimitives": [{
            "id": "representation-boundary-breach.v1",
            "status": "candidate",
            "evidence": ["OBS01"],
            "directorControls": ["CTRL01"],
        }],
        "experimentGate": {
            "status": "blocked",
            "candidatePrimitiveRefs": ["representation-boundary-breach.v1"],
            "reason": "Primitive is not approved.",
        },
    }


def _write_reference(tmp_path, data):
    path = tmp_path / "reference.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_generic_motion_reference_validator_accepts_governed_fixture():
    validator = _validator()
    fixture = ROOT / "fixtures/motion-references/magical-ai-books.yaml"
    assert validator(fixture, ROOT) == []


def test_motion_reference_rejects_unknown_inference_evidence(tmp_path):
    validator = _validator()
    data = _base_reference()
    data["interpretations"][0]["evidence"] = ["OBS404"]
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("unknown observation OBS404" in error for error in errors)


def test_motion_reference_rejects_unverified_true_origami_claim(tmp_path):
    validator = _validator()
    data = _base_reference()
    data["paperFoldEvidence"] = {
        "classification": "true-origami-verified",
        "structuralEvidenceRefs": ["OBS01"],
    }
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("true-origami-verified requires human-verified structural evidence" in error for error in errors)


def test_motion_reference_rejects_event_without_manner(tmp_path):
    validator = _validator()
    data = _base_reference()
    del data["scenes"][0]["movementEvents"][0]["manner"]
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("manner" in error for error in errors)


def test_motion_reference_rejects_unmeasured_media_claims(tmp_path):
    validator = _validator()
    data = _base_reference()
    data["source"]["durationSeconds"] = 117.0
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("unmeasured source cannot claim measured field durationSeconds" in error for error in errors)


def test_motion_reference_rejects_unreceipted_primitive_approval(tmp_path):
    validator = _validator()
    data = _base_reference()
    data["candidatePrimitives"][0]["status"] = "approved"
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("approved primitive requires approval receipt" in error for error in errors)


def test_motion_reference_rejects_executable_gate_for_candidate_primitive(tmp_path):
    validator = _validator()
    data = _base_reference()
    data["experimentGate"]["status"] = "executable"
    errors = validator(_write_reference(tmp_path, data), ROOT)
    assert any("experiment gate cannot be executable" in error for error in errors)


def test_magical_ai_books_fixture_preserves_imported_scene_and_director_context():
    _validator()
    fixture = yaml.safe_load((ROOT / "fixtures/motion-references/magical-ai-books.yaml").read_text(encoding="utf-8"))
    assert [scene["id"] for scene in fixture["scenes"]] == [f"S{i:02d}" for i in range(1, 11)]
    assert {item["term"] for item in fixture["directorVocabulary"]} == {
        "rigid", "staggered", "stiff", "shuffling", "tessellating", "bending",
        "wrapping", "folding", "contorting", "linking", "creasing",
    }
    assert all(scene["provenance"]["kind"] == "model-derived-observation" for scene in fixture["scenes"])
    assert any(event.get("manner", {}).get("directorPhrase") for scene in fixture["scenes"] for event in scene["movementEvents"])
    assert {item["id"] for item in fixture["interpretations"]} == {
        "INF.REPRESENTATION_BOUNDARY_BREACH",
        "INF.DIEGETIC_WITNESS_INTERACTION",
        "INF.SOURCE_PLANE_PERSISTENCE",
        "INF.LOCALIZED_DEPTH_ESCALATION",
        "INF.PHYSICAL_CONSEQUENCE",
    }


def test_director_controls_explain_visible_effect_and_failure_extremes():
    _validator()
    fixture = yaml.safe_load((ROOT / "fixtures/motion-references/magical-ai-books.yaml").read_text(encoding="utf-8"))
    expected = {
        "source_plane_persistence", "breach_amount", "panel_rigidity", "fold_localization",
        "stagger_amount", "cascade_direction", "catch_lock_strength", "secondary_lag",
        "asymmetry", "settling_amount", "witness_interaction", "camera_reaction", "environment_spill",
    }
    controls = {item["id"]: item for item in fixture["directorControls"]}
    assert expected <= set(controls)
    for control_id in expected:
        control = controls[control_id]
        assert control["question"]
        assert control["whatYouWillSee"]
        assert control["tooLowLooksLike"]
        assert control["tooHighLooksLike"]
        assert control["basis"] in {"observation-backed", "inference-backed", "exploratory"}
