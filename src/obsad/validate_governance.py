from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fastjsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROVENANCE_SCHEMA = ROOT / "schemas" / "prompt-family-provenance.schema.json"
CHANGE_SCHEMA = ROOT / "schemas" / "semantic-change-proposal.schema.json"
PROVENANCE_DIR = ROOT / "config" / "prompt-family-provenance"
CHANGE_DIR = ROOT / "config" / "semantic-change-proposals"
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


def _validate_authority_semantics(path: Path, data: dict) -> list[str]:
    errors: list[str] = []
    source = data.get("canonicalSource") or {}
    status = source.get("authorityStatus")
    locator = source.get("locator")
    version = data.get("sourceVersion")
    source_hash = data.get("sourceHash")
    prefix = str(path.relative_to(ROOT))

    if status == "unresolved":
        if locator != "unresolved-canonical-repository":
            errors.append(f"{prefix}: unresolved authority must use unresolved-canonical-repository locator")
        if version != "unresolved":
            errors.append(f"{prefix}: unresolved authority must keep sourceVersion unresolved")
        if source_hash != "unresolved":
            errors.append(f"{prefix}: unresolved authority must keep sourceHash unresolved")
        return errors

    if status in {"provisional", "canonical"}:
        if not isinstance(locator, str) or "@" not in locator:
            errors.append(f"{prefix}: {status} authority must use an immutable locator containing '@<ref>'")
        if not isinstance(version, str) or not version.startswith("git:") or len(version) != 44:
            errors.append(f"{prefix}: {status} authority must pin sourceVersion as git:<40-char-sha>")

    if status == "canonical" and source_hash == "unresolved":
        errors.append(f"{prefix}: canonical authority requires a resolved sourceHash")

    return errors


def _protected_digest(family: dict, protected_fields: list[str]) -> str:
    projection = {field: family.get(field) for field in protected_fields}
    canonical = json.dumps(
        projection,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _load_change_proposals() -> tuple[list[dict], list[str]]:
    if not CHANGE_DIR.exists():
        return [], []

    schema = json.loads(CHANGE_SCHEMA.read_text(encoding="utf-8"))
    validate = fastjsonschema.compile(schema)
    proposals: list[dict] = []
    errors: list[str] = []
    for path in sorted(CHANGE_DIR.glob("*.yaml")):
        try:
            proposal = _load_yaml(path)
            validate(proposal)
            proposals.append(proposal)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return proposals, errors


def _find_approved_change(
    family_id: str,
    previous_digest: str,
    proposed_digest: str,
    protected_fields: list[str],
    proposals: list[dict],
) -> dict | None:
    for proposal in proposals:
        if proposal.get("status") != "approved":
            continue
        if proposal.get("familyId") != family_id:
            continue
        if proposal.get("previousProtectedDigest") != previous_digest:
            continue
        if proposal.get("proposedProtectedDigest") != proposed_digest:
            continue
        changed = set(proposal.get("changedProtectedFields") or [])
        if not changed or not changed.issubset(set(protected_fields)):
            continue
        if proposal.get("previousVersion") == proposal.get("proposedVersion"):
            continue
        return proposal
    return None


def _validate_family_binding(path: Path, data: dict, proposals: list[dict]) -> list[str]:
    binding = data.get("familyBinding")
    if not binding:
        return []

    prefix = str(path.relative_to(ROOT))
    family_path = ROOT / binding["path"]
    if not family_path.is_file():
        return [f"{prefix}: bound prompt family does not exist: {binding['path']}"]

    family = _load_yaml(family_path)
    if family.get("id") != binding["id"]:
        return [
            f"{prefix}: family id mismatch; provenance binds {binding['id']} "
            f"but {binding['path']} declares {family.get('id')!r}"
        ]

    missing = [field for field in binding["protectedFields"] if field not in family]
    if missing:
        return [
            f"{prefix}: protected fields missing from {binding['path']}: "
            + ", ".join(sorted(missing))
        ]

    actual = _protected_digest(family, binding["protectedFields"])
    expected = binding["protectedDigest"]
    if actual == expected:
        return []

    approved = _find_approved_change(
        binding["id"],
        expected,
        actual,
        binding["protectedFields"],
        proposals,
    )
    if approved:
        return [
            f"{prefix}: approved semantic change {approved['proposalId']} exists for {binding['id']} "
            "but provenance protectedDigest has not been advanced to the approved digest"
        ]

    return [
        f"{prefix}: protected semantic drift detected for {binding['id']}; "
        f"expected {expected}, got {actual}. Create and approve a semantic-change proposal with "
        "reason, evidence, compatibility, version transition, changed fields, and downstream impacts before advancing provenance."
    ]


def validate_prompt_family_provenance() -> list[str]:
    schema = json.loads(PROVENANCE_SCHEMA.read_text(encoding="utf-8"))
    validate = fastjsonschema.compile(schema)
    errors: list[str] = []

    if not PROVENANCE_DIR.exists():
        return [f"missing provenance directory: {PROVENANCE_DIR}"]

    proposals, proposal_errors = _load_change_proposals()
    errors.extend(proposal_errors)

    fixtures = sorted(PROVENANCE_DIR.glob("*.yaml"))
    if not fixtures:
        return [f"no provenance fixtures found in {PROVENANCE_DIR}"]

    for path in fixtures:
        try:
            data = _load_yaml(path)
            validate(data)
            errors.extend(_validate_authority_semantics(path, data))
            errors.extend(_validate_family_binding(path, data, proposals))
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
