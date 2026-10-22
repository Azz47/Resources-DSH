// 汇总 session 转录：列出所有 user 消息（截断预览）与记录类型统计
const fs = require('fs');
const src = process.argv[2];
const lines = fs.readFileSync(src, 'utf8').split('\n').filter(Boolean);
const types = {};
const users = [];
lines.forEach((line, idx) => {
  let rec;
  try { rec = JSON.parse(line); } catch (e) { types['PARSE_FAIL'] = (types['PARSE_FAIL'] || 0) + 1; return; }
  const t = rec.type || 'unknown';
  types[t] = (types[t] || 0) + 1;
  if (t === 'user' || t === 'message' || t === 'human') {
    // 尽力提取文本
    let text = '';
    if (typeof rec.text === 'string') text = rec.text;
    else if (rec.message && typeof rec.message === 'string') text = rec.message;
    else if (rec.message && rec.message.content) text = JSON.stringify(rec.message.content);
    else if (rec.content) text = typeof rec.content === 'string' ? rec.content : JSON.stringify(rec.content);
    else text = JSON.stringify(rec).slice(0, 400);
    const role = (rec.role || (rec.message && rec.message.role) || t);
    users.push({ idx, role, len: text.length, preview: text.slice(0, 120).replace(/\s+/g, ' ') });
  }
});
console.log('types: ' + JSON.stringify(types));
console.log('total lines: ' + lines.length);
console.log('--- user-ish records: ' + users.length + ' ---');
users.forEach(u => console.log('#' + u.idx + ' [' + u.role + '] len=' + u.len + ' :: ' + u.preview));
