# Motion Reference Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a governed, human-directable motion-reference analysis path that preserves observations, material/movement quality, mannerism, interpretation, director controls, and downstream experiment gates without weakening the existing mandala contract.

**Architecture:** Keep PR #1's four-source mandala validator intact. Add a parallel generic reference schema/validator plus one fully traceable *Magical AI Books* specimen. Derive a static review payload from canonical YAML and expose it through the existing read-only review surface; candidate primitives and Wan/Comfy experiments stay blocked until explicit approval.

**Tech Stack:** Python 3.10+, fastjsonschema, PyYAML, pytest, static HTML/CSS/JavaScript, GitHub Actions, Vercel static output.

**Spec:** `docs/superpowers/specs/2026-08-24-motion-reference-intelligence-design.md`

## Global Constraints

- Base is `qt314wink/observation-ad-pipeline` PR #1 head `485b0e80864b99fe1601082d074801ad17de4fb9`.
- Existing `validate_motion_fixture()` semantics for the four mandala sources remain intact.
- No technical media measurement may be invented from a YouTube summary.
- Higgsfield output is `model-derived-observation` and `imported-unverified` until human verification.
- Human-provided vocabulary is stored as `director-provided`, reference-level evidence until mapped to specific scenes.
- `true-origami-verified` is forbidden without verified structural evidence.
- Git/YAML is canonical; the browser workbench is read-only and derived.
- Motion Oracle promotion and Wan/Comfy execution remain blocked in this slice.
- No merge or production promotion.

---

### Task 1: RED contract tests and CI coverage

**Files:**
- Modify: `tests/test_motion_analysis.py`
- Modify: `tests/test_review_ui.py`
- Modify: `.github/workflows/governance-validation.yml`

**Interfaces:**
- Consumes: existing `obsad.validate_motion` module and static review conventions.
- Produces: failing behavioral expectations for `validate_motion_reference`, canonical review-data digest, corpus index, and preserved mandala behavior.

- [ ] **Step 1: Add a failing generic-validator test without causing import collection errors**

Append a test that uses `getattr(validate_motion, "validate_motion_reference", None)`, asserts it is callable, then validates `fixtures/motion-references/magical-ai-books.yaml` and expects no errors. This initially fails on the callable assertion.

- [ ] **Step 2: Add failing invariant tests**

Add tests requiring the new validator to reject:

- inference references to missing observation IDs
- `true-origami-verified` without human-verified structural evidence
- movement events missing `manner`
- unmeasured sources claiming `durationSeconds`
- candidate primitive `approved` without an approval record
- executable experiment gate while candidate status is not approved

Use temporary YAML fixtures assembled from a small valid base record so failures are assertions on returned validator errors, not exceptions.

- [ ] **Step 3: Add failing review-UI tests**

Require `review/data/index.json`, `review/data/magical-ai-books.json`, generic headings (`Movement quality`, `Director controls`, `What we think`, `What remains uncertain`), and preservation of the existing mandala dataset.

- [ ] **Step 4: Extend workflow path filters and focused pytest command**

Include:

- `fixtures/motion-references/**`
- `schemas/motion-reference-analysis.schema.json`
- `schemas/motion-primitive-candidate.schema.json`
- `config/motion-analysis-profiles/**`
- `motion-primitives/**`
- `experiments/wan/**`
- `src/obsad/motion_reference.py`

Run the existing tests plus `tests/test_motion_analysis.py` and `tests/test_review_ui.py`; do not add a second workflow.

- [ ] **Step 5: Open a draft stacked PR and verify RED**

Base the PR on `governance/prompt-provenance-workflow`. Confirm the governance workflow fails for the expected missing generic implementation/workbench contract, not for unrelated baseline failures.

---

### Task 2: Generic schema and validator

**Files:**
- Create: `schemas/motion-reference-analysis.schema.json`
- Create: `schemas/motion-primitive-candidate.schema.json`
- Create: `src/obsad/motion_reference.py`
- Modify: `tests/test_motion_analysis.py`

**Interfaces:**
- Produces: `load_reference(path: Path) -> dict[str, Any]`, `validate_motion_reference(path: Path, root: Path) -> list[str]`, `canonical_sha256(value: Any) -> str`, `build_review_payload(data: dict[str, Any]) -> dict[str, Any]`.

- [ ] **Step 1: Run Task 1 tests and preserve RED evidence**

Expected failure: generic validator callable assertion and workbench-data assertions fail.

- [ ] **Step 2: Implement JSON Schema 2020-12 core shape**

Require top-level:

`schemaVersion`, `referenceId`, `source`, `analysisRuns`, `directorVocabulary`, `scenes`, `observations`, `interpretations`, `directorControls`, `candidatePrimitives`, `experimentGate`.

Observation requires `id`, `scope`, `category`, `statement`, `provenance`, `confidence`, `verificationStatus`.

Movement event requires `id`, `action`, `materialBehavior`, `movementQuality`, `manner`, `provenance`.

