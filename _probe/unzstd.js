// 解压 DSH session 的 zstd jsonl 转录，输出到指定文件
const fs = require('fs');
const zlib = require('zlib');
const [src, dst] = process.argv.slice(2);
const buf = fs.readFileSync(src);
const out = zlib.zstdDecompressSync(buf);
fs.writeFileSync(dst, out);
console.log('src_bytes=' + buf.length + ' out_bytes=' + out.length);
