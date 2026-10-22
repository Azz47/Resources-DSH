# -*- coding: utf-8 -*-
"""pptx 真渲染 vs 预览截图：同一页同一区域等高放大对比（页眉带 / 顶部元素）"""
from PIL import Image, ImageDraw
import os
T = r"D:\Resources\DSH\_probe\va_true"
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
# (原页号, 真渲染文件名)
pairs = [(5, "page-0002.png"), (8, "page-0003.png"), (17, "page-0004.png"), (27, "page-0005.png"),
         (33, "page-0006.png"), (37, "page-0007.png"), (41, "page-0008.png"), (44, "page-0009.png")]
# 真渲染 1921x1081 对应 960x540 → 缩放系数 2.001
Z = 1921.0 / 960.0
box = (30, 8, 660, 140)  # 960x540 坐标系
w = box[2] - box[0]; h = box[3] - box[1]
sc = 1.5
cw, ch = int(w * sc), int(h * sc)
canvas = Image.new("RGB", (2 * cw + 30, len(pairs) * (ch + 24) + 8), (255, 255, 255))
dr = ImageDraw.Draw(canvas)
for i, (pg, fn) in enumerate(pairs):
    a_full = Image.open(os.path.join(T, fn)).convert("RGB")
    a = a_full.crop((int(box[0] * Z), int(box[1] * Z), int(box[2] * Z), int(box[3] * Z))).resize((cw, ch), Image.LANCZOS)
    b = Image.open(os.path.join(S, "%02d.png" % pg)).convert("RGB").crop(box).resize((cw, ch), Image.LANCZOS)
    y = 8 + i * (ch + 24)
    dr.text((8, y), "p%02d  ← LibreOffice真渲染        pptd预览截图 →" % pg, fill=(160, 0, 0))
    canvas.paste(a, (8, y + 16))
    canvas.paste(b, (cw + 22, y + 16))
canvas.save(r"D:\Resources\DSH\_probe\va_top_cmp.png")
print(canvas.size)
