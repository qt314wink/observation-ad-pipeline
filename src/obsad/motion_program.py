from __future__ import annotations

import copy
import hashlib
import json
import math
from importlib.resources import files
from pathlib import Path
from typing import Any

import fastjsonschema
import yaml

DEFAULT_SCHEMA_PATH = files("obsad.schemas").joinpath("motion-program.schema.json")

SUPPORTED_PROVIDERS = {"generic", "xai", "wan", "comfyui"}

# These relationships are pinned to the Motion Oracle compatibility surface.
TOPOLOGY_GRAMMARS = {
    "radial_annular": {"radial.counterphase", "radial.hinged_aperture"},
    "radial_petaled": {"radial.counterphase", "radial.hinged_aperture"},
    "lattice": {"lattice.excavation"},
    "stratified_relief": {"relief.stratified"},
    "directional_procession": {"directional.procession"},
    "network": {"network.propagation"},
    "cellular": {"cellular.diffusion"},
    "architecture": {"architecture.depth"},
    "portrait_anchor": {"portrait.anchor"},
    "material_macro": {"material.macro"},
}

# Only these primitives change a region's physical placement or shape. They
# must not be applied to locked or stationary regions.
GEOMETRY_CHANGING_PRIMITIVES = {
    "rotate.local",
    "rotate.counterphase",
    "translate.radial",
    "translate.tangential",
    "translate.depth",
    "fold.root_hinge",
    "fold.medial_ridge",
    "fold.saddle",
    "fold.counter",
    "cell.normal_displace",
    "cell.neighbor_diffuse",
}

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


