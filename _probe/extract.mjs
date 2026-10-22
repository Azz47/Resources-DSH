import fs from 'node:fs';

const lines = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean);
const want = (process.argv[3] || 'user,deliv').split(',');
const out = [];

const txt = (content) => {
  if (typeof content === 'string') return content;
  if (!Array.isArray(content)) return '';
  return content.map((c) => (typeof c === 'string' ? c : c?.type === 'text' ? c.text || '' : c?.type === 'tool_use' ? '[tool:' + c.name + ']' : '')).join('\n');
};

for (const l of lines) {
  let r; try { r = JSON.parse(l); } catch { continue; }
  const t = r.type;
  const ts = Number.isFinite(r.time) ? new Date(r.time).toISOString().replace('T', ' ').slice(0, 19) : 'seq' + r.seq;
  if (want.includes('user') && t === 'user/message') {
    const kind = r.data?.source?.kind;
    if (kind === 'runtime-context') continue;
    out.push(`[${ts}] USER(${kind || '?'}): ${txt(r.data.content).replace(/\s+/g, ' ').slice(0, 500)}`);
  }
  if (want.includes('deliv') && (t === 'deliverables/presented' || t === 'workspace/changes')) {
    out.push(`[${ts}] ${t}: ${JSON.stringify(r.data).slice(0, 800)}`);
  }
  if (want.includes('asst') && t === 'assistant/message') {
    const s = txt(r.data?.content).replace(/\s+/g, ' ');
    if (s.length > 60) out.push(`[${ts}] ASST: ${s.slice(0, Number(process.argv[4] || 400))}`);
  }
  if (want.includes('tool') && t === 'tool/call') {
    const s = JSON.stringify(r.data).slice(0, Number(process.argv[4] || 300));
    out.push(`[${ts}] TOOL: ${s}`);
  }
}
fs.writeFileSync(process.argv[5] || 'D:/Resources/DSH/_probe/_out.txt', out.join('\n'), 'utf8');
console.log('lines', out.length);
