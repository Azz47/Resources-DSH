const fs = require('fs');
const path = require('path');
const profile = process.argv[2];
if (!profile) { console.error('profile path required'); process.exit(2); }

const pkgPath = path.join(profile, 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const bundles = pkg?.dsh?.profile?.bundles;
if (!Array.isArray(bundles)) { console.error('dsh.profile.bundles missing'); process.exit(3); }

// F2: remove run2skill from the loaded bundle set.
const removeBundles = new Set(['dsh-run2skill']);
let next = bundles.filter(x => !removeBundles.has(x));

// Keep the five already-staged compatible plugins; restore order before dshmarket if absent.
const staged = ['dsh-image-gen', 'dsh-context', 'dsh-animations', 'dsh-whale-widget', '@michengai/dsh-im-connect'];
const missing = staged.filter(x => !next.includes(x));
if (missing.length) {
  const at = next.indexOf('dshmarket');
  if (at >= 0) next.splice(at, 0, ...missing);
  else next.push(...missing);
}
pkg.dsh.profile.bundles = next;
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n', 'utf8');

// C1: exact-version exemption for teaching-board 0.6.0 on the running host version.
const compatPath = path.join(profile, 'compatibility.json');
let compat = {};
try { compat = JSON.parse(fs.readFileSync(compatPath, 'utf8')); } catch (e) { compat = {}; }
const key = '@arcaneorion/dsh-teaching-board@0.6.0';
if (!Array.isArray(compat[key])) compat[key] = [];
for (const v of ['0.2.0-rc.2', '0.2.1-rc.2']) {
  if (!compat[key].includes(v)) compat[key].push(v);
}
fs.writeFileSync(compatPath, JSON.stringify(compat, null, 2) + '\n', 'utf8');

console.log('BUNDLES=' + pkg.dsh.profile.bundles.length);
console.log('RUN2SKILL=' + pkg.dsh.profile.bundles.includes('dsh-run2skill'));
console.log('TEACHING_EXEMPT=' + compat[key].join(','));
