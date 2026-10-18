---
name: audio-reactive-motion-lab
description: Compile user-provided or synthetic audio into validated, bounded visual-control packets; run auditable one-factor tests and prepare portable adapters for Motion Program, WebGL, Hydra, or VJ tools. Use when an audiovisual reference needs to become an executable, reproducible reactive visual experiment.
---
# Audio-Reactive Motion Lab

## Invocation
Use when asked to analyze audio-reactive visual references, implement sound-to-motion controls, reproduce audiovisual dynamics, or hand off a tested control program. Read this file and [control contract](../../integrations/audio-reactive/control-packet.schema.json) before any integration change. Read [experiment notes](../../docs/audio-reactive-ozora-2025.md) for authority and verification boundaries.

## Authority rules
1. **Observed:** Quote concrete published source facts with URLs and retrieval dates.
2. **Inferred:** Mark hypothesized sound/visual relationships as unverified.
3. **Authored:** Declare proposed mappings and calibration parameters; do not attribute them to original artists.
4. **Verified:** Record exact command output, artifact hash/commit SHA and device/browser results. Never mark an unrun test as passing.
5. **Rights:** Do not scrape/download concert footage or embed recordings in a repository. Use user-authorized local audio or synthetic signals.

## Execution plan
1. Record source identity, version and objective. Prefer a 15–30-second user-owned clip or the built-in synthetic fixture to start.
2. Establish baseline using Node 20+: node --test integrations/audio-reactive/engine.test.mjs
3. Serve with python -m http.server 8000, visit http://localhost:8000/integrations/audio-reactive/, click **Synthetic demo**. Confirm visible motion, capture count and packet export.
4. Load a local audio file, click **Play file**. Observe RMS/novelty and smoothness. Flux is spectral novelty, not a robust beat tracker.
5. Change **one control at a time**. Keep source, browser, device, resolution, start point, and other sliders fixed.
6. Export a JSON packet trace and validate shape against [the JSON schema](../../integrations/audio-reactive/control-packet.schema.json). Preserve code SHA, input-file hash (locally if authorized), config, source/permission, browser/device, and measured FPS in a separate run receipt.
7. Evaluate mapping quality: correct transients; no random spikes in silence; bounded hue/pulse; smooth release; no geometry discontinuity; pause/resume; phone portrait; reduced-motion behavior.
8. Only then build an adapter. Map energy to bounded camera/breath; fold to radial-local distortion; shimmer to lighting/material; hue to palette shift; density to particle emission; pulse to local emphasis. Any Motion Program adapter must honor region/topology locks and existing semantic authority. Never silently add global spin from kick energy.
9. Change documents, algorithm and tests together. Keep exports provider-neutral. Prefer a reviewable PR over an unreviewed merge.

## Failure handling
- Audio cannot start: request explicit play gesture and check supported local format. No autoplay workaround.
- FFT bins changed: clear previous-spectrum state, do not compare inconsistent FFT vectors.
- Silence causes movement: distinguish deliberate idle animation from audio-driven channels.
- Full-scale signals: lower sensitivity or introduce explicit, logged per-source normalization; never silently change limits.
- Motion stutters: measure FPS for the same input on the target device; cap pixels and particles first.
- Invalid packet: fail closed; never forward invalid controls to a model or renderer.
- CI failure: stop PR merge and repair in-scope. Unavailable scene evidence must remain UNKNOWN.

## Definition of Done
- Deterministic unit tests and schema contract committed.
- Browser experiment runnable without extra dependencies and with no auto-upload.
- Source/evidence distinctions and copyright boundary clear.
- One-factor calibration matrix and observations documented.
- Actual CI state captured, PR diff reviewed, user given commands/links.
- Renderer-bridge status explicit: present browser renderer versus future adapters.

## Related
- [Experiment README](../../integrations/audio-reactive/README.md)
- [Research and architecture](../../docs/audio-reactive-ozora-2025.md)
- [Motion Program IR](../../docs/MOTION_PROGRAM.md)
