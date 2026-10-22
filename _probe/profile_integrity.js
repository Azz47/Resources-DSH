// Check that every plugin installed into the DSH desktop profile resolves and has its
// declared entry files on disk. A crashed / interrupted pnpm install leaves partial dirs.
//   node profile_integrity.js [profileDir]
const fs = require('fs');
const path = require('path');

const profile = process.argv[2] || 'C:/Users/Administrator/.dsh/profiles/desktop';
const nm = path.join(profile, 'node_modules');
const pkgPath = path.join(profile, 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const deps = Object.keys(pkg.dependencies || {});

function exists(p) { try { return fs.statSync(p).isFile() || fs.statSync(p).isDirectory(); } catch { return false; } }

const rows = [];
for (const name of deps.sort()) {
  const dir = path.join(nm, name);
  const pj = path.join(dir, 'package.json');
  if (!exists(pj)) { rows.push([name, 'MISSING package.json', '']); continue; }
  let meta;
  try { meta = JSON.parse(fs.readFileSync(pj, 'utf8')); } catch (e) { rows.push([name, 'UNPARSABLE package.json', String(e.message).slice(0, 60)]); continue; }
  const checks = [];
  const main = meta.main || 'index.js';
  checks.push(['main', main]);
  const exportsClient = meta.exports && typeof meta.exports === 'object' && meta.exports['./client'];
  let clientRel = null;
  if (typeof exportsClient === 'string') clientRel = exportsClient;
  else if (exportsClient && typeof exportsClient === 'object') clientRel = exportsClient.default || exportsClient.import || null;
  if (clientRel) checks.push(['client', clientRel]);
  const missing = [];
  for (const [kind, rel] of checks) {
    if (typeof rel !== 'string') continue;
    const abs = path.join(dir, rel);
    if (!exists(abs)) missing.push(kind + ':' + rel);
  }
  rows.push([name, meta.version || '?', missing.length ? 'MISSING ' + missing.join(', ') : 'ok', clientRel ? String(clientRel) : '']);
}

const bad = rows.filter((r) => r[2] !== 'ok' && r[2] !== '');
console.log('profile   :', profile);
console.log('deps      :', deps.length);
for (const r of rows) console.log('  ' + (r[2] === 'ok' ? 'OK   ' : 'BAD  ') + r[0].padEnd(46) + ' v' + String(r[1]).padEnd(12) + (r[2] === 'ok' ? '' : r[2]));
console.log('problems  :', bad.length);
