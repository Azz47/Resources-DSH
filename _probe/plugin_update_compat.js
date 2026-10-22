const fs = require('fs');
const path = require('path');
const semver = require('C:/Program Files/nodejs/node_modules/npm/node_modules/semver');

const HOST = {
  cordis: '4.0.5',
  schemastery: '3.18.5',
  core: '0.2.1-rc.2'
};

const targets = [
  '@arcaneorion/dsh-teaching-board',
  '@haoranwang0921/dsh-session-cleaner',
  'dsh-plugin-education',
  'dsh-run2skill'
];

function hostVersion(peer) {
  if (peer === '@deepseek-ai/cordis') return HOST.cordis;
  if (peer === '@deepseek-ai/schemastery') return HOST.schemastery;
  if (peer.startsWith('@deepseek-ai/')) return HOST.core;
  return undefined;
}

function checkPeers(meta) {
  const bad = [];
  for (const [peer, range] of Object.entries(meta.peerDependencies || {})) {
    const have = hostVersion(peer);
    if (!have) continue;
    try {
      if (!semver.satisfies(have, range, { includePrerelease: true })) bad.push(peer + ': need ' + range + ', have ' + have);
    } catch { bad.push(peer + ': unparsable range ' + range); }
  }
  return bad;
}

async function fetchJson(url) {
  const r = await fetch(url, { headers: { accept: 'application/json' } });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

(async () => {
  for (const name of targets) {
    console.log('===== ' + name + ' =====');
    let doc;
    try { doc = await fetchJson('https://registry.npmjs.org/' + name.replace('/', '%2F')); }
    catch (e) { console.log('registry error: ' + e.message); continue; }
    const tags = doc['dist-tags'] || {};
    const versions = Object.keys(doc.versions || {});
    const latest = tags.latest;
    console.log('latest=' + latest + ' published=' + (doc.time && doc.time[latest]));
    const latestMeta = doc.versions[latest];
    const latestBad = checkPeers(latestMeta);
    console.log('latest compatible with host: ' + (latestBad.length === 0 ? 'YES' : 'NO'));
    for (const b of latestBad) console.log('  x ' + b);
    // newest version that satisfies all host peers (including prereleases)
    const candidates = versions.filter(v => {
      const m = doc.versions[v];
      return m && checkPeers(m).length === 0;
    });
    candidates.sort((a, b) => semver.rcompare(a, b, { includePrerelease: true }));
    console.log('newest host-compatible versions: ' + (candidates.slice(0, 5).join(', ') || 'NONE'));
    if (candidates.length && candidates[0] !== latest) {
      const c = doc.versions[candidates[0]];
      console.log('  recommended=' + candidates[0] + ' published=' + (doc.time && doc.time[candidates[0]]));
      console.log('  peers=' + JSON.stringify(c.peerDependencies || {}));
    }
  }
})().catch(e => { console.error(e); process.exit(1); });
