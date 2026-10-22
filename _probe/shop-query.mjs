import fs from 'node:fs';

const file = 'D:/Resources/DSH/_probe/catalogs/dsh-plugin-shop-catalog/package/v1/plugins.58c8672fc03c76240314cf13230a844331e19529635c52f4be539ed29387eb6f.json';
const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const plugins = data.plugins;

const args = process.argv.slice(2);
const nameOnly = args.includes('--name-only');
const terms = args.filter((a) => a !== '--name-only').map((t) => t.toLowerCase());

const hits = [];
for (const p of plugins) {
  const name = (p.name || '').toLowerCase();
  const summary = ((p.catalog?.summary?.en || '') + ' ' + (p.catalog?.summary?.zh || '')).toLowerCase();
  const repo = (p.repository || '').toLowerCase();
  for (const t of terms) {
    if (nameOnly ? name.includes(t) : (name.includes(t) || summary.includes(t) || repo.includes(t))) {
      hits.push({ term: t, p });
      break;
    }
  }
}
console.log(`catalog size=${plugins.length}  hits=${hits.length}`);
for (const { term, p } of hits.slice(0, 60)) {
  const s = (p.catalog?.summary?.en || p.catalog?.summary?.zh || '').slice(0, 150);
  console.log(`[${term}] ${p.name}@${p.version}  repo=${(p.repository || '-').replace('https://github.com/', '')}\n      ${s}`);
}
