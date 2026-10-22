# -*- coding: utf-8 -*-
"""盘点已装插件对「每轮上下文」的占用 —— 这是"优化"最直接可量化的部分。

做法：扫每个插件包里注册系统提示段的代码（systemPrompt.section / prompt.section /
instructions），把其中的长字符串字面量抽出来量长度。这是**上界估计**（有些段落带条件
或随会话变化），但足以排出大小次序。

用法: python plugin_cost.py
"""
import json
import os
import re

PROFILE = r"C:\Users\Administrator\.dsh\profiles\desktop"
PKG = os.path.join(PROFILE, "package.json")

deps = json.load(open(PKG, encoding="utf-8"))["dependencies"]

# 抓 systemPrompt.section(...) / prompt.section(...) / registerSection 附近的长字符串
PAT = re.compile(
    r"(?:systemPrompt|prompt|instructions)\s*\.\s*(?:section|register|add)\s*\("
    r"|name\s*:\s*['\"][a-z0-9:_\-]+['\"]\s*,\s*order\s*:",
    re.I)
STR = re.compile(r"""(['"`])((?:\\\1|(?!\1).){200,})\1""", re.S)


def walk(pkg_dir):
    total = 0
    for dirpath, dirnames, files in os.walk(pkg_dir):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git", "test", "tests")]
        for f in files:
            if not f.endswith((".js", ".mjs", ".cjs", ".ts")):
                continue
            p = os.path.join(dirpath, f)
            try:
                if os.path.getsize(p) > 3_000_000:
                    continue
                src = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if not re.search(r"systemPrompt|prompt\s*\.\s*section|persona", src, re.I):
                continue
            for m in STR.finditer(src):
                s = m.group(2)
                # 只算看起来像文档/提示词的：含中文或较长的英文句子
                if len(s) >= 200:
                    total += len(s)
    return total


rows = []
for name in sorted(deps):
    d = os.path.join(PROFILE, "node_modules", name)
    if not os.path.isdir(d):
        rows.append((name, -1, "未落盘"))
        continue
    try:
        n = walk(d)
    except Exception as e:
        n = -1
    rows.append((name, n, ""))

rows.sort(key=lambda r: -r[1])
print(f"{'插件':<46}{'提示词字符数(上界)':>18}  备注")
print("-" * 84)
tot = 0
for name, n, note in rows:
    disp = "—" if n < 0 else f"{n:,}"
    if n > 0:
        tot += n
    print(f"{name:<46}{disp:>18}  {note}")
print("-" * 84)
print(f"{'合计（可估部分）':<46}{tot:>18,}  约 {tot/3.2:,.0f} tokens/轮" if tot else "")
