#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把用户技能根（74 个）按来源仓库分组，输出精确对照表（10-14 扩容用）。

来源判定：本次导入的目录名 = `_skillinstall\\<repo>\\...\\<dirname>` 的 basename（kebab），
逐层在暂存目录里找同名目录，最外层仓库名即来源。
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"C:\Users\Administrator\.dsh\skills"
STAGE = r"D:\Resources\DSH\_skillinstall"
SELF = {"daofa-contest-pack", "daofa-lesson-prep", "pptx-layout-craft"}

# 暂存目录里：目录名 -> 所属仓库（最外层子目录名）
index = defaultdict(list)
for repo in sorted(os.listdir(STAGE)):
    rp = os.path.join(STAGE, repo)
    if not os.path.isdir(rp):
        continue
    for dirpath, dirnames, filenames in os.walk(rp):
        if ".git" in dirpath:
            continue
        for d in dirnames:
            index[d].append(repo)

rows = []
for name in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, name)
    if not os.path.isdir(p):
        continue
    has = os.path.exists(os.path.join(p, "SKILL.md"))
    if name in SELF:
        repo = "(自建)"
    else:
        cands = [r for r in index.get(name, []) if r != "_named"]
        repo = cands[0] if cands else "(?)"
    rows.append((repo, name, has))

byrepo = defaultdict(list)
for repo, name, has in rows:
    byrepo[repo].append((name, has))

print("### 用户技能根分组（%d 个目录）" % len(rows))
for repo, items in sorted(byrepo.items(), key=lambda x: -len(x[1])):
    print("\n%-42s %d" % (repo, len(items)))
    for name, has in items:
        print("    %-34s SKILL.md=%s" % (name, "Y" if has else "N"))

missing = [n for _, n, has in rows if not has]
print("\n缺 SKILL.md：", missing or "无")

# 磁盘占用
total = 0
for repo, items in byrepo.items():
    sz = 0
    for name, _ in items:
        for dp, dn, fn in os.walk(os.path.join(ROOT, name)):
            for f in fn:
                try:
                    sz += os.path.getsize(os.path.join(dp, f))
                except OSError:
                    pass
    total += sz
    print("%-42s %8.2f MB" % (repo, sz / 1048576))
print("%-42s %8.2f MB" % ("合计", total / 1048576))

# 与 inventory JSON 核对
inv = json.load(open(r"D:\Resources\DSH\_probe\skills-inventory.json", encoding="utf-8"))
items = inv if isinstance(inv, list) else inv.get("skills", inv.get("items", []))
user = [i for i in items if i.get("source") == "user"]
print("\ninventory: total=%d user=%d plugin=%d active=%d inactive=%d" % (
    len(items), len(user), len(items) - len(user),
    sum(1 for i in items if i.get("active")), sum(1 for i in items if not i.get("active"))))
print("按 pkg:", dict(Counter(i.get("pkg") for i in items)))
