# Recursive Mandala Motion Language — Design Specification

**Date:** 2026-08-12  
**Status:** Approved design; implementation pending written-spec review  
**Branch:** `feature/recursive-mandala-motion-language`  
**Source evidence:** `10006.mp4`, `8586.mp4`, `8594.mp4`, `9040.mp4` supplied by the user  
**Scope decision:** combine the immediately usable vocabulary/prompt/example layer with a first-class schema and compiler expansion.

## 1. Problem

OBSAD currently compiles motion into at most five prose actions, one camera family, one emphasis event, and one final state. That is useful for ordinary image-to-video work but cannot explicitly represent recursive radial animation in which multiple concentric rings, symmetry sectors, materials, colors, and scale levels transform independently while sharing a locked visual center.

The system needs to distinguish what is directly witnessed from inferred technique, encode the witnessed behavior as reusable parameters, compile those parameters into bounded model prompts, and preserve splice continuity across independently generated clips.

## 2. Goals

1. Record evidence-backed behavior for each supplied video without claiming unavailable generator settings.
2. Establish a precise vocabulary for radial topology, symmetry, recursion, phase, ring behavior, color migration, morphing, alignment, waves, frequency response, and splice continuity.
3. Provide actionable motion prompts and governed variations suited to the user's mandala and kaleidoscopic work.
4. Map musical structure to visual control signals without treating a marketing label such as “432 Hz” as evidence of a special physical effect.
5. Extend task validation and compilation so the vocabulary is machine-readable, deterministic, optional, and backward-compatible.
6. Produce fixtures that can later drive a review UI and Vercel specimen.

## 3. Non-goals

- Automatic audio analysis in this patch.
- Claiming exact BPM, key, beat grid, or spectral content without the source audio.
- Shipping the uploaded binaries into Git until storage, licensing, and provenance policy are decided.
- Replacing deterministic post-production for exact frame cuts, platform audio attachment, captions, or CTA timing.
- Adding autonomous publishing or production mutation.

## 4. Evidence model

Each observation must contain:

- `source_id`: stable identifier for the supplied video.
- `time_range`: observed interval.
- `observation`: visible behavior only.
- `mechanism_label`: controlled descriptive term.
- `confidence`: high, medium, or low.
- `inference`: optional interpretation, explicitly separated.
- `derived_capability`: reusable motion operation supported by the observation.
- `splice_affordance`: visible state that can connect to another clip.
- `provenance`: filename, duration, dimensions, frame rate, inspection method, and source status.

Video binaries remain external governed sources in this patch. Fixtures use metadata and cryptographic hashes when computed during implementation; they must not invent hashes.

## 5. Witnessed motion families

### 5.1 Recursive macro-zoom and semantic reconstruction — `10006.mp4`

A centered metallic floral mandala continuously increases in apparent scale. Successive inner structures resolve as previous rings leave the frame. The motif family changes from eightfold floral geometry toward layered nacre and heart-like structures while center registration remains stable.

Reusable capabilities:

- center-locked recursive descent;
- scale-threshold substitution;
- nested motif revelation;
- semantic center transition;
- scale-equivalent loop closure.

### 5.2 Chromatic species-morph — `8586.mp4`

The radial center remains stable while sector contents change among botanical, avian, insectile, lattice, and petal-like forms. Cyan/yellow dominance migrates toward magenta, violet, and gold. Sector registration persists even as motif identity changes.

Reusable capabilities:

- topology-preserving motif substitution;
- palette-state migration;
- sectorwise material/species transformation;
- radial registration under morph;
- sequential or wave-propagated substitution.

### 5.3 Concentric ring replacement — `8594.mp4`

The center and circular organization persist while concentric petal systems change hue, count, width, material, and apparent relief. Later frames resolve toward sharper purple-blue lattice petals.

Reusable capabilities:

- ring-addressable replacement;
- petal-count transition at gated moments;
- concentric convergence;
- material sharpening;
- ringwise phase delay.

