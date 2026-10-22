const fs = require('fs');
const path = require('path');

let yaml;
try {
  yaml = require('C:/Users/Administrator/.dsh/profiles/desktop/node_modules/js-yaml');
} catch (e) {
  console.error('js-yaml not available: ' + e.message);
  process.exit(1);
}

const roots = [
  { source: 'user', dir: 'C:/Users/Administrator/.dsh/skills' },
  { source: 'runtime', dir: 'D:/tools/dsh/resources/runtime/office-skills' }
];

// Plugin-provided skills: scan each top-level package for SKILL.md files.
const nm = 'C:/Users/Administrator/.dsh/profiles/desktop/node_modules';
function listPackageDirs() {
  const out = [];
  for (const entry of fs.readdirSync(nm, { withFileTypes: true })) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue;
    if (entry.name.startsWith('.')) continue;
    const full = path.join(nm, entry.name);
    if (entry.name.startsWith('@')) {
      let subs = [];
      try { subs = fs.readdirSync(full, { withFileTypes: true }); } catch { continue; }
      for (const s of subs) {
        if (s.isDirectory() || s.isSymbolicLink()) out.push(path.join(full, s.name));
      }
    } else {
      out.push(full);
    }
  }
  return out;
}

function walk(dir, depth, acc) {
  if (depth > 5) return;
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
  for (const e of entries) {
    if (e.name === 'node_modules' || e.name === '.git') continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full, depth + 1, acc);
    else if (e.isFile() && e.name === 'SKILL.md') acc.push(full);
  }
}

for (const pkg of listPackageDirs()) {
  const acc = [];
  walk(pkg, 0, acc);
  for (const f of acc) roots.push({ source: 'plugin', dir: path.dirname(f), file: f });
}

function parseFrontmatter(text) {
  const clean = text.replace(/^\uFEFF/, '');
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(clean);
  if (!m) return { error: '缺少 frontmatter（首行必须是 ---）' };
  let data;
  try { data = yaml.load(m[1]); } catch (e) { return { error: 'YAML 解析失败: ' + String(e.message).split('\n')[0] }; }
  if (data === null || typeof data !== 'object' || Array.isArray(data)) return { error: 'frontmatter 不是对象' };
  return { data, body: clean.slice(m[0].length) };
}

const rows = [];
for (const root of roots) {
  let files = [];
  if (root.file) files = [root.file];
  else {
    if (!fs.existsSync(root.dir)) continue;
    for (const e of fs.readdirSync(root.dir, { withFileTypes: true })) {
      if (!e.isDirectory()) continue;
      const f = path.join(root.dir, e.name, 'SKILL.md');
      if (fs.existsSync(f)) files.push(f);
    }
  }
  for (const file of files) {
    const dir = path.dirname(file);
    const dirName = path.basename(dir);
    const row = { source: root.source, file, dirName, name: '', descriptionLen: 0, issues: [], notes: [] };
    let text = '';
    try { text = fs.readFileSync(file, 'utf8'); } catch (e) { row.issues.push('读取失败: ' + e.message); rows.push(row); continue; }
    if (text.includes('\uFFFD')) row.issues.push('包含 U+FFFD 替换字符（编码损坏）');
    if (text.trim().length < 20) row.issues.push('内容过短');
    if (text.length > 1024 * 1024) row.notes.push('文件超过 1MB');
    const parsed = parseFrontmatter(text);
    if (parsed.error) { row.issues.push(parsed.error); rows.push(row); continue; }
    const fm = parsed.data;
    row.name = typeof fm.name === 'string' ? fm.name.trim() : '';
    const desc = typeof fm.description === 'string' ? fm.description.trim() : '';
    row.descriptionLen = desc.length;
    if (!row.name) row.issues.push('name 缺失或不是字符串');
    if (!desc) row.issues.push('description 缺失或不是字符串');
    if (row.name && row.name.length > 64) row.issues.push('name 超过 64 字符');
    if (desc.length > 1024) row.issues.push('description 超过 1024 字符');
    if (Object.prototype.hasOwnProperty.call(fm, 'allowed-tools')) {
      const at = fm['allowed-tools'];
      if (typeof at !== 'string' && !(Array.isArray(at) && at.every(x => typeof x === 'string'))) {
        row.issues.push('allowed-tools 类型不是字符串或字符串数组');
      }
    }
    if (row.name && row.name !== dirName) {
      if (/^[\x20-\x7E]+$/.test(row.name)) row.notes.push('name 与目录名不同');
      else row.notes.push('name 非 ASCII，目录名回退为 ' + dirName);
    }
    if (parsed.body && parsed.body.trim().length < 20) row.issues.push('frontmatter 后正文过短');
    rows.push(row);
  }
}

// Duplicate names across all scanned skills.
const seen = new Map();
for (const r of rows) {
  if (!r.name) continue;
  const key = r.name.toLowerCase();
  if (!seen.has(key)) seen.set(key, []);
  seen.get(key).push(r);
}
for (const [key, list] of seen) {
  if (list.length > 1) {
    const where = list.map(r => r.source + ':' + r.dirName).join(', ');
    for (const r of list) r.issues.push('name 重复: ' + where);
  }
}

const bad = rows.filter(r => r.issues.length);
const summary = {
  scanned: rows.length,
  bySource: rows.reduce((a, r) => { a[r.source] = (a[r.source] || 0) + 1; return a; }, {}),
  withIssues: bad.length,
  ok: rows.length - bad.length
};
console.log(JSON.stringify(summary, null, 2));
for (const r of bad) {
  console.log('BAD [' + r.source + '] ' + r.dirName + ' -> ' + (r.name || '(no name)'));
  for (const i of r.issues) console.log('  x ' + i);
}
const notes = rows.filter(r => !r.issues.length && r.notes.length);
console.log('notes (no issues, ' + notes.length + '):');
for (const r of notes.slice(0, 60)) console.log('  ~ [' + r.source + '] ' + r.dirName + ' -> ' + r.name + ' | ' + r.notes.join('; '));
fs.writeFileSync('D:/Resources/DSH/_probe/skill_compat_20261019_1950.json', JSON.stringify({ summary, rows }, null, 2), 'utf8');
