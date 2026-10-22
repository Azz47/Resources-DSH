import fs from 'node:fs';

const d = JSON.parse(fs.readFileSync('D:/Resources/DSH/_probe/awesome-plugins.json', 'utf8'));
const plugins = d.plugins;

const GROUPS = {
  '教学/课程': ['教学', '课程', '课堂', '授课', '备课', '教案', '讲解', '讲透', 'learn', 'lesson', 'course', 'teach', 'tutor', 'study'],
  '课件/PPT': ['ppt', 'pptx', 'slide', 'deck', 'presentation', '幻灯片', '演示', '课件'],
  '出题/测评': ['试卷', '命题', '题库', '测验', '作业', 'quiz', 'exam', 'question', '测评'],
  '视频/动画/微课': ['视频', '动画', '微课', 'video', 'animation', 'motion', 'remotion', 'ffmpeg', '录屏', '配音', '语音合成', 'tts'],
  '图形/板书/可视化': ['板书', '白板', '白板', '画板', '思维导图', 'mindmap', 'diagram', '图表', '可视化', 'canvas', 'whiteboard'],
  '学科/教材': ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '道法', '道德与法治', '教材', '课本', '学科', 'textbook'],
};
const NEG = ['高考', '考研', '雅思', '托福', 'GRE'];

const installed = new Set([
  'dsh-ppt-studio', 'dsh-craft-your-textbook', 'dsh-plugin-education', '@arcaneorion/dsh-teaching-board',
  'dsh-mindmap', 'dsh-context', 'dsh-better-sidebar', 'dsh-hotspots', 'dsh-image-generation', 'dshmarket',
  'dsh-skill-mcp-manager', '@haoranwang0921/dsh-session-cleaner', '@michengai/dsh-archive-manager',
  'dsh-whale-widget', '@tt-a1i/archify-dsh', 'billion-context',
]);

const asText = (v) => (typeof v === 'string' ? v : JSON.stringify(v ?? ''));

const hits = new Map();
for (const p of plugins) {
  const hay = ((p.name || '') + ' ' + asText(p.description) + ' ' + asText(p.category) + ' ' +
    asText(p.capabilities)).toLowerCase();
  if (NEG.some((n) => hay.includes(n.toLowerCase()))) continue;
  for (const [group, kws] of Object.entries(GROUPS)) {
    if (kws.some((k) => hay.includes(k.toLowerCase()))) {
      if (!hits.has(p.name)) hits.set(p.name, { p, groups: new Set() });
      hits.get(p.name).groups.add(group);
    }
  }
}

const rows = [...hits.values()].sort((a, b) => (b.p.stars || 0) - (a.p.stars || 0));
console.log(`matched ${rows.length} / ${plugins.length}\n`);
for (const { p, groups } of rows.slice(0, 70)) {
  const tag = installed.has(p.npm) || installed.has(p.name) ? '[已装]' : '      ';
  console.log(`${tag} ★${String(p.stars || 0).padEnd(5)} ${p.npm || p.name}`);
  console.log(`        ${[...groups].join('/')}  ::  ${asText(p.description).replace(/\s+/g, ' ').slice(0, 105)}`);
}
