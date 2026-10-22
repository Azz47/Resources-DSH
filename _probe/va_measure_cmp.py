# -*- coding: utf-8 -*-
"""定量对比：真渲染(pptx) vs 预览截图 —— 用已知设计坐标的特征做标定
已知设计（960x540）：hd_rule = 深色横线 x178..640, y120, h2；hd_title 文本框 (44,71,596,42)
"""
from PIL import Image
import os, statistics

T = r"D:\Resources\DSH\_probe\va_true"
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
pairs = [(5, "page-0002.png"), (8, "page-0003.png"), (17, "page-0004.png"), (27, "page-0005.png"),
         (33, "page-0006.png"), (37, "page-0007.png"), (41, "page-0008.png"), (44, "page-0009.png")]


def darkest_row(im, y0, y1, x0, x1, bg):
    """在 y0..y1 内找与背景色差最大的行，返回 (y, 该行平均亮度差, 该行暗像素的 x 跨度)"""
    best = None
    px = im.load()
    for y in range(y0, y1):
        s = 0; xs = []
        for x in range(x0, x1):
            r, g, b = px[x, y]
            d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            s += d
            if d > 150: xs.append(x)
        if best is None or s > best[1]:
            best = (y, s, (min(xs), max(xs)) if xs else None)
    return best


def dark_text_bbox(im, box, thr=120):
    px = im.load()
    x0, y0, x1, y1 = box
    xs = []; ys = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if r < thr and g < thr:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


out = []
for pg, fn in pairs:
    a = Image.open(os.path.join(T, fn)).convert("RGB").resize((960, 540), Image.LANCZOS)
    b = Image.open(os.path.join(S, "%02d.png" % pg)).convert("RGB")
    # 背景基准：取右 1/3 中部（46 页统一 #A0E0B0）
    bg = b.getpixel((800, 300))
    bga = a.getpixel((800, 300))
    # 结构线：在左侧内容列找"最暗的横线"，搜索窗比设计值放宽
    ra = darkest_row(a, 100, 170, 180, 630, bga)
    rb = darkest_row(b, 100, 170, 180, 630, bg)
    # 标题文字包围盒（设计区 x44..640, y60..120）
    ta = dark_text_bbox(a, (44, 55, 645, 145))
    tb = dark_text_bbox(b, (44, 55, 645, 145))
    out.append("p%-3d | 真渲染 rule y=%-4s 跨x=%-14s | 预览 rule y=%-4s 跨x=%-14s | 真渲染标题bbox h=%-4s | 预览标题bbox h=%-4s | bg真%s 预%s" % (
        pg,
        ra[0], ra[2], rb[0], rb[2],
        (ta[3] - ta[1] + 1) if ta else "NA", (tb[3] - tb[1] + 1) if tb else "NA",
        bga, bg))
print("\n".join(out))

# 整页差异比例
import itertools
out2 = []
for pg, fn in pairs:
    a = Image.open(os.path.join(T, fn)).convert("RGB").resize((960, 540), Image.LANCZOS)
    b = Image.open(os.path.join(S, "%02d.png" % pg)).convert("RGB")
    pa = a.load(); pb = b.load()
    diff = 0; tot = 960 * 540
    for y in range(540):
        for x in range(960):
            r1, g1, b1 = pa[x, y]; r2, g2, b2 = pb[x, y]
            if abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2) > 60:
                diff += 1
    out2.append("p%-3d 差异像素 %5.1f%%" % (pg, 100.0 * diff / tot))
print("\n".join(out2))
