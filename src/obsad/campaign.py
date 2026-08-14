from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import fastjsonschema
import yaml

SECTION_ORDER = (
    "subject",
    "intent",
    "camera",
    "motion",
    "light",
    "environment",
    "proof",
    "timing",
    "typography_placeholder",
    "negative_constraints",
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
        errors.append(exc.message)
    if sum(contract["qa_requirements"]["weights"].values()) != 100:
        errors.append("qa_requirements.weights must total 100")
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
    for target in contract["platform_targets"]:
        if target["derives_from"] != "campaign_contract" and not any(
            parent["id"] == target["derives_from"] for parent in contract["platform_targets"]
        ):
            errors.append(f"{target['id']}: derives_from target does not exist")
    return errors


def compile_provider(directory: Path, provider: str, *, model: str | None = None) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}; expected one of {sorted(PROVIDERS)}")
    contract = load(directory / "creative-contract.json")
    semantic = load(directory / "prompts/semantic.yaml")
    adapter = load(directory / f"prompts/providers/{provider}.yaml")
    sections: list[dict[str, str]] = []
    for key in SECTION_ORDER:
        values = semantic[key]
        if key == "negative_constraints":
            values = contract["negative_constraints"] + contract["healthcare_claim_constraints"] + values
        rendered = adapter["joiner"].join(str(value).strip() for value in values if str(value).strip())
        sections.append({"name": key.upper(), "text": rendered})
    model_env = contract["provider_targets"][provider]["model_env"]
    resolved_model = model or os.getenv(model_env) or f"${{{model_env}}}"
    payload = {
        "campaign_id": contract["campaign_id"],
        "contract_sha256": sha256(contract),
        "provider": provider,
        "model": resolved_model,
        "mode": contract["provider_targets"][provider]["mode"],
        "sections": sections,
        "provider_directives": adapter["directives"],
    }
    payload["compiled_sha256"] = sha256(payload)
    return payload
