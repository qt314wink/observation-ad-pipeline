import {
  analyzeFrame, mapFeatures, smoothControls, makePacket, silenceControls,
  DEFAULT_CONFIG, CONTRACT_VERSION
} from "./engine.mjs";

const $ = id => document.getElementById(id);
const canvas = $("visual"), g = canvas.getContext("2d", {alpha:false});
const player = $("player");
const modeLabel = $("mode"), stateLabel = $("state"), statistics = $("stats");
const config = {...DEFAULT_CONFIG};
const memory = {controls:silenceControls(), magnitudes:null, records:[], mode:"idle", firstFrame:0,
  latestCapture:0, lastFrame:0, fpsFrames:0, lastFpsAt:0, fps:0, meanFlux:0};
let audioContext, analyser, waveform, spectrum, mediaSource, fileUrl;
const LIMIT = 3600; // bounded, 10 Hz capture = latest 6 minutes
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

function resize() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 1.75, Math.sqrt(1_600_000 / Math.max(1,rect.width*rect.height)));
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
  g.setTransform(dpr,0,0,dpr,0,0);
}
addEventListener("resize", resize, {passive:true});
resize();

function reset(mode) {
  memory.mode=mode; memory.controls=silenceControls(); memory.magnitudes=null;
  memory.records=[]; memory.firstFrame=performance.now(); memory.latestCapture=0; memory.lastFrame=0;
  memory.meanFlux=0;
  modeLabel.textContent = mode === "demo" ? "Synthetic signal (not festival audio)" : mode === "file" ? "Local file" : "Idle";
}

async function ensureAudio() {
  if (!audioContext) {
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0; // smoothing happens in semantic controls
    analyser.minDecibels=-100; analyser.maxDecibels=-10;
    waveform = new Float32Array(analyser.fftSize);
    spectrum = new Float32Array(analyser.frequencyBinCount);
    mediaSource = audioContext.createMediaElementSource(player);
    mediaSource.connect(analyser);
    analyser.connect(audioContext.destination);
  }
  if (audioContext.state === "suspended") await audioContext.resume();
}

$("file").addEventListener("change", event => {
  const f = event.target.files?.[0];
  if (!f) return;
  if (fileUrl) URL.revokeObjectURL(fileUrl);
  fileUrl = URL.createObjectURL(f);
  player.pause(); player.src = fileUrl; player.load();
  reset("file");
  stateLabel.textContent = "File loaded locally. Press Play file.";
});
$("play").addEventListener("click", async () => {
  if (!player.src) {stateLabel.textContent = "Choose an audio file first.";return;}
  try {
    reset("file");
    await ensureAudio();
    await player.play();
    stateLabel.textContent = "Playing local audio.";
  } catch (error) {stateLabel.textContent = "Playback blocked: " + error.message;}
});
$("demo").addEventListener("click", () => {
  player.pause(); reset("demo"); stateLabel.textContent = "Synthetic demonstration running.";
});
$("stop").addEventListener("click", () => {
  player.pause(); reset("idle"); stateLabel.textContent = "Stopped.";
});
for (const [element,key,min,max] of [
  ["sensitivity","sensitivity",1,40], ["attack","attackSeconds",.02,.8],
  ["release","releaseSeconds",.06,2], ["intensity","visualIntensity",0,1],
  ["sectors","sectors",4,20]
]) {
  const input = $(element);
  input.addEventListener("input", () => {
    config[key] = Math.max(min, Math.min(max,Number(input.value)));
    $(element+"-out").textContent = String(config[key]);
  });
}

