# Codex Handoff — Calcium / NOURISH THE SIGNAL Execution Evidence v1

## Repository and branch

- Repository: `qt314wink/observation-ad-pipeline`
- Base: current `main`
- Working branch: `campaign/calcium-nourish-the-signal-execution-v1`
- Base state includes merged PR #2 (Calcium governed campaign package) and merged PR #5 (second governed campaign specimen).
- Do not merge. Stop at a reviewable branch/PR state.

## Why this branch exists

The Calcium campaign architecture is already implemented on `main`. The remaining gap is execution evidence.

Current canonical evidence:
- `campaigns/calcium-nourish-the-signal/creative-contract.json` exists and validates.
- K01–K08 keyframes and M01–M08 motion isolates are declared.
- Wan/ComfyUI workflow template and patches exist.
- QA weights and blocking dimensions exist.
- `generation-ledger.yaml` contains no generation attempts.
- final asset manifest still marks the master as planned and channel derivatives as blocked.

Therefore this branch MUST NOT rebuild the campaign architecture. Its mission is to move the governed package from PLANNED to EVIDENCED through the smallest defensible execution slice.

## Goal

Produce a traceable first execution proof for **NOURISH THE SIGNAL**:

`contract -> compiled prompt -> anchor keyframes -> selected/rejected receipts -> one motion isolate -> QA -> lightweight portfolio evidence`

Primary success state:
1. baseline and campaign tests pass;
2. current provider docs are re-verified;
3. 4 anchor keyframes are compiled deterministically;
4. if an authorized runtime is available, at least one anchor generation is executed and receipted;
5. only after two adjacent keyframes are selected, one motion isolate is attempted;
6. no final 15-second master is claimed until isolate QA passes;
7. all generated/selected/rejected states are represented truthfully.

## Critical current provider decision

OpenAI's Sora 2 Videos API is currently documented as deprecated and scheduled to shut down on **2026-09-24**. Do not invest in a new OpenAI video execution adapter on this branch.

IF the official OpenAI docs still show that shutdown when work starts:
- keep OpenAI as image/keyframe-only for this campaign;
- use current GPT Image generation only for still/keyframe experiments;
- use xAI and/or ComfyUI/Wan for motion;
- update stale campaign wording only if necessary, refresh the contract hash/manifest, and keep the change campaign-scoped unless a generic defect is proven.

IF OpenAI has published a replacement supported video API before execution:
- document the replacement source and capability;
- do not adopt it without a bounded compatibility patch + tests.

## Environment

### Tier A — Codex development/verification environment

Preferred:
- Linux / Ubuntu
- Python 3.12 (matches campaign CI)
- git
- curl
- jq
- ffmpeg
- Python virtual environment

No GPU is required for contract work, compilation, deterministic tests, receipts, or dry runs.

Run:
`bash scripts/bootstrap-calcium-execution.sh`

### Tier B — generation runtime

Preferred order:
1. existing authenticated remote ComfyUI GPU endpoint via `COMFY_URL`;
2. xAI API if `XAI_API_KEY` is explicitly available;
3. OpenAI image generation if `OPENAI_API_KEY` is explicitly available.

Do not copy secrets into files, prompts, logs, commits, issue text, or PR text.

Do not download large model weights into the Codex environment by default.

IF `COMFY_URL` is set:
- run `obsad doctor --url "$COMFY_URL"`;
- inspect installed-node/workflow compatibility before execution;
- use the existing `/prompt` workflow path.

IF no generation runtime is available:
- complete compile/determinism/runtime-capability evidence;
- produce exact execution commands and stop with `BLOCKED_RUNTIME_AUTHORITY`;
- do not fabricate candidates.

## First execution slice

Do not start with all eight keyframes.

Compile and inspect these four anchors first:

- K01 — microscopic signal
- K04 — biology/human transition
- K07 — hand/connection
- K08 — negative-space final hold

These cover the hardest visual state transitions with the fewest calls.

For each anchor:
- compile provider payload;
- preserve contract SHA;
- preserve seed where provider supports seed control;
- record actual model identifier;
- record prompt/output hashes where possible;
- store candidate status;
- create rejection reason for failures;
- never represent a planned task as a generated candidate.

After anchor review:

IF K01/K04/K07/K08 do not share a coherent visual family:
- STOP motion generation;
- revise only the smallest prompt/token/reference delta;
- keep rejected evidence.

IF they do:
- generate the missing intermediate keyframes required for one adjacent transition;
- select exactly one M01–M08 isolate for first motion execution.

Recommended first isolate:
- M01 if K01 and K02 are coherent, because it has the lowest human/anatomy risk.
- Otherwise M07 only after K07/K08 human anatomy/identity consistency passes.

Do not attempt M04 biology-to-human first unless reference control is strong enough to prevent morphing/anatomy drift.

## Build order

### FL-0 — Repository orientation
Read before edits:
- `README.md`
- `ARCHITECTURE.md`
- `campaigns/calcium-nourish-the-signal/**`
- `src/obsad/campaign.py`
- `src/obsad/cli.py`
- `tests/test_campaign.py`
- `.github/workflows/campaign-validation.yml`
- `integrations/wan/**`

Record current HEAD.

### FL-1 — Baseline proof
Run:
- `python -m obsad.cli campaign-validate campaigns/calcium-nourish-the-signal`
- `pytest -q tests/test_campaign.py`
- `PYTHONPATH=src python -m unittest discover -s tests -v`
- `git diff --check`

STOP if baseline fails. Diagnose before campaign edits.

### FL-2 — External capability re-verification
Verify official sources listed in `campaigns/calcium-nourish-the-signal/references/source-registry-2026-09-20.md`.

