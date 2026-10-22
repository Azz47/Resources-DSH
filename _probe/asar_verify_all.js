// Verify every file entry in an asar archive against its embedded SHA256 integrity.
//   node asar_verify_all.js <asar>
const fs = require('fs');
const crypto = require('crypto');

const asarPath = process.argv[2];
const fd = fs.openSync(asarPath, 'r');
const probe = Buffer.alloc(64);
fs.readSync(fd, probe, 0, 64, 0);
const size = probe.readUInt32LE(4);
const buf = Buffer.alloc(size);
fs.readSync(fd, buf, 0, size, 8);
const start = buf.indexOf(0x7b);
let depth = 0, inStr = false, esc = false, end = -1;
for (let i = start; i < buf.length; i++) {
  const c = buf[i];
  if (inStr) { if (esc) esc = false; else if (c === 0x5c) esc = true; else if (c === 0x22) inStr = false; continue; }
  if (c === 0x22) inStr = true;
  else if (c === 0x7b) depth++;
  else if (c === 0x7d) { depth--; if (depth === 0) { end = i + 1; break; } }
}
const header = JSON.parse(buf.slice(start, end).toString('utf8'));
const dataOffset = 8 + size;

let files = 0, dirs = 0, ok = 0, mismatch = 0, noIntegrity = 0, bytes = 0;
let unpacked = 0, noOffset = 0;
const problems = [];
function walk(node, prefix) {
  for (const [name, child] of Object.entries(node.files || {})) {
    const p = prefix ? prefix + '/' + name : name;
    if (child.files) { dirs++; walk(child, p); continue; }
    files++;
    if (child.unpacked === true || child.link !== undefined) { unpacked++; continue; }
    const n = Number(child.size);
    const off = Number(child.offset);
    if (!Number.isFinite(n) || !Number.isFinite(off)) { noOffset++; continue; }
    bytes += n;
    const c = Buffer.alloc(n);
    fs.readSync(fd, c, 0, n, dataOffset + off);
    const h = crypto.createHash('sha256').update(c).digest('hex');
    const stated = child.integrity && child.integrity.hash;
    if (!stated) { noIntegrity++; if (problems.length < 10) problems.push('NOINTEGRITY ' + p); continue; }
    if (stated === h) ok++;
    else { mismatch++; if (problems.length < 10) problems.push('MISMATCH ' + p + ' stated=' + stated.slice(0, 12) + ' actual=' + h.slice(0, 12)); }
  }
}
walk(header, '');
fs.closeSync(fd);
console.log('archive   :', asarPath, fs.statSync(asarPath).size, 'bytes');
console.log('entries   : files=' + files + ' dirs=' + dirs + ' contentBytes=' + bytes);
console.log('integrity : ok=' + ok + ' mismatch=' + mismatch + ' noHash=' + noIntegrity);
console.log('skipped   : unpacked=' + unpacked + ' badOffset=' + noOffset);
if (problems.length) console.log('problems  :\n  ' + problems.join('\n  '));
console.log('result    :', mismatch === 0 ? 'ALL MATCH' : 'FAILED');
process.exit(mismatch === 0 ? 0 : 1);
