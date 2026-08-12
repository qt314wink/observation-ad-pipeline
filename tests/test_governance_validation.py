from __future__ import annotations

import copy
from pathlib import Path

import fastjsonschema

from obsad.validate_governance import REQUIRED_WAN_EXCLUSIONS, _validate_authority_semantics


def test_prompt_provenance_schema_rejects_missing_forbidden_mutations():
    schema = {
        "type": "object",
        "required": [
            "canonicalSource",
            "derivationType",
            "sourceVersion",
            "allowedLocalOverrides",
            "forbiddenLocalMutations",
        ],
        "properties": {
            "canonicalSource": {"type": "object"},
            "derivationType": {"type": "string"},
            "sourceVersion": {"type": "string"},
            "allowedLocalOverrides": {"type": "array"},
            "forbiddenLocalMutations": {"type": "array", "minItems": 1},
        },
    }
    validate = fastjsonschema.compile(schema)
    invalid = {
        "canonicalSource": {},
        "derivationType": "bounded-adaptation",
        "sourceVersion": "unresolved",
        "allowedLocalOverrides": [],
    }

    try:
        validate(invalid)
    except fastjsonschema.JsonSchemaException:
        return
    raise AssertionError("missing forbiddenLocalMutations must fail validation")


def test_provisional_authority_requires_immutable_git_ref():
    data = {
        "canonicalSource": {
            "project": "LithoMemphis",
            "locator": "github:qt314wink/nextjs-boilerplate/main/docs/lithomemphis-v2-plan.md",
            "authorityStatus": "provisional",
        },
        "sourceVersion": "main",
        "sourceHash": "unresolved",
    }
    errors = _validate_authority_semantics(Path("config/prompt-family-provenance/example.yaml"), data)
    assert any("immutable locator" in error for error in errors)
    assert any("git:<40-char-sha>" in error for error in errors)


def test_unresolved_authority_cannot_look_resolved():
    data = {
        "canonicalSource": {
            "project": "NACRE//OS",
            "locator": "github:some/repo@abcdef",
            "authorityStatus": "unresolved",
        },
        "sourceVersion": "git:1234567890123456789012345678901234567890",
        "sourceHash": "unresolved",
    }
    errors = _validate_authority_semantics(Path("config/prompt-family-provenance/example.yaml"), data)
    assert any("unresolved-canonical-repository" in error for error in errors)
    assert any("sourceVersion unresolved" in error for error in errors)


def test_canonical_authority_requires_resolved_hash():
    data = {
        "canonicalSource": {
            "project": "Example",
            "locator": "github:owner/repo@1234567890123456789012345678901234567890/path",
            "authorityStatus": "canonical",
        },
        "sourceVersion": "git:1234567890123456789012345678901234567890",
        "sourceHash": "unresolved",
    }
    errors = _validate_authority_semantics(Path("config/prompt-family-provenance/example.yaml"), data)
    assert any("requires a resolved sourceHash" in error for error in errors)


def test_wan_required_exclusions_are_security_and_privacy_boundaries():
    expected = {
        "model-weights",
        "private-inputs",
        "generated-media",
        "credentials",
        "tunnel-urls",
    }
    assert REQUIRED_WAN_EXCLUSIONS == expected


def test_required_exclusion_removal_is_detectable():
    exclusions = copy.copy(REQUIRED_WAN_EXCLUSIONS)
    exclusions.remove("credentials")
    assert REQUIRED_WAN_EXCLUSIONS - exclusions == {"credentials"}