`manner` requires `coordination`, `cadence`, `transitionCharacter`, `phaseSequence`, `directorPhrase`.

- [ ] **Step 3: Implement cross-record validation**

`validate_motion_reference()` must:

- schema-validate with fastjsonschema
- enforce unique observation/event/inference/control/candidate IDs
- reject unknown evidence refs
- reject unknown scene refs
- reject measured fields (`sha256`, `bytes`, `durationSeconds`, `width`, `height`, `fps`, `codec`) when `source.mediaMeasurementStatus != measured`
- reject `true-origami-verified` unless at least one cited structural observation is `human-verified`
- reject approved primitives without `approval.approvedBy`, `approval.approvedAt`, and evidence refs
- reject `experimentGate.status == executable` unless all referenced candidate primitives are approved

Return stable human-readable error strings; never throw for ordinary validation failures.

- [ ] **Step 4: Implement deterministic review payload**

`build_review_payload()` returns a compact JSON-safe structure with `canonicalDigest`, reference summary, scenes, movement events, interpretations, director controls, candidate status, and blockers. Digest uses sorted canonical JSON of the YAML-loaded data.

- [ ] **Step 5: Run focused tests**

`pytest -q tests/test_motion_analysis.py`

Expected: original mandala tests and new generic validator tests pass.

---

### Task 3: Magical AI Books governed specimen

**Files:**
- Create: `config/motion-analysis-profiles/representation-boundary.yaml`
- Create: `fixtures/motion-references/magical-ai-books.yaml`
- Create: `motion-primitives/candidates/representation-boundary-breach.yaml`
- Modify: `tests/test_motion_analysis.py`

**Interfaces:**
- Consumes: generic schema/validator.
- Produces: first non-mandala corpus record and blocked candidate primitive.

- [ ] **Step 1: Add failing completeness tests**

Require the fixture to contain exactly ten imported Higgsfield scenes (`S01`–`S10`), all director vocabulary terms from the approved session, at least one movement event with a complete manner record, and the five initial interpretations from the spec.

- [ ] **Step 2: Add source/provenance block**

Record:

- reference ID `video:reference:kelly-boesch:magical-ai-books`
- YouTube video ID `kvsjRbUgzNI`
- canonical YouTube URL
- creator `Kelly Boesch AI Art`
- title `Magical AI Books`
- rights posture `reference-analysis-only`
- media measurement status `unmeasured`
- Higgsfield analysis ID `1f45a6f6-3795-4502-834f-732e53730173`
- analysis coverage `10 scenes returned, approximately 0:00–1:57`

Do not store an authoritative duration, codec, dimensions, FPS, bytes, or media hash.

- [ ] **Step 3: Structure all ten scenes**

Transcribe the existing Higgsfield summaries into scene records preserving visual, audio, camera, light/color, actors/objects, and interaction/context. Mark their provenance `model-derived-observation` and status `imported-unverified`.

- [ ] **Step 4: Preserve the human director vocabulary without over-assigning it**

Store exactly:

`rigid`, `staggered`, `stiff`, `shuffling`, `tessellating`, `bending`, `wrapping`, `folding`, `contorting`, `linking`, `creasing`

with source `human director working session 2026-08-24`, scope `reference`, and a verification task to map each term to specific scenes/events.

- [ ] **Step 5: Add movement events only where the existing evidence supports the event**

Examples may include book opening, owl emergence/wing motion, wave crossing, deer stepping, gear rotation/rise, planetary rotation, page fanning/flower growth, book float, city rise/rain, and book closure. Do not invent crease topology or panel sequencing. For the owl, where mannerism detail is not measured, use unknown values plus an explicit director hypothesis rather than presenting the detailed staggered-panel example as fact.

- [ ] **Step 6: Add interpretations and falsifiers**

Create candidate interpretations:

- `INF.REPRESENTATION_BOUNDARY_BREACH`
- `INF.DIEGETIC_WITNESS_INTERACTION`
- `INF.SOURCE_PLANE_PERSISTENCE`
- `INF.LOCALIZED_DEPTH_ESCALATION`
- `INF.PHYSICAL_CONSEQUENCE`

Each cites observations, has confidence, usefulness, and a falsifier.

- [ ] **Step 7: Add candidate primitive file**

Status `candidate`; evidence points into the fixture; states are `latent`, `activated`, `dimensionalized`, `boundary-crossing`, `consequential`, `expanded`, `resolved`; approval absent; Motion Oracle destination documented but blocked.

- [ ] **Step 8: Run focused tests**

`pytest -q tests/test_motion_analysis.py`

---

### Task 4: Human director controls and CLI

**Files:**
- Modify: `fixtures/motion-references/magical-ai-books.yaml`
- Modify: `src/obsad/cli.py`
- Modify: `tests/test_motion_analysis.py`

**Interfaces:**
- Consumes: `validate_motion_reference`, `build_review_payload`.
- Produces CLI commands `motion-reference-validate` and `motion-reference-render`.

