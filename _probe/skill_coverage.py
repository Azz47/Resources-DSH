import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

inv = json.load(open(r"D:\Resources\DSH\_probe\skills-inventory.json", encoding="utf-8"))
names = set()
owners = {}


def walk(o, root=None):
    if isinstance(o, dict):
        if isinstance(o.get("root"), str):
            root = o["root"]
        for k, v in o.items():
            if k in ("name", "skill") and isinstance(v, str):
                names.add(v)
                owners.setdefault(v, root or "?")
            walk(v, root)
    elif isinstance(o, list):
        for x in o:
            walk(x, root)


walk(inv)

txt = open(r"C:\Users\Administrator\.dsh\AGENTS.md", encoding="utf-8").read()
miss = sorted(n for n in names if n not in txt)

print("技能总数 %d  已引用 %d  未引用 %d" % (len(names), len(names) - len(miss), len(miss)))
print()

cnt = Counter(owners.get(n, "?") for n in miss)
for root, k in cnt.most_common():
    got = [n for n in miss if owners.get(n, "?") == root]
    label = root.replace("C:\\Users\\Administrator\\.dsh\\skills", "[自建]").replace("\\", "/")
    print("  %2d  %s" % (k, label))
    print("      " + ", ".join(got))
