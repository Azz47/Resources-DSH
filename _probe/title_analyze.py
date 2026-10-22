# -*- coding: utf-8 -*-
"""从课件标题语料中提取「叙述逻辑 / 授课思路 / 课件类型」的分布规律。

标题里藏着的信息：年级册别、课型（新授/复习/专题）、是否有比赛标签、
是否带情境/议题字样、单元归属。这些比页面像素更能反映「课是怎么组织的」。

用法: python title_analyze.py <index.jsonl> [<index2.jsonl> ...]
"""
import json
import re
import sys
from collections import Counter

rows = []
for p in sys.argv[1:]:
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

print(f"课件记录: {len(rows)}\n")

BOOK = re.compile(r"([七八九])年级\s*([上下])册|(七|八|九)\s*([上下])")
GRADE = re.compile(r"([七八九一二三四五六])年级")
UNIT = re.compile(r"第([一二三四五六七八九十]+)单元")
LESSON = re.compile(r"第([一二三四五六七八九十\d]+)课")
FRAME = re.compile(r"第([一二三四五六七八九十\d]+)框")

KIND = {
    "新授/常态课": ["新授", "常态", "课件ppt", "ppt课件"],
    "复习/总复习": ["复习", "总复习", "中考复习", "期末"],
    "专题/探究": ["专题", "探究", "综合探究", "议题"],
    "试卷/讲评": ["试卷", "试题", "讲评", "练习", "检测"],
    "开学/班会": ["开学第一课", "班会", "家长会"],
}
TAG = {
    "比赛标签": ["一等奖", "优质课", "公开课", "获奖", "赛课", "大赛", "示范课", "精品"],
    "免费/下载词": ["免费", "下载"],
}


def hit(text, words):
    return any(w in text for w in words)


c = {k: 0 for k in KIND}
t = {k: 0 for k in TAG}
books, grades, units, lessons, frames = Counter(), Counter(), Counter(), Counter(), Counter()
subjects = Counter()

for r in rows:
    title = r.get("title", "")
    cat = r.get("cat", "")
    subjects[cat] += 1
    for k, ws in KIND.items():
        if hit(title, ws):
            c[k] += 1
    for k, ws in TAG.items():
        if hit(title, ws):
            t[k] += 1
    m = BOOK.search(title)
    if m:
        g = m.group(1) or m.group(3)
        s = m.group(2) or m.group(4)
        if g and s:
            books[f"{g}{s}"] += 1
    m = GRADE.search(title)
    if m:
        grades[m.group(1)] += 1
    m = UNIT.search(title)
    if m:
        units[m.group(1)] += 1
    if LESSON.search(title):
        lessons[LESSON.search(title).group(1)] += 1
    if FRAME.search(title):
        frames[FRAME.search(title).group(1)] += 1


def show(name, counter, top=12):
    if not counter:
        return
    print(f"--- {name} ---")
    for k, v in counter.most_common(top):
        print(f"   {str(k):16s} {v:4d}  ({v / len(rows) * 100:.1f}%)")
    print()


show("学科/分类分布", subjects, 15)
show("年级册别（从标题解析）", books, 10)
show("年级", grades, 8)
show("单元号", units, 12)
show("课号", lessons, 12)
show("框题号", frames, 6)
show("课型（关键词命中，可多重）", Counter(c))
show("比赛标签（关键词命中）", Counter(t))

print("--- 标题长度 ---")
lens = [len(r.get("title", "")) for r in rows]
lens.sort()
print(f"   中位 {lens[len(lens)//2]} 字，最短 {lens[0]}，最长 {lens[-1]}")