function syntheticFeatures(t) {
  // Contrived signals make mapping reproducible for visual testing; not measured audio.
  const wave = (hz, phase=0) => (Math.sin(2*Math.PI*hz*t+phase)+1)/2;
  const kick = Math.exp(-Math.pow((t%1.2)/.14,2));
  const transient = Math.exp(-Math.pow((t%.6)/.075,2));
  return {
    rms: .02+.06*wave(.11)+.075*kick,
    low: .008+.045*kick,
    mid: .012+.045*wave(.23),
    high: .01+.06*wave(.41),
    centroid:.25+.48*wave(.08),
    flux:transient*.65
  };
}
function currentFeatures(t) {
  if(memory.mode === "demo") return syntheticFeatures(t);
  if(memory.mode !== "file" || player.paused || !analyser) return {
    rms:0,low:0,mid:0,high:0,centroid:0,flux:0
  };
  analyser.getFloatTimeDomainData(waveform);
  analyser.getFloatFrequencyData(spectrum);
  const result = analyzeFrame(waveform,spectrum,audioContext.sampleRate,memory.magnitudes);
  memory.magnitudes = result.magnitudes;
  return result.features;
}
function color(h, s, l, a=1) {return "hsla("+((h%360+360)%360)+","+s+"%,"+l+"%,"+a+")";}
function render(t, controls) {
  const w=canvas.clientWidth, h=canvas.clientHeight;
  if (w===0 || h===0) return;
  const r=Math.min(w,h)*.44, sectorCount=Math.round(config.sectors);
  g.clearRect(0,0,w,h);
  const backdrop=g.createRadialGradient(w*.5,h*.5,0,w*.5,h*.5,Math.max(w,h)*.65);
  backdrop.addColorStop(0,"#17234d"); backdrop.addColorStop(.6,"#100e2b");
  backdrop.addColorStop(1,"#060711");
  g.fillStyle=backdrop; g.fillRect(0,0,w,h);
  g.save();
  g.translate(w/2,h/2);
  const time = reducedMotion ? 0 : t;
  const rotation = Math.sin(time*.11)*.04 + (reducedMotion ? 0 : time*.016);
  const aperture= .69+.12*controls.fold+.04*Math.sin(time*.7);
  const hue=190+controls.hue*118;
  // Mirror every second petal; independent material/optical channels.
  for(let sector=0;sector<sectorCount;sector++) {
    g.save();
    g.rotate(rotation+sector*2*Math.PI/sectorCount);
    if(sector%2===1) g.scale(1,-1);
    for(let band=0;band<5;band++) {
      const u=band/5;
      const near=r*(.08+u*.74);
      const far=r*(.28+u*.69)*aperture;
      const offset=Math.sin(time*(.48+u*.3)+band*1.7)*r*.02*controls.fold;
      g.beginPath();
      g.moveTo(near,0);
      g.quadraticCurveTo((near+far)*.49, r*(.04+.08*controls.fold)+offset,far,r*.08);
      g.quadraticCurveTo((near+far)*.54,-r*.05-offset,near,0);
      g.fillStyle=color(hue+band*15+sector%2*10, 80, 28+band*6+controls.shimmer*13, .16+.11*controls.energy);
      g.fill();
      g.strokeStyle=color(hue-20+band*21,85,51+controls.shimmer*20,.25+.35*controls.energy);
      g.lineWidth=.6+controls.shimmer*1.2;
      g.stroke();
    }
    g.beginPath();
    g.moveTo(r*.14,0);
    g.quadraticCurveTo(r*.58,r*.13*(.5+controls.fold),r*(.8+.13*controls.fold),0);
    g.strokeStyle=color(hue+40,95,60+controls.shimmer*17,.35+.42*controls.shimmer);
    g.lineWidth=.5+controls.pulse*2.2;
    g.stroke();
    g.restore();
  }
  // A few restrained concentric interference rings, no strobes.
  for(let ring=0; ring<5;ring++){
    const rad=r*(.18+ring*.155)*(1+.018*controls.pulse);
    g.beginPath();g.arc(0,0,rad,0,2*Math.PI);
    g.strokeStyle=color(hue+ring*24,85,45+ring*4,.12+.20*controls.shimmer);
    g.lineWidth=.6+controls.shimmer;g.stroke();
  }
  // Density maps to count, not to hue or global spin.
  const count=Math.round(15+controls.density*70);
  for(let i=0;i<count;i++){
    const a=i*2.399963229728653;
    const rr=r*Math.sqrt((i+.5)/(count+.5));
    const x=Math.cos(a)*rr, y=Math.sin(a)*rr;
    const point= .6+1.4*controls.shimmer + .3*Math.sin(i*3+time*.8);
    g.beginPath();g.arc(x,y,Math.max(.3,point),0,2*Math.PI);
    g.fillStyle=color(hue+60+i%3*15,88,70,.15+.30*controls.shimmer);
    g.fill();
  }
  // Center is preserved: pulse changes a local radius only.
  g.beginPath();g.arc(0,0,r*(.037+.021*controls.pulse),0,2*Math.PI);
  g.fillStyle=color(hue+35,80,82,.65);
  g.fill();g.restore();
}
function tick(now) {
  const dt = memory.lastFrame ? Math.min(.25,(now-memory.lastFrame)/1000) : 1/60;
  memory.lastFrame=now;
  const t = (now-memory.firstFrame)/1000;
  const f=currentFeatures(t);
  memory.controls=smoothControls(mapFeatures(f,config),memory.controls,dt,config);
  render(t,memory.controls);
  if(memory.mode !== "idle" && now-memory.latestCapture >= 100) {
    const time = memory.mode==="file" ? player.currentTime : t;
    const packet=makePacket(time,memory.controls);
    memory.records.push(packet);
    if(memory.records.length>LIMIT) memory.records.shift();
    memory.latestCapture=now;
  }
  memory.fpsFrames++;
  if(now-memory.lastFpsAt>1000) {
    memory.fps=Math.round(memory.fpsFrames*1000/Math.max(1,now-memory.lastFpsAt));
    memory.lastFpsAt=now;memory.fpsFrames=0;
    statistics.textContent="Rendered "+memory.fps+" fps · RMS "+f.rms.toFixed(3)+
      " · spectral novelty "+f.flux.toFixed(3)+" · captured packets "+memory.records.length;
  }
  requestAnimationFrame(tick);
}
memory.firstFrame=performance.now();memory.lastFpsAt=performance.now();
requestAnimationFrame(tick);

$("export").addEventListener("click", () => {
  if(!memory.records.length){stateLabel.textContent="No captured controls. Play or run synthetic demo first.";return;}
  const payload={
    format:"audio-reactive-capture.v0.1", contract:CONTRACT_VERSION,
    source: memory.mode === "file" ? "local-audio-file" : "synthetic-demo",
    source_media_included:false, sample_interval_target_ms:100,
    max_retained_packets:LIMIT, config:{...config},
    provenance:{
      reference:"https://www.youtube.com/watch?v=3GtpHGZZdUc",
      reference_role:"artistic reference only; no extracted video or audio",
      generated_at:new Date().toISOString()
    },
    packets:memory.records
  };
  const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}));
  const link=document.createElement("a");
  link.href=url;link.download="audio-reactive-control-capture.json";link.click();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
  stateLabel.textContent="Downloaded JSON control capture; original audio was not included.";
});
