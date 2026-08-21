# Motion Program IR v0.1

Motion Program is the provider-neutral control surface between evidence/structure analysis and renderer-specific execution.

It exists to stop descriptive motion language from collapsing into unbounded global effects. A program names the source topology, regions, preservation locks, materials, local motion channels, choreography, lighting behavior, camera limits, loop state, failure classes, and calibration experiments before any provider prompt is assembled.

## Contract

`schemas/motion-program.schema.json` defines the machine-readable surface. `src/obsad/motion_program.py` validates cross-field invariants, compiles deterministic provider payloads, and creates one-factor experiment variants.

Compiler order:

`SUBJECT → STRUCTURE → PRESERVATION → MOTION → MATERIALS → LIGHTING → CAMERA → TIMING → NEGATIVE`

The prompt is a compiled view, not the parameter store. Numeric controls remain available in `controls`; Wan/ComfyUI payloads are explicitly marked `requires_provider_workflow_binding` until a concrete installed workflow maps them to nodes.

## Semantic authority

Motion Program consumes, but does not own, the meaning of the generative motion vocabulary. `config/motion-program-semantics-authority.yaml` pins the current provisional Motion Oracle authority to an immutable Melodyfire commit and states which fields are upstream-owned versus local OBSAD authority.

Motion Oracle owns topology/grammar identifiers, material-response meanings, modifier/easing profiles, and the failure taxonomy. OBSAD owns the Motion Program contract, evidence/preservation records, deterministic compilation, calibration programs, and experiment receipts. The authority pin must be advanced and revalidated after the upstream Motion Oracle PR merges; provider behavior is never allowed to silently redefine the semantic layer.

## Motion grammar

The first grammar set is intentionally topology-based rather than aesthetic:

- `radial.counterphase`
- `radial.hinged_aperture`
- `lattice.excavation`
- `relief.stratified`
- `directional.procession`
- `network.propagation`
- `cellular.diffusion`
- `architecture.depth`
- `portrait.anchor`
- `material.macro`

A mandala does not imply spinning. A portrait does not imply facial motion. Material shimmer does not imply recoloring the whole frame.

## Calibration

`examples/motion-programs/radial-relief-calibration.yaml` is a deliberately information-rich test plate contract. Its base-image prompt separates four radial zones and several materials so locality, topology drift, material spill, loop error and texture boiling can be judged independently.

The included experiments use one-factor sweeps for fold strength, sector phase offset, contained distortion strength and mineral-light incidence angle. Run the same reference, model, seed and execution settings while changing only the declared parameter.

## Validation

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_motion_*.py' -v
```

The tests assert deterministic compilation, target locality, loop closure, explicit global-spin prohibition, graph-control retention, one-factor experiment isolation, and an immutable cross-repo semantic-authority boundary.

## Boundary with existing OBSAD work

This layer is additive to the current `master-contract` and task compiler. It does not replace campaign contracts or the governed motion-evidence fixture under review in PRs #1/#2. When those branches reconcile, campaign/keyframe tasks may reference a Motion Program by ID/hash instead of duplicating choreography prose.

Observed motion remains evidence. Designed motion remains an authored program. Provider workflow bindings remain execution configuration.
