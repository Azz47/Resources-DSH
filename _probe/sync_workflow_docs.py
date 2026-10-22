# -*- coding: utf-8 -*-
"""Sync skill count 157->158 (new bundled install-dsh-image-gen) + add workflow pointers."""
import io, sys

def load(p):
    return io.open(p, "r", encoding="utf-8", newline="").read(), io.open(p, "rb").read()

def save(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

report = []

# ---------- 1. 技能现状速查.md ----------
P1 = r"D:\Resources\DSH\技能现状速查.md"
s = io.open(P1, encoding="utf-8", newline="").read()
orig = s
cnt157 = s.count("157")
s = s.replace("157", "158")
s = s.replace("插件 **70**", "插件 **71**")
report.append(("速查:157->158", cnt157))

lines = s.split("\n")
out = []
inserted_row = False
inserted_ptr = False
for ln in lines:
    out.append(ln)
    if (not inserted_row) and ln.startswith("| `dsh-craft-your-textbook` |"):
        out.append("| `dsh-image-gen` | 1 | `install-dsh-image-gen`（配置/校验/移除生图通道；**不在会话技能索引**，只能按文件读 `…\\dsh-image-gen\\skills\\install-dsh-image-gen\\SKILL.md`） |")
        inserted_row = True
    if (not inserted_ptr) and ln.startswith("## 四、路由"):
        out.append("")
        out.append("> 全量任务工作流（预设划分 + 专家/技能/插件/动效配方 + 验收门）见 `D:\\Resources\\DSH\\任务工作流总纲.md`；本节是技能侧的取用索引。")
        inserted_ptr = True
s = "\n".join(out)
report.append(("速查:row", inserted_row))
report.append(("速查:pointer", inserted_ptr))
if s != orig:
    save(P1, s)

# ---------- 2. 任务工作流总纲.md ----------
P2 = r"D:\Resources\DSH\任务工作流总纲.md"
s2 = io.open(P2, encoding="utf-8", newline="").read()
o2 = s2
s2 = s2.replace("| 技能 | **157** 个 `SKILL.md` | 插件自带 70 + 用户技能根 87（自建 3 + 导入 84） |",
                "| 技能 | **158** 个 `SKILL.md` | 插件自带 71 + 用户技能根 87（自建 3 + 导入 84） |")
lines = s2.split("\n")
out = []
added = False
for ln in lines:
    out.append(ln)
    if (not added) and ln.startswith("| `vision-router`"):
        out.append("| `install-dsh-image-gen` | P3 / P12 | dsh-image-gen 自带的配置/校验技能，索引外按文件读 |")
        added = True
s2 = "\n".join(out)
report.append(("总纲:count", o2 != s2))
report.append(("总纲:audit-row", added))
if s2 != o2:
    save(P2, s2)

# ---------- 3. AGENTS.md ----------
P3 = r"C:\Users\Administrator\.dsh\AGENTS.md"
s3 = io.open(P3, encoding="utf-8", newline="").read()
o3 = s3
s3 = s3.replace("全机 157 个 `SKILL.md`", "全机 158 个 `SKILL.md`")
report.append(("AGENTS:count", o3 != s3))
if s3 != o3:
    save(P3, s3)

for k, v in report:
    print(k, "=", v)
