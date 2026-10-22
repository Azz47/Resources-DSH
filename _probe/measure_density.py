# -*- coding: utf-8 -*-
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")


def density(p):
    z = zipfile.ZipFile(p)
    slides = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    sp = pic = tbl = 0
    for n in slides:
        x = z.read(n).decode("utf-8", "ignore")
        sp += len(re.findall(r"<p:sp>", x))
        pic += len(re.findall(r"<p:pic>", x))
        tbl += len(re.findall(r"<a:tbl>", x))
    return len(slides), sp, pic, tbl, round(sp / max(len(slides), 1), 1)


paths = [
    r"D:\Resources\DSH\decks\进入新时代-参赛版-v2\第二单元 进入新时代-单元思考与行动-参赛版-v2.pptx",
    r"D:\Resources\DSH\corpus\_web\gordensun\red-teaching-framework.pptx",
    r"D:\Resources\DSH\corpus\_web\gordensun\data-viz-deck.pptx",
    r"D:\Resources\DSH\corpus\_web\gordensun\report-massive-charts.pptx",
]
for p in paths:
    print(os.path.basename(p)[:40], density(p))

rows = [json.loads(l) for l in io.open(r"D:\Resources\DSH\corpus\1ppt2\index.jsonl", encoding="utf-8") if l.strip()]
print("\ntitles:", len(rows))
kw = Counter()
for r in rows:
    t = r.get("title") or ""
    for w in ["课件", "复习", "单元", "第", "课", "中考", "高考", "说课", "微课", "优质课",
              "公开课", "一轮", "二轮", "专题", "试卷", "讲评", "教案", "教学设计", "班会", "家长会", "新授", "练习"]:
        if w in t:
            kw[w] += 1
print("标题关键词:", kw.most_common(22))
lens = sorted(len(r.get("title") or "") for r in rows)
print("标题长度中位:", lens[len(lens) // 2])
