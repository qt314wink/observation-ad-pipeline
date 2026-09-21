# Motion Reference Intelligence — Design Spec

## Purpose

Turn motion references into reusable, inspectable creative knowledge instead of descriptive prompt fragments.

The system must answer, separately and traceably:

1. **What happened?** — observable scene event.
2. **How was it physically achieved or constrained?** — structural/material mechanism.
3. **What quality did the movement have?** — rigid, bound, staggered, fluid, shuffling, etc.
4. **How was that quality performed?** — sequencing, cadence, hesitation, catch/release, lead/lag, asymmetry, settling, and micro-mannerism.
5. **What do we think that means?** — explicit interpretation/hypothesis, never silently promoted to observation.
6. **What can a human director change?** — plain-language controls with predicted visual consequence and failure modes.
7. **Can the mechanism be reproduced without copying the source surface?** — controlled downstream experiments with receipts.

This slice uses Kelly Boesch AI Art's *Magical AI Books* YouTube reference as the first non-mandala specimen. It does **not** declare the reference to be true origami. It records paper/fold/origami evidence only at the confidence the source supports.

## Stakes

If OBSAD stores only aesthetic prose, it becomes a prompt scrapbook. If it stores only low-level geometry, it becomes hard for an art director to steer. The useful middle is a governed creative-analysis layer that preserves evidence, movement character, uncertainty, and human intent while remaining executable downstream.

The immediate portfolio proof should be understandable in under a minute:

`REFERENCE → SCENES → OBSERVATIONS → HOW IT MOVES → HYPOTHESIS → DIRECTOR CONTROLS → CONTROLLED TEST`

The longer-term product value is a reusable motion-language engine: analyze a compelling movement, recover the hidden rules, expose them as directable controls, then test whether those rules transfer to new subjects, materials, brands, interfaces, and models.

## Current Repo Boundary

PR #1 (`governance/prompt-provenance-workflow` @ `485b0e80864b99fe1601082d074801ad17de4fb9`) remains the first bounded governed-motion proof. Its mandala fixture intentionally requires exactly four sources and exactly eight dimensions. This design does not mutate that contract in place.

This branch adds a second, generic reference-analysis path alongside the mandala path. After two corpus types have proved useful, a later reconciliation may extract a shared v2 core. That migration is explicitly out of scope here.

## External Patterns We Borrow, Not Dependencies We Add

- **CVAT-style temporal annotation:** identity over time, tracks/keyframes, occlusion/z-order, and mutable attributes are useful ideas for separating event timing from object description.
- **FiftyOne-style labels:** typed labels, confidence, instances, and extensible attributes are useful for keeping machine-readable annotations composable.
- **FOLD origami format:** frames, vertices, edges, faces, mountain/valley/boundary assignments, and optional geometry show how to represent fold structure without forcing every record to contain every field.
- **Laban-like movement axes:** bound/free, sudden/sustained, direct/indirect, and light/strong are useful qualitative axes, but OBSAD does not claim formal Laban notation. Material-specific behavior is added separately.

No external package is required for these ideas.

## Evidence Classes

Every claim must declare its provenance class.

- `source-derived`: directly measured or directly inspected from retained media.
- `model-derived-observation`: produced by an analysis tool such as Higgsfield; useful but not yet human-verified.
- `director-provided`: supplied by the human directing the analysis.
- `derived-measurement`: computed from source media by a deterministic tool.
- `interpretation`: a hypothesis about mechanism, meaning, perceptual effect, or reusable principle.

A model-derived observation may become human-verified later, but the original provenance remains in history.

## Reference Record

A motion reference record requires:

- schema version and stable reference ID
- source title, creator, platform, canonical URL, access date
- rights/use posture (`reference-analysis-only` unless otherwise established)
- retained-media state and digest only when a lawful local copy exists
- external analysis runs with provider, analysis ID, status, date, and coverage note
- human/director vocabulary supplied during review
- scenes
- observations
- interpretations
- director controls
- candidate primitives
- downstream experiment gate

Technical media facts such as codec, exact duration, dimensions, FPS, byte count, and SHA-256 must not be inferred from a YouTube summary. They are allowed only when measured from retained media or supplied by an authoritative metadata source with provenance.

## Scene Model

Each scene has:

- stable scene ID
- imported temporal span (`start`, `end`) with provenance and confidence
- imported visual summary and audio summary
- camera description
- light/color description
- environment/context description
- visible actors/objects
- interaction/contact notes
- scene-level observations
- zero or more movement events

The Higgsfield run for this specimen returned ten scenes covering approximately `0:00–1:57`. That is stored as analysis coverage, not as authoritative source duration.

## Observation Model

An observation records:

- `id`
- `scope` (`reference`, `scene`, `event`, `object`, `part`)
- `category`
- `statement`
- `provenance.kind`
- `provenance.sourceRef`
- `confidence`
- `verificationStatus` (`imported-unverified`, `human-verified`, `contested`, `rejected`)
- optional `timeRef`, `sceneRef`, `eventRef`, `objectRef`