Do not trust repository model names when official model identifiers have changed.

Record verification date + source URL in a receipt.

### FL-3 — Deterministic compile proof
Compile K01/K04/K07/K08 twice for every declared provider.

For identical input and unresolved environment model placeholders, normalized compiled payloads must be byte-identical and hashes equal.

Write generated compile artifacts under an ignored local evidence directory unless the repo has an existing lightweight committed convention.

### FL-4 — Runtime probe
Probe:
- ComfyUI `/system_stats` if `COMFY_URL` exists;
- presence only of API keys, never values;
- ffmpeg;
- model/workflow compatibility where available.

Generate a capability receipt.

### FL-5 — Anchor execution
Only if runtime authority exists.

Budget guard:
- first pass max 4 anchor tasks;
- max 2 candidates per anchor per provider unless an explicit human override exists;
- prefer low/medium image quality during exploration;
- no speculative large-batch generation.

### FL-6 — Human selection gate
Do not self-promote a candidate to final merely because generation succeeded.

Create candidate receipts with:
- selected/rejected/pending-human-review;
- rationale;
- contract dimensions assessed;
- blocking failures.

If human review is unavailable, use `pending_human_review` and stop progression.

### FL-7 — First motion isolate
Only after start/end frames pass selection gate.

Execute one isolate.
Validate:
- causality;
- continuity;
- anatomy;
- no random morph;
- no generated typography;
- duration;
- resolution;
- black-tail/file integrity.

### FL-8 — Portfolio evidence
Update the case-study summary only with facts supported by receipts.
Allowed evidence:
- contract;
- prompts;
- provider/model;
- selected/rejected candidates;
- hashes;
- QA;
- real outputs.

Do not invent CTR, engagement, client approval, commissioned status, or healthcare outcomes.

### FL-9 — Reuse review
Only after real execution evidence exists, revisit deferred abstractions in `reuse-candidate-report.md`.

Promote a generic abstraction only if the second campaign specimen plus Calcium execution demonstrates it is truly generic.

## Files allowed to change

Preferred campaign scope:
- `campaigns/calcium-nourish-the-signal/**`
- focused campaign tests
- this handoff/bootstrap documentation

Generic files may change only if a real execution exposes a generic defect:
- `src/obsad/campaign.py`
- `src/obsad/cli.py`
- `schemas/campaign-contract.schema.json`
- focused CI/test files

Any generic change requires:
- failing test first or reproducible defect;
- minimal patch;
- full regression suite.

## Files/areas not to disturb

- other campaign creative contracts
- PR #4 branch semantics
- unrelated governance files
- existing Motion Program authority
- repository-wide restructuring

## Subagent operating contract

Use subagents to parallelize READ/ANALYZE work. Serialize writes to shared files.

### Subagent A — repo/evidence auditor
Task:
- inventory current Calcium campaign;
- report exact planned/completed/blocked states;
- identify stale assumptions.
No writes except a bounded report if coordinator requests one.

### Subagent B — provider capability verifier
Task:
- verify official OpenAI, xAI, ComfyUI, Wan sources;
- return current model/API/runtime constraints;
- flag deprecations and model-name drift.
No provider implementation changes.

### Subagent C — compile/determinism verifier
Task:
- compile K01/K04/K07/K08 twice per provider;
- compare normalized bytes/hashes;
- report mismatches.
May add focused tests only after coordinator approval.

### Subagent D — runtime/workflow auditor
Task:
- inspect `wan-staged-api.json`, patches, ComfyUI node/runtime availability;
- identify missing nodes/models without downloading weights;
- produce exact install requirements.
Do not install models unless runtime + storage + license are explicitly authorized.

### Subagent E — QA/receipt designer
Task:
- map candidate outputs to existing QA weights/rejection taxonomy;
- ensure healthcare_safety and technical_integrity remain blocking;
- prepare receipt templates.
Do not score nonexistent outputs.

### Coordinator rules
- integrate findings;
- prevent two subagents from writing the same file concurrently;
- stop agents that broaden scope;
- prefer evidence-producing changes over architecture;
- reject any claim unsupported by a receipt.

## If/then rules

IF baseline tests fail -> stop campaign execution and repair only the regression.

IF provider docs contradict repo model names -> update configuration/reference notes before execution; do not silently substitute a model.

IF OpenAI Sora shutdown remains scheduled -> no new OpenAI video integration.

IF credentials are absent -> compile/dry-run only; return exact commands for user-run execution.

IF ComfyUI is reachable but required nodes/models are absent -> write a capability gap report; do not auto-download weights.

IF a candidate violates healthcare safety -> hard reject regardless of aggregate QA score.

IF anatomy/identity drifts between anchor frames -> do not proceed to motion.

IF a motion isolate contains uncontrolled morphing/black tail/wrong dimensions -> reject and preserve receipt.

IF a change appears generic -> prove it with tests and a second campaign before moving it out of the Calcium namespace.

IF a generated binary is large -> keep it out of Git unless repository storage policy explicitly supports it; commit hashes/manifests/lightweight previews instead.

## Definition of done

Return a completion report with:
1. branch and HEAD SHA;
2. baseline test results;
3. provider docs re-verified + dates;
4. runtime capabilities detected;
5. compiled anchor artifacts + hashes;
6. generations attempted;
7. selected/rejected/pending-human-review candidates;
8. first isolate outcome, if authorized;
9. QA receipts;
10. files changed;
11. generic defects found;
12. blockers;
13. exact next human decision/action;
14. whether branch is safe to open as a draft PR.

Do not merge.
