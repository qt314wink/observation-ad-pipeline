from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import fastjsonschema
import yaml

SECTION_ORDER = (
    "subject", "intent", "camera", "motion", "light", "environment",
    "proof", "timing", "typography_placeholder", "negative_constraints",
)
PROVIDERS = {"openai", "xai", "comfyui", "wan"}


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def validate_campaign(directory: Path, schema_path: Path) -> list[str]:
    errors: list[str] = []
    contract = load(directory / "creative-contract.json")
    schema = load(schema_path)
    try:
        fastjsonschema.compile(schema)(contract)
    except fastjsonschema.JsonSchemaException as exc:
        return [exc.message]

    weights = contract["qa_requirements"]["weights"]
    if sum(weights.values()) != 100:
        errors.append("qa_requirements.weights must total 100")
    unknown_blockers = set(contract["qa_requirements"]["blocking_dimensions"]) - set(weights)
    if unknown_blockers:
        errors.append(f"qa_requirements.blocking_dimensions are not weighted: {sorted(unknown_blockers)}")

    observations = load(directory / "observations/evidence.yaml")
    observation_ids = {item["id"] for item in observations.get("observations", [])}
    for inference in observations.get("creative_inferences", []):
        if not set(inference.get("evidence", [])) <= observation_ids:
            errors.append(f"{inference.get('id')}: inference cites an unknown observation")

    tokens = load(directory / "tokens.json")
    if set(contract["color_tokens"]) != set(tokens["colors"]):
        errors.append("contract color_tokens and token dictionary colors differ")
    if set(contract["material_tokens"]) != set(tokens["materials"]):
        errors.append("contract material_tokens and token dictionary materials differ")

    declared_providers = set(contract["provider_targets"])
    if not declared_providers <= PROVIDERS:
        errors.append(f"unsupported provider targets: {sorted(declared_providers - PROVIDERS)}")

    parents = {target["id"]: target["derives_from"] for target in contract["platform_targets"]}
    for target_id in parents:
        current = target_id
        seen: set[str] = set()
        while current != "campaign_contract":
            if current in seen:
                errors.append(f"{target_id}: cyclic platform derivation")
                break
            seen.add(current)
            parent = parents.get(current)
            if parent is None:
                errors.append(f"{target_id}: derives_from target does not exist")
                break
            current = parent

    manifest = load(directory / "outputs/final-asset-manifest.json")
    if manifest.get("contract_sha256") != sha256(contract):
        errors.append("final asset manifest contract_sha256 does not match creative-contract.json")
    return errors


def compile_provider(
    directory: Path,
    provider: str,
    *,
    model: str | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; expected one of {sorted(PROVIDERS)}")
    contract = load(directory / "creative-contract.json")
    if provider not in contract["provider_targets"]:
        raise ValueError(f"Provider {provider!r} is not declared by this campaign")
    semantic = load(directory / "prompts/semantic.yaml")
    adapter = load(directory / f"prompts/providers/{provider}.yaml")

    task = None
    if task_id:
        tasks = load(directory / "tasks/keyframes.yaml")["keyframes"]
        task = next((item for item in tasks if item["id"] == task_id), None)
        if task is None:
            raise ValueError(f"Unknown keyframe task {task_id!r}")

    sections: list[dict[str, str]] = []
    for key in SECTION_ORDER:
        values = list(semantic[key])
        if task and key == "subject":
            values = [task["subject_override"]]
        elif task and key == "motion":
            values = [task["motion_verb"], *values]
        elif task and key == "camera":
            values = [f"camera phase: {task['camera_phase']}", *values]
        if key == "negative_constraints":
            values = contract["negative_constraints"] + contract["healthcare_claim_constraints"] + values
        rendered = adapter["joiner"].join(str(value).strip() for value in values if str(value).strip())
        sections.append({"name": key.upper(), "text": rendered})

    model_env = contract["provider_targets"][provider]["model_env"]
    resolved_model = model or os.getenv(model_env) or f"${{{model_env}}}"
    positive = adapter["joiner"].join(
        section["text"] for section in sections if section["name"] != "NEGATIVE_CONSTRAINTS"
    )
    negative = next(section["text"] for section in sections if section["name"] == "NEGATIVE_CONSTRAINTS")
    payload = {
        "campaign_id": contract["campaign_id"],
        "contract_sha256": sha256(contract),
        "provider": provider,
        "model": resolved_model,
        "mode": contract["provider_targets"][provider]["mode"],
        "sections": sections,
        "positive": positive,
        "negative": negative,
        "provider_directives": adapter["directives"],
    }
    if task:
        payload["task"] = {
            key: task.get(key)
            for key in ("id", "name", "subject_override", "motion_verb", "camera_phase", "seed", "lineage")
        }
        payload["seed"] = task["seed"]
    payload["compiled_sha256"] = sha256(payload)
    return payload