### 5.4 Axial botanical expansion with anchor orbs — `9040.mp4`

A vertically mirrored botanical structure expands toward the viewer. Blue glass spheres persist as strong anchors while leaves, droplets, feather forms, and eye-like motifs reorganize. The rainbow center remains an attractor; the final state resolves into an elongated yellow-green floral architecture.

Reusable capabilities:

- axial/radial hybrid topology;
- persistent anchor objects;
- botanical unfolding;
- orbit-to-petal correspondence;
- center-aperture continuity.

## 6. Controlled vocabulary

### Topology

- `radial`
- `concentric`
- `axial_mirror`
- `radial_axial_hybrid`
- `recursive_nested`

### Transform operators

- `recursive_zoom`
- `ring_replacement`
- `sector_substitution`
- `topology_preserving_morph`
- `material_transmutation`
- `chromatic_migration`
- `counter_rotation_alignment`
- `radial_wave`
- `symmetry_order_transition`
- `anchor_orbit`
- `aperture_revelation`

### Temporal modes

- `continuous`
- `beat_gated`
- `bar_gated`
- `phase_delayed`
- `alternating`
- `accumulative_then_resolve`
- `breath_cycle`

### Splice strategies

- `scale_equivalent`
- `center_shape_match`
- `palette_bridge`
- `symmetry_phase_match`
- `motion_vector_match`
- `material_anchor_match`
- `exact_loop_return`

## 7. Machine-readable task extension

Add an optional `motion_system` object to `schemas/task.schema.json`. Existing tasks remain valid.

Proposed fields:

```yaml
motion_system:
  topology:
    family: recursive_nested
    center_lock: true
    symmetry_order: 8
    radial_registration: strict
  layers:
    - id: core
      region: center
      operator: aperture_revelation
    - id: ring-01
      region: ring
      index: 1
      operator: radial_wave
      phase_offset_beats: 0.125
  transform:
    primary: recursive_zoom
    direction: inward
    scale_start: 1.0
    scale_end: 4.0
    morph_depth: 0.65
    topology_preservation: 0.95
  color:
    mode: chromatic_migration
    palette_states: [violet-cyan, emerald-gold]
    interpolation: perceptual
  audio_binding:
    timing_source: external_markers
    downbeat_action: alignment
    transient_action: restrained_pulse
    low_band_action: radial_expansion
    high_band_action: texture_shimmer
  splice:
    strategy: scale_equivalent
    outgoing_phase_degrees: 0
    preserve_velocity: true
    handle_frames: 12
  qa:
    max_center_drift_percent: 1.0
    symmetry_tolerance_degrees: 0.5
    require_first_last_comparison: true
```

Validation constraints:

- `symmetry_order`: integer 2–64.
- normalized intensity/depth/preservation values: 0–1.
- `phase_offset_beats`: number 0–16.
- `outgoing_phase_degrees`: -360–360.
- `handle_frames`: integer 0–120.
- layer IDs unique within a task.
- strict radial registration requires `center_lock: true`.
- exact loop return requires first/last comparison QA.
- no field may imply measured audio data unless a timing source or analysis artifact is declared.

## 8. Compiler behavior

The compiler will:

1. Validate the ordinary task contract.
2. If `motion_system` exists, normalize it into a stable order.
3. Convert structured operators into concise visible actions.
4. Place topology and continuity locks before motion instructions.
5. Compile no more than five primary model-visible actions.
6. Compile exact beat/frame instructions into a deterministic post-production/marker manifest when the target generator cannot guarantee them.
7. Preserve the full structured object in the immutable run manifest even when the model prompt is distilled.
8. Emit warnings for incompatible requests rather than silently discarding them.

Compiled prompt order remains:

`TASK → LOCK → MOTION → CAMERA → EVENT → FINAL → STYLE → NEGATIVE`

The new structured representation informs `LOCK`, `MOTION`, `EVENT`, and `FINAL`; it does not bypass the existing contract.

## 9. Prompt pack

Create `prompt-packs/motion/recursive-mandala.yaml` containing:

