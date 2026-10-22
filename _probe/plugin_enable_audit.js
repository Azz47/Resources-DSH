const fs = require('fs');
const path = require('path');
const semver = require('C:/Program Files/nodejs/node_modules/npm/node_modules/semver');

const PROFILE = 'C:/Users/Administrator/.dsh/profiles/desktop';
const pkg = JSON.parse(fs.readFileSync(path.join(PROFILE, 'package.json'), 'utf8'));
const bundles = Array.isArray(pkg.dsh?.profile?.bundles) ? pkg.dsh.profile.bundles : [];
const deps = pkg.dependencies || {};
const HOST = { '@deepseek-ai/cordis': '4.0.5', '@deepseek-ai/schemastery': '3.18.5' };
const CORE = '0.2.1-rc.2';
const readJson = p => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
const installed = name => readJson(path.join(PROFILE, 'node_modules', name, 'package.json'));

function hostVersion(peer) {
  if (HOST[peer]) return HOST[peer];
  if (peer.startsWith('@deepseek-ai/')) return CORE;
  const local = installed(peer);
  return local?.version;
}
function peerIssues(meta) {
  const out = [];
  for (const [peer, range] of Object.entries(meta.peerDependencies || {})) {
    const have = hostVersion(peer);
    if (!have) {
      const optional = meta.peerDependenciesMeta?.[peer]?.optional;
      out.push({ peer, range, have: null, optional: !!optional, ok: !!optional, missing: true });
      continue;
    }
    let ok = false;
    try { ok = semver.satisfies(have, range, { includePrerelease: true }); } catch { ok = false; }
    out.push({ peer, range, have, optional: !!meta.peerDependenciesMeta?.[peer]?.optional, ok, missing: false });
  }
  return out;
}

const rows = [];
for (const name of Object.keys(deps)) {
  const meta = installed(name);
  if (!meta) { rows.push({ name, dep: deps[name], installed: null, error: 'not installed' }); continue; }
  const bundleDecl = meta.dsh?.bundle;
  const rawPatches = typeof bundleDecl === 'string'
    ? [bundleDecl]
    : Array.isArray(bundleDecl)
      ? bundleDecl
      : (bundleDecl?.patch ?? bundleDecl?.patches ?? []);
  const bundlePatches = (Array.isArray(rawPatches) ? rawPatches : [rawPatches]).filter(v => typeof v === 'string');
  const patchExists = bundlePatches.length > 0 && bundlePatches.some(p => fs.existsSync(path.join(PROFILE, 'node_modules', name, p)));
  const issues = peerIssues(meta);
  const bad = issues.filter(i => !i.ok && !i.optional);
  const optionalMissing = issues.filter(i => i.missing && i.optional);
  rows.push({
    name,
    dep: deps[name],
    installed: meta.version,
    inBundles: bundles.includes(name),
    hasBundle: !!bundleDecl,
    bundlePatch: bundlePatches.length ? bundlePatches : null,
    patchExists,
    client: !!meta.dsh?.client,
    platform: Array.isArray(meta.dsh?.client?.platform) ? meta.dsh.client.platform.join(',') : (meta.dsh?.client?.platform || null),
    peerBad: bad,
    optionalMissing: optionalMissing.map(i => i.peer)
  });
}

const missingBundles = bundles.filter(b => !deps[b] && !rows.some(r => r.name === b));
const enableCandidates = rows.filter(r => r.installed && r.hasBundle && !r.inBundles && r.peerBad.length === 0 && r.patchExists);
const blockedCandidates = rows.filter(r => r.installed && r.hasBundle && !r.inBundles && (r.peerBad.length > 0 || !r.patchExists));
const alreadyOn = rows.filter(r => r.inBundles);
const libraries = rows.filter(r => r.installed && !r.hasBundle && !r.inBundles);

console.log('bundles', bundles.length, 'direct deps', rows.length);
console.log('alreadyOn', alreadyOn.length, 'enableCandidates', enableCandidates.length, 'blockedCandidates', blockedCandidates.length, 'libraries', libraries.length);
console.log('\n=== ENABLE CANDIDATES (bundle, compatible, not in bundles) ===');
for (const r of enableCandidates) console.log(`${r.name}@${r.installed} client=${r.client}${r.platform ? '(' + r.platform + ')' : ''}`);
console.log('\n=== BLOCKED CANDIDATES (bundle present, but peer/patch issue) ===');
for (const r of blockedCandidates) console.log(`${r.name}@${r.installed} inBundles=${r.inBundles} patch=${r.patchExists} peers=${r.peerBad.map(p => `${p.peer}:${p.have} !~ ${p.range}`).join(' ; ')}`);
console.log('\n=== ALREADY IN BUNDLES ===');
for (const r of alreadyOn) console.log(`${r.name}@${r.installed} peersBad=${r.peerBad.length} client=${r.client}`);
console.log('\n=== DIRECT DEPS WITHOUT BUNDLE (libraries/tools) ===');
for (const r of libraries) console.log(`${r.name}@${r.installed} inBundles=${r.inBundles} client=${r.client}`);
console.log('\n=== BUNDLES NOT IN DIRECT DEPS (built-in or transitive) ===');
for (const b of missingBundles) console.log(b);

fs.writeFileSync('D:/Resources/DSH/_probe/plugin_audit_20261021_2320.json', JSON.stringify({ bundles, rows, enableCandidates, blockedCandidates, missingBundles }, null, 2), 'utf8');
