# -*- coding: utf-8 -*-
"""从课件语料里筛出「自标为比赛/获奖/优质课」的子集 —— 这是最接近"优秀课程"的样本。

用法: python filter_contest.py <out.jsonl> <index.jsonl> ...
"""
import json
import os
import sys

TAG = ["一等奖", "优质课", "公开课", "获奖", "赛课", "大赛", "示范课", "精品", "教学能手", "名师"]

rows = []
for p in sys.argv[2:]:
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

hit = [r for r in rows if any(t in r.get("title", "") for t in TAG)]
print(f"总记录 {len(rows)}，命中比赛/优质课标签 {len(hit)} 份（{len(hit)/max(1,len(rows))*100:.1f}%）\n")

by_cat = {}
for r in hit:
    by_cat.setdefault(r.get("cat", "?"), []).append(r)
for cat, items in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
    print(f"## {cat}  ({len(items)})")
    for r in items[:12]:
        # 去掉"PPT免费下载"这类营销后缀，露出真实课题
        t = r["title"]
        for suf in ("PPT免费下载", "PPT课件下载", "PPT下载", "ppt免费下载", "PPT优秀课件", "PPT优质课件", "PPT课件", "免费下载"):
            t = t.replace(suf, "")
        print(f"   {t.strip(' 《》')[:46]:48s}  pages={r.get('pages')}")
    if len(items) > 12:
        print(f"   … 另有 {len(items)-12} 份")
    print()

with open(sys.argv[1], "w", encoding="utf-8") as fh:
    for r in hit:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"-> {sys.argv[1]}")