- [ ] **Step 1: Write failing CLI tests or direct Click runner tests using the existing project testing convention**

Require:

`obsad motion-reference-validate fixtures/motion-references/magical-ai-books.yaml`

returns `valid`, and

`obsad motion-reference-render <fixture> --out <json>`

writes deterministic JSON with canonical digest.

- [ ] **Step 2: Add director controls**

At minimum:

`source_plane_persistence`, `breach_amount`, `panel_rigidity`, `fold_localization`, `stagger_amount`, `cascade_direction`, `catch_lock_strength`, `secondary_lag`, `asymmetry`, `settling_amount`, `witness_interaction`, `camera_reaction`, `environment_spill`.

Every control has a plain-language question, allowed values/range, `whatYouWillSee`, `tooLowLooksLike`, `tooHighLooksLike`, evidence refs, confidence, and basis (`observation-backed`, `inference-backed`, `exploratory`).

- [ ] **Step 3: Add CLI commands as thin adapters**

Import from `obsad.motion_reference`; do not duplicate validation logic in `cli.py`.

- [ ] **Step 4: Verify deterministic render**

Render twice and assert byte-identical JSON output.

---

### Task 5: Read-only Motion Reference Workbench

**Files:**
- Create: `review/data/index.json`
- Create: `review/data/magical-ai-books.json`
- Modify: `review/index.html`
- Modify: `review/app.js`
- Modify: `review/styles.css`
- Modify: `tests/test_review_ui.py`

**Interfaces:**
- Consumes: deterministic review payload from Task 4 and existing `mandala-reel-set.json`.
- Produces: static portfolio/review surface; no mutations.

- [ ] **Step 1: Read accessibility/testing visualization skills before implementation**

Use semantic landmarks, keyboard navigation, visible focus, text status, reduced-motion safety, and no color-only meaning.

- [ ] **Step 2: Write failing structure tests**

Require dataset navigation, scene navigation, evidence badges with text, movement-quality/manner sections, director controls, hypotheses/falsifiers, blocked experiment status, and canonical digest display.

- [ ] **Step 3: Build corpus selector**

`index.json` declares `mandala-reel-set` and `magical-ai-books`. Query parameter `?dataset=` may select a corpus; invalid values fall back safely.

- [ ] **Step 4: Build the fast-read hierarchy**

Top of page:

- title / source / provenance status
- one-sentence point
- proof chain
- key blocker

Then:

- scenes
- movement events with `action → mechanism → quality → manner`
- director vocabulary needing verification
- interpretations with evidence and falsifiers
- director controls with predicted visual effects
- candidate primitive / experiment gate

- [ ] **Step 5: Keep mandala behavior available**

The first corpus must remain inspectable. Do not falsely add analysis that PR #1 intentionally blocks.

- [ ] **Step 6: Run UI tests and static integrity checks**

`pytest -q tests/test_review_ui.py`

---

### Task 6: Wan/Comfy benchmark contract, documentation, and whole-branch verification

**Files:**
- Create: `experiments/wan/representation-boundary-breach.yaml`
- Create: `docs/motion/references/magical-ai-books.md`
- Modify: `README.md` only if a short Motion Reference Workbench entry can be added without colliding with active branch context.
- Modify: `.github/workflows/governance-validation.yml` if final paths differ from Task 1.

**Interfaces:**
- Consumes: candidate primitive and director controls.
- Produces: blocked but executable-in-principle benchmark contract and human case-study explanation.

- [ ] **Step 1: Write failing experiment-gate test**

An experiment marked executable while the primitive is candidate must fail; the committed manifest must validate as blocked/planned.

- [ ] **Step 2: Add three controlled benchmark variants**

`relief_only`, `partial_breach`, `full_breach_contact`.

Each declares controlled constants, varied mechanism, evaluation metrics, required receipts, and provider-neutral intent. Wan/Comfy are execution targets, not semantic authorities.

- [ ] **Step 3: Write the human case-study note**

Explain in plain English:

- what the reference initially looked like
- what the first analysis captured
- what it missed about movement mannerism
- why “origami-like” is not the same as verified origami
- how the repo now separates evidence, motion quality, manner, hypothesis, and controls
- what a future experiment would prove
- why this is useful commercially and as a portfolio proof

- [ ] **Step 4: Run full verification**

Required fresh evidence:

- `pytest -q tests/test_governance_validation.py tests/test_motion_analysis.py tests/test_review_ui.py`
- `python -m obsad.validate_governance`
- `python -m compileall src tests`
- schema/fixture validation through the CLI
- deterministic review render twice with byte comparison
- GitHub Actions workflow on the draft PR

- [ ] **Step 5: Review diff against the spec**

Check every required field and every explicit non-goal. Confirm no fabricated timing, origami structure, media measurement, approval, generation result, or Motion Oracle canonization appears.

- [ ] **Step 6: Leave the PR draft**

Report exact head SHA, CI status, files changed, known evidence gaps, and the smallest next experiment. Do not merge.
