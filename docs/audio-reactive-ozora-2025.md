# Audiovisual continuity reference → audio control lab v0.1

**Status (2026-10-18):** Implementation and tests authored on a feature branch; browser/device acceptance must be verified by a human with local audio. This is not a transcript- or scene-validated reconstruction of the concert.

## Evidence ledger and rights

| Claim | Class | Basis | Limitation |
|---|---|---|---|
| Unknown Reality performed the opening set at The Dome, O.Z.O.R.A., on July 28, 2025 | Source-reported fact | [Official upload description](https://www.youtube.com/watch?v=3GtpHGZZdUc) | Description, not independent event verification |
| The uploaded set contains 21 listed tracks, starting with Intro and ending with Magic | Source-reported fact | Same published tracklist | Individual transition timestamps not verified |
| The performance could inspire long-form audiovisual continuity | Research hypothesis | Ambient/chill labels and stated complete-set format | No scene-level synchronization observations |
| Low frequency controls local fold, high frequency controls shimmer, novelty controls pulse | **Our authored mapping** | Implementation in engine.mjs | NOT reported methodology of Unknown Reality or Upvisuals |
| Transients correspond to visual scene changes | **Unverified inference** | None at present | Requires human audiovisual coding/timecoded evidence |

**Rights:** The source audio and concert video are not distributed, stored or downloaded by this lab. Use local recordings only with appropriate permission. Cite the artists when using the *reference* and clearly separate our authored visualization from the original.

## Signal / control / renderer authority boundary

1. **Capture**: A user-authorized local audio file plays through HTMLMediaElement → MediaElementAudioSourceNode → AnalyserNode → speakers. Web Audio starts after explicit gesture.
2. **Analysis**: Samples at sample rate S and FFT size N=2048. Bin k frequency approximates k*S/N. Define waveform RMS = sqrt(mean(x_i²)). Convert spectral dB to magnitude 10^(dB/20). Compute RMS magnitude per low/mid/high band; centroid = sum(f_k*m_k)/sum(m_k); novelty = sum(max(0,m_k(t)-m_k(t-1))) / (sum(m_k(t-1))+epsilon), clipped to [0,1]. No BPM estimation.
3. **Semantic mapping**: Configured gain and artistic mapping translate measured values into six targets: energy, fold, shimmer, hue, density, pulse. Only this stage owns mapping semantics. The output of a channel is finite and in [0,1].
4. **Smoothing**: alpha = 1 - exp(-dt/tau). tau_attack when target rises; tau_release when it falls. Never interpolate based solely on frames; clamp dt after tab-background gaps. Note browser tab throttling still affects real-time timing.
5. **Validation**: makePacket(version,time_s,controls) rejects unexpected keys, nonfinite values or values outside [0,1]. Packets are JSON-serializable; keep raw features conceptually distinct from controls.
6. **Render**: Canvas2D mirrored petal topology; fold alters local geometry, shimmer changes local highlights, hue shifts the palette, density changes point count, pulse changes local center/emphasis, energy modulates translucency. The renderer has independent slow idle drift. It is not a reconstruction of the original VJ setup.
7. **Export**: Up to 3,600 bounded packets in the browser at a 100 ms target sample interval. Captures have source class, model version, config, timestamp and explicit non-inclusion of source media.

Reference: [MDN AnalyserNode](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode); [MDN getFloatFrequencyData](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/getFloatFrequencyData); [MDN smoothingTimeConstant](https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/smoothingTimeConstant). We set WebAudio smoothing to zero and apply explicit time-constant smoothing after feature mapping to make control behavior auditable.

## Portable control channels (all 0..1)

| Channel | Input | V0 renderer effect | Potential adapter (not wired) | Lock |
|---|---|---|---|---|
| energy | waveform RMS | petal opacity | camera micro-breath or material luminance | no large zoom/flash |
| fold | 30–180 Hz band | local petal aperture | radial field displacement | preserve topology, no global spin |
| shimmer | 2–10 kHz band | highlight and interference ring | nacre/specular response | no global recolor |
| hue | spectral centroid / 10 kHz | controlled palette shift | paletteShift uniform | keep semantic palette limits |
| density | 180–2000 Hz band | point count | particle emitter birth rate | hard cap |
| pulse | positive spectral novelty | bounded core radius | transient event envelope | no strobe |

## Why this design, versus alternatives

- **Browser Web Audio + Canvas2D first:** minimal dependencies, phone/desktop testing, immediate local feedback. Does not imply 60 FPS on all devices, and is not suitable for advanced GPU scattering or exact video-frame replay.
- **Semantic controls instead of direct FFT-to-shader:** a small stable interface decouples measured audio from aesthetic choices, allows schema checking and downstream renderer replacement.
- **Static normalization instead of automatic learning:** sensitivity is explicit and comparable across runs; dynamic normalization would make comparisons source-dependent without a recorded calibration state.
- **Frame independent attack/release instead of rolling-frame averaging:** time constants are interpretable and portable across refresh rates.
- **Spectral novelty instead of beat detector:** enough for a bounded prototype. Novelty can respond to noise and timbral changes; do not label it BPM, onset truth, or section transitions.
- **Control export instead of audio import/export APIs:** avoids bundling third-party music and supports tool handoff. Export retention is bounded.

## Deterministic and perceptual test protocol

Hold source, 20-second section, device, browser, viewport, code SHA and all but one slider constant. Record (a) slider tuple (b) actual mean/min fps (c) observed latency to response (d) silence artifacts (e) export packet validity (f) notable failures.

| Test | Baseline | One change | Predicted result | Failure evidence |
|---|---|---|---|---|
| CAL-01 transient | sensitivity 14 | sensitivity 8 → 22 | higher response but still bounded | saturation/flatline |
| CAL-02 motion attack | .08 seconds | .04 → .24 | faster/slower rise only | jumps, perceptual alias |
| CAL-03 motion release | .4 seconds | .15 → .8 | shorter/longer decay only | restless lag |
| CAL-04 symmetry | 12 sectors | 8 → 16 | symmetry changes, signal trace unchanged | topology corruption |
| CAL-05 reduced motion | OS default | enable reduced motion | continuous rotation suppressed | unexpected spin |
| CAL-06 silence | synthetic then stop | zero audio | signal channels decay toward zero | pulse at silence, unless independently authored idle |

**Programmatic checks**: node --test integrations/audio-reactive/engine.test.mjs. Test includes silence, repeat-frame novelty, positive novelty, FFT consistency, pathological gain, asymmetric attack/release, frame-rate invariance, invalid packet rejection and deterministic mapping.

## Integration gates

**G0** reference and permissions; **G1** separate observed / inferred / authored; **G2** fixed channel contract; **G3** synthetic trace; **G4** local licensed audio and measurements; **G5** timecoded audiovisual comparison; **G6** minimal renderer adapter; **G7** repeatable human QA; **G8** archive manifest and future synthesis.

For OBSAD Motion Program: audio control IR sits *upstream* of the existing semantic authority pin described in [MOTION_PROGRAM.md](./MOTION_PROGRAM.md). It cannot override source topology, preservation locks, material response semantics, or provider workflow bindings. A future adapter must translate these channels into named, locally-scoped Motion Program channels, validate cross-field invariants, then compile for the target provider. A claim that a Wan/ComfyUI/Hydra/Resolume bridge is wired requires an executable integration test, not merely a mapping table.

## Risks, ambiguities, and follow-ups

- The uploaded video is a reference to the performance, **not direct evidence** of how audio and visuals are algorithmically coupled; the link alone does not establish the routing, projection, audio analysis or timing.
- End-to-end browser performance, autoplay behavior, mobile layout, and reduced-motion accessibility have not been measured here.
- Fixed FFT bins give coarse low-end resolution (S/N ≈ 23.4 Hz at 48 kHz); bass transients merit better multi-resolution handling later.
- Spectral feature magnitudes are affected by mastering level, sample rate, and analysis window; compare calibrated sources, never assume cross-recording equivalence.
- V0 capture is a rolling sampled control trace, not sample-accurate offline render or immutable source hash.
- **Next milestone:** choose one short locally authorized excerpt, export controls, score the visual against a timecoded human annotation, then build one validated Shader Gallery/WebGL adapter. Leave external VJ integrations as proposals until tested.

## Decision record
2026-10-18 / DEC-AUD-001 — Isolated experimental module in OBSAD because this repository owns evidence-led motion specification, tests, and cross-provider compilation. Shader Gallery consumes a later validated control contract; Motion Oracle remains source of motion semantics; no forced change to ComfyUI execution.
