const q = process.argv[2];
const r = await fetch(`https://registry.npmjs.org/-/v1/search?text=${encodeURIComponent(q)}&size=25`);
const j = await r.json();
console.log(`=== "${q}" total=${j.total} ===`);
for (const o of j.objects) {
  const d = (o.package.description || '').replace(/\s+/g, ' ').slice(0, 105);
  console.log(`  ${o.package.name}@${o.package.version}  ::  ${d}`);
}