- identity and purpose;
- preservation defaults;
- topology defaults;
- named recipes:
  - recursive portal descent;
  - delayed radial wave;
  - alternating harmonic alignment;
  - controlled symmetry fracture and resolution;
  - botanical–crystalline transmutation;
  - scale-equivalent infinite loop;
- critical negatives:
  - center drift;
  - accidental asymmetry;
  - texture boiling;
  - uncontrolled petal multiplication;
  - lateral camera drift;
  - random rotation;
  - boundary tearing;
  - anchor disappearance;
  - terminal freeze or black tail.

## 10. Music-response mapping

The patch treats musical descriptors as control strategies, not unverifiable claims.

- Atmospheric, downtempo, dreamlike: recursive push, slow palette migration, center revelation.
- Wave/pulse/floating: delayed ring expansion, amplitude envelope, traveling phase.
- Ritual/meditative: symmetry convergence, crown emergence, harmonic breathing.
- Glitch/bass/808: quantized sector alternation, controlled fracture, exact realignment.
- Organic/coastal: tidal scale breathing, refraction, current-like counter-rotation.
- Balance/tension-release: complementary ring exchange, expansion/contraction pairs.

A later audio-analysis module may populate BPM, beats, onsets, sections, and band envelopes from actual files. Until then, tasks use external markers or declared editorial timing.

## 11. Seam contract

Every generated segment declares an entry and exit state:

- topology family;
- symmetry order;
- center coordinates;
- phase angle;
- scale and scale velocity;
- dominant palette;
- center motif;
- persistent materials/anchors;
- motion vector;
- handle length.

A splice is valid when required fields match within declared tolerances. Reversal requires an explicit musical or narrative event. Unmatched transitions must be labeled intentional discontinuities.

## 12. Files to change

### Design/evidence layer

- `docs/superpowers/specs/2026-08-12-recursive-mandala-motion-language-design.md`
- `docs/project-context/MANDALA_MOTION_LANGUAGE.md`
- `fixtures/motion/mandala-videos/manifest.yaml`
- `fixtures/motion/mandala-videos/observations.yaml`
- `prompt-packs/motion/recursive-mandala.yaml`
- `examples/tasks/recursive-mandala-motion.yaml`

### Schema/compiler layer

- `schemas/task.schema.json`
- `src/obsad/cli.py` or a new focused compiler module extracted from it
- tests for schema validation, deterministic compilation, legacy compatibility, splice validation, and failure cases
- README/architecture references where necessary

Implementation should extract focused motion compilation/validation units if adding this behavior directly to `cli.py` would make responsibilities less clear.

## 13. QA and acceptance criteria

1. All existing example tasks still validate and compile identically.
2. The recursive mandala example validates.
3. Invalid symmetry, phase, center-lock, and loop combinations fail with specific messages.
4. Two compilations of the same task produce byte-identical structured manifests and prompts.
5. Each of the four source fixtures has observations separated from inferences.
6. Every prompt recipe includes preservation locks, a final state, and critical negatives.
7. Splice validation reports pass/fail plus field-level evidence.
8. Documentation defines every enum used in the example.
9. No uploaded binary is committed without an explicit source-media governance decision.
10. Tests record that music mappings are declared/editorial unless backed by an analysis artifact.

## 14. Future increments

- Audio feature extraction and beat/section manifests.
- Review UI with synchronized source playback, frame evidence, radial overlays, and editable observation records.
- Vercel preview of the first governed motion-analysis specimen.
- Generator-specific adapters for Wan, Kling, Runway, Veo, and ComfyUI workflows.
- Measured performance feedback linking motion choices to retention, replay, saves, click intent, and audience scenario.
- Additional motion families from future supplied videos.

## 15. Decision record

The user approved combining:

1. vocabulary + prompt pack + executable example; and
3. first-class schema/compiler expansion.

The patch is additive and backward-compatible. Source videos act as governed evidence fixtures; their binaries remain external until provenance and storage policy are approved.
