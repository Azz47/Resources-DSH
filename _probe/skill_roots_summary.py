"""汇总技能清单：总数 / 生效数 / 按技能根分组。用于把「10 根 / 64 个 SKILL.md」这类旧说法对齐到实测。"""
import json
import sys
from collections import Counter, OrderedDict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PATH = r"D:\Resources\DSH\_probe\skills-inventory.json"
data = json.load(open(PATH, encoding="utf-8"))

if isinstance(data, dict):
    print("top-level keys:", list(data.keys())[:20])
    for k, v in data.items():
        if isinstance(v, list):
            items = v
            print("using list under key:", k, "len:", len(items))
            break
    else:
        items = []
else:
    items = data

print("total:", len(items))
if items:
    print("first record keys:", list(items[0].keys()))
    print("first record:", json.dumps(items[0], ensure_ascii=False)[:300])

# 自动挑选「技能根」字段
candidates = ["root", "rootDir", "source", "sourceRoot", "pkg", "package", "plugin", "dir", "base", "origin"]
for c in candidates:
    if items and c in items[0]:
        print("\n== group by", c, "==")
        cnt = Counter(str(it.get(c)) for it in items)
        for name, n in cnt.most_common():
            print("%4d  %s" % (n, name))
        print("roots:", len(cnt))

active_field = None
for c in ["active", "enabled", "loaded"]:
    if items and c in items[0]:
        active_field = c
        break
if active_field:
    act = sum(1 for it in items if it.get(active_field))
    print("\n%s: active=%d inactive=%d" % (active_field, act, len(items) - act))
    inact = [it for it in items if not it.get(active_field)]
    for it in inact:
        print("  inactive:", it.get("name"), "|", it.get("root") or it.get("plugin") or it.get("source"))
