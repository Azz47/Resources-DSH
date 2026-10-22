const fs = require('fs');
const audit = JSON.parse(fs.readFileSync('D:/Resources/DSH/_probe/plugin_audit_20261021_2320.json', 'utf8'));
const staged = new Set(['@michengai/dsh-im-connect','dsh-animations','dsh-context','dsh-image-gen','dsh-whale-widget']);
const held = 'dsh-free-search';

function peerText(row) {
  const bad = (row.peerBad || []).map(p => `${p.peer} 需 ${p.range}，实有 ${p.have}`);
  const opt = (row.optionalMissing || []).map(p => p.peer || p);
  let s = bad.join('；');
  if (opt.length) s += (s ? '；' : '') + `可选 peer 缺 ${opt.join(', ')}（不阻塞）`;
  return s || '—';
}
function reactDomOnly(row) {
  return row.peerBad.length > 0 && row.peerBad.every(p => p.peer === 'react-dom');
}
function status(row) {
  if (row.inBundles && row.peerBad.length === 0) return '启用';
  if (row.inBundles && reactDomOnly(row)) return '启用（react-dom 警告）';
  if (row.inBundles) return '启动拒绝';
  if (staged.has(row.name)) return '候选（已暂存）';
  if (row.name === held) return '候选（待选）';
  if (reactDomOnly(row)) return '候选（react-dom 警告）';
  if (row.peerBad.length > 0) return '阻塞';
  return '候选（未暂存）';
}
const rows = [...audit.rows].sort((a,b) => (Number(b.inBundles)-Number(a.inBundles)) || a.name.localeCompare(b.name));
const lines = [];
lines.push('# DSH 桌面端插件兼容性全表（2026-10-21 23:20）');
lines.push('');
lines.push(`- 宿主：DSH Desktop 0.2.1-rc.2；cordis 4.0.5；schemastery 3.18.5；React 19.2.7；Node 24.21.0；pnpm 11.28.5`);
lines.push(`- 审计时：40 bundles（30 个 profile 依赖 + 10 个内置 bundle）；37 个直接依赖`);
lines.push(`- 暂存后：45 bundles（新增 5 个候选；另有 1 个候选待选、1 个仅 react-dom 警告、4 个启动拒绝）`);
lines.push(`- 说明：Bundle=是 表示已在 dsh.profile.bundles；兼容=按 peerDependencies 与本地包解析；“启用”仍需重启后验证。`);
lines.push('');
lines.push('| # | 插件 | 版本 | Bundle | 状态 | 兼容问题 / 说明 |');
lines.push('|---:|---|---|:---:|---|---|');
rows.forEach((r, i) => {
  lines.push(`| ${i+1} | \`${r.name}\` | ${r.installed} | ${r.inBundles ? '是' : '否'} | ${status(r)} | ${peerText(r)} |`);
});
lines.push('');
lines.push('## 统计');
lines.push('');
const enabled = rows.filter(r => r.inBundles && r.peerBad.length === 0).length;
const warn = rows.filter(r => r.inBundles && reactDomOnly(r)).length;
const denied = rows.filter(r => r.inBundles && r.peerBad.length > 0 && !reactDomOnly(r)).length;
const candidates = rows.filter(r => !r.inBundles && r.peerBad.length === 0).length;
const blocked = rows.filter(r => !r.inBundles && r.peerBad.length > 0).length;
lines.push(`- 已启用且 peer 通过：${enabled}`);
lines.push(`- 已启用、仅 react-dom 警告（实际工作）：${warn}`);
lines.push(`- 已启用且硬拒绝：${denied}`);
lines.push(`- 未启用且 peer 通过（候选）：${candidates}`);
lines.push(`- 未启用且 peer 警告/阻塞：${blocked}`);
lines.push(`- 直接依赖总数：${rows.length}`);
lines.push('');
lines.push('## 启动拒绝明细');
lines.push('');
rows.filter(r => r.inBundles && r.peerBad.length > 0 && !reactDomOnly(r)).forEach(r => {
  lines.push(`### ${r.name}@${r.installed}`);
  (r.peerBad || []).forEach(p => lines.push(`- \`${p.peer}\` 需 \`${p.range}\`，实有 \`${p.have}\``));
  lines.push('');
});
lines.push('## react-dom 警告（客户端依赖，非硬拒绝）');
lines.push('');
rows.filter(r => r.peerBad.length > 0 && reactDomOnly(r)).forEach(r => {
  lines.push(`- \`${r.name}@${r.installed}\` — react-dom 需 \`^18.2.0\`，宿主解析为 null（由 web 客户端提供，当前插件实际工作）`);
});
lines.push('');
lines.push('## 未启用候选');
lines.push('');
rows.filter(r => !r.inBundles && r.peerBad.length === 0).forEach(r => {
  lines.push(`- \`${r.name}@${r.installed}\` — ${status(r)}`);
});
lines.push('');
const out = 'D:/Resources/DSH/插件兼容性全表-20261021.md';
fs.writeFileSync(out, lines.join('\n'), 'utf8');
console.log(out);
console.log(lines.join('\n'));
