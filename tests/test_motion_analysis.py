from copy import deepcopy
from pathlib import Path

import yaml

import obsad.validate_motion as motion_validation
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
        "subjectContinuity": [],
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


def test_owl_subject_continuity_reads_as_a_before_during_after_story():
    _validator()
    fixture = yaml.safe_load((ROOT / "fixtures/motion-references/magical-ai-books.yaml").read_text(encoding="utf-8"))
    owl = next(item for item in fixture["subjectContinuity"] if item["id"] == "SUBJ.OWL")
    assert owl["sceneRef"] == "S01"
    assert [state["phase"] for state in owl["states"]] == [
        "before-emergence", "threshold", "emerging", "newly-spatial", "aftermath"
    ]
    required_story_fields = {
        "appearance", "material", "texture", "construction", "composition",
        "behavior", "characteristics", "movementQuality", "provenance", "verificationStatus"
    }
    for state in owl["states"]:
        assert required_story_fields <= set(state)
        assert state["appearance"]["summary"]
        assert state["composition"]["relationshipToSourcePlane"]
    assert owl["continuityQuestions"]
    assert owl["unknowns"]


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


def test_future_information_ablation_experiment_is_case_study_ready():
    manifest = yaml.safe_load((ROOT / "experiments/wan/representation-boundary-breach.yaml").read_text(encoding="utf-8"))
    ablation = manifest["informationAblation"]
    assert ablation["status"] == "planned-blocked"
    assert {variant["id"] for variant in ablation["variants"]} >= {
        "full-record", "every-third-field", "every-fourth-field", "targeted-erasure", "mad-libs-replacement"
    }
    capture = manifest["caseStudyCapture"]
    for field in (
        "challenge", "hypothesis", "inputSnapshot", "compiledArtifact", "runtimeReceipt",
        "outputAssets", "evaluation", "failureAnalysis", "selectionDecision", "lessons"
    ):
        assert field in capture
    assert "mannerism_fidelity" in manifest["evaluationMetrics"]
    assert "subject_state_fidelity" in manifest["evaluationMetrics"]
