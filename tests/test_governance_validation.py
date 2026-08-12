from __future__ import annotations

import copy

import fastjsonschema

from obsad.validate_governance import (
    REQUIRED_WAN_EXCLUSIONS,
    ROOT,
    _find_approved_change,
    _protected_digest,
    _validate_authority_semantics,
    _validate_downstream_impact,
)


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


def _fixture_path():
    return ROOT / "config" / "prompt-family-provenance" / "example.yaml"


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
    errors = _validate_authority_semantics(_fixture_path(), data)
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
    errors = _validate_authority_semantics(_fixture_path(), data)
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
    errors = _validate_authority_semantics(_fixture_path(), data)
    assert any("requires a resolved sourceHash" in error for error in errors)


def test_protected_digest_is_deterministic_and_field_scoped():
    family = {
        "id": "photo.lithomemphis.v1",
        "name": "Lithomemphis",
        "materials": ["lithograph paper", "marble"],
        "palette": ["black", "warm ivory"],
        "intent": ["local campaign wording"],
    }
    fields = ["name", "materials", "palette"]
    baseline = _protected_digest(family, fields)
    reordered = {
        "intent": ["different local wording"],
        "palette": ["black", "warm ivory"],
        "materials": ["lithograph paper", "marble"],
        "name": "Lithomemphis",
        "id": "photo.lithomemphis.v1",
    }
    assert _protected_digest(reordered, fields) == baseline


def test_protected_digest_changes_when_upstream_semantic_changes():
    family = {
        "name": "Lithomemphis",
        "materials": ["lithograph paper", "marble"],
        "palette": ["black", "warm ivory"],
    }
    fields = ["name", "materials", "palette"]
    baseline = _protected_digest(family, fields)
    drifted = copy.deepcopy(family)
    drifted["palette"].append("electric cyan")
    assert _protected_digest(drifted, fields) != baseline


def test_unprotected_local_override_does_not_change_protected_digest():
    family = {
        "name": "Lithomemphis",
        "materials": ["lithograph paper", "marble"],
        "palette": ["black", "warm ivory"],
        "intent": ["tactile editorial authority"],
    }
    fields = ["name", "materials", "palette"]
    baseline = _protected_digest(family, fields)
    family["intent"] = ["campaign-local conversion framing"]
    assert _protected_digest(family, fields) == baseline


def _approved_change(previous: str, proposed: str, previous_version: str = "v1", proposed_version: str = "v2"):
    return {
        "proposalId": "chg:lithomemphis.palette-v2",
        "familyId": "photo.lithomemphis.v1",
        "status": "approved",
        "reason": "Upstream source explicitly changes the protected palette contract.",
        "evidenceRefs": ["github:example/evidence"],
        "compatibility": "minor-compatible",
        "previousVersion": previous_version,
        "proposedVersion": proposed_version,
        "previousProtectedDigest": previous,
        "proposedProtectedDigest": proposed,
        "changedProtectedFields": ["palette"],
        "downstreamImpacts": ["Observation photo prompt renderer"],
        "approvalRequired": True,
        "approvedBy": "Jennipher",
        "approvedAt": "2026-08-11T22:50:00-04:00",
    }


def test_only_approved_exact_digest_transition_authorizes_change():
    previous = "sha256:" + "1" * 64
    proposed = "sha256:" + "2" * 64
    proposal = _approved_change(previous, proposed)
    match = _find_approved_change(
        "photo.lithomemphis.v1",
        previous,
        proposed,
        ["name", "materials", "palette"],
        [proposal],
    )
    assert match is proposal


def test_proposed_change_does_not_authorize_drift():
    previous = "sha256:" + "1" * 64
    proposed = "sha256:" + "2" * 64
    proposal = _approved_change(previous, proposed)
    proposal["status"] = "proposed"
    assert _find_approved_change(
        "photo.lithomemphis.v1", previous, proposed, ["name", "materials", "palette"], [proposal]
    ) is None


def test_change_requires_version_transition():
    previous = "sha256:" + "1" * 64
    proposed = "sha256:" + "2" * 64
    proposal = _approved_change(previous, proposed, previous_version="v1", proposed_version="v1")
    assert _find_approved_change(
        "photo.lithomemphis.v1", previous, proposed, ["name", "materials", "palette"], [proposal]
    ) is None


def test_changed_fields_must_be_within_protected_contract():
    previous = "sha256:" + "1" * 64
    proposed = "sha256:" + "2" * 64
    proposal = _approved_change(previous, proposed)
    proposal["changedProtectedFields"] = ["intent"]
    assert _find_approved_change(
        "photo.lithomemphis.v1", previous, proposed, ["name", "materials", "palette"], [proposal]
    ) is None


def _impact_declaration(digest: str, classification: str = "must-revalidate", receipt_digest: str | None = None):
    consumer = {
        "id": "obsad.photo-renderer.lithomemphis",
        "kind": "renderer",
        "classification": classification,
        "target": "src/obsad",
    }
    if receipt_digest is not None:
        consumer["receipt"] = {
            "validatedProtectedDigest": receipt_digest,
            "evidenceRef": "tests/test_governance_validation.py",
        }
    return {
        "familyId": "photo.lithomemphis.v1",
        "sourceProtectedDigest": digest,
        "consumers": [consumer],
    }


def test_current_lithomemphis_impact_receipts_are_current():
    digest = "sha256:" + "1" * 64
    declaration = _impact_declaration(digest, receipt_digest=digest)
    assert _validate_downstream_impact("photo.lithomemphis.v1", digest, [declaration]) == []


def test_missing_must_revalidate_receipt_fails():
    digest = "sha256:" + "1" * 64
    declaration = _impact_declaration(digest)
    errors = _validate_downstream_impact("photo.lithomemphis.v1", digest, [declaration])
    assert any("requires revalidation but has no receipt" in error for error in errors)


def test_stale_revalidation_receipt_fails():
    digest = "sha256:" + "1" * 64
    stale = "sha256:" + "2" * 64
    declaration = _impact_declaration(digest, receipt_digest=stale)
    errors = _validate_downstream_impact("photo.lithomemphis.v1", digest, [declaration])
    assert any("stale revalidation receipt" in error for error in errors)


def test_compatible_consumer_does_not_require_receipt():
    digest = "sha256:" + "1" * 64
    declaration = _impact_declaration(digest, classification="compatible")
    assert _validate_downstream_impact("photo.lithomemphis.v1", digest, [declaration]) == []


def test_unrelated_family_does_not_satisfy_impact_declaration():
    digest = "sha256:" + "1" * 64
    declaration = _impact_declaration(digest, receipt_digest=digest)
    declaration["familyId"] = "photo.other.v1"
    errors = _validate_downstream_impact("photo.lithomemphis.v1", digest, [declaration])
    assert any("missing or duplicated" in error for error in errors)


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
