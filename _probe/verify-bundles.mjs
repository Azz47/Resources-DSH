import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const profile = 'C:/Users/Administrator/.dsh/profiles/desktop';
const names = ['dsh-mindmap', 'dsh-ppt-studio', 'dsh-craft-your-textbook', 'dsh-context',
  'dsh-better-sidebar', 'dsh-hotspots', 'dsh-image-generation', 'dshmarket',
  '@arcaneorion/dsh-teaching-board', 'dsh-plugin-education'];

for (const name of names) {
  const dir = path.join(profile, 'node_modules', name);
  let pkg;
  try { pkg = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8')); }
  catch (e) { console.log(`${name}: cannot read package.json (${e.code})`); continue; }

  const patch = pkg.dsh?.bundle?.patch;
  const patchFiles = patch === undefined ? [] : (Array.isArray(patch) ? patch : [patch]);
  const results = [];
  for (const rel of patchFiles) {
    const p = path.join(dir, rel);
    if (!fs.existsSync(p)) { results.push(`MISSING PATCH ${rel}`); continue; }
    const text = fs.readFileSync(p, 'utf8');
    // every `name:` that looks like a module id, check resolvability relative to the plugin
    const ids = [...text.matchAll(/^\s*name:\s*['"]?([^'"\s]+)['"]?\s*$/gm)].map((m) => m[1]);
    for (const id of new Set(ids)) {
      if (id.startsWith('cordis:')) continue;
      const base = id.startsWith('.') || id.startsWith('/') ? path.resolve(dir, id) : null;
      if (base) { results.push(fs.existsSync(base) ? `ok ${id}` : `MISSING ${id}`); continue; }
      try {
        const req = createRequire(path.join(dir, 'package.json'));
        req.resolve(id);
        results.push(`ok ${id}`);
      } catch {
        // host-provided package: not installed in the profile, resolved by the app at runtime
        results.push(`host ${id}`);
      }
    }
  }
  const bad = results.filter((r) => r.startsWith('MISSING'));
  console.log(`${name}@${pkg.version}  patches=${patchFiles.length}  ids=${results.length}  unresolved=${bad.length}`);
  for (const b of bad) console.log('    ' + b);
}