Observation text must describe something potentially falsifiable from the source. Words such as “magical,” “convincing,” or “portal” belong in interpretation unless they identify literal source content.

## Movement Event Model — the Core Addition

A movement event captures both mechanics and manner.

### Identity

- event ID
- scene reference
- actor/object
- moving part or region
- source state
- destination state
- temporal span or relative order when known

### Action

Plain verb or verb phrase: `opens`, `rises`, `folds`, `wraps`, `shuffles`, `fans`, `rotates`, `tessellates outward`, `interlocks`, `settles`.

### Structural mechanism

What appears to permit the movement:

- `hinge`
- `crease`
- `bend`
- `curl`
- `wrap`
- `twist`
- `slide`
- `shuffle`
- `stack-separate`
- `interlock-link`
- `tessellate`
- `extrude`
- `inflate`
- `morph`
- `unknown`

Multiple mechanisms may coexist. Mechanism is still observational only when visible evidence supports it; otherwise it is an interpretation.

### Material behavior

- rigidity: `rigid`, `semi-rigid`, `flexible`, `mixed`, `unknown`
- surface stretch: `none-visible`, `limited`, `substantial`, `unknown`
- face planarity: `preserved`, `partly-preserved`, `not-preserved`, `unknown`
- articulation locality: `edge/crease-localized`, `distributed`, `mixed`, `unknown`
- thickness behavior: `constant-looking`, `variable-looking`, `unknown`
- collision/contact: `none-visible`, `contact`, `interpenetration-suspected`, `unknown`

### Movement quality

Broad character axes:

- flow: `bound`, `free`, `mixed`, `unknown`
- time: `sudden`, `sustained`, `mixed`, `unknown`
- space: `direct`, `indirect`, `mixed`, `unknown`
- weight/force impression: `light`, `strong`, `mixed`, `unknown`
- continuity: `continuous`, `segmented`, `stepped`, `pulsed`, `mixed`, `unknown`
- stiffness impression: `soft`, `supple`, `firm`, `stiff`, `rigid`, `mixed`, `unknown`

These are descriptors of visible performance, not claims about actual physical material properties.

### Manner / phrasing — “the how of the how”

This is the differentiating field. It records how the quality unfolds.

- `leadPart`: what initiates
- `followParts`: what follows
- `coordination`: simultaneous / sequential / overlapping / counterphase / leader-follower / cascading
- `cadence`: continuous / staggered / alternating / step-hold-release / pulse-pause / accelerating / decelerating / irregular
- `transitionCharacter`: snap / ease / catch / drag / rebound / overshoot / settle / lock / release
- `phaseSequence`: ordered phases such as `root lift → inner panel release → outer panel lag → brief lock → settle`
- `microMannerisms`: head lag, edge tremor, panel flutter, secondary rocking, asymmetric delay, corrective settle, etc.
- `directorPhrase`: one compact plain-English description of how it performs

The director phrase must remain editable by a human and should be capable of standing on its own in an animation brief.

### Spatial path

- local direction
- path family: linear / arc / hinge-arc / radial / spiral / wrap-around-edge / inward curl / outward fan / orbit / irregular
- origin and destination relationship when visible
- screen-space versus scene-space status when known

### Timing

Store measured numbers only when measured. Until then use relative timing:

- before / after / overlaps
- short lag / medium lag / long lag
- brief hold / sustained hold
- slow / moderate / fast apparent tempo

Later source hydration may replace qualitative timing with frame/time measurements while preserving the earlier annotation provenance.

## Paper / Fold / Origami Evidence

Do not use `origami` as a blanket aesthetic label.

Classification options:

- `paper-textured-3d`
- `paper-constructed`
- `origami-like`
- `fold-constrained`
- `true-origami-verified`
- `unknown`

`true-origami-verified` is blocked unless there is human-verified structural evidence or a fold model supporting it.

Optional structural evidence:

- visible crease lines
- rigid/planar faces
- hinge-like rotation around edges
- mountain/valley direction if confidently visible
- face adjacency persistence
- boundary-edge persistence
- fold propagation sequence
- layering/occlusion order
- self-contact or collision
- unfolding/refolding reversibility

Optional future FOLD-compatible data may record vertices, edges, faces, crease assignments, and frame states. The Magical AI Books specimen does not invent these geometries.

## Representation-Boundary Profile

The first domain profile asks questions specific to a representation becoming spatially consequential:

- source-plane persistence
- activation cue
- dimensionalization
- extrusion/depth emergence
- boundary crossing
- occlusion/contact
- physical consequence
- environment spill
- light-source migration
- witness/human interaction
- camera response
- closure/reversibility

These dimensions are optional modules, not universal motion truth.

## Director Vocabulary Captured From This Session

At reference level, record the human-provided vocabulary exactly as a steering vocabulary pending scene mapping:

`rigid`, `staggered`, `stiff`, `shuffling`, `tessellating`, `bending`, `wrapping`, `folding`, `contorting`, `linking`, `creasing`.

These words are not automatically assigned to a particular scene or object. Each requires evidence mapping during review.

## Interpretation Model

Interpretations are separate records with:

- ID
- label
- statement
- evidence references
- confidence
- status (`candidate`, `supported`, `contested`, `rejected`)
- falsifier / what evidence would weaken it
- usefulness / what downstream decision it changes

Initial hypotheses include:

- `representation-boundary-breach`
- `diegetic-witness-interaction`
- `source-plane-persistence`
- `localized-depth-escalation`
- `physical-consequence-as-believability-proof`

None become Motion Oracle canon from this branch.

## Human Director Controls

Every promoted or candidate mechanism exposes controls in conversational language.

A control requires:

- stable ID
- label
- plain-language question, e.g. “How stiff should the unfolding feel?”
- target record fields
- value type and allowed values/range
- default/locked state
- `whatYouWillSee` — predicted visible change
- `tooLowLooksLike`
- `tooHighLooksLike`
- evidence references
- confidence
- whether the control is observation-backed, inference-backed, or exploratory

Initial controls:

- source-plane persistence
- breach amount
- panel rigidity
- fold/hinge localization
- stagger amount
- cascade direction
- catch/lock strength
- secondary lag
- asymmetry
- settling amount
- witness interaction strength
- camera reaction
- environment spill

The workbench presents these as director questions, not raw JSON first.

## Candidate Primitive

Working primitive: `representation-boundary-breach.v1`.

State hypothesis:

`latent → activated → dimensionalized → boundary-crossing → consequential → expanded → resolved`

Possible reverse/closure path is recorded only where evidence supports it.

The candidate stores required cues, optional cues, anti-patterns, evidence refs, director-control refs, and promotion status. Status remains `candidate` in this slice.

## Downstream Experiment Gate

No model execution is required to complete this slice. A blocked experiment manifest is still useful if it specifies exactly what will be tested once approved.

Three benchmark variants:

1. plane → relief only
2. plane → partial breach
3. plane → full breach + contact consequence

Hold constant where the runtime supports it:

- source/reference frame
- seed
- duration
- FPS
- resolution
- base subject/scene
- negative constraints

Measure/score:

- identity retention
- source-plane retention
- depth legibility
- boundary-crossing legibility
- contact plausibility
- temporal causality
- topology stability
- mannerism fidelity
- artifact rate
- closure stability

The manifest is blocked until the primitive is explicitly approved.

## Human-Facing Review Workbench

The existing read-only review UI becomes a generic **Motion Reference Workbench** on this stacked branch. Git/YAML remains canonical.

The default view should answer in this order:

1. What are we looking at?
2. What did the analyzer actually report?
3. What did the human director add?
4. How does each important part move?
5. What do we think the mechanism is?
6. What can I tune and what will that do?
7. What is still uncertain or blocked?
8. What experiment would prove or disprove the idea?

The mandala fixture remains selectable as the first corpus; Magical AI Books becomes the second.

Accessibility requirements:

- semantic headings and landmark structure
- keyboard-reachable dataset/scene navigation
- no information encoded by color alone
- director controls readable without hover
- status changes exposed through `aria-live`
- reduced-motion-safe UI (the review surface itself does not need decorative animation)

## Validation Rules

The validator must reject:

- duplicate IDs
- observation/inference mixing
- inference references to nonexistent evidence
- director controls that cite nonexistent evidence
- movement events without action, quality, manner, or provenance
- `true-origami-verified` without verified structural evidence
- measured technical fields on unhydrated/unmeasured media
- candidate primitive marked approved without explicit approval record
- experiment manifest marked executable while the primitive remains unapproved
- review payload whose canonical-source digest does not match its YAML source

The original mandala validator and tests must remain passing and unchanged in meaning.

## Portfolio / Commercial Proof

The useful demo is not “AI analyzed a video.” The useful demo is:

> A reference that looked like an aesthetic trick was decomposed into evidence, material behavior, movement mannerisms, editable director controls, and a controlled test plan that can transfer the mechanism to new creative work.

This supports several sellable positions:

- motion-language reconstruction
- AI art direction / motion systems
- reference-to-executable creative tooling
- design-system reconstruction extended into time and material behavior
- governed generative production pipelines

A hiring manager should be able to see judgment, visual sensitivity, systems thinking, data modeling, human-centered tooling, provenance discipline, and executable creative direction in one compact artifact.

## Explicit Non-Goals

- Do not imitate Kelly Boesch's exact scenes, subjects, or style.
- Do not claim true origami without structural proof.
- Do not infer exact frame timing from scene summaries.
- Do not merge PR #1.
- Do not canonize the primitive in Motion Oracle.
- Do not run Wan/Comfy generation as part of this first slice.
- Do not replace the existing mandala fixture.
- Do not turn the review UI into a source of truth.
