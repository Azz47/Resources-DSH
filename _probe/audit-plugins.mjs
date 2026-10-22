import fs from 'node:fs';
import path from 'node:path';

const NM = 'C:\\Users\\Administrator\\.dsh\\profiles\\desktop\\node_modules';
const pkgs = [
  'dsh-plugin-education', 'dsh-craft-your-textbook', 'dsh-ppt-studio',
  '@arcaneorion/dsh-teaching-board', 'dsh-mindmap', 'dsh-hotspots',
  'dsh-image-generation', '@tt-a1i/archify-dsh', '@michengai/dsh-skills-manager',
  'dsh-skill-mcp-manager', '@michengai/dsh-agency-agents', '@michengai/dsh-automation',
];

function walk(dir, out = [], depth = 0) {
  if (depth > 6) return out;
  let ents;
  try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of ents) {
    if (e.name === 'node_modules' || e.name === '.git') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out, depth + 1);
    else out.push(p);
  }
  return out;
}

for (const name of pkgs) {
  const dir = path.join(NM, name);
  if (!fs.existsSync(dir)) { console.log(`\n### ${name}  -- NOT INSTALLED`); continue; }
  let pkg = {};
  try { pkg = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8')); } catch {}
  console.log(`\n### ${name}@${pkg.version}`);

  const files = walk(dir);
  const jsFiles = files.filter((f) => /\.(js|mjs|cjs)$/.test(f) && !/node_modules/.test(f));

  // tool names
  const tools = new Set();
  for (const f of jsFiles) {
    let t;
    try { t = fs.readFileSync(f, 'utf8'); } catch { continue; }
    for (const m of t.matchAll(/defineTool\s*\(\s*\{[\s\S]{0,400}?name:\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]/g)) tools.add(m[1]);
    for (const m of t.matchAll(/toolName:\s*['"]([A-Za-z_][A-Za-z0-9_]*)['"]/g)) tools.add(m[1]);
  }
  console.log('  tools: ' + (tools.size ? [...tools].join(', ') : '(none found by regex)'));

  // shipped skills
  const skillFiles = files.filter((f) => path.basename(f) === 'SKILL.md');
  if (skillFiles.length) {
    for (const sf of skillFiles) {
      const rel = path.relative(dir, sf).replace(/\\/g, '/');
      let fm = '';
      try {
        const head = fs.readFileSync(sf, 'utf8').slice(0, 700);
        const nm = head.match(/^name:\s*(.+)$/m);
        const de = head.match(/^description:\s*(.+)$/m);
        fm = `${nm ? nm[1].trim() : '?'} :: ${de ? de[1].trim().slice(0, 120) : '?'}`;
      } catch {}
      console.log(`  SKILL ${rel}  ->  ${fm}`);
    }
  }
}
