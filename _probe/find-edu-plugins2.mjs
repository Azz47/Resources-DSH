import fs from 'node:fs';

const d = JSON.parse(fs.readFileSync('D:/Resources/DSH/_probe/awesome-plugins.json', 'utf8'));
const plugins = d.plugins;
const asText = (v) => (typeof v === 'string' ? v : JSON.stringify(v ?? ''));
const txt = (p) => (p.name + ' ' + asText(p.description) + ' ' + asText(p.capabilities)).toLowerCase();

// 只保留真正服务「备课/课件/微课/可视化/出题」的类别词
const WANT = [
  'ppt', 'pptx', 'slide', '幻灯片', '课件', '演示文稿',
  '微课', 'video', '视频', 'animation', '动画', 'remotion', 'ffmpeg', '录屏', '配音', '语音合成', 'tts', 'read-aloud', '朗读',
  'mindmap', '思维导图', '板书', 'whiteboard', '画板', 'diagram', '图表', 'genui', '交互式',
  '教学', '课堂', '授课', '讲解', '苏格拉底', 'socratic', 'course', 'lesson', 'tutor', 'openmaic',
  '试卷', '命题', '题库', '测验', 'quiz',
  'office', 'docx', 'xlsx',
  'skill',  // 技能包，服务第②项
];
const OUT = [
  'wallpaper', 'pet', 'skin', 'theme', 'memory', 'meme', 'git-graph', 'pet-', 'desktop pet',
  'cost', 'balance', 'token', 'notifier', 'pentest', 'deja', 'strata', 'subscriptions',
  '高考', '考研', 'chat-import', 'humanizer', 'lark', 'feishu', 'wallpaper-engine',
];

const seen = new Set();
const rows = [];
for (const p of plugins) {
  const t = txt(p);
  if (OUT.some((o) => t.includes(o))) continue;
  if (!WANT.some((w) => t.includes(w))) continue;
  const key = p.npm || p.name;
  if (seen.has(key)) continue;
  seen.add(key);
  rows.push(p);
}
rows.sort((a, b) => (b.stars || 0) - (a.stars || 0));

console.log(`candidates: ${rows.length}\n`);
for (const p of rows.slice(0, 45)) {
  const inst = p.install || (p.npm ? `dsh plugin --profile desktop add ${p.npm}` : '(no npm)');
  console.log(`★${String(p.stars || 0).padEnd(5)} ${p.npm || p.name}`);
  console.log(`   ${asText(p.description).replace(/\s+/g, ' ').slice(0, 130)}`);
  console.log(`   install: ${inst}`);
}
