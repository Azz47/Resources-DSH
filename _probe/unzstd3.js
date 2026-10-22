// 逐帧解压 DSH session 的 zstd 拼接文件（每帧一条 jsonl 记录）
const fs = require('fs');
const zlib = require('zlib');
const [src, dst] = process.argv.slice(2);
const buf = fs.readFileSync(src);
const magic = Buffer.from([0x28, 0xb5, 0x2f, 0xfd]);
const pos = [];
for (let i = 0; i + 4 <= buf.length; i++) {
  if (buf[i] === 0x28 && buf[i+1] === 0xb5 && buf[i+2] === 0x2f && buf[i+3] === 0xfd) pos.push(i);
}
const chunks = [];
let ok = 0, fail = 0;
const failAt = [];
for (let k = 0; k < pos.length; k++) {
  const start = pos[k];
  const end = (k + 1 < pos.length) ? pos[k + 1] : buf.length;
  try {
    const out = zlib.zstdDecompressSync(buf.subarray(start, end));
    chunks.push(out);
    ok++;
  } catch (e) {
    fail++;
    if (failAt.length < 5) failAt.push(start + ':' + e.message);
  }
}
const all = Buffer.concat(chunks);
fs.writeFileSync(dst, all);
console.log('frames=' + pos.length + ' ok=' + ok + ' fail=' + fail + ' out_bytes=' + all.length);
if (failAt.length) console.log('failAt: ' + failAt.join(' | '));
