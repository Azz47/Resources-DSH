// 按行号提取某条记录的完整文本
const fs = require('fs');
const src = process.argv[2];
const idx = parseInt(process.argv[3], 10);
const lines = fs.readFileSync(src, 'utf8').split('\n');
const line = lines[idx];
if (!line) { console.log('no line ' + idx + ' (total ' + lines.length + ')'); process.exit(1); }
const rec = JSON.parse(line);
console.log('type=' + rec.type + ' seq=' + rec.seq + ' time=' + new Date(rec.time).toISOString());
const d = rec.data || {};
const collect = (v, out) => {
  if (typeof v === 'string') out.push(v);
  else if (Array.isArray(v)) v.forEach(x => collect(x, out));
  else if (v && typeof v === 'object') {
    if (typeof v.text === 'string') out.push(v.text);
    else Object.values(v).forEach(x => collect(x, out));
  }
};
const out = [];
collect(d.content || d.message || d, out);
console.log(out.join('\n---\n'));
