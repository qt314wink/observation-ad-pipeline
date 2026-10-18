# Audio-reactive control lab v0.1

An isolated dependency-free browser experiment which measures **audio features** and compiles **bounded control vectors** to drive a mirrored radial Canvas2D instrument. It does not alter the existing OBSAD task compiler or Wan/ComfyUI model bindings.

## Run it exactly

From the repository root:

    node --version
    node --test integrations/audio-reactive/engine.test.mjs
    python -m http.server 8000

Open http://localhost:8000/integrations/audio-reactive/ in a modern browser. Click **Synthetic demo** for a no-audio smoke test. Then choose your own licensed audio file and click **Play file** (user gesture required for Web Audio). Try the sensitivity and attack sliders one at a time, then **Export control JSON**.

To fetch the branch for the experiment:

    git clone https://github.com/qt314wink/observation-ad-pipeline.git
    cd observation-ad-pipeline
    git switch feat/audio-reactive-control-lab-v0

Node 20+ for tests, modern browser with Web Audio for playback, Python 3 for static server; no npm install or API key. Python server is unnecessary if you already use another local static web server. A local server is required for ES-module loading in several browser environments.

## What is measured versus authored

- Measured via Web Audio: waveform RMS, 30–180 Hz energy, 180–2000 Hz energy, 2000–10000 Hz energy, spectral centroid and **positive spectral novelty**.
- Authored: sensitivity, channel assignments, attack/release coefficients, mirrored sector count, optical color palette, geometric pulse.
- Rendered: mirrored petal fields, translucent interference arcs, small highlights and density-mapped points. No claim of matching the actual festival stage production.

    Audio file → AnalyserNode → analyzeFrame → mapFeatures → smoothControls
                                  ↓               ↓                ↓
                            raw features     targets [0,1]    controls [0,1]
                                                                     ↓
                                                   validated packet → renderer
                                                                     ↓
                                                       bounded JSON capture

Feature extraction runs in the animation loop. Control envelopes use elapsed seconds and exponential attack/release smoothing. The JSON capture retains the latest 3,600 packets at roughly 10 Hz (approx. six minutes). All input stays local; the exported control trace contains no audio sample content.

## Contract and preservation

The output schema is [control-packet.schema.json](./control-packet.schema.json); the pure compiler is [engine.mjs](./engine.mjs); the unit tests are [engine.test.mjs](./engine.test.mjs). The semantic channels are energy, fold, shimmer, hue, density and pulse (all finite in [0,1]). Reject unexpected channels or nonfinite values. FFT changes require previous-spectrum reset.

This is a **bounded integration candidate**, not an existing provider binding. For OBSAD Motion Program see [MOTION_PROGRAM.md](../../docs/MOTION_PROGRAM.md): an adapter must preserve locked regions and never redefine Motion Oracle topologies. For additional sources, algorithms, calibrations, observed/inferred/authored distinctions and known gaps see [research notes](../../docs/audio-reactive-ozora-2025.md).

## Browser QA

1. Synthetic demo: moving petals; no audio playback or network uploads.
2. Audio: local playback after explicit click; sane RMS and novelty.
3. Silence: measured features zero, control envelopes decay; note renderer's explicitly authored idle drift.
4. Change one slider only; look for smooth transitions and absence of white flashes.
5. Pause, seek, change file, resume; verify no errors and reset state when source changes.
6. Portrait/mobile; confirm controls reachable and exported packets valid.
7. Record measured FPS in a run receipt. Do not interpret requestAnimationFrame as guaranteed 60 FPS.
8. Test reduced-motion OS preference; continuous rotation is suppressed, with controlled geometric modulation still possible.

## Limitations / next adapters

This v0.1 cannot ingest audio from a third-party YouTube page or automatically synchronize with external festival video. Spectral novelty is **not** BPM, onset labeling, song segmentation or audiovisual causal inference. The preview uses Canvas2D; WebGL2/Hydra/Resolume/Spout and post-production adapters are future tasks. Stable offline replay requires a future timestamp-driven renderer rather than relying on requestAnimationFrame scheduling.
