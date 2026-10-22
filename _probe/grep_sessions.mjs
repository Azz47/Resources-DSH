import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const root = 'C:/Users/Administrator/.dsh/sessions/--D-Resources-DSH--';
const needles = ['以礼待人', '第四课第二框'];

function frames(buf) {
  const offs = [];
  for (let i = 0; i < buf.length - 3; i++) {
    if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) offs.push(i);
  }
  offs.push(buf.length);
  const parts = [];
  for (let k = 0; k < offs.length - 1; k++) {
    try { parts.push(zlib.zstdDecompressSync(buf.subarray(offs[k], offs[k + 1]))); } catch {}
  }
  return Buffer.concat(parts).toString('utf8');
}

for (const d of fs.readdirSync(root)) {
  const f = path.join(root, d, 'session.v4.jsonl.zstd');
  if (!fs.existsSync(f)) continue;
  let text;
  try { text = frames(fs.readFileSync(f)); } catch (e) { console.log(d, 'ERR', e.message); continue; }
  const idx = [];
  for (const n of needles) {
    let p = -1;
    while ((p = text.indexOf(n, p + 1)) !== -1) idx.push([n, p]);
  }
  if (!idx.length) continue;
  const first = idx[0][1];
  const last = idx[idx.length - 1][1];
  const around = text.slice(Math.max(0, first - 200), first + 200).replace(/\s+/g, ' ');
  console.log(`${d}  hits=${idx.length} firstAt=${first} lastAt=${last} (len=${text.length})`);
  console.log('   ' + around.slice(0, 330));
  console.log('   LASTCTX: ' + text.slice(Math.max(0, last - 150), last + 150).replace(/\s+/g, ' ').slice(0, 300));
}
