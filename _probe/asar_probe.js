// Probe the DSH app.asar archive without any external dependency.
//   node asar_probe.js list <asar> <needle> [limit]
//   node asar_probe.js extract <asar> <needle> <outDir>
// The asar header is a chromium Pickle: [u32 payloadSize][u32 headerSize] then the
// header Pickle holding a length-prefixed JSON string, then the data section.
const fs = require('fs');
const path = require('path');

const mode = process.argv[2];
const asarPath = process.argv[3];
const needle = (process.argv[4] || '').toLowerCase();
const arg5 = process.argv[5];

function readHeader(fd) {
  const probe = Buffer.alloc(64);
  fs.readSync(fd, probe, 0, 64, 0);
  const size = probe.readUInt32LE(4);
  if (!(size > 0 && size < 64 * 1024 * 1024)) throw new Error('implausible header size: ' + size);
  const buf = Buffer.alloc(size);
  fs.readSync(fd, buf, 0, size, 8);
  const start = buf.indexOf(0x7b); // '{'
  if (start < 0) throw new Error('no JSON object in header pickle');
  let depth = 0, inStr = false, esc = false, end = -1;
  for (let i = start; i < buf.length; i++) {
    const c = buf[i];
    if (inStr) {
      if (esc) esc = false;
      else if (c === 0x5c) esc = true;
      else if (c === 0x22) inStr = false;
      continue;
    }
    if (c === 0x22) inStr = true;
    else if (c === 0x7b) depth++;
    else if (c === 0x7d) { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  if (end < 0) throw new Error('unterminated header JSON');
  return { header: JSON.parse(buf.slice(start, end).toString('utf8')), dataOffset: 8 + size };
}

function walk(node, prefix, out) {
  for (const [name, child] of Object.entries(node.files || {})) {
    const full = prefix ? prefix + '/' + name : name;
    if (child.files) walk(child, full, out);
    else out.push({ path: full, size: Number(child.size || 0), offset: Number(child.offset || 0) });
  }
}

const fd = fs.openSync(asarPath, 'r');
let res;
try { res = readHeader(fd); } finally { /* keep fd for extract */ }
const files = [];
walk(res.header, '', files);

if (mode === 'list') {
  const limit = Number(arg5 || 200);
  const hits = files.filter(f => f.path.toLowerCase().includes(needle)).slice(0, limit);
  console.log('total entries: ' + files.length);
  for (const h of hits) console.log(String(h.size).padStart(10) + '  ' + h.path);
  fs.closeSync(fd);
  process.exit(0);
}

if (mode === 'extract') {
  const outDir = arg5;
  const base = res.dataOffset;
  const hits = files.filter(f => f.path.toLowerCase().includes(needle));
  const buf = Buffer.alloc(4 * 1024 * 1024);
  for (const h of hits) {
    const dest = path.join(outDir, h.path);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    const wfd = fs.openSync(dest, 'w');
    let left = h.size, pos = base + h.offset;
    while (left > 0) {
      const n = fs.readSync(fd, buf, 0, Math.min(buf.length, left), pos);
      if (n <= 0) break;
      fs.writeSync(wfd, buf, 0, n);
      left -= n; pos += n;
    }
    fs.closeSync(wfd);
    console.log(String(h.size).padStart(10) + '  ' + h.path);
  }
  console.log('extracted ' + hits.length + ' file(s) to ' + outDir);
  fs.closeSync(fd);
  process.exit(0);
}

if (mode === 'grep') {
  // Scan entry contents for a plain string; prints path, hit count and first snippet.
  const maxHits = Number(arg5 || 10);
  const base = res.dataOffset;
  const chunk = Buffer.alloc(4 * 1024 * 1024);
  const needleBuf = Buffer.from(needle, 'utf8');
  let found = 0;
  for (const h of files) {
    if (found >= maxHits) break;
    if (h.size < 64 || h.size > 40 * 1024 * 1024) continue;
    let buf = Buffer.alloc(h.size), got = 0, pos = base + h.offset;
    while (got < h.size) {
      const n = fs.readSync(fd, buf, got, Math.min(chunk.length, h.size - got), pos + got);
      if (n <= 0) break;
      got += n;
    }
    buf = buf.slice(0, got);
    let count = 0, firstAt = -1, i = buf.indexOf(needleBuf);
    while (i >= 0) { count++; if (firstAt < 0) firstAt = i; i = buf.indexOf(needleBuf, i + 1); }
    if (count > 0) {
      found++;
      const snip = buf.slice(Math.max(0, firstAt - 120), firstAt + 160).toString('utf8').replace(/[\r\n]+/g, ' ');
      console.log('--- ' + h.path + '  (hits: ' + count + ')');
      console.log('    ' + snip);
    }
  }
  console.log('scanned ' + files.length + ' entries, matched ' + found + ' file(s)');
  fs.closeSync(fd);
  process.exit(0);
}

console.error('usage: node asar_probe.js list|extract|grep <asar> <needle> [limit|outDir|maxHits]');
fs.closeSync(fd);
process.exit(2);
