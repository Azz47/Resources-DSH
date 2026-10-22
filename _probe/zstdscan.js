const fs = require('fs');
const src = process.argv[2];
const buf = fs.readFileSync(src);
console.log('size', buf.length);
// 找 zstd magic: 28 B5 2F FD ; skippable: 50 2A 4D 18 + 4字节大小
const hits = [];
for (let i = 0; i + 4 <= buf.length; i++) {
  if (buf[i] === 0x28 && buf[i+1] === 0xb5 && buf[i+2] === 0x2f && buf[i+3] === 0xfd) hits.push(['ZSTD', i]);
  if (buf[i] === 0x50 && buf[i+1] === 0x2a && buf[i+2] === 0x4d && buf[i+3] === 0x18) hits.push(['SKIP', i]);
}
console.log('magic hits:', hits.length);
console.log(hits.slice(0, 20).map(h => h.join('@')).join(' '));
console.log('head hex:', buf.subarray(0, 16).toString('hex'));
