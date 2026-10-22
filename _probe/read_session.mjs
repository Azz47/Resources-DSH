import fs from 'node:fs';
import zlib from 'node:zlib';

const src = process.argv[2];
const mode = process.argv[3] || 'user';
const limit = Number(process.argv[4] || 40);

const raw = fs.readFileSync(src);
const text = zlib.zstdDecompressSync(raw).toString('utf8');
const lines = text.split('\n').filter(Boolean);

const out = [];
for (const line of lines) {
  let rec;
  try { rec = JSON.parse(line); } catch { continue; }
  const role = rec.role || rec.type || rec?.message?.role;
  const m = rec.message || rec;
  let content = m?.content ?? rec?.content;
  let txt = '';
  if (typeof content === 'string') txt = content;
  else if (Array.isArray(content)) {
    txt = content.map((c) => {
      if (typeof c === 'string') return c;
      if (c?.type === 'text') return c.text || '';
      if (c?.type === 'tool_use') return `[tool:${c.name}]`;
      if (c?.type === 'tool_result') return '[tool_result]';
      return '';
    }).join('\n');
  }
  if (!txt.trim()) continue;
  out.push({ role: (role || '?'), text: txt });
}

const users = out.filter((r) => r.role === 'user' && !/^\[tool/.test(r.text));
const assistants = out.filter((r) => r.role === 'assistant');

let picked;
if (mode === 'user') picked = users;
else if (mode === 'assistant') picked = assistants.slice(-limit);
else if (mode === 'grep') picked = out.filter((r) => r.text.includes(limit > 0 && false ? '' : String(process.argv[4])));

const res = picked.map((r, i) => {
  const t = r.text.replace(/\s+/g, ' ').trim();
  return `--- [${i}] ${r.role} len=${r.text.length} ---\n${t.length > limit ? t.slice(0, limit) : t}`;
}).join('\n');
fs.writeFileSync(process.argv[5] || 'D:/Resources/DSH/_probe/_session_dump.txt', `records=${out.length} users=${users.length} assistants=${assistants.length}\n${res}`, 'utf8');
console.log(`records=${out.length} users=${users.length} assistants=${assistants.length}`);
