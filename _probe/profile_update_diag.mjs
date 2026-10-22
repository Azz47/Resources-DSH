import fs from 'node:fs';

const cwd = 'C:/Users/Administrator/.dsh/profiles/desktop';
const lock = fs.readFileSync(cwd + '/pnpm-lock.yaml', 'utf8');
for (const n of ['billion-context', 'dshmarket', '@michengai/dsh-automation']) {
  const re = new RegExp(`^\\s+'?${n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^:]*:`, 'gm');
  console.log('=== lock ' + n + ' ===');
  console.log((lock.match(re) || []).slice(0, 10).join('\n'));
}

for (const p of ['@michengai/dsh-automation', 'billion-context', 'dshmarket']) {
  const url = 'https://registry.npmjs.org/' + p.replace('/', '%2F');
  try {
    const r = await fetch(url);
    if (!r.ok) { console.log(p, 'fetch failed', r.status); continue; }
    const j = await r.json();
    const entries = Object.entries(j.time || {}).filter(([v]) => v !== 'created' && v !== 'modified');
    entries.sort((a, b) => new Date(b[1]) - new Date(a[1]));
    console.log('=== registry ' + p + ' latest 8 ===');
    for (const [v, t] of entries.slice(0, 8)) {
      const ageH = ((Date.now() - new Date(t).getTime()) / 3600000).toFixed(1);
      const tags = Object.entries(j['dist-tags'] || {}).filter(([, val]) => val === v).map(([k]) => k).join(',');
      console.log(v.padEnd(12), t, 'age_h=' + ageH, tags ? 'tag=' + tags : '');
    }
  } catch (e) {
    console.log(p, 'fetch error', e.message);
  }
}

const asar = fs.readFileSync('D:/tools/dsh/resources/app.asar');
for (const needleStr of ['minimumReleaseAge', 'minimum-release-age']) {
  const needle = Buffer.from(needleStr);
  let idx = -1, count = 0;
  while ((idx = asar.indexOf(needle, idx + 1)) !== -1 && count < 10) {
    const start = Math.max(0, idx - 220);
    const end = Math.min(asar.length, idx + 280);
    console.log('--- ' + needleStr + ' @' + idx + ' ---');
    console.log(asar.slice(start, end).toString('utf8').replace(/[^\x20-\x7E\n]/g, ' '));
    count++;
  }
  console.log('matches shown for ' + needleStr + ':', count);
}
