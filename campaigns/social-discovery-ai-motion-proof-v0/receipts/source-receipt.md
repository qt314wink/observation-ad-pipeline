# Source receipt — SDG AI Motion Proof v0

## Authority and scope

- Campaign root: `campaigns/social-discovery-ai-motion-proof-v0/`
- Repository: `qt314wink/observation-ad-pipeline`
- Base: `main@36e1775d7c42fa34963ea44fdd5a200e884ccffe`
- Requested branch: `campaign/social-discovery-ai-motion-proof-v0`
- Source brief: user-supplied Social Discovery Group AI Motion Designer (Freelance) opportunity in the Connection Nucleus Observation conversation.
- Application status: speculative application/portfolio proof.
- Commission status: no commissioned Social Discovery Group work.

The opportunity brief is bounded input, not independent verification of an employer listing. It supports role-scope observations only. It does not supply a client product, brand assets, approved copy, permitted claims, compensation, a paid-trial agreement, or campaign performance baseline.

## Repository evidence

The package uses the existing OBSAD campaign contract, token dictionary, provider declarations, platform derivation, and manifest hash conventions. No generic schema, compiler, provider semantic, existing campaign, Motion Program IR file, or PR #4 implementation is modified by this envelope.

## Planned proof chain

`ROLE SIGNAL → OBSERVATIONS → INFERENCES → CONNECTION NUCLEUS CONTRACT → THREE CONTROLLED HOOKS → PLANNED OUTPUTS → VALIDATION`

The three hooks are recorded as hypotheses. No provider has been executed, no source frame has been supplied, and no generated candidate, selected take, rejected take, assembly, QA result, or performance result exists yet.

## Validation receipt

The exact commands for this handoff are:

```text
python -m obsad.cli campaign-validate campaigns/social-discovery-ai-motion-proof-v0
pytest -q tests/test_campaign.py
git diff --check
git status --short --branch
git log -1 --oneline
```

Recorded after execution:

- Campaign validation: `valid`
- Campaign regression tests: `10 passed` (`python -m pytest -q tests/test_campaign.py`)
- Whitespace check: `passed` (`git diff --check`)
- Envelope commit SHA: `fd278a6383c30a01ad2087e788313ab7db0e45ea`
- Draft PR: `#5` — https://github.com/qt314wink/observation-ad-pipeline/pull/5
- Vercel preview state: `Ready` / GitHub status `success`
- Vercel preview URL: https://observation-ad-pipeline-git-campaign-social-3a39ab-melodicbloom.vercel.app
- Preview access: the URL responds with the Vercel login page because deployment protection is enabled; the deployment itself is ready.

The content commit remains limited to this seven-file envelope. The receipt update is confined to this approved receipt path and does not alter generic architecture or campaign semantics.
