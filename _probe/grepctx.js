// Usage: node grepctx.js <file> <regex> [ctxChars=120] [maxHits=20]
const fs = require('fs');
const [, , file, pattern, ctxArg, maxArg] = process.argv;
const ctx = Number(ctxArg || 120);
const max = Number(maxArg || 20);
const text = fs.readFileSync(file, 'utf8');
let re;
try { re = new RegExp(pattern, 'g'); } catch (e) { console.error('bad regex: ' + e.message); process.exit(2); }
let m, n = 0;
while ((m = re.exec(text)) !== null) {
  if (n >= max) break;
  const a = Math.max(0, m.index - ctx), b = Math.min(text.length, m.index + m[0].length + ctx);
  console.log('#' + (n + 1) + ' @' + m.index + '  ...' + text.slice(a, b).replace(/\s+/g, ' ') + '...');
  n++;
  if (m.index === re.lastIndex) re.lastIndex++;
}
console.log('hits shown: ' + n + ' / file ' + text.length + ' chars');
