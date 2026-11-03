import test from 'node:test';
import assert from 'node:assert/strict';

let now = 0, nextFrame, lastBlob, sourceConnections = 0;
class Element extends EventTarget {
  constructor(id) { super(); this.id=id; this.value=''; this.textContent=''; this.paused=true; this.src=''; this.files=[]; this.currentTime=0; this.readyState=4; this.clientWidth=300; this.clientHeight=200; }
  click() { this.dispatchEvent(new Event('click')); }
  async play() { this.paused=false; this.dispatchEvent(new Event('play')); }
  pause() { if (!this.paused) { this.paused=true; this.dispatchEvent(new Event('pause')); } }
  load() {}
  getBoundingClientRect() { return {width:300,height:200}; }
  getContext() { return new Proxy({}, {get:(_,name) => name==='createRadialGradient' ? () => ({addColorStop(){}}) : () => {}}); }
}
const elements = new Map();
const element = id => { if (!elements.has(id)) elements.set(id,new Element(id)); return elements.get(id); };
globalThis.document={getElementById:element,createElement:() => new Element('anchor')};
globalThis.window=globalThis; globalThis.devicePixelRatio=1;
globalThis.addEventListener=()=>{}; globalThis.matchMedia=()=>({matches:false});
globalThis.requestAnimationFrame=cb => { nextFrame=cb; return 1; };
globalThis.setTimeout=()=>0;
Object.defineProperty(globalThis,'performance',{configurable:true,value:{now:()=>now}});
URL.createObjectURL=blob => { if(blob instanceof Blob) lastBlob=blob; return 'blob:fixture'; };
URL.revokeObjectURL=()=>{};
globalThis.AudioContext=class {
  constructor() { this.state='running'; this.sampleRate=48000; this.destination={}; }
  createAnalyser() { return {fftSize:2048,frequencyBinCount:1024,connect(){},getFloatTimeDomainData(a){a.fill(.1);},getFloatFrequencyData(a){a.fill(-30);}}; }
  createMediaElementSource() { sourceConnections++; return {connect(){}}; }
  async resume() { this.state='running'; }
};
await import('./app.mjs');
const settle = async () => { for(let i=0;i<5;i++) await Promise.resolve(); };
const step = (amount=150) => { now+=amount; const cb=nextFrame; cb(now); };

test('native player starts analysis before recording local audio', async () => {
  const file=element('file'); file.files=[{name:'tone.wav'}]; file.dispatchEvent(new Event('change'));
  await element('player').play(); await settle(); step();
  assert.equal(sourceConnections,1,'native playback must connect the audio analyser');
});

test('each captured configuration remains associated with its own packets', async () => {
  element('demo').click(); step(); step();
  const sensitivity=element('sensitivity'); sensitivity.value='22'; sensitivity.dispatchEvent(new Event('input'));
  step(); step(); sensitivity.value='30'; sensitivity.dispatchEvent(new Event('input'));
  element('export').click();
  assert.ok(lastBlob,'capture should be downloadable');
  const payload=JSON.parse(await lastBlob.text());
  assert.ok(Array.isArray(payload.config_segments),'capture must include configuration history');
  assert.deepEqual(payload.config_segments.map(s=>s.config.sensitivity),[14,22]);
  assert.equal(payload.config_segments[0].start_packet,0);
  assert.equal(payload.config_segments.at(-1).end_packet_exclusive,payload.packets.length);
});

test('stop preserves the capture for export', async () => {
  element('stop').click(); lastBlob=null; element('export').click();
  assert.ok(lastBlob,'stopping should not discard the captured evidence');
  const payload=JSON.parse(await lastBlob.text());
  assert.equal(payload.source,'synthetic-demo');
  assert.ok(payload.packets.length>0);
});

test('rolling retention trims old packets and reindexes configuration segments', async () => {
  const sensitivity=element('sensitivity'); sensitivity.value='14'; sensitivity.dispatchEvent(new Event('input'));
  element('demo').click(); for(let i=0;i<10;i++) step();
  sensitivity.value='22'; sensitivity.dispatchEvent(new Event('input'));
  for(let i=0;i<3595;i++) step();
  element('export').click(); let payload=JSON.parse(await lastBlob.text());
  assert.equal(payload.packets.length,3600);
  assert.deepEqual(payload.config_segments.map(s=>[s.start_packet,s.end_packet_exclusive,s.config.sensitivity]),[[0,5,14],[5,3600,22]]);
  for(let i=0;i<5;i++) step();
  element('export').click(); payload=JSON.parse(await lastBlob.text());
  assert.equal(payload.packets.length,3600);
  assert.deepEqual(payload.config_segments.map(s=>[s.start_packet,s.end_packet_exclusive,s.config.sensitivity]),[[0,3600,22]]);
});
