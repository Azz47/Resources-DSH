import fs from 'node:fs';

const d = JSON.parse(fs.readFileSync('D:/Resources/DSH/_probe/awesome-plugins.json', 'utf8'));
console.log('top-level keys:', Object.keys(d).join(', '));
for (const [k, v] of Object.entries(d)) {
  if (Array.isArray(v)) console.log(`  ${k}: array(${v.length})`);
  else if (v && typeof v === 'object') console.log(`  ${k}: object{${Object.keys(v).slice(0, 8).join(',')}}`);
  else console.log(`  ${k}: ${typeof v} = ${String(v).slice(0, 60)}`);
}
