# -*- coding: utf-8 -*-
"""对比「自标比赛/优质课/获奖」课件与普通课件的版式差异。

不需要重新处理图片 —— 直接复用已算好的 pages.jsonl（每页一行指标），
用文件名里的课件 ID 与 contest.jsonl 做 join。

用法: python compare_contest.py <contest.jsonl> <pages.jsonl> ...
"""
import json
import re
import statistics as st
import sys
from collections import Counter

TAG = ["一等奖", "优质课", "公开课", "获奖", "赛课", "大赛", "示范课", "精品", "教学能手", "名师"]

contest_ids = set()
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    m = re.search(r"/(\d+)\.html", r.get("url", ""))
    if m:
        contest_ids.add(m.group(1))
print(f"比赛/优质课课件: {len(contest_ids)} 份\n")

ID_RE = re.compile(r"_(\d{5,})_")

pages = {"contest": [], "normal": []}
for p in sys.argv[2:]:
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        m = ID_RE.search(r["file"])
        grp = "contest" if (m and m.group(1) in contest_ids) else "normal"
        pages[grp].append(r)

print(f"页数: 比赛组 {len(pages['contest'])}  普通组 {len(pages['normal'])}\n")

if not pages["contest"] or not pages["normal"]:
    print("样本不足，无法对比"); sys.exit(0)


def med(rows, k):
    return round(st.median(r[k] for r in rows), 3)


def ratio(rows, k):
    return round(sum(1 for r in rows if r[k]) / len(rows), 3)


def bands(rows):
    return [round(sum(r["bands"][i] for r in rows) / len(rows), 3) for i in range(10)]


def palette(rows, n=6):
    c = Counter()
    for r in rows:
        for q in r["palette"][:3]:
            c[q["rgb"]] += q["pct"]
    return c.most_common(n)


print("=" * 74)
print(f"{'指标':<18}{'比赛/优质课':>18}{'普通课件':>18}{'差异':>18}")
print("=" * 74)
rows = [
    ("内容覆盖率", med(pages["contest"], "coverage"), med(pages["normal"], "coverage"), "高=更满"),
    ("对比度", med(pages["contest"], "contrast"), med(pages["normal"], "contrast"), "高=更抢眼"),
    ("边缘密度", med(pages["contest"], "edge_density"), med(pages["normal"], "edge_density"), "高=元素更多"),
    ("色彩丰富度", med(pages["contest"], "colorfulness"), med(pages["normal"], "colorfulness"), "高=更花"),
    ("亮底比例", ratio(pages["contest"], "light_bg"), ratio(pages["normal"], "light_bg"), "高=更少深色页"),
]
for name, a, b, note in rows:
    d = "—" if b == 0 else f"{(a - b) / b * 100:+.1f}%"
    print(f"{name:<18}{a:>18}{b:>18}{d:>12}  {note}")

print("\n--- 横向 10 条带内容分布（越高的带=内容越重）---")
bc, bn = bands(pages["contest"]), bands(pages["normal"])
print("带序        " + "".join(f"{i+1:>7}" for i in range(10)))
print("比赛/优质课 " + "".join(f"{v:>7.3f}" for v in bc))
print("普通课件    " + "".join(f"{v:>7.3f}" for v in bn))
print("差值        " + "".join(f"{bc[i]-bn[i]:>+7.3f}" for i in range(10)))

print("\n--- 高频色（比赛组）---")
for rgb, w in palette(pages["contest"]):
    print(f"   {rgb}  {w:.1f}")
print("--- 高频色（普通组）---")
for rgb, w in palette(pages["normal"]):
    print(f"   {rgb}  {w:.1f}")
