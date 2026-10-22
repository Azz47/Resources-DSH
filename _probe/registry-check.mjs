import fs from 'node:fs';

const data = JSON.parse(fs.readFileSync('D:/Resources/DSH/_probe/awesome-plugins.json', 'utf8'));
const arr = Array.isArray(data) ? data : (data.plugins || data.items || data.entries || Object.values(data));
console.log('entries:', Array.isArray(arr) ? arr.length : typeof arr);

const nameOf = (e) => e.name || e.package || e.npm || e.id || (e.repo || e.repository || '');
const targets = ['dsh-ppt-studio', 'dsh-craft-your-textbook', 'dsh-plugin-education', 'dsh-teaching-board',
  'dsh-mindmap', 'dsh-context', 'dsh-better-sidebar', 'dsh-hotspots', 'dsh-image-generation', 'dshmarket'];

for (const t of targets) {
  const hit = arr.find((e) => {
    const n = nameOf(e).toLowerCase();
    return n === t || n.endsWith('/' + t);
  });
  if (!hit) { console.log(`${t.padEnd(26)} NOT FOUND in registry`); continue; }
  const stars = hit.stars ?? hit.stargazers_count ?? hit.starsCount ?? '?';
  console.log(`${t.padEnd(26)} name=${nameOf(hit)}  stars=${stars}  install=${hit.install || hit.command || '-'}`);
}
