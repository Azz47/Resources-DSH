import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2];
const walk = (d, o = []) => {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p, o);
    else if (/\.(js|mjs|cjs)$/.test(e.name)) o.push(p);
  }
  return o;
};

const files = walk(root);
const imports = new Map();
for (const f of files) {
  const t = fs.readFileSync(f, 'utf8');
  for (const m of t.matchAll(/(?:from|require\()\s*["']([^"']+)["']/g)) {
    const spec = m[1];
    if (!spec.startsWith('@deepseek-ai/')) continue;
    if (!imports.has(spec)) imports.set(spec, new Set());
    imports.get(spec).add(path.relative(root, f));
  }
}
console.log(`scanned ${files.length} files under ${root}`);
console.log('DSH host packages imported at runtime:');
for (const [spec, where] of [...imports].sort()) {
  console.log(`  ${spec}   <- ${[...where].slice(0, 4).join(', ')}`);
}
