// Download big binaries with node fetch (PowerShell's Invoke-WebRequest cannot reach the GH release CDN here).
import fs from 'node:fs';
import path from 'node:path';

const [url, out] = process.argv.slice(2);
if (!url || !out) { console.error('usage: fetch-big.mjs <url> <outfile>'); process.exit(2); }

fs.mkdirSync(path.dirname(out), { recursive: true });
const tmp = out + '.part';

console.log('GET', url);
const res = await fetch(url, { redirect: 'follow' });
if (!res.ok) { console.error('HTTP', res.status, res.statusText); process.exit(1); }

const total = Number(res.headers.get('content-length') || 0);
console.log('status', res.status, 'content-length', total ? (total / 1048576).toFixed(1) + ' MB' : 'unknown');

const ws = fs.createWriteStream(tmp);
let got = 0, lastPct = -1;
const reader = res.body.getReader();
for (;;) {
  const { done, value } = await reader.read();
  if (done) break;
  ws.write(Buffer.from(value));
  got += value.length;
  if (total) {
    const pct = Math.floor((got / total) * 100);
    if (pct >= lastPct + 10) { lastPct = pct; console.log(`  ${pct}%  ${(got / 1048576).toFixed(1)} MB`); }
  }
}
await new Promise((r) => ws.end(r));
fs.renameSync(tmp, out);
console.log('saved', out, (fs.statSync(out).size / 1048576).toFixed(1) + ' MB');
