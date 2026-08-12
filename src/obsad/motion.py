from __future__ import annotations

from copy import deepcopy
from typing import Any


OPERATOR_PHRASES = {
    "recursive_zoom": "perform a center-locked recursive zoom",
    "ring_replacement": "replace concentric rings at gated scale thresholds",
    "sector_substitution": "substitute registered radial sectors sequentially",
    "topology_preserving_morph": "morph motifs while preserving radial topology",
    "material_transmutation": "transmute material while preserving motif silhouettes",
    "chromatic_migration": "migrate the dominant palette through registered regions",
    "counter_rotation_alignment": "counter-rotate alternating sectors into exact alignment",
    "radial_wave": "propagate one delayed displacement wave from center to perimeter",
    "symmetry_order_transition": "transition symmetry order only at a gated emphasis event",
    "anchor_orbit": "orbit persistent anchors without changing radial registration",
    "aperture_revelation": "reveal a nested motif through the central aperture",
}

SPLICE_FINALS = {
    "scale_equivalent": "end on a scale-equivalent registered state with matched motion continuity",
    "center_shape_match": "end on the declared matching center motif",
    "palette_bridge": "end on the declared bridge palette",
    "symmetry_phase_match": "end at the declared symmetry-compatible phase",
    "motion_vector_match": "end with the declared motion vector and velocity",
    "material_anchor_match": "end with persistent material anchors registered",
    "exact_loop_return": "return exactly to the opening topology, phase, palette, and velocity",
}

CRITICAL_NEGATIVES = [
    "center drift", "accidental asymmetry", "boiling textures", "uncontrolled petal multiplication",
    "lateral camera drift", "random rotation", "boundary tearing", "anchor disappearance",
    "terminal freeze", "black tail",
]


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def canonical_motion_manifest(system: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic deep copy with a stable top-level key order."""
    order = ("topology", "layers", "transform", "color", "audio_binding", "splice", "qa")
    return {key: deepcopy(system[key]) for key in order if key in system}


def compile_motion_system(system: dict[str, Any]) -> dict[str, Any]:
    topology = system.get("topology", {})
    transform = system.get("transform", {})
    locks: list[str] = []
    if topology.get("center_lock"):
        locks.append("visual center")
    if topology.get("symmetry_order"):
        names = {8: "eightfold", 12: "twelvefold", 16: "sixteenfold"}
        order = topology["symmetry_order"]
        locks.append(f"{names.get(order, str(order) + '-fold')} radial symmetry")
    if topology.get("radial_registration") == "strict":
        locks.append("strict radial registration")
    locks.extend(f"persistent anchor {anchor}" for anchor in topology.get("persistent_anchors", []))

    actions: list[str] = []
    primary = transform.get("primary")
    if primary:
        action = OPERATOR_PHRASES[primary]
        direction = transform.get("direction")
        if direction and direction != "stationary":
            action += " " + direction.replace("_", " ")
        actions.append(action)
    actions.extend(OPERATOR_PHRASES[layer["operator"]] for layer in system.get("layers", []))
    color = system.get("color", {})
    if color.get("mode") == "chromatic_migration":
        actions.append(OPERATOR_PHRASES["chromatic_migration"])

    splice = system.get("splice", {})
    strategy = splice.get("strategy")
    return {
        "locks": _dedupe(locks),
        "actions": _dedupe(actions)[:5],
        "event": system.get("audio_binding", {}).get("downbeat_action", ""),
        "final_state": SPLICE_FINALS.get(strategy, ""),
        "negative": list(CRITICAL_NEGATIVES),
        "manifest": canonical_motion_manifest(system),
    }


def compare_splice(
    exit_state: dict[str, Any],
    entry_state: dict[str, Any],
    tolerances: dict[str, float] | None = None,
) -> dict[str, Any]:
    tolerances = {"center": 0.01, "phase_degrees": 0.5, "scale": 0.01, "scale_velocity": 0.01, **(tolerances or {})}
    ordered = (
        "topology_family", "symmetry_order", "center", "phase_degrees", "scale",
        "scale_velocity", "palette", "center_motif", "persistent_anchors", "motion_vector",
    )
    checks: list[dict[str, Any]] = []
    for field in ordered:
        expected, actual = exit_state.get(field), entry_state.get(field)
        check: dict[str, Any] = {"field": field, "expected": expected, "actual": actual}
        if field == "center" and expected is not None and actual is not None:
            delta = round(max(abs(float(a) - float(b)) for a, b in zip(expected, actual)), 6)
            tolerance = tolerances[field]
            check.update(delta=delta, tolerance=tolerance, valid=delta <= tolerance)
        elif field == "phase_degrees" and expected is not None and actual is not None:
            raw = abs(float(expected) - float(actual)) % 360
            delta = min(raw, 360 - raw)
            tolerance = tolerances[field]
            check.update(delta=delta, tolerance=tolerance, valid=delta <= tolerance)
        elif field in {"scale", "scale_velocity"} and expected is not None and actual is not None:
            delta = round(abs(float(expected) - float(actual)), 6)
            tolerance = tolerances[field]
            check.update(delta=delta, tolerance=tolerance, valid=delta <= tolerance)
        else:
            check["valid"] = expected == actual
        checks.append(check)
    return {
        "valid": all(check["valid"] for check in checks),
        "strategy": exit_state.get("strategy") or entry_state.get("strategy"),
        "checks": checks,
    }


def validate_motion_system(system: dict[str, Any]) -> list[str]:
    """Return deterministic cross-field validation errors."""
    errors: list[str] = []
    topology = system.get("topology", {})
    if topology.get("radial_registration") == "strict" and topology.get("center_lock") is not True:
        errors.append("motion_system.topology.center_lock: required when radial_registration is strict")

    identifiers = [layer.get("id") for layer in system.get("layers", [])]
    if len(identifiers) != len(set(identifiers)):
        errors.append("motion_system.layers: layer ids must be unique")

    splice = system.get("splice", {})
    qa = system.get("qa", {})
    if splice.get("strategy") == "exact_loop_return" and qa.get("require_first_last_comparison") is not True:
        errors.append("motion_system.qa.require_first_last_comparison: required for exact_loop_return")

    audio = system.get("audio_binding", {})
    if audio.get("timing_source") == "measured_analysis" and not audio.get("analysis_artifact"):
        errors.append("motion_system.audio_binding.analysis_artifact: required for measured_analysis")
    return errors
