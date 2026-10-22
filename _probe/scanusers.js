// 列出每个 session 的真实用户消息（source.kind=user），输出预览
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const root = process.argv[2];
const maxLen = parseInt(process.argv[3] || '260', 10);

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
const rows = [];
for (const d of dirs) {
  const f = path.join(root, d, 'session.v4.jsonl.zstd');
  if (!fs.existsSync(f)) continue;
  let text;
  try { text = decompressFrames(fs.readFileSync(f)); } catch (e) { continue; }
  const lines = text.split('\n').filter(Boolean);
  let first = null, last = null, n = 0;
  const msgs = [];
  for (const line of lines) {
    if (!line.includes('"user/message"')) continue;
    let rec; try { rec = JSON.parse(line); } catch (e) { continue; }
    const d2 = rec.data || {};
    const kind = (d2.source && d2.source.kind) || '';
    if (kind !== 'user') continue;
    let txt = '';
    const c = d2.content;
    if (Array.isArray(c)) txt = c.map(x => x.text || '').join(' ');
    else if (typeof c === 'string') txt = c;
    txt = txt.replace(/\s+/g, ' ').trim();
    if (!txt || /^Time sampled|^Current runtime context|^<system-reminder>/.test(txt)) continue;
    if (!first) first = rec.time;
    last = rec.time;
    n++;
    msgs.push(txt);
  }
  if (!n) continue;
  rows.push({ d, first, last, n, msgs });
}
rows.sort((a, b) => a.first - b.first);
for (const r of rows) {
  console.log('\n######## ' + r.d + '  first=' + new Date(r.first).toISOString() + ' last=' + new Date(r.last).toISOString() + ' userMsgs=' + r.n);
  r.msgs.slice(0, 12).forEach((m, i) => console.log('  (' + i + ') ' + m.slice(0, maxLen)));
  if (r.msgs.length > 12) console.log('  ... +' + (r.msgs.length - 12) + ' more');
}
