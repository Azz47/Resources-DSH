# -*- coding: utf-8 -*-
"""细节放大：右下角灰色带 / 底部注记条 chip 与横条关系"""
from PIL import Image, ImageDraw
import os
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"

# A. 右下角区域（讲师站位底部）放大 4x
box = (820, 390, 960, 540)
crops = [Image.open(os.path.join(S, "%02d.png" % p)).convert("RGB").crop(box) for p in (1, 12, 25, 46)]
w, h = crops[0].size
z = 4
canvas = Image.new("RGB", (len(crops) * (w * z + 8) + 8, h * z + 30), (255, 255, 255))
dr = ImageDraw.Draw(canvas)
for i, c in enumerate(crops):
    x = 8 + i * (w * z + 8)
    dr.text((x, 4), "p%02d 右下角 x4" % (1, 12, 25, 46)[i], fill=(0, 0, 0))
    canvas.paste(c.resize((w * z, h * z), Image.NEAREST), (x, 26))
canvas.save(r"D:\Resources\DSH\_probe\va_zoom_br.png")
print("br", canvas.size)

# B. 底部注记条放大 2x（对比 chip 与横条）
pgs = [2, 3, 6, 7, 17, 18, 21, 33, 35, 37, 38, 41, 43, 44]
box2 = (36, 378, 660, 462)
cs = [Image.open(os.path.join(S, "%02d.png" % p)).convert("RGB").crop(box2) for p in pgs]
w2, h2 = cs[0].size
z2 = 2
rowh = h2 * z2 + 22
canvas2 = Image.new("RGB", (w2 * z2 + 16, rowh * len(cs) + 8), (255, 255, 255))
dr2 = ImageDraw.Draw(canvas2)
for i, c in enumerate(cs):
    y = 4 + i * rowh
    dr2.text((6, y), "p%02d" % pgs[i], fill=(200, 0, 0))
    canvas2.paste(c.resize((w2 * z2, h2 * z2), Image.LANCZOS), (8, y + 16))
canvas2.save(r"D:\Resources\DSH\_probe\va_zoom_note.png")
print("note", canvas2.size)
