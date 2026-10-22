# -*- coding: utf-8 -*-
"""Patch AGENTS.md: preset routing wording + self-check rows + notes bullets."""
import io, sys

P = r"C:\Users\Administrator\.dsh\AGENTS.md"
with io.open(P, "r", encoding="utf-8", newline="") as f:
    s = f.read()
orig = s
applied = []

# R1: point section one at presets + domain table
old1 = '**判定标准**：任务命中第二节任一"触发信号"→ **必须**调用对应资源。'
new1 = '**判定标准**：任务命中第二节的预设、或第三节任一"触发信号" → **必须**调用对应资源。'
if old1 in s:
    s = s.replace(old1, new1, 1); applied.append("R1")
else:
    applied.append("R1-MISS")

# R2a: self-check row - preset
old2 = '| 对口技能加载了吗？ | 手写了一遍本该用技能做的事 |'
new2 = ('| 预设定对了吗？ | 没想预设就开做，做完发现该走另一套资源 |\n'
        '| 对口技能加载了吗？ | 手写了一遍本该用技能做的事 |')
if old2 in s:
    s = s.replace(old2, new2, 1); applied.append("R2a")
else:
    applied.append("R2a-MISS")

# R2b: self-check row - plugin tool
old3 = '| 状态汇报用组件了吗？ | ≥3 条并列 / 有数字，却写成 markdown 表格或纯 bullet |'
new3 = old3 + '\n| 插件工具优先了吗？ | 手搓第三方 API / 自己拼 XML，而插件已有现成工具 |'
if old3 in s:
    s = s.replace(old3, new3, 1); applied.append("R2b")
else:
    applied.append("R2b-MISS")

# R3: append notes bullets
tail = ('- **技能名以会话技能目录为准**：全机 157 个 `SKILL.md`，但 `skill()` 只认目录里的名字；'
        '`ppt-studio-*`（预设隔离）、`stage-panel` 子模式、`dsh-craft-your-textbook`（技能根是 `resources\\`）'
        '都只能按文件读，详见 `D:\\Resources\\DSH\\技能现状速查.md` 第七节。')
add = (
    '\n- **动效按内容选技能**：页面/镜头 → `ppt-animation` / `video-shot-demos`；关系/流程 → `flowchart` / `dynamic-archify`；'
    '界面 → `phone-ui-demos`；笔记 → `scholar-notes`；卡片叙事 → `card-theater`；协议 → `network-protocol-viz`。'
    '选择矩阵见 `D:\\Resources\\DSH\\任务工作流总纲.md` 第 7 节。'
    '\n- **预设表与领域表的分工**：第二节定"走哪条流水线"，第三节查"这一步用哪个技能/专家/工具"；'
    '完整配方（含产物、验收、坑）只在总纲里。'
    '\n- **插件热更后必须完全重启**：否则页面内旧模块与新磁盘文件错配 → 白屏/错误页；'
    '`profile desktop` 的插件只能走 GUI 更新（`dsh plugin --profile desktop` 会被 Electron 拒绝）。'
)
if tail in s:
    s = s.replace(tail, tail + add, 1); applied.append("R3")
else:
    applied.append("R3-MISS")

if s != orig:
    with io.open(P, "w", encoding="utf-8", newline="") as f:
        f.write(s)

lines = s.count("\n") + (0 if s.endswith("\n") else 1)
print("applied:", ",".join(applied))
print("lines:", lines, "bytes:", len(s.encode("utf-8")))
for h in [l for l in s.splitlines() if l.startswith("## ")]:
    print("H2:", h)
