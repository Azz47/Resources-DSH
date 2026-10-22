#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""10-14 收尾修正三处：
  1) verify_agents_names.py —— 参照物升级：区分「可 skill() 加载的名字」与「只能按文件读的名字」
     （旧版拿 frontmatter name 当现实，导致 scholar-notes 被误判、学霸笔记 被当成漏路由）
  2) AGENTS.md F 区 —— understand 的 8 个子技能写全名（解析器只认完整名字）
  3) 技能现状速查.md —— mattpocock 分组数量按实测改（engineering 20 / productivity 7 / in-progress 7 / misc 4）
"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BAK = ".bak-before-namefix-20261014"


def backup(p):
    d = p + BAK
    if not os.path.exists(d):
        shutil.copy2(p, d)


def sub(t, old, new, tag):
    n = t.count(old)
    assert n == 1, "[%s] 命中 %d 次（要求 1）" % (tag, n)
    return t.replace(old, new)


# ---------------------------------------------------------------- 1) checker
V = r"D:\Resources\DSH\_probe\verify_agents_names.py"
v = open(V, encoding="utf-8").read()
backup(V)

OLD = '''skill_rows = [r for r in inv if isinstance(r, dict) and r.get("name")]
real_skills = {r["name"] for r in skill_rows}'''
NEW = '''skill_rows = [r for r in inv if isinstance(r, dict) and r.get("name")]


def _loadable(r):
    """会话技能目录能不能直接 skill() 到它：SKILL.md 的父目录必须是技能根 skills\\\\。"""
    p = (r.get("path") or "").replace("/", "\\\\")
    return os.path.basename(os.path.dirname(p)) == "skills"


def _call_name(r):
    """调用名 = frontmatter name（ASCII 时）；非 ASCII（如「学霸笔记」）回落到目录名。"""
    n = (r.get("name") or "").strip()
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", n):
        return n
    return (r.get("dir") or n).strip()


real_skills = {_call_name(r) for r in skill_rows if _loadable(r)}          # 可直接 skill()
file_only = {_call_name(r) for r in skill_rows if not _loadable(r)}       # 只能按文件读
real_skills_all = real_skills | file_only
raw_names = {r["name"] for r in skill_rows}'''
v = sub(v, OLD, NEW, "checker-reality")

v = sub(v, "import io\nimport json\nimport re\nimport sys",
        "import io\nimport json\nimport os\nimport re\nimport sys", "checker-import")

v = sub(v, '''    if t in real_skills:                                # 现实里确有此技能 → 一定是技能名''',
        '''    if t in real_skills_all:                            # 现实里确有此技能 → 一定是技能名''', "checker-claim")

v = sub(v, '''    elif re.fullmatch(r"[\\u4e00-\\u9fff]+", t):          # 中文技能名，如「学霸笔记」''',
        '''    elif t in raw_names:                                # frontmatter 名（可能与调用名不同）
        skill_claims.add(t)
    elif re.fullmatch(r"[\\u4e00-\\u9fff]+", t):          # 中文技能名''', "checker-raw")

v = sub(v, '''fake = sorted(s for s in skill_claims if s not in real_skills)''',
        '''fake = sorted(s for s in skill_claims if s not in real_skills_all)''', "checker-fake")

v = sub(v, '''print("现实：技能 %d 个（生效 %d / 未生效 %d） / 专家 %d 位"
      % (len(real_skills), len(real_skills_active), len(inactive), len(real_experts)))''',
        '''print("现实：技能 %d 个（可直接 skill() %d + 只能按文件读 %d；生效 %d / 未生效 %d） / 专家 %d 位"
      % (len(real_skills_all), len(real_skills), len(file_only),
         len(real_skills_active), len(inactive), len(real_experts)))
print("      只能按文件读（名字不可 skill()，表里必须带 ⚠️）：%s" % ", ".join(sorted(file_only)))''',
        "checker-report")

v = sub(v, '''missing_from_table = sorted(real_skills_active - skill_claims)''',
        '''missing_from_table = sorted(real_skills - skill_claims)''', "checker-missing")

v = sub(v, '''print("      反向：生效技能里、表里没提的 %d 个 %s"''',
        '''print("      反向：可直接加载的技能里、表里没提的 %d 个 %s"''', "checker-label")

open(V, "w", encoding="utf-8", newline="\n").write(v)
print("checker 已升级")

# ---------------------------------------------------------------- 2) AGENTS.md
A = r"C:\Users\Administrator\.dsh\AGENTS.md"
a = open(A, encoding="utf-8").read()
backup(A)
a = sub(
    a,
    "| 读陌生代码库（知识图谱） | `understand`（+ `understand-chat` / `-dashboard` / `-diff` / `-domain` / `-explain` / `-figma` / `-knowledge` / `-onboard`） |",
    "| 读陌生代码库（知识图谱） | `understand`；按需取 `understand-chat`（问答）、`understand-dashboard`（看板）、`understand-diff`（diff/PR 影响面）、`understand-domain`（业务领域图）、`understand-explain`（单文件/函数深讲）、`understand-figma`（Figma 设计图）、`understand-knowledge`（LLM wiki 知识库）、`understand-onboard`（新人上手） |",
    "agents-understand",
)
open(A, "w", encoding="utf-8", newline="\n").write(a)
print("AGENTS.md F 区已写全 8 个 understand 子技能")

# ---------------------------------------------------------------- 3) 速查
S = r"D:\Resources\DSH\技能现状速查.md"
s = open(S, encoding="utf-8").read()
backup(S)
s = sub(
    s,
    "组目录：engineering 18 / productivity 6 / in-progress 8 / misc 6（合计 38，另有 4 个 `README.md` 被刻意跳过）",
    "组目录：engineering 20 / productivity 7 / in-progress 7 / misc 4（另有 `deprecated` 空组；合计 38，另有 4 个 `README.md` 被刻意跳过）",
    "su-cha-groups",
)
open(S, "w", encoding="utf-8", newline="\n").write(s)
print("速查分组数量已按实测修正")
