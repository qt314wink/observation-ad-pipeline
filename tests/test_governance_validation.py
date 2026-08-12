from __future__ import annotations

import copy

import fastjsonschema

from obsad.validate_governance import REQUIRED_WAN_EXCLUSIONS


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
