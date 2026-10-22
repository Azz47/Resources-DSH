# -*- coding: utf-8 -*-
"""底角贴纸 vs 注记条：裁左下/右下角放大，检查是否与内容相撞。"""
from PIL import Image, ImageDraw
import os

SH = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
PGS = [4, 16, 23, 27, 33, 41, 44, 46]
# 左下角 x0..170 y395..540；右下角 x600..960 y395..540
regions = [("左下角", (0, 395, 170, 540)), ("右下角", (600, 395, 960, 540))]
Z = 3
cells = []
for name, box in regions:
    w, h = box[2] - box[0], box[3] - box[1]
    sheet = Image.new("RGB", (w * Z, (h * Z + 26) * len(PGS)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for k, pg in enumerate(PGS):
        im = Image.open(os.path.join(SH, "%02d.png" % pg)).convert("RGB")
        c = im.crop(box).resize((w * Z, h * Z), Image.LANCZOS)
        y = k * (h * Z + 26)
        d.text((6, y + 6), "%s  p%02d" % (name, pg), fill=(0, 0, 0))
        sheet.paste(c, (0, y + 24))
    cells.append(sheet)
W = sum(c.width for c in cells)
H = max(c.height for c in cells)
out = Image.new("RGB", (W, H), (255, 255, 255))
x = 0
for c in cells:
    out.paste(c, (x, 0)); x += c.width
out.save(r"D:\Resources\DSH\_probe\va_corners.png")
print(out.size)

# 定量：注记条左端 vs 贴纸右缘 —— 找 y=430 行上「非背景色」的连通段
import collections
for pg in PGS:
    im = Image.open(os.path.join(SH, "%02d.png" % pg)).convert("RGB")
    # 背景色 = 右 1/3 采样
    bg = im.getpixel((800, 300))
    row = 440
    segs, cur = [], None
    for x in range(0, 700):
        r, g, b = im.getpixel((x, row))
        diff = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
        if diff > 60:
            if cur is None: cur = x
        else:
            if cur is not None: segs.append((cur, x - 1)); cur = None
    if cur is not None: segs.append((cur, 699))
    print("p%02d y=440 非背景段: %s" % (pg, segs[:8]))
