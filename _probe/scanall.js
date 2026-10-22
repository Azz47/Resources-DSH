// 扫描所有 DSH session 转录，搜索关键词，输出用户消息命中片段
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const root = process.argv[2];
const kws = process.argv.slice(3);

function decompressFrames(buf) {
  const pos = [];
  for (let i = 0; i + 4 <= buf.length; i++) {
    if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) pos.push(i);
  }
  const chunks = [];
  for (let k = 0; k < pos.length; k++) {
    const start = pos[k];
    const end = (k + 1 < pos.length) ? pos[k + 1] : buf.length;
    try { chunks.push(zlib.zstdDecompressSync(buf.subarray(start, end))); } catch (e) { /* skip */ }
  }
  return Buffer.concat(chunks).toString('utf8');
}

const dirs = fs.readdirSync(root, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);
for (const d of dirs) {
  const f = path.join(root, d, 'session.v4.jsonl.zstd');
  if (!fs.existsSync(f)) continue;
  let text;
  try { text = decompressFrames(fs.readFileSync(f)); } catch (e) { console.log('SKIP ' + d + ' ' + e.message); continue; }
  const lines = text.split('\n').filter(Boolean);
  let printed = 0;
  for (const line of lines) {
    if (!line.includes('"user/message"')) continue;
    let rec; try { rec = JSON.parse(line); } catch (e) { continue; }
    const content = JSON.stringify(rec.data || {});
    // 只关心真正来自用户的消息（source.kind === 'user'）
    const kind = (rec.data && rec.data.source && rec.data.source.kind) || '';
    const isUser = kind === 'user' || kind === 'plugin:@michengai/dsh-pua/runtime';
    if (!isUser) continue;
    for (const kw of kws) {
      let p = content.indexOf(kw);
      if (p >= 0) {
        const seg = content.slice(Math.max(0, p - 200), p + 400).replace(/\\n/g, ' ').replace(/\\"/g, '"').replace(/\s+/g, ' ');
        console.log('=== [' + d.slice(0, 8) + ' ' + new Date(rec.time).toISOString().slice(0, 16) + '] kw=' + kw);
        console.log('    ' + seg);
        printed++;
        break;
      }
    }
    if (printed >= 8) break;
  }
}
console.log('DONE');
