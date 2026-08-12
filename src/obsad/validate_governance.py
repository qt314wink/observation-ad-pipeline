from __future__ import annotations

import json
from pathlib import Path

import fastjsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROVENANCE_SCHEMA = ROOT / "schemas" / "prompt-family-provenance.schema.json"
PROVENANCE_DIR = ROOT / "config" / "prompt-family-provenance"
WAN_MANIFEST = ROOT / "integrations" / "wan" / "manifest.yaml"

REQUIRED_WAN_EXCLUSIONS = {
    "model-weights",
    "private-inputs",
    "generated-media",
    "credentials",
    "tunnel-urls",
}


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping")
    return data


def validate_prompt_family_provenance() -> list[str]:
    schema = json.loads(PROVENANCE_SCHEMA.read_text(encoding="utf-8"))
    validate = fastjsonschema.compile(schema)
    errors: list[str] = []

    if not PROVENANCE_DIR.exists():
        return [f"missing provenance directory: {PROVENANCE_DIR}"]

    fixtures = sorted(PROVENANCE_DIR.glob("*.yaml"))
    if not fixtures:
        return [f"no provenance fixtures found in {PROVENANCE_DIR}"]

    for path in fixtures:
        try:
            data = _load_yaml(path)
            validate(data)
        except Exception as exc:  # validation boundary intentionally reports all failures
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def validate_wan_manifest() -> list[str]:
    errors: list[str] = []
    data = _load_yaml(WAN_MANIFEST)

    if data.get("engine") != "wan":
        errors.append("integrations/wan/manifest.yaml: engine must be 'wan'")
    if data.get("transport") != "comfyui":
        errors.append("integrations/wan/manifest.yaml: transport must be 'comfyui'")

    excluded = set(data.get("exclude") or [])
    missing = sorted(REQUIRED_WAN_EXCLUSIONS - excluded)
    if missing:
        errors.append(
            "integrations/wan/manifest.yaml: missing required exclusions: "
            + ", ".join(missing)
        )
    return errors


def run() -> int:
    errors = [*validate_prompt_family_provenance(), *validate_wan_manifest()]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("governance validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
