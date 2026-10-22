// Search GitHub for repos likely to contain courseware PPTX corpora (api.github.com is reachable here).
const queries = [
  '课件 pptx in:name,description,readme',
  '教学课件 in:name,description',
  'ppt 模板 教育 in:name,description',
  'courseware pptx in:name,description',
  'presentation slides education chinese in:name,description',
];

for (const q of queries) {
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=12`;
  try {
    const r = await fetch(url, { headers: { Accept: 'application/vnd.github+json' }, signal: AbortSignal.timeout(30000) });
    if (!r.ok) { console.log(`\n### ${q}  -> HTTP ${r.status}`); continue; }
    const j = await r.json();
    console.log(`\n### ${q}   (total ${j.total_count})`);
    for (const it of j.items || []) {
      console.log(`  ★${String(it.stargazers_count).padEnd(6)} ${it.full_name}  [${it.language || '-'}]  size=${it.size}KB`);
      console.log(`      ${(it.description || '').replace(/\s+/g, ' ').slice(0, 110)}`);
    }
  } catch (e) {
    console.log(`\n### ${q}  -> ERR ${e.cause?.code || e.name}`);
  }
}
