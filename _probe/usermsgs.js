// 提取 session 转录里的用户消息文本
const fs = require('fs');
const src = process.argv[2];
const mode = process.argv[3] || 'list';
const lines = fs.readFileSync(src, 'utf8').split('\n').filter(Boolean);
const out = [];
lines.forEach((line, idx) => {
  let rec;
  try { rec = JSON.parse(line); } catch (e) { return; }
  if (rec.type !== 'user/message') return;
  let text = '';
  if (typeof rec.text === 'string') text = rec.text;
  else if (rec.content) text = typeof rec.content === 'string' ? rec.content : JSON.stringify(rec.content);
  else if (rec.message) text = typeof rec.message === 'string' ? rec.message : JSON.stringify(rec.message);
  else text = JSON.stringify(rec);
  out.push({ idx, len: text.length, text });
});
if (mode === 'list') {
  console.log('user messages: ' + out.length);
  out.forEach(u => console.log('#' + u.idx + ' len=' + u.len + ' :: ' + u.text.slice(0, 160).replace(/\s+/g, ' ')));
} else {
  const k = parseInt(mode, 10);
  const u = out[k];
  if (!u) { console.log('no message at index ' + k + ' (have ' + out.length + ')'); process.exit(1); }
  console.log('=== user message #' + u.idx + ' (ordinal ' + k + ', len ' + u.len + ') ===');
  console.log(u.text);
}
