# -*- coding: utf-8 -*-
"""真渲染(LibreOffice) vs 预览截图 并排对比：抓 pptd 预览与真实导出的分叉"""
from PIL import Image, ImageDraw
import os

T = r"D:\Resources\DSH\_probe\va_true"
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
pairs = [(1, "page-0001.png"), (5, "page-0002.png"), (8, "page-0003.png"), (17, "page-0004.png"),
         (27, "page-0005.png"), (33, "page-0006.png"), (37, "page-0007.png"), (41, "page-0008.png"),
         (44, "page-0009.png"), (46, "page-0010.png")]
W, H = 470, 264
rows = 5
canvas = Image.new("RGB", (2 * (W + 6) + 6 + 2 * (W + 6), rows * (H + 20) + 6), (255, 255, 255))
dr = ImageDraw.Draw(canvas)
for idx, (pg, fn) in enumerate(pairs):
    r, c = divmod(idx, 2)
    a = Image.open(os.path.join(T, fn)).convert("RGB").resize((W, H), Image.LANCZOS)
    b = Image.open(os.path.join(S, "%02d.png" % pg)).convert("RGB").resize((W, H), Image.LANCZOS)
    x0 = 6 + c * (2 * (W + 6))
    y0 = 6 + r * (H + 20)
    dr.text((x0, y0), "p%02d LibreOffice渲染" % pg, fill=(180, 0, 0))
    canvas.paste(a, (x0, y0 + 16))
    dr.text((x0 + W + 12, y0), "p%02d pptd预览截图" % pg, fill=(0, 90, 180))
    canvas.paste(b, (x0 + W + 12, y0 + 16))
# 只保留上半部分即可看；输出全图
canvas.save(r"D:\Resources\DSH\_probe\va_true_vs_preview.png")
print(canvas.size)
