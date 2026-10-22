import fs from 'node:fs';
import path from 'node:path';

const [file, innerPath, outPath] = process.argv.slice(2);

const fd = fs.openSync(file, 'r');
const head = Buffer.alloc(16);
fs.readSync(fd, head, 0, 16, 0);
const pickleSize = head.readUInt32LE(4);
const jsonSize = head.readUInt32LE(12);
const jsonBuf = Buffer.alloc(jsonSize);
fs.readSync(fd, jsonBuf, 0, jsonSize, 16);
const header = JSON.parse(jsonBuf.toString('utf8'));
const dataStart = 8 + pickleSize;

function resolve(node, p) {
  let cur = node;
  for (const part of p.split('/').filter(Boolean)) {
    if (!cur.files || !cur.files[part]) return null;
    cur = cur.files[part];
  }
  return cur;
}

const target = resolve(header, innerPath);
if (!target) { console.error('NOT FOUND ' + innerPath); process.exit(2); }

let count = 0;
function materialize(n, dest) {
  if (n.files) {
    fs.mkdirSync(dest, { recursive: true });
    for (const [name, child] of Object.entries(n.files)) materialize(child, path.join(dest, name));
    return;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  const size = Number(n.size) || 0;
  const buf = Buffer.alloc(size);
  if (size) fs.readSync(fd, buf, 0, size, dataStart + Number(n.offset));
  fs.writeFileSync(dest, buf);
  count++;
}
materialize(target, outPath);
fs.closeSync(fd);
console.log(`extracted ${count} file(s) -> ${outPath}`);