def load(path: Any) -> Any:
    text = path.read_text(encoding="utf-8")
    suffix = Path(path.name).suffix.lower()
    return yaml.safe_load(text) if suffix in {".yaml", ".yml"} else json.loads(text)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _region_map(program: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {region["id"]: region for region in program["structure"]["regions"]}


def _mapping_key_path(path: str, key: Any) -> str:
    return f"{path}.{key}" if isinstance(key, str) else f"{path}[{key!r}]"


def _non_string_mapping_key_paths(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        errors = [path for key in value if not isinstance(key, str)]
        for key, item in value.items():
            errors.extend(_non_string_mapping_key_paths(item, _mapping_key_path(path, key)))
        return errors
    if isinstance(value, list):
        return [
            child
            for index, item in enumerate(value)
            for child in _non_string_mapping_key_paths(item, f"{path}[{index}]")
        ]
    return []


def _non_finite_number_paths(value: Any, path: str = "$") -> list[str]:
    if isinstance(value, float) and not math.isfinite(value):
        return [path]
    if isinstance(value, dict):
        return [
            child
            for key, item in value.items()
            for child in _non_finite_number_paths(item, _mapping_key_path(path, key))
        ]
    if isinstance(value, list):
        return [
            child
            for index, item in enumerate(value)
            for child in _non_finite_number_paths(item, f"{path}[{index}]")
        ]
    return []


def validate_motion_program(program: dict[str, Any], schema_path: Any = DEFAULT_SCHEMA_PATH) -> list[str]:
    non_string_key_paths = _non_string_mapping_key_paths(program)
    if non_string_key_paths:
        return [f"{path} must use string mapping keys" for path in non_string_key_paths]

    non_finite_paths = _non_finite_number_paths(program)
    if non_finite_paths:
        return [f"{path} must be a finite number" for path in non_finite_paths]

    try:
        fastjsonschema.compile(load(schema_path))(program)
    except fastjsonschema.JsonSchemaException as exc:
        return [exc.message]

    errors: list[str] = []
    regions = program["structure"]["regions"]
    region_ids = [region["id"] for region in regions]
    if len(region_ids) != len(set(region_ids)):
        errors.append("structure.regions ids must be unique")

    for region in regions:
        radius = region.get("radius")
        if radius is not None and radius[0] > radius[1]:
            errors.append(
                f"structure.regions.{region['id']}.radius must be ordered inner<=outer; got {radius}"
            )

    scene_ids = [scene["id"] for scene in program["scenes"]]
    if len(scene_ids) != len(set(scene_ids)):
        errors.append("scenes ids must be unique")

    temporal = program["temporal"]
    if "scene_order" in temporal and temporal["scene_order"] != scene_ids:
        errors.append("temporal.scene_order must exactly match scenes order")

    material_names = set(program["materials"])
    shared_target_names = set(region_ids) & material_names
    if shared_target_names:
        errors.append(
            "structure.regions ids and materials keys must be disjoint; shared names: "
            + ", ".join(sorted(shared_target_names))
        )

    experiment_ids = [experiment["id"] for experiment in program.get("calibration", {}).get("experiments", [])]
    if len(experiment_ids) != len(set(experiment_ids)):
        errors.append("calibration.experiments ids must be unique")

    # Only declared regions/materials plus derivable symbolic targets are valid.
    # Microtexture/micro-pattern masks must be explicitly declared rather than
    # silently receiving provider binding authority.
    known_targets = set(region_ids) | material_names | {"all_movable_regions"}
    region_by_id = _region_map(program)
    locked_regions = set(program["preservation"]["locks"]) & set(region_ids)
    allowed_grammars = TOPOLOGY_GRAMMARS[program["semantic"]["topology"]]
    for scene in program["scenes"]:
        if scene["grammar"] not in allowed_grammars:
            errors.append(
                f"{scene['id']}: grammar {scene['grammar']!r} is incompatible with "
                f"topology {program['semantic']['topology']!r}"
            )
        for channel in scene["channels"]:
            target = channel["target"]
            if target not in known_targets:
                errors.append(f"{scene['id']}: channel target {target!r} is not a declared region/material target")
            primitive = channel["primitive"]
            if target in locked_regions and primitive in GEOMETRY_CHANGING_PRIMITIVES:
                errors.append(f"{scene['id']}: {primitive} cannot target locked region {target!r}")
            elif target in region_by_id and not region_by_id[target]["movable"]:
                if primitive in GEOMETRY_CHANGING_PRIMITIVES:
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
        f"{name}: {program['materials'][name]['description']} / response={program['materials'][name]['response']}"
        for name in sorted(program["materials"])
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

    validation_errors = validate_motion_program(program)
    if validation_errors:
        raise ValueError("invalid motion program: " + "; ".join(validation_errors))

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
    for key in sorted(program["constraints"]["failure_classes"]):
        negative_terms.extend(program["constraints"]["failure_classes"][key])
    negative = joiner.join(dict.fromkeys(negative_terms))

    # Deep-copy the entire structured control snapshot. Compiled payloads must
    # remain immutable even if the caller mutates the source program for a
    # later calibration experiment.
    controls = copy.deepcopy({
        "structure": program["structure"],
        "preservation": program["preservation"],
        "materials": program["materials"],
        "scenes": program["scenes"],
        "lighting": program["lighting"],
        "camera": program["camera"],
        "temporal": program["temporal"],
        "constraints": program["constraints"],
    })

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
                "channels": copy.deepcopy(scene["channels"]),
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


def _json_pointer_parts(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError("JSON Pointer paths must begin with '/'")

    parts: list[str] = []
    for token in pointer[1:].split("/"):
        decoded: list[str] = []
        index = 0
        while index < len(token):
            if token[index] != "~":
                decoded.append(token[index])
                index += 1
                continue
            if index + 1 >= len(token) or token[index + 1] not in {"0", "1"}:
                raise ValueError(f"invalid JSON Pointer escape in segment {token!r}")
            decoded.append("~" if token[index + 1] == "0" else "/")
            index += 2
        parts.append("".join(decoded))
    return parts


def _path_parts(path: str) -> list[str]:
    if not isinstance(path, str) or not path:
        raise ValueError("experiment parameter paths must be non-empty strings")
    return _json_pointer_parts(path) if path.startswith("/") else path.split(".")


def get_dotted(value: dict[str, Any], dotted: str) -> Any:
    """Resolve a legacy dotted path or an RFC 6901 JSON Pointer path."""
    current: Any = value
    for part in _path_parts(dotted):
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError as exc:
                raise KeyError(f"list segment {part!r} is not an integer index") from exc
            if index < 0 or index >= len(current):
                raise KeyError(f"list index {index} out of range")
            current = current[index]
        elif isinstance(current, dict):
            if part not in current:
                raise KeyError(f"mapping key {part!r} does not exist")
            current = current[part]
        else:
            raise KeyError(f"cannot descend through scalar at segment {part!r}")
    return current


def set_dotted(value: dict[str, Any], dotted: str, replacement: Any) -> None:
    # Resolve first so a typo can never create a new permissive mapping key.
    get_dotted(value, dotted)
    current: Any = value
    parts = _path_parts(dotted)
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    leaf = parts[-1]
    if isinstance(current, list):
        current[int(leaf)] = replacement
    else:
        current[leaf] = replacement


def _candidate_matches_control_type(reference: Any, candidate: Any) -> bool:
    if isinstance(reference, bool):
        return isinstance(candidate, bool)
    if isinstance(reference, (int, float)) and not isinstance(reference, bool):
        return (
            isinstance(candidate, (int, float))
            and not isinstance(candidate, bool)
            and math.isfinite(float(candidate))
        )
    return type(candidate) is type(reference)


def build_experiment_variants(
    program: dict[str, Any],
    schema_path: Any = DEFAULT_SCHEMA_PATH,
) -> list[dict[str, Any]]:
    calibration = program.get("calibration", {})
    experiments = calibration.get("experiments", [])
    experiment_ids = [experiment["id"] for experiment in experiments]
    if len(experiment_ids) != len(set(experiment_ids)):
        raise ValueError("calibration.experiments ids must be unique")

    variants: list[dict[str, Any]] = []
    for experiment in experiments:
        parameter = experiment["parameter"]
        try:
            reference_value = get_dotted(program, parameter)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError(
                f"{experiment['id']}: experiment parameter {parameter!r} does not resolve: {exc}"
            ) from exc

        for candidate in experiment["values"]:
            if not _candidate_matches_control_type(reference_value, candidate):
                raise ValueError(
                    f"{experiment['id']}: candidate {candidate!r} for {parameter!r} "
                    f"must match the existing {type(reference_value).__name__} control type"
                )
            mutated = copy.deepcopy(program)
            set_dotted(mutated, parameter, candidate)
            errors = validate_motion_program(mutated, schema_path)
            if errors:
                raise ValueError(
                    f"{experiment['id']}: candidate {candidate!r} for {parameter!r} produces an invalid motion program: "
                    + "; ".join(errors)
                )
            variants.append(
                {
                    "experiment_id": experiment["id"],
                    "parameter": parameter,
                    "value": candidate,
                    "prediction": experiment["prediction"],
                    "program": mutated,
                    "program_sha256": sha256(mutated),
                }
            )
    return variants
