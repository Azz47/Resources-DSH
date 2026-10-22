# -*- coding: utf-8 -*-
"""核对 AGENTS.md 里写的技能名 / 专家名是否真实存在。

★ 方向很重要：本脚本查的是 **AGENTS.md → 现实**（表里写的名字必须真实存在），
  和 skill_coverage.py 正好相反（那个查 现实 → 表，看有没有技能被漏掉）。
  两个方向都要过，只查一边会出现「表里 64 个名字、现实只有 60 个」这种假通过。

数据来源（都不是手写的，是现查的）：
  - 技能：`daofa-lesson-prep/scripts/inventory-skills.py` 生成的 skills-inventory.json
    （每条带 active 字段：所属插件没装进 profile bundles 的技能算未生效，不要求被路由）
  - 专家：`list_experts(<division>)` 的返回，6 个分区 27 位，逐字抄进 EXPERTS 常量

2026-10-08 修订：技能识别改为数据驱动（t in real_skills 直接算技能名），
不再依赖手写前缀表。旧版前缀表漏掉了 dsh-univer-office 的 8 个 univer-* 与
hindsight-coding-agent，导致「反向：现实里有、表里没提」长期假报 10 项；
同时把插件包名（如 dsh-echocat-skill-panel）加进 NOT_SKILLS，避免误判成假技能。

用法: python verify_agents_names.py
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AGENTS = r"C:\Users\Administrator\.dsh\AGENTS.md"
INV = r"D:\Resources\DSH\_probe\skills-inventory.json"

# ---------- 现实：真实存在的 27 位专家（来自 list_experts 六个分区，逐字抄录） ----------
EXPERTS = {
    "学术": ["人类学家", "地理学家", "历史学家", "叙事学家", "心理学家", "统计学家"],
    "设计": ["AI 图像设计师", "无障碍设计师", "用户体验设计师", "UI 设计师",
             "UI 视觉验收设计师", "视频提示词工程师", "视觉传达设计师"],
    "工程": ["代码审查工程师", "工程效率工程师", "数据可视化工程师", "开发者工具工程师",
             "知识图谱工程师", "LLM 后训练工程师", "低风险变更工程师", "提示词工程师",
             "实时协作工程师", "高级开发者"],
    "法务": ["制度文件撰写专家"],
    "专业": ["企业培训师", "文档工程师"],
    "测试": ["验收测试工程师"],
}
real_experts = {e for v in EXPERTS.values() for e in v}
# 比较用：去掉空格再比。表里写作「AI图像设计师」，名册写作「AI 图像设计师」，
# 不归一化会把 4 位带空格的专家（AI 图像设计师 / LLM 后训练工程师 / UI 设计师 /
# UI 视觉验收设计师）全部误报成名册外。
_norm = lambda s: s.replace(" ", "").replace("\u3000", "")
real_experts_norm = {_norm(e): e for e in real_experts}

# 反引号里这些不是技能名，是围栏标签 / 命令 / 工具 / 插件包名，别误报
NOT_SKILLS = {"dsh-ui", "git", "automation_create", "schedule_create",
              "dsh-echocat-skill-panel"}

# ---------- 现实：真实存在的技能 ----------
with io.open(INV, "r", encoding="utf-8") as f:
    inv = json.load(f)
skill_rows = [r for r in inv if isinstance(r, dict) and r.get("name")]


def _loadable(r):
    """会话技能目录能不能直接 skill() 到它。

    结构判据：SKILL.md 的上上级目录名必须是 skills\\。
    例外白名单：SKILL.md 位于插件根（或 skill\\ 目录）但**确实出现在会话技能目录**里，
    即 genui（@changfenhuang/dsh-genui 包根即技能）与 hindsight-coding-agent
    （@vectorize-io/hindsight-coding-agents\\skill\\）；两者本会话 skill() 可用。
    真正的「只能按文件读」= stage-panel 5 个子模式 + dsh-craft-your-textbook（resources\\）。
    """
    p = (r.get("path") or "").replace("/", os.sep)
    if os.path.basename(os.path.dirname(os.path.dirname(p))) == "skills":
        return True
    return _call_name(r) in {"genui", "hindsight-coding-agent"}


def _call_name(r):
    """调用名 = frontmatter name（ASCII 时）；非 ASCII（如「学霸笔记」）回落到目录名。"""
    n = (r.get("name") or "").strip()
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", n):
        return n
    return (r.get("dir") or n).strip()


real_skills = {_call_name(r) for r in skill_rows if _loadable(r)}          # 可直接 skill()
file_only = {_call_name(r) for r in skill_rows if not _loadable(r)}       # 只能按文件读
real_skills_all = real_skills | file_only
raw_names = {r["name"] for r in skill_rows}
# 未生效 = 所属插件不在 profile bundles 里（装载不到，不要求进路由表）
inactive = sorted(r["name"] for r in skill_rows if r.get("active") is False)
real_skills_active = real_skills - set(inactive)

# ---------- AGENTS.md ----------
with io.open(AGENTS, "r", encoding="utf-8") as f:
    md = f.read()

tokens = {t.strip() for t in re.findall(r"`([^`\n]+)`", md)}

# 兜底启发式：只服务于「表里写了现实不存在的技能名」这一方向（抓错别字 / 假名字）。
SKILL_PREFIX = ("ppt-", "ppt_studio", "daofa-", "pptx-", "pua", "dsh-", "using-",
                "writing-", "executing-", "diagnosing-", "systematic-", "requesting-",
                "receiving-", "test-", "brainstorming", "dispatching-", "subagent-",
                "verification-", "finishing-")
BARE = {"code", "learn", "game-study", "ml", "quant", "genui", "stage-panel",
        "flowchart", "archify", "dynamic-archify", "network-protocol-viz",
        "card-theater", "video-shot-demos", "phone-ui-demos",
        "yes", "mama", "ding", "pro", "shot", "p7", "p9", "p10"}

skill_claims = set()
for t in tokens:
    if t in NOT_SKILLS:
        continue
    if t in real_skills_all:                            # 现实里确有此技能 → 一定是技能名
        skill_claims.add(t)
    elif t in raw_names:                                # frontmatter 名（可能与调用名不同）
        skill_claims.add(t)
    elif re.fullmatch(r"[\u4e00-\u9fff]+", t):          # 中文技能名
        skill_claims.add(t)
    elif re.fullmatch(r"[a-z0-9][a-z0-9._-]*", t) and (t.startswith(SKILL_PREFIX) or t in BARE):
        skill_claims.add(t)

# 专家：表格第 3 列（"专家"列）里出现的名字
expert_claims, unknown_experts = set(), set()
for line in md.split("\n"):
    if not line.startswith("|") or line.startswith("| ---"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 3:
        continue
    for part in re.split(r"[、,，/]", cells[2].replace("**", "").replace(" ", "")):
        part = part.strip()
        if not part or part in ("—", "专家", "技能", "工具", "动作", "触发信号"):
            continue
        if not re.fullmatch(r"[\u4e00-\u9fffA-Za-z]+", part):
            continue
        (expert_claims if part in real_experts_norm else unknown_experts).add(part)

# 归一化回名册里的标准写法，方便对比与报告
expert_claims = {real_experts_norm.get(_norm(p), p) for p in expert_claims}

# ---------- 报告 ----------
print("=" * 74)
print("方向：AGENTS.md → 现实（表里写的名字必须真实存在）")
print("=" * 74)
print("AGENTS.md: %d 字节 / %d 行" % (len(md.encode("utf-8")), len(md.split("\n"))))
print("现实：技能 %d 个（可直接 skill() %d + 只能按文件读 %d；生效 %d / 未生效 %d） / 专家 %d 位"
      % (len(real_skills_all), len(real_skills), len(file_only),
         len(real_skills_active), len(inactive), len(real_experts)))
print("      只能按文件读（名字不可 skill()，表里必须带 ⚠️）：%s" % ", ".join(sorted(file_only)))
if inactive:
    print("      未生效（所属插件未装载，不要求路由）：%s" % ", ".join(inactive))
print()

fake = sorted(s for s in skill_claims if s not in real_skills_all)
print("【技能】表里引用 %d 个 → ✅ 真实存在 %d   ❌ 不存在 %d"
      % (len(skill_claims), len(skill_claims) - len(fake), len(fake)))
for s in fake:
    print("      ❌ %s" % s)
missing_from_table = sorted(real_skills - skill_claims)
print("      反向：可直接加载的技能里、表里没提的 %d 个 %s"
      % (len(missing_from_table), ("→ " + ", ".join(missing_from_table)) if missing_from_table else "✅"))
print()

print("【专家】表里出现 %d 位 → ✅ 全部命中现实名册   ❓ 名册外 %d"
      % (len(expert_claims), len(unknown_experts)))
for s in sorted(unknown_experts):
    print("      ❓ %s" % s)
not_routed = sorted(real_experts - expert_claims)
print("      反向：现实里有、表里没路由的 %d 位 %s"
      % (len(not_routed), ("→ " + ", ".join(not_routed)) if not_routed else "✅"))
print()

verdict = (not fake) and (not unknown_experts) and (not missing_from_table) and (not not_routed)
print("总判定：%s" % ("✅ 双向核对通过——表里每个名字都真实存在，现实里每个生效资源都被表覆盖"
                     if verdict else "❌ 有未对齐项，见上"))
