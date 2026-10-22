// 流式解压：支持 zstd 多帧拼接
const fs = require('fs');
const zlib = require('zlib');
const [src, dst] = process.argv.slice(2);
const input = fs.createReadStream(src);
const output = fs.createWriteStream(dst);
const dec = zlib.createZstdDecompress();
input.pipe(dec).pipe(output);
output.on('finish', () => {
  console.log('out_bytes=' + fs.statSync(dst).size + ' src_bytes=' + fs.statSync(src).size);
});
dec.on('error', (e) => { console.error('DEC_ERR ' + e.message); process.exit(2); });
