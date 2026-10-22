import fs from 'node:fs';

const file = 'D:/Resources/DSH/_probe/catalogs/dsh-plugin-shop-catalog/package/v1/plugins.58c8672fc03c76240314cf13230a844331e19529635c52f4be539ed29387eb6f.json';
const plugins = JSON.parse(fs.readFileSync(file, 'utf8')).plugins;

const wanted = process.argv.slice(2);
for (const w of wanted) {
  const matches = plugins.filter((p) => p.name === w || p.name.endsWith('/' + w));
  if (!matches.length) { console.log(`${w}  -> NOT IN CATALOG`); continue; }
  for (const p of matches) {
    console.log(`${p.name}@${p.version}  src=${p.source}  repo=${(p.repository || '-').replace('https://github.com/', '')}`);
    console.log(`    peers: ${JSON.stringify(p.peers || [])}`);
    console.log(`    ${(p.catalog?.summary?.en || p.catalog?.summary?.zh || '').slice(0, 200)}`);
  }
}
