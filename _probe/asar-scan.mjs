import fs from 'node:fs';

const asar = process.argv[2];
const max = Number(process.argv[3] || 8);
const ctx = Number(process.argv[4] || 300);
const needles = process.argv.slice(5);

const buf = fs.readFileSync(asar);
console.log(`asar size = ${buf.length}`);

for (const needle of needles) {
  const nb = Buffer.from(needle);
  let i = 0, n = 0;
  while (n < max) {
    i = buf.indexOf(nb, i);
    if (i === -1) break;
    const s = Math.max(0, i - ctx);
    const e = Math.min(buf.length, i + ctx);
    console.log(`\n=== [${needle}] @${i} ===`);
    console.log(buf.slice(s, e).toString('utf8').replace(/[^\x20-\x7e\n\r\t]/g, '.'));
    i += nb.length;
    n++;
  }
  console.log(`\n--- hits for [${needle}]: ${n}`);
}
