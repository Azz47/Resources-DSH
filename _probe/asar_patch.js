// Surgical, size-preserving patch of one file inside an asar archive.
//   node asar_patch.js <asar> <innerPath> --info
//   node asar_patch.js <asar> <innerPath> <edits.json> [--apply]
// edits.json = [{ "search": "...", "replace": "..." }]  (each search must occur exactly once)
// The replacement may be shorter or longer; the result is padded with spaces to the original
// byte length, so every offset in the archive stays valid. The entry's embedded SHA256
// integrity (hash + blocks[0]) is rewritten to match the new content.
const fs = require('fs');
const crypto = require('crypto');

const asarPath = process.argv[2];
const innerPath = process.argv[3];
const argA = process.argv[4];
const apply = process.argv.includes('--apply');

function readHeader(fd) {
  const probe = Buffer.alloc(64);
  fs.readSync(fd, probe, 0, 64, 0);
  const size = probe.readUInt32LE(4);
  if (!(size > 0 && size < 64 * 1024 * 1024)) throw new Error('implausible header size: ' + size);
  const buf = Buffer.alloc(size);
  fs.readSync(fd, buf, 0, size, 8);
  const start = buf.indexOf(0x7b);
  if (start < 0) throw new Error('no JSON object in header');
  let depth = 0, inStr = false, esc = false, end = -1;
  for (let i = start; i < buf.length; i++) {
    const c = buf[i];
    if (inStr) { if (esc) esc = false; else if (c === 0x5c) esc = true; else if (c === 0x22) inStr = false; continue; }
    if (c === 0x22) inStr = true;
    else if (c === 0x7b) depth++;
    else if (c === 0x7d) { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  if (end < 0) throw new Error('unterminated header JSON');
  return { jsonStart: 8 + start, jsonEnd: 8 + end, header: JSON.parse(buf.slice(start, end).toString('utf8')), dataOffset: 8 + size };
}

function findEntry(header, p) {
  let node = header;
  for (const part of p.split('/')) {
    if (!node.files || !node.files[part]) return null;
    node = node.files[part];
  }
  return node;
}

const fd = fs.openSync(asarPath, 'r+');
const res = readHeader(fd);
const entry = findEntry(res.header, innerPath);
if (!entry) { console.error('entry not found: ' + innerPath); process.exit(3); }
const size = Number(entry.size);
const offset = Number(entry.offset);
const abs = res.dataOffset + offset;
const original = Buffer.alloc(size);
fs.readSync(fd, original, 0, size, abs);
const oldHash = crypto.createHash('sha256').update(original).digest('hex');
const statedHash = entry.integrity && entry.integrity.hash;

console.log('entry      :', innerPath);
console.log('size       :', size, '| offset(rel):', offset, '| abs:', abs);
console.log('stated hash:', statedHash);
console.log('actual hash:', oldHash, statedHash === oldHash ? '(MATCH)' : '(MISMATCH)');
console.log('blocks     :', JSON.stringify(entry.integrity && entry.integrity.blocks));

if (argA === '--info' || argA === undefined) { fs.closeSync(fd); process.exit(statedHash === oldHash ? 0 : 4); }

const edits = JSON.parse(fs.readFileSync(argA, 'utf8'));
let text = original.toString('utf8');
for (const e of edits) {
  const first = text.indexOf(e.search);
  if (first < 0) { console.error('search not found: ' + e.search); process.exit(5); }
  if (text.indexOf(e.search, first + 1) >= 0) { console.error('search not unique: ' + e.search); process.exit(5); }
  text = text.slice(0, first) + e.replace + text.slice(first + e.search.length);
  console.log('edit       : replaced 1 occurrence (' + e.search.length + ' -> ' + e.replace.length + ' chars)');
}
let newBuf = Buffer.from(text, 'utf8');
if (newBuf.length > size) { console.error('patched content is LONGER than the original slot'); process.exit(6); }
const pad = size - newBuf.length;
if (pad > 0) newBuf = Buffer.concat([newBuf, Buffer.alloc(pad, 0x20)]);
if (newBuf.length !== size) { console.error('padding failed'); process.exit(6); }
const newHash = crypto.createHash('sha256').update(newBuf).digest('hex');
console.log('new hash   :', newHash, '| padding:', pad, 'bytes');
console.log('mode       :', apply ? 'APPLY' : 'DRY-RUN (pass --apply to write)');
if (!apply) { fs.closeSync(fd); process.exit(0); }
if (statedHash && statedHash !== oldHash) { console.error('refusing to patch: header integrity does not match current content'); process.exit(7); }

// Locate the header's integrity strings for this entry: anchor on its unique offset value.
const hdrLen = res.jsonEnd - res.jsonStart;
const hdr = Buffer.alloc(hdrLen);
fs.readSync(fd, hdr, 0, hdrLen, res.jsonStart);
const anchor = Buffer.from('"offset":"' + offset + '"', 'utf8');
let at = hdr.indexOf(anchor);
if (at < 0 || hdr.indexOf(anchor, at + 1) >= 0) { console.error('offset anchor not unique in header'); process.exit(8); }
const hashKey = Buffer.from('"hash":"', 'utf8');
const hashPos = hdr.indexOf(hashKey, at);
if (hashPos < 0) { console.error('no "hash" after anchor'); process.exit(8); }
const hashStrPos = hashPos + hashKey.length;
if (hdr.slice(hashStrPos, hashStrPos + 64).toString('utf8') !== statedHash) { console.error('hash slot mismatch'); process.exit(8); }
const blockKey = Buffer.from('"blocks":["', 'utf8');
const blockPos = hdr.indexOf(blockKey, hashPos);
if (blockPos < 0) { console.error('no blocks array after hash'); process.exit(8); }
const blockStrPos = blockPos + blockKey.length;
if (hdr.slice(blockStrPos, blockStrPos + 64).toString('utf8') !== statedHash) { console.error('blocks[0] slot mismatch'); process.exit(8); }

// 1. content, 2. header hashes (same byte length, offsets untouched)
fs.writeSync(fd, newBuf, 0, newBuf.length, abs);
const hv = Buffer.from(newHash, 'utf8');
fs.writeSync(fd, hv, 0, hv.length, res.jsonStart + hashStrPos);
fs.writeSync(fd, hv, 0, hv.length, res.jsonStart + blockStrPos);
fs.fsyncSync(fd);
fs.closeSync(fd);

// Verify by re-reading the archive from scratch.
const fd2 = fs.openSync(asarPath, 'r');
const res2 = readHeader(fd2);
const e2 = findEntry(res2.header, innerPath);
const check = Buffer.alloc(Number(e2.size));
fs.readSync(fd2, check, 0, check.length, res2.dataOffset + Number(e2.offset));
const finalHash = crypto.createHash('sha256').update(check).digest('hex');
console.log('verify     : size=' + Number(e2.size) + ' statedHash=' + e2.integrity.hash + ' actualHash=' + finalHash);
console.log('verify     : ' + (finalHash === newHash && e2.integrity.hash === newHash ? 'OK' : 'FAILED'));
fs.closeSync(fd2);
