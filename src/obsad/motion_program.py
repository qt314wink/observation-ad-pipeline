from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import fastjsonschema
import yaml

SUPPORTED_PROVIDERS = {"generic", "xai", "wan", "comfyui"}
SECTION_ORDER = (
    "SUBJECT",
    "STRUCTURE",
    "PRESERVATION",
    "MOTION",
    "MATERIALS",
    "LIGHTING",
    "CAMERA",
    "TIMING",
)

PROVIDER_JOINERS = {
    "generic": " ",
    "xai": "; ",
    "wan": ", ",
    "comfyui": ", ",
}


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(text)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _region_map(program: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {region["id"]: region for region in program["structure"]["regions"]}


def validate_motion_program(program: dict[str, Any], schema_path: Path) -> list[str]:
    try:
        fastjsonschema.compile(load(schema_path))(program)
    except fastjsonschema.JsonSchemaException as exc:
        return [exc.message]

    errors: list[str] = []
    regions = program["structure"]["regions"]
    region_ids = [region["id"] for region in regions]
    if len(region_ids) != len(set(region_ids)):
        errors.append("structure.regions ids must be unique")

    scene_ids = [scene["id"] for scene in program["scenes"]]
    if len(scene_ids) != len(set(scene_ids)):
        errors.append("scenes ids must be unique")

    declared_order = program["temporal"].get("scene_order", [])
    if declared_order and declared_order != scene_ids:
        errors.append("temporal.scene_order must exactly match scenes order")

    known_targets = set(region_ids) | set(program["materials"]) | {
        "all_movable_regions",
        "paper_microtexture",
        "micro_patterns",
    }
    region_by_id = _region_map(program)
    for scene in program["scenes"]:
        for channel in scene["channels"]:
            target = channel["target"]
            if target not in known_targets:
                errors.append(f"{scene['id']}: channel target {target!r} is not a declared region/material target")
            if target in region_by_id and not region_by_id[target]["movable"]:
                primitive = channel["primitive"]
                if primitive.startswith(("rotate.", "translate.", "fold.")):
                    errors.append(f"{scene['id']}: {primitive} cannot target stationary region {target!r}")

    if program["temporal"].get("loop") and not program["temporal"].get("first_last_state_match", False):
        errors.append("looped programs must set temporal.first_last_state_match=true")

    if "whole_object_spin" not in set(program["preservation"]["prohibited"]):
        errors.append("preservation.prohibited must explicitly state whole_object_spin unless intentionally authorized")

    return errors


def _fmt_structure(program: dict[str, Any]) -> str:
    pieces = []
    for region in program["structure"]["regions"]:
        state = "movable" if region["movable"] else "stationary"
        detail = region.get("description", region["id"])
        pieces.append(f"{region['id']} ({state}): {detail}")
    symmetry = program["structure"].get("symmetry_order")
    prefix = f"{symmetry}-fold symmetry. " if symmetry else ""
    return prefix + "; ".join(pieces)


def _fmt_channel(channel: dict[str, Any]) -> str:
    parts = [channel["primitive"], f"target={channel['target']}"]
    for key in ("amplitude", "unit", "strength", "start", "end", "phase_offset_s"):
        if key in channel:
            parts.append(f"{key}={channel[key]}")
    parts.append(f"easing={channel['easing']}")
    return " ".join(parts)


def _fmt_motion(program: dict[str, Any]) -> str:
    scenes = []
    for scene in program["scenes"]:
        channels = "; ".join(_fmt_channel(channel) for channel in scene["channels"])
        scenes.append(f"{scene['id']} [{scene['grammar']}, {scene['duration_s']}s]: {channels}")
    return " | ".join(scenes)


def _fmt_materials(program: dict[str, Any]) -> str:
    return "; ".join(
        f"{name}: {spec['description']} / response={spec['response']}"
        for name, spec in program["materials"].items()
    )


def _fmt_lighting(program: dict[str, Any]) -> str:
    return canonical_json(program["lighting"])


def _fmt_camera(program: dict[str, Any]) -> str:
    return canonical_json(program["camera"])


def _fmt_timing(program: dict[str, Any]) -> str:
    temporal = program["temporal"]
    total = sum(float(scene["duration_s"]) for scene in program["scenes"])
    order = temporal.get("scene_order") or [scene["id"] for scene in program["scenes"]]
    return f"scene_order={order}; total_duration_s={total}; fps={temporal['fps']}; loop={temporal['loop']}; first_last_state_match={temporal.get('first_last_state_match', False)}"


def compile_motion_program(program: dict[str, Any], provider: str = "generic") -> dict[str, Any]:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported provider {provider!r}; expected one of {sorted(SUPPORTED_PROVIDERS)}")

    sections = [
        {"name": "SUBJECT", "text": f"{program['semantic']['subject']}. Intent: {program['semantic']['intent']}. Perceptual goal: {', '.join(program['semantic']['perceptual_goal'])}."},
        {"name": "STRUCTURE", "text": _fmt_structure(program)},
        {"name": "PRESERVATION", "text": "LOCK: " + ", ".join(program["preservation"]["locks"]) + "."},
        {"name": "MOTION", "text": _fmt_motion(program)},
        {"name": "MATERIALS", "text": _fmt_materials(program)},
        {"name": "LIGHTING", "text": _fmt_lighting(program)},
        {"name": "CAMERA", "text": _fmt_camera(program)},
        {"name": "TIMING", "text": _fmt_timing(program)},
    ]

    joiner = PROVIDER_JOINERS[provider]
    positive = joiner.join(section["text"] for section in sections)
    negative_terms = list(program["preservation"]["prohibited"])
    for values in program["constraints"]["failure_classes"].values():
        negative_terms.extend(values)
    negative = joiner.join(dict.fromkeys(negative_terms))

    controls = {
        "structure": program["structure"],
        "scenes": program["scenes"],
        "lighting": program["lighting"],
        "camera": program["camera"],
        "temporal": program["temporal"],
        "constraints": program["constraints"],
    }

    payload: dict[str, Any] = {
        "motion_program_id": program["id"],
        "program_sha256": sha256(program),
        "provider": provider,
        "sections": sections,
        "positive": positive,
        "negative": negative,
        "controls": controls,
    }

    if provider in {"wan", "comfyui"}:
        payload["stages"] = [
            {
                "scene_id": scene["id"],
                "grammar": scene["grammar"],
                "duration_s": scene["duration_s"],
                "channels": scene["channels"],
                "execution_status": "requires_provider_workflow_binding",
            }
            for scene in program["scenes"]
        ]
        payload["provider_directive"] = (
            "Bind controls to graph/workflow nodes; keep seed, frame count, masks, sampler, "
            "scheduler, checkpoints, references and output hashes outside prompt prose."
        )
    elif provider == "xai":
        payload["provider_directive"] = (
            "Use the reference image as the structural authority; follow named local targets and "
            "numeric bounds; do not substitute global spin, liquid warping or duplicate overlays."
        )

    payload["compiled_sha256"] = sha256(payload)
    return payload


def set_dotted(value: dict[str, Any], dotted: str, replacement: Any) -> None:
    current: Any = value
    parts = dotted.split(".")
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    leaf = parts[-1]
    if isinstance(current, list):
        current[int(leaf)] = replacement
    else:
        current[leaf] = replacement


def build_experiment_variants(program: dict[str, Any]) -> list[dict[str, Any]]:
    calibration = program.get("calibration", {})
    variants: list[dict[str, Any]] = []
    for experiment in calibration.get("experiments", []):
        for candidate in experiment["values"]:
            mutated = copy.deepcopy(program)
            set_dotted(mutated, experiment["parameter"], candidate)
            variants.append(
                {
                    "experiment_id": experiment["id"],
                    "parameter": experiment["parameter"],
                    "value": candidate,
                    "prediction": experiment["prediction"],
                    "program": mutated,
                    "program_sha256": sha256(mutated),
                }
            )
    return variants
