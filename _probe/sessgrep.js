// 在 session 转录中搜索关键词，输出命中记录的上下文片段
const fs = require('fs');
const src = process.argv[2];
const kws = process.argv.slice(3);
const lines = fs.readFileSync(src, 'utf8').split('\n').filter(Boolean);
let hits = 0;
lines.forEach((line, idx) => {
  let rec;
  try { rec = JSON.parse(line); } catch (e) { return; }
  const t = rec.type || '';
  if (!/user\/message|assistant\/message|command\/run|deliverables|compaction/.test(t)) return;
  const low = line;
  for (const kw of kws) {
    let from = 0;
    while (true) {
      const p = low.indexOf(kw, from);
      if (p < 0) break;
      const seg = low.slice(Math.max(0, p - 220), p + 320).replace(/\\n/g, ' ').replace(/\s+/g, ' ');
      console.log('[' + t + ' #' + idx + ' @' + p + ' kw=' + kw + '] ...' + seg + '...');
      hits++;
      from = p + kw.length;
      if (hits > 400) process.exit(0);
    }
  }
});
console.log('total hits: ' + hits);
