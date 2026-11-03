import test from "node:test";
import assert from "node:assert/strict";
import {
  CONTRACT_VERSION, analyzeFrame, mapFeatures, smoothControls,
  silenceControls, makePacket, validatePacket, CONTROL_KEYS
} from "./engine.mjs";

const fixture = (value = -42, size = 1024) => new Float32Array(size).fill(value);
const wave = value => new Float32Array(2048).fill(value);

test("silence gives finite zeros and no false onset", () => {
  const out = analyzeFrame(wave(0), fixture(-Infinity), 48000);
  assert.deepEqual(out.features, {rms: 0, low: 0, mid: 0, high: 0, centroid: 0, flux: 0});
  assert.deepEqual(mapFeatures(out.features), silenceControls());
});
test("constant tone never yields spontaneous repeat transient", () => {
  const a = analyzeFrame(wave(.12), fixture(-45), 48000);
  const b = analyzeFrame(wave(.12), fixture(-45), 48000, a.magnitudes);
  assert.equal(b.features.flux, 0);
});
test("spectral increase creates positive bounded flux", () => {
  const a = analyzeFrame(wave(.10), fixture(-55), 48000);
  const b = analyzeFrame(wave(.30), fixture(-22), 48000, a.magnitudes);
  assert.ok(b.features.flux > 0 && b.features.flux <= 1);
});
test("FFT size mismatch fails instead of silently rebinding state", () => {
  assert.throws(() => analyzeFrame(wave(0), fixture(-20), 44100, new Float32Array(300)), /FFT size changed/);
});
test("targets remain bounded under pathological inputs", () => {
  const target = mapFeatures({rms: 1e12,low: Infinity,mid: -5,high: 900,centroid: 20,flux: NaN},
    {sensitivity: 1e9,visualIntensity: 1e9});
  for (const v of Object.values(target)) assert.ok(Number.isFinite(v) && v >= 0 && v <= 1);
});
test("attack rises faster than release falls", () => {
  const target = Object.fromEntries(CONTROL_KEYS.map(k => [k, 1]));
  const up = smoothControls(target, silenceControls(), 1 / 60);
  const down = smoothControls(silenceControls(), target, 1 / 60);
  assert.ok(up.energy > 1 - down.energy);
});
test("exponential envelopes roughly match across frame rates", () => {
  const target = Object.fromEntries(CONTROL_KEYS.map(k => [k, 1]));
  let a = silenceControls(), b = silenceControls();
  for (let i = 0; i < 60; i++) a = smoothControls(target, a, 1 / 60);
  for (let i = 0; i < 30; i++) b = smoothControls(target, b, 1 / 30);
  for (const key of CONTROL_KEYS) assert.ok(Math.abs(a[key] - b[key]) < 1e-8);
});
test("packet rejects unknown values and channels", () => {
  const packet = makePacket(1.5, silenceControls());
  assert.equal(packet.version, CONTRACT_VERSION);
  assert.equal(validatePacket(packet).valid, true);
  assert.equal(validatePacket({...packet, controls:{...packet.controls, x:0}}).valid, false);
  assert.equal(validatePacket({...packet, controls:{...packet.controls, pulse:NaN}}).valid, false);
  assert.equal(validatePacket({...packet, time_s:-1}).valid, false);
});
test("analysis and mapping are deterministic for identical inputs", () => {
  const f = analyzeFrame(wave(.25), fixture(-28), 44100).features;
  assert.deepEqual(mapFeatures(f), mapFeatures(f));
  assert.deepEqual(makePacket(5,smoothControls(mapFeatures(f))),makePacket(5,smoothControls(mapFeatures(f))));
});
