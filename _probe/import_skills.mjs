// import_skills.mjs —— 用 skills-manager 自己的 importSkill 把已克隆好的仓库装进 DSH 用户技能根
// 用法:
//   node import_skills.mjs --dirs --dry <根目录>...   # 递归找出所有含 SKILL.md 的目录，逐个预演
//   node import_skills.mjs --dirs <根目录>...         # 真装（同名冲突 skip）
//   node import_skills.mjs --dry <批量源目录>...      # 走插件的 batch 语义（直接子目录）
// 说明: importSkill 目标根 = $DSH_HOME/skills（本机 C:\Users\Administrator\.dsh\skills），名称强制 kebab-case；
//       --dirs 模式刻意跳过 README.md 之类的顶层散装 .md（插件 batch 语义会把它们也当技能收进来）。
import { readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';

const CORE = 'file:///C:/Users/Administrator/.dsh/profiles/desktop/node_modules/@michengai/dsh-skills-manager/lib/core.js';
const core = await import(CORE);

const argv = process.argv.slice(2);
const dry = argv.includes('--dry');
const dirsMode = argv.includes('--dirs');
const inputs = argv.filter(a => !a.startsWith('--'));

async function findSkillDirs(root) {
  const out = [];
  async function walk(dir) {
    let hasDoc = false;
    try { hasDoc = (await stat(join(dir, 'SKILL.md'))).isFile(); } catch { hasDoc = false; }
    if (hasDoc) { out.push(dir); return; }
    let items = [];
    try { items = await readdir(dir, { withFileTypes: true }); } catch { return; }
    for (const it of items) {
      if (!it.isDirectory() || it.name === '.git' || it.name === 'node_modules') continue;
      await walk(join(dir, it.name));
    }
  }
  await walk(root);
  return out;
}

const sources = [];
if (dirsMode) {
  for (const root of inputs) sources.push(...(await findSkillDirs(root)));
} else {
  sources.push(...inputs);
}

const target = core.userRoots().find(r => r.key === 'dsh');
console.log(`[root] dsh -> ${target?.path}  (mutable=${target?.mutable})`);
console.log(`[mode] ${dirsMode ? '--dirs ' : ''}${dry ? 'DRY-RUN (不写盘)' : 'REAL IMPORT (conflict=skip)'}  候选=${sources.length}`);

const tally = { imported: [], skipped: [], conflicts: [], failed: [], pending: [] };

for (const src of sources) {
  const log = (t, m) => console.log(`    [${t}] ${m}`);
  const res = dry
    ? await core.importSkill(src, log, { dryRun: true })
    : await core.importSkill(src, log, { conflict: 'skip' });

  const ok = res.ok !== false;
  const pend = res.pending || [];
  const imp = res.imported || [];
  const conf = res.conflicts || [];
  const skip = res.skipped || [];
  const fail = res.failed || [];
  const tag = dry ? (pend.length ? `plan ${pend.map(p => p.name).join(',')}` : '-')
                  : (imp.length ? `OK ${imp.map(i => i.name).join(',')}` : '-');
  if (!ok || fail.length) console.log(`  FAIL ${src}\n        ${res.error || fail.map(f => `${f.name || f.source}: ${f.error}`).join(' ; ')}`);
  else if (conf.length) console.log(`  CONFLICT ${conf.map(c => c.name).join(',')} (已存在 -> skip)`);
  else console.log(`  ${tag}`);

  for (const p of pend) tally.pending.push(p.name);
  for (const i of imp) tally.imported.push(i.name);
  for (const c of conf) tally.conflicts.push(c.name);
  for (const s of skip) tally.skipped.push(s.name);
  for (const f of fail) tally.failed.push(f.name || f.source);
}

const uniq = a => [...new Set(a)];
console.log('\n========== 汇总 ==========');
console.log(dry ? `待安装 ${uniq(tally.pending).length} 个` : `已安装 ${uniq(tally.imported).length} 个`);
console.log((dry ? uniq(tally.pending) : uniq(tally.imported)).join(', '));
console.log(`冲突(skip) ${uniq(tally.conflicts).length}${tally.conflicts.length ? ': ' + uniq(tally.conflicts).join(', ') : ''}`);
console.log(`失败 ${uniq(tally.failed).length}${tally.failed.length ? ': ' + uniq(tally.failed).join(', ') : ''}`);
