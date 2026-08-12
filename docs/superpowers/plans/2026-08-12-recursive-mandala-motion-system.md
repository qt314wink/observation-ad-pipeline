# Recursive Mandala Motion System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make recursive mandala motion evidence, parameters, prompt compilation, splice validation, and reusable recipes first-class OBSAD capabilities while preserving existing task behavior.

**Architecture:** Add the optional `motion_system` contract to the existing task schema, then isolate normalization, semantic validation, prompt phrases, deterministic manifests, and splice comparison in `src/obsad/motion.py`. The CLI delegates structured motion work to this module and continues using the existing prompt order and five-action budget. Governed fixtures and prompt packs remain declarative YAML.

**Tech Stack:** Python 3.10+, fastjsonschema 2.20–<3, PyYAML 6–<7, Click 8.1–<9, pytest 8.

## Global Constraints

- Existing tasks without `motion_system` must validate and compile identically.
- `symmetry_order` is an integer from 2 through 64.
- Normalized intensity, morph depth, and topology-preservation values range from 0 through 1.
- `phase_offset_beats` ranges from 0 through 16.
- `outgoing_phase_degrees` ranges from -360 through 360.
- `handle_frames` ranges from 0 through 120.
- Strict radial registration requires center lock.
- Exact-loop return requires first/last comparison QA.
- Audio behavior remains declared/editorial unless an analysis artifact is supplied.
- The uploaded video binaries are not committed.
- All observations remain separate from inferences.
- Output ordering must be deterministic.

---

### Task 1: Schema and semantic validation

**Files:**
- Modify: `schemas/task.schema.json`
- Create: `src/obsad/motion.py`
- Create: `tests/test_motion_validation.py`

**Interfaces:**
- Produces: `validate_motion_system(motion_system: dict[str, Any]) -> list[str]`
- Consumes: optional task-level `motion_system`

- [ ] **Step 1: Write failing tests**

