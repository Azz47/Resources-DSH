const names = process.argv.slice(2);
const get = async (url) => {
  const r = await fetch(url);
  if (!r.ok) return null;
  return r.json();
};
for (const n of names) {
  const enc = n.replace('/', '%2f');
  const j = await get(`https://registry.npmjs.org/${enc}/latest`);
  if (!j) { console.log(`${n.padEnd(38)} MISS`); continue; }
  const repo = (j.repository && j.repository.url ? j.repository.url : '-').replace(/^git\+|\.git$/g, '');
  const desc = (j.description || '').replace(/\s+/g, ' ').slice(0, 110);
  console.log(`${n.padEnd(38)} v${String(j.version).padEnd(10)} ${repo}`);
  console.log(`${' '.repeat(38)} ${desc}`);
}
