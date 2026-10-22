# -*- coding: utf-8 -*-
"""确定性测量：形状/背景在"真渲染"与"预览截图"中的相对占比是否一致"""
from PIL import Image
import os

T = r"D:\Resources\DSH\_probe\va_true"
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"

def load(path, size=(960, 540)):
    return Image.open(path).convert("RGB").resize(size, Image.LANCZOS)

def near(c, t, tol=42):
    return abs(c[0] - t[0]) <= tol and abs(c[1] - t[1]) <= tol and abs(c[2] - t[2]) <= tol

def mask_extent(im, target, tol=42, y=None):
    """返回 target 色像素的 x 范围（占宽比）；y 给定时只看该行"""
    px = im.load(); W, H = im.size
    xs = []
    ys = range(y, y + 1) if y is not None else range(H)
    for yy in ys:
        for x in range(W):
            if near(px[x, yy], target, tol):
                xs.append(x)
    if not xs:
        return None
    return (min(xs), max(xs), min(xs) / W, max(xs) / W)

def row_extent(im, target, y, tol=42):
    px = im.load(); W = im.size[0]
    xs = [x for x in range(W) if near(px[x, y], target, tol)]
    return (min(xs), max(xs), min(xs) / W, max(xs) / W) if xs else None

AMBER = (232, 192, 88)
MINT = (160, 224, 176)
WHITE = (255, 255, 255)

print("== 设计基准：内容右界 640/960 = 0.6667 ; 页背景 #A0E0B0 ; 横条 44..640 = 0.0458..0.6667 ==")
print()
for pg, fn, ybar in [(17, "page-0004.png", 430), (33, "page-0006.png", 430)]:
    a = load(os.path.join(T, fn))
    b = load(os.path.join(S, "%02d.png" % pg))
    print("--- p%d ---" % pg)
    for tag, im in (("真渲染", a), ("预览 ", b)):
        am = row_extent(im, AMBER, ybar)
        wh = mask_extent(im, WHITE, tol=10)
        mi = row_extent(im, MINT, 300)
        print("  %s y=%d 琥珀条 x范围=%s" % (tag, ybar, am))
        print("  %s 白色像素 x范围=(%.3f..%.3f) 占比宽度 %.1f%%" % (
            tag, wh[2], wh[3], (wh[3] - wh[2]) * 100))
        print("  %s y=300 薄荷背景 x范围=%s" % (tag, mi))
    print()

# 背景木框内沿（板面左边界）扫描：找最左侧的大片薄荷
print("--- 木框内沿（薄荷起始 x 占比）---")
for pg, fn in [(17, "page-0004.png"), (33, "page-0006.png"), (5, "page-0002.png")]:
    a = load(os.path.join(T, fn)); b = load(os.path.join(S, "%02d.png" % pg))
    for tag, im in (("真渲染", a), ("预览 ", b)):
        px = im.load(); W, H = im.size
        row = H // 2
        first = None
        for x in range(W):
            if near(px[x, row], MINT, 50):
                first = x; break
        # 右侧薄荷终点
        last = None
        for x in range(W - 1, -1, -1):
            if near(px[x, row], MINT, 50):
                last = x; break
        print("  p%-3d %s 薄荷板面 y=中间 : x %.3f → %.3f" % (pg, tag, first / W, last / W))
