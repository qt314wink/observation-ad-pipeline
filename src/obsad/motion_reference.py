from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import fastjsonschema
import yaml


MEASURED_FIELDS = {"sha256", "bytes", "durationSeconds", "width", "height", "fps", "codec"}


def load_reference(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: motion reference must be a mapping")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _schema(root: Path) -> dict[str, Any]:
    return json.loads((root / "schemas" / "motion-reference-analysis.schema.json").read_text(encoding="utf-8"))


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dupes: set[str] = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    return sorted(dupes)


def _all_events(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [event for scene in data.get("scenes", []) for event in scene.get("movementEvents", [])]


def validate_motion_reference(path: Path, root: Path) -> list[str]:
    try:
        data = load_reference(path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [str(exc)]

    try:
        fastjsonschema.compile(_schema(root))(data)
    except fastjsonschema.JsonSchemaException as exc:
        location = "/".join(str(part) for part in getattr(exc, "path", []) if part != "data") or "<root>"
        return [f"schema {location}: {exc.message}"]

    errors: list[str] = []
    observations = data.get("observations", [])
    scenes = data.get("scenes", [])
    events = _all_events(data)
    interpretations = data.get("interpretations", [])
    controls = data.get("directorControls", [])
    candidates = data.get("candidatePrimitives", [])

    id_groups = {
        "observation": [item["id"] for item in observations],
        "scene": [item["id"] for item in scenes],
        "movement event": [item["id"] for item in events],
        "interpretation": [item["id"] for item in interpretations],
        "director control": [item["id"] for item in controls],
        "candidate primitive": [item["id"] for item in candidates],
    }
    for label, values in id_groups.items():
        duplicate_ids = _duplicates(values)
        if duplicate_ids:
            errors.append(f"duplicate {label} ids: {duplicate_ids}")

    observation_by_id = {item["id"]: item for item in observations}
    observation_ids = set(observation_by_id)
    scene_ids = {item["id"] for item in scenes}
    event_ids = {item["id"] for item in events}
    control_ids = {item["id"] for item in controls}
    candidate_by_id = {item["id"]: item for item in candidates}

    source = data.get("source", {})
    if source.get("mediaMeasurementStatus") != "measured":
        for field in sorted(MEASURED_FIELDS):
            if field in source:
                errors.append(f"unmeasured source cannot claim measured field {field}")

    for observation in observations:
        scene_ref = observation.get("sceneRef")
        event_ref = observation.get("eventRef")
        if scene_ref and scene_ref not in scene_ids:
            errors.append(f"{observation['id']}: unknown scene {scene_ref}")
        if event_ref and event_ref not in event_ids:
            errors.append(f"{observation['id']}: unknown event {event_ref}")

    for interpretation in interpretations:
        for ref in interpretation.get("evidence", []):
            if ref not in observation_ids:
                errors.append(f"{interpretation['id']}: unknown observation {ref}")

    for control in controls:
        for ref in control.get("evidence", []):
            if ref not in observation_ids:
                errors.append(f"{control['id']}: unknown observation {ref}")

    paper_fold = data.get("paperFoldEvidence", {})
    if paper_fold.get("classification") == "true-origami-verified":
        verified_structural = False
        for ref in paper_fold.get("structuralEvidenceRefs", []):
            observation = observation_by_id.get(ref)
            if observation and observation.get("verificationStatus") == "human-verified":
                verified_structural = True
                break
        if not verified_structural:
            errors.append("true-origami-verified requires human-verified structural evidence")

    for candidate in candidates:
        for ref in candidate.get("evidence", []):
            if ref not in observation_ids:
                errors.append(f"{candidate['id']}: unknown observation {ref}")
        for control_ref in candidate.get("directorControls", []):
            if control_ref not in control_ids:
                errors.append(f"{candidate['id']}: unknown director control {control_ref}")
        if candidate.get("status") == "approved":
            approval = candidate.get("approval") or {}
            if not all(approval.get(key) for key in ("approvedBy", "approvedAt", "evidenceRefs")):
                errors.append(f"{candidate['id']}: approved primitive requires approval receipt")

    gate = data.get("experimentGate", {})
    for ref in gate.get("candidatePrimitiveRefs", []):
        if ref not in candidate_by_id:
            errors.append(f"experiment gate references unknown candidate primitive {ref}")
    if gate.get("status") == "executable":
        blocked = [
            ref for ref in gate.get("candidatePrimitiveRefs", [])
            if candidate_by_id.get(ref, {}).get("status") != "approved"
        ]
        if blocked:
            errors.append(f"experiment gate cannot be executable while candidate primitives are unapproved: {blocked}")

    return errors


def build_review_payload(data: dict[str, Any]) -> dict[str, Any]:
    guide = data.get("humanGuide", {})
    source = data.get("source", {})
    return {
        "canonicalDigest": canonical_sha256(data),
        "referenceId": data["referenceId"],
        "title": source.get("title", data["referenceId"]),
        "creator": source.get("creator"),
        "platform": source.get("platform"),
        "canonicalUrl": source.get("canonicalUrl"),
        "rightsStatus": source.get("rightsStatus"),
        "measurementStatus": source.get("mediaMeasurementStatus"),
        "point": guide.get("point", "Recover how the motion works, not just what it resembles."),
        "proofChain": guide.get(
            "proofChain",
            ["reference", "scenes", "observations", "movement quality", "manner", "hypothesis", "director controls", "test"],
        ),
        "analysisRuns": data.get("analysisRuns", []),
        "directorVocabulary": data.get("directorVocabulary", []),
        "paperFoldEvidence": data.get("paperFoldEvidence", {}),
        "scenes": data.get("scenes", []),
        "observations": data.get("observations", []),
        "interpretations": data.get("interpretations", []),
        "directorControls": data.get("directorControls", []),
        "candidatePrimitives": data.get("candidatePrimitives", []),
        "experimentGate": data.get("experimentGate", {}),
        "blockers": guide.get("blockers", []),
    }