Test a valid recursive system and failures for symmetry 1/65, normalized values outside 0–1, duplicate layer IDs, strict registration without center lock, exact-loop strategy without first/last QA, and measured audio bindings without `analysis_artifact`.

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_motion_validation.py -q`  
Expected: import or validation failures because the module/schema does not exist.

- [ ] **Step 3: Extend JSON Schema**

Define `motion_system` with `additionalProperties: false` for its governed subobjects, controlled enums from the approved vocabulary, numeric bounds, required layer fields, splice fields, audio provenance fields, and QA tolerances.

- [ ] **Step 4: Implement cross-field validation**

```python
def validate_motion_system(system: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    topology = system.get("topology", {})
    splice = system.get("splice", {})
    qa = system.get("qa", {})
    if topology.get("radial_registration") == "strict" and topology.get("center_lock") is not True:
        errors.append("motion_system.topology.center_lock: required when radial_registration is strict")
    ids = [layer.get("id") for layer in system.get("layers", [])]
    if len(ids) != len(set(ids)):
        errors.append("motion_system.layers: layer ids must be unique")
    if splice.get("strategy") == "exact_loop_return" and qa.get("require_first_last_comparison") is not True:
        errors.append("motion_system.qa.require_first_last_comparison: required for exact_loop_return")
    audio = system.get("audio_binding", {})
    if audio.get("timing_source") == "measured_analysis" and not audio.get("analysis_artifact"):
        errors.append("motion_system.audio_binding.analysis_artifact: required for measured_analysis")
    return errors
```

- [ ] **Step 5: Wire semantic validation into `validate_task` and `run_task`**

Call `validate_motion_system(task.get("motion_system", {}))` after JSON Schema validation.

- [ ] **Step 6: Verify tests pass and commit**

Run: `pytest tests/test_motion_validation.py -q`  
Expected: PASS.  
Commit: `feat: validate recursive mandala motion contracts`

### Task 2: Deterministic compilation and manifest

**Files:**
- Modify: `src/obsad/motion.py`
- Modify: `src/obsad/cli.py`
- Create: `tests/test_motion_compilation.py`

**Interfaces:**
- Produces: `compile_motion_system(system: dict[str, Any]) -> dict[str, Any]`
- Produces: `canonical_motion_manifest(system: dict[str, Any]) -> dict[str, Any]`
- CLI consumes `locks`, `actions`, `event`, `final_state`, `negative`, and `manifest`.

- [ ] **Step 1: Write failing deterministic-compilation tests**

Assert stable ordering, exact repeated output, maximum five compiled actions after merging, topology locks before motion, controlled phrase mapping, and byte-identical legacy compilation.

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_motion_compilation.py -q`  
Expected: missing compilation functions.

- [ ] **Step 3: Implement canonical normalization**

Deep-copy governed keys in declared order, preserve declared layer order, sort only unordered mapping keys, normalize phase to a numeric value, and return no timestamps or random identifiers.

- [ ] **Step 4: Implement operator phrase mapping**

Map every approved operator to a concise visible action. Examples:

```python
OPERATOR_PHRASES = {
    "recursive_zoom": "perform a center-locked recursive zoom",
    "ring_replacement": "replace concentric rings at gated scale thresholds",
    "sector_substitution": "substitute registered radial sectors sequentially",
    "topology_preserving_morph": "morph motifs while preserving radial topology",
    "radial_wave": "propagate one delayed displacement wave from center to perimeter",
}
```

Derive locks from center lock, symmetry order, registration strictness, persistent anchors, and topology preservation. Derive final-state continuity from the splice strategy. Deduplicate before returning.

- [ ] **Step 5: Merge structured compilation into `compile_prompt`**

Structured locks precede prose locks. Structured actions precede general actions but the combined list remains capped at five. Structured negatives join the existing prohibited/avoid list and remain capped at eighteen. Add `motion_manifest` to the returned compiled object only when `motion_system` exists.

- [ ] **Step 6: Persist manifest during runs**

The existing run manifest keeps the original task, compiled prompt, structured `motion_manifest`, workflow hash, and outputs.

- [ ] **Step 7: Verify and commit**

Run: `pytest tests/test_motion_compilation.py -q`  
Expected: PASS.  
Commit: `feat: compile deterministic mandala motion manifests`

### Task 3: Splice validator

**Files:**
- Modify: `src/obsad/motion.py`
- Modify: `src/obsad/cli.py`
- Create: `tests/test_splice_validation.py`

**Interfaces:**
- Produces: `compare_splice(exit_state: dict[str, Any], entry_state: dict[str, Any], tolerances: dict[str, float] | None = None) -> dict[str, Any]`
- Produces CLI command: `obsad splice-check EXIT_STATE ENTRY_STATE`

- [ ] **Step 1: Write failing tests**

Cover exact pass, center drift failure, phase failure with circular angle distance, scale-velocity mismatch, palette bridge, persistent-anchor mismatch, and deterministic field ordering.

- [ ] **Step 2: Verify failure**

Run: `pytest tests/test_splice_validation.py -q`  
Expected: missing comparison function.

- [ ] **Step 3: Implement comparison**

Return:

```python
{
    "valid": False,
    "strategy": "scale_equivalent",
    "checks": [
        {"field": "center", "valid": False, "expected": [0.5, 0.5], "actual": [0.53, 0.5], "delta": 0.03, "tolerance": 0.01}
    ]
}
```

Use circular phase distance `min(abs(a-b) % 360, 360 - abs(a-b) % 360)`. Preserve a fixed check order.

- [ ] **Step 4: Add CLI command**

Read YAML or JSON state files, print the comparison as JSON, and raise `ClickException` when invalid.

- [ ] **Step 5: Verify and commit**

Run: `pytest tests/test_splice_validation.py -q`  
Expected: PASS.  
Commit: `feat: add evidence-producing splice validation`

### Task 4: Governed evidence fixtures and motion pack

**Files:**
- Create: `fixtures/motion/mandala-videos/manifest.yaml`
- Create: `fixtures/motion/mandala-videos/observations.yaml`
- Create: `prompt-packs/motion/recursive-mandala.yaml`
- Create: `examples/tasks/recursive-mandala-motion.yaml`
- Create: `docs/project-context/MANDALA_MOTION_LANGUAGE.md`
- Create: `tests/test_mandala_fixtures.py`

**Interfaces:**
- Fixtures consume the four externally governed source IDs.
- The example task consumes schema and compiler interfaces from Tasks 1–2.

- [ ] **Step 1: Write failing fixture tests**

Require four unique sources; dimensions, duration, and FPS; observation/inference separation; allowed vocabulary; splice affordances; six prompt recipes; every recipe containing locks, final state, and negatives; and a valid compilable example task.

- [ ] **Step 2: Verify failure**

Run: `pytest tests/test_mandala_fixtures.py -q`  
Expected: missing fixtures.

- [ ] **Step 3: Create source manifest**

Record:

- `10006.mp4`: 16.0 s, 960×960, 24 fps.
- `8586.mp4`: 10.041667 s, 640×1408, 24 fps.
- `8594.mp4`: 10.041667 s, 640×1408, 24 fps.
- `9040.mp4`: 10.041667 s, 640×1408, 24 fps.

Set `binary_committed: false`, `source_status: user_supplied_external`, and `hash_status: pending_governed_ingestion`. Do not invent hashes.

- [ ] **Step 4: Create observations**

Encode the four approved motion families with visible facts, confidence, explicitly separate inferences, derived capabilities, and splice affordances.

- [ ] **Step 5: Create prompt pack**

Add six named recipes: recursive portal descent, delayed radial wave, alternating harmonic alignment, controlled symmetry fracture, botanical–crystalline transmutation, and scale-equivalent infinite loop.

- [ ] **Step 6: Create executable example and documentation**

The example uses manifest-only provider, strict center lock, eightfold symmetry, recursive zoom, radial wave layer, external markers, scale-equivalent splice, and declared QA. Documentation defines every enum and maps song families to editorial controls without unsupported frequency claims.

- [ ] **Step 7: Verify and commit**

Run: `pytest tests/test_mandala_fixtures.py -q`  
Expected: PASS.  
Commit: `docs: add governed mandala motion fixtures and recipes`

### Task 5: Full regression, versioned documentation, and delivery

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `pyproject.toml`
- Create: `tests/test_legacy_compatibility.py`

**Interfaces:**
- Documents all public commands and task fields.
- Locks legacy compiler output as a regression fixture.

- [ ] **Step 1: Add legacy regression test**

Compile `examples/tasks/generate.yaml` and assert the complete prior `positive`, `negative`, and `stats` object remains byte-identical when no structured motion exists.

- [ ] **Step 2: Update documentation and package version**

Document `motion_system`, `motion_manifest`, `splice-check`, evidence fixture status, and external-marker audio semantics. Increment package/version display from 0.2.1 to 0.3.0 because this is an additive public capability.

- [ ] **Step 3: Run complete verification**

Run:

```bash
python -m pip install -e .
pytest -q
obsad validate examples/tasks/recursive-mandala-motion.yaml
obsad compile examples/tasks/recursive-mandala-motion.yaml
obsad validate examples/tasks/generate.yaml
```

Expected: all tests pass; both example tasks validate; structured output contains `motion_manifest`; legacy output does not.

- [ ] **Step 4: Determinism verification**

Compile the recursive example twice and compare SHA-256 hashes of normalized JSON. Expected: identical hashes.

- [ ] **Step 5: Review branch diff and commit**

Confirm no media binaries, generated outputs, credentials, or unrelated changes.  
Commit: `feat: ship recursive mandala motion language`

- [ ] **Step 6: Open a draft PR**

Title: `feat: add recursive mandala motion language`

The PR body records scope, evidence source status, schema/compiler behavior, backward compatibility, validation commands, and the remaining future work: measured audio analysis and review UI.
