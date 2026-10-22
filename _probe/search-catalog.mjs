import fs from 'node:fs';
import path from 'node:path';

const root = 'D:/Resources/DSH/_probe/catalogs';
const patterns = process.argv.slice(2).map((p) => new RegExp(p, 'i'));

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (/\.(json|js|md)$/.test(e.name) && !/package-lock/.test(e.name)) out.push(p);
  }
  return out;
}

const seen = new Set();
for (const file of walk(root)) {
  let text;
  try { text = fs.readFileSync(file, 'utf8'); } catch { continue; }
  if (text.length > 40_000_000) continue;
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.length > 4000) {
      // minified JSON: extract object-ish chunks around matches
      for (const re of patterns) {
        const m = line.match(re);
        if (m) {
          const idx = line.search(re);
          const chunk = line.slice(Math.max(0, idx - 260), idx + 320);
          const key = path.basename(file) + '|' + chunk;
          if (!seen.has(key)) { seen.add(key); console.log(`[${path.basename(file)}] ...${chunk}...`); }
        }
      }
      continue;
    }
    if (patterns.some((re) => re.test(line))) {
      const key = path.basename(file) + '|' + i;
      if (!seen.has(key)) { seen.add(key); console.log(`[${path.basename(file)}:${i + 1}] ${line.trim().slice(0, 400)}`); }
    }
  }
}
