const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const legacyDatasetPath = 'data/mandala-reel-set.json';
const list = (values, className = '') => (values || []).map(value =>
  `<li class="${className}">${esc(typeof value === 'string' ? value : JSON.stringify(value))}</li>`
).join('');

async function loadWorkbench() {
  const index = await fetch('data/index.json').then(response => response.json());
  const requested = new URLSearchParams(window.location.search).get('dataset');
  const dataset = index.datasets.find(item => item.id === requested) || index.datasets[0];
  const data = await fetch(dataset.path).then(response => response.json());

  document.querySelector('#dataset-nav').innerHTML = index.datasets.map(item =>
    `<a href="?dataset=${encodeURIComponent(item.id)}" ${item.id === dataset.id ? 'aria-current="page"' : ''}>${esc(item.label)}</a>`
  ).join(' ');
  document.querySelector('#authority-card').innerHTML = `
    <strong>${esc(data.title || dataset.label)}</strong>
    <p>${esc(data.creator || data.authority?.project || 'Governed corpus')}</p>
    <p>${esc(data.point || data.authority?.commit || '')}</p>
    ${data.canonicalDigest ? `<p>Canonical digest: <code>${esc(data.canonicalDigest)}</code></p>` : ''}
    <span class="badge">${dataset.readOnly ? 'DERIVED / READ-ONLY' : 'SOURCE LEDGER'}</span>`;

  const scenes = data.scenes || data.sources || [];
  document.querySelector('#scene-grid').innerHTML = scenes.map(scene => `
    <article class="card">
      <h3>${esc(scene.label || scene.id || scene.file)}</h3>
      <p>${esc(scene.visualSummary || scene.id || scene.file)}</p>
      ${(scene.movementEvents || []).map(event => `
        <p><strong>${esc(event.action)}</strong> → ${esc((event.structuralMechanisms || []).join(', '))}
        <br><span>Quality: ${esc(JSON.stringify(event.movementQuality || {}))}</span>
        <br><span>Manner: ${esc(event.manner?.directorPhrase || 'unresolved')}</span></p>`).join('')}
      <span class="badge">${esc(scene.provenance?.kind || scene.evidenceStatus || 'UNVERIFIED')}</span>
    </article>`).join('');

  document.querySelector('#vocabulary').innerHTML = list(data.directorVocabulary?.map(item =>
    `${item.term} (${item.verificationStatus})`));
  document.querySelector('#interpretations').innerHTML = (data.interpretations || data.taxonomy || []).map(item =>
    `<article class="card"><h3>${esc(item.label || item)}</h3><p>${esc(item.statement || item)}</p>
    ${item.falsifier ? `<p><strong>Falsifier:</strong> ${esc(item.falsifier)}</p>` : ''}</article>`).join('');
  document.querySelector('#controls').innerHTML = (data.directorControls || []).map(control =>
    `<article class="card"><h3>${esc(control.label)}</h3><p>${esc(control.question)}</p>
    <p>${esc(control.whatYouWillSee)}</p><small>Low: ${esc(control.tooLowLooksLike)} High: ${esc(control.tooHighLooksLike)}</small></article>`).join('');
  document.querySelector('#uncertain').innerHTML = list(data.blockers || data.authority?.blockers || ['No additional uncertainty recorded.']);
  document.querySelector('#gate').textContent = data.experimentGate
    ? `${data.experimentGate.status}: ${data.experimentGate.reason}`
    : 'Analysis remains evidence-blocked.';
  document.querySelector('#status').textContent = `${dataset.label} loaded. Evidence remains read-only.`;
}

loadWorkbench().catch(() => {
  document.querySelector('#status').textContent = 'Governed record could not be loaded.';
});
