/**
 * Audio Reactive Control Plane v0.1
 * Dependency-free, portable signal-to-control compiler. No browser globals.
 * Important: spectral flux is a transient heuristic, NOT beat or BPM detection.
 */
export const CONTRACT_VERSION = "audio-control.v0.1";
export const CONTROL_KEYS = Object.freeze(["energy", "fold", "shimmer", "hue", "density", "pulse"]);
export const DEFAULT_CONFIG = Object.freeze({
  sensitivity: 14, attackSeconds: 0.08, releaseSeconds: 0.40,
  visualIntensity: 0.80, sectors: 12
});

const clamp = (n, low = 0, high = 1) => Math.min(high, Math.max(low, Number.isFinite(n) ? n : 0));
const EMPTY = () => Object.fromEntries(CONTROL_KEYS.map(k => [k, 0]));
const safeMagnitude = db => Number.isFinite(db) ? Math.pow(10, Math.max(-120, Math.min(0, db)) / 20) : 0;

/**
 * FFT magnitudes are supplied by WebAudio getFloatFrequencyData (dB).
 * bins[i] spans i * sampleRate/(2*bins.length) Hz. Time-domain samples are [-1, 1].
 * Previous magnitudes must be from the preceding frame with the same FFT size.
 */
export function analyzeFrame(samples, binsDb, sampleRate, previousMagnitudes = null) {
  if (!samples?.length || !binsDb?.length || !Number.isFinite(sampleRate) || sampleRate <= 0) {
    throw new TypeError("Nonempty waveform, spectrum and positive sample rate required");
  }
  if (previousMagnitudes && previousMagnitudes.length !== binsDb.length) {
    throw new TypeError("FFT size changed; reset previous magnitudes");
  }
  let squared = 0;
  for (const s of samples) squared += clamp(s, -1, 1) ** 2;
  const rms = Math.sqrt(squared / samples.length);
  const magnitudes = new Float32Array(binsDb.length);
  const bands = { low: [0, 0], mid: [0, 0], high: [0, 0] };
  const hzPerBin = sampleRate / (2 * binsDb.length);
  let weightedHz = 0, totalMag = 0, diff = 0, previousTotal = 0;
  for (let i = 0; i < binsDb.length; i++) {
    const hz = i * hzPerBin, mag = safeMagnitude(binsDb[i]);
    magnitudes[i] = mag;
    if (hz >= 30 && hz < 180) { bands.low[0] += mag * mag; bands.low[1]++; }
    else if (hz >= 180 && hz < 2000) { bands.mid[0] += mag * mag; bands.mid[1]++; }
    else if (hz >= 2000 && hz < 10000) { bands.high[0] += mag * mag; bands.high[1]++; }
    if (hz > 0) { weightedHz += hz * mag; totalMag += mag; }
    if (previousMagnitudes) {
      const prior = Math.max(0, previousMagnitudes[i] || 0);
      diff += Math.max(0, mag - prior);
      previousTotal += prior;
    }
  }
  const energy = key => Math.sqrt(bands[key][0] / Math.max(1, bands[key][1]));
  // Normalize positive spectral novelty against previous spectrum; ignore low-level noise.
  // Float32Array rounding can otherwise produce positive novelty on an unchanged spectrum.
  const relativeNovelty = previousMagnitudes && rms > 0.003 && previousTotal > 0.00001
    ? diff / previousTotal : 0;
  const flux = relativeNovelty > 1e-6 ? clamp(relativeNovelty) : 0;
  return {
    features: {
      rms: clamp(rms), low: clamp(energy("low")), mid: clamp(energy("mid")),
      high: clamp(energy("high")), centroid: clamp(weightedHz / Math.max(1e-8, totalMag) / 10000),
      flux
    },
    magnitudes
  };
}

/** Distinct from analysis: authored mappings may change without redefining features. */
export function mapFeatures(features, config = DEFAULT_CONFIG) {
  const gain = clamp(config.sensitivity ?? 14, 0, 40);
  const strength = clamp(config.visualIntensity ?? 0.8);
  const f = Object.fromEntries(["rms", "low", "mid", "high", "centroid", "flux"]
    .map(k => [k, clamp(features?.[k])]));
  return {
    energy: clamp(f.rms * gain * strength),
    fold: clamp(f.low * gain * strength),
    shimmer: clamp(f.high * gain * strength),
    hue: clamp(f.centroid * 1.3 * strength),
    density: clamp(f.mid * gain * strength),
    pulse: clamp(f.flux * 1.8 * strength)
  };
}

/** Attack / release exponential smoothing; time constants are in seconds, not frames. */
export function smoothControls(target, previous = EMPTY(), dt = 1 / 60, config = DEFAULT_CONFIG) {
  const attack = clamp(config.attackSeconds ?? 0.08, 0.005, 10);
  const release = clamp(config.releaseSeconds ?? 0.4, 0.005, 10);
  const elapsed = clamp(dt, 0, 0.25);
  const out = {};
  for (const key of CONTROL_KEYS) {
    const start = clamp(previous[key]), end = clamp(target[key]);
    const tau = end > start ? attack : release;
    const alpha = 1 - Math.exp(-elapsed / tau);
    out[key] = clamp(start + (end - start) * alpha);
  }
  return out;
}

/** Rejects unknown channels, NaN, impossible ranges and unsupported revisions. */
export function validatePacket(packet) {
  if (!packet || packet.version !== CONTRACT_VERSION || !Number.isFinite(packet.time_s) || packet.time_s < 0) {
    return { valid: false, error: "Invalid version or timestamp" };
  }
  if (!packet.controls || Object.keys(packet.controls).sort().join(",") !== [...CONTROL_KEYS].sort().join(",")) {
    return { valid: false, error: "Unknown or missing control channels" };
  }
  for (const k of CONTROL_KEYS) {
    const v = packet.controls[k];
    if (typeof v !== "number" || !Number.isFinite(v) || v < 0 || v > 1) {
      return { valid: false, error: "Unbounded channel: " + k };
    }
  }
  return { valid: true };
}
export function makePacket(timeSeconds, controls) {
  const packet = { version: CONTRACT_VERSION, time_s: timeSeconds, controls: { ...controls } };
  const status = validatePacket(packet);
  if (!status.valid) throw new TypeError(status.error);
  return packet;
}
export function silenceControls() { return EMPTY(); }
