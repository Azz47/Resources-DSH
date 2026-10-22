import fs from 'node:fs';
import zlib from 'node:zlib';

const p = process.argv[2];
const outPath = process.argv[3] || 'D:/Resources/DSH/_probe/_full.jsonl';
const buf = fs.readFileSync(p);

// find zstd frame magics
const offs = [];
for (let i = 0; i < buf.length - 3; i++) {
  if (buf[i] === 0x28 && buf[i + 1] === 0xB5 && buf[i + 2] === 0x2F && buf[i + 3] === 0xFD) offs.push(i);
}
offs.push(buf.length);

const parts = [];
let ok = 0, fail = 0;
for (let k = 0; k < offs.length - 1; k++) {
  const chunk = buf.subarray(offs[k], offs[k + 1]);
  try {
    parts.push(zlib.zstdDecompressSync(chunk));
    ok++;
  } catch {
    fail++;
  }
}
const text = Buffer.concat(parts).toString('utf8');
fs.writeFileSync(outPath, text, 'utf8');
console.log(`frames=${offs.length - 1} ok=${ok} fail=${fail} textLen=${text.length}`);
