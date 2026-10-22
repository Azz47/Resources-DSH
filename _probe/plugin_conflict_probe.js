const fs = require('fs');
const path = require('path');
const P = 'C:/Users/Administrator/.dsh/profiles/desktop/node_modules';
const names = [
  '@michengai/dsh-im-connect', 'dsh-animations', 'dsh-context', 'dsh-free-search',
  'dsh-image-gen', 'dsh-whale-widget', '@michengai/dsh-skills-manager',
  'dsh-skill-mcp-manager', 'billion-context', '@vectorize-io/hindsight-coding-agents',
  'dsh-vision-router', '@nanmicoder/dsh-agent-teams',
  '@arcaneorion/dsh-teaching-board', '@haoranwang0921/dsh-session-cleaner',
  'dsh-plugin-education', 'dsh-run2skill'
];
for (const name of names) {
  const dir = path.join(P, name);
  const pkgPath = path.join(dir, 'package.json');
  if (!fs.existsSync(pkgPath)) { console.log('### ' + name + ' : NOT INSTALLED'); continue; }
  const meta = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  console.log('\n### ' + name + '@' + meta.version);
  console.log('description:', (meta.description || '').replace(/\s+/g, ' ').slice(0, 260));
  console.log('dsh:', JSON.stringify(meta.dsh || {}));
  const bundle = meta.dsh?.bundle;
  const patch = typeof bundle === 'string' ? bundle : bundle?.patch;
  const patches = Array.isArray(patch) ? patch : patch ? [patch] : [];
  for (const rel of patches) {
    const fp = path.join(dir, rel);
    if (!fs.existsSync(fp)) { console.log('patch missing:', rel); continue; }
    const text = fs.readFileSync(fp, 'utf8');
    const ids = [...text.matchAll(/^\s*-\s*(?:id|insert):\s*(["']?)([^\n"']+)\1/gm)].map(m => m[2].trim());
    console.log('patch:', rel, 'bytes', Buffer.byteLength(text), 'ids:', [...new Set(ids)].slice(0, 20).join(', '));
  }
}
