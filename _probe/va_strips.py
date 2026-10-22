# -*- coding: utf-8 -*-
"""生成横向条带对比图：页眉带 / 底部注记带，用于跨页一致性目视判定"""
from PIL import Image
import os, io

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")

def strip(y0, y1, x0, x1, out, cols=6, scale=0.5):
    imgs = []
    for i in range(1, 47):
        p = os.path.join(SH, "%02d.png" % i)
        im = Image.open(p).convert("RGB").crop((x0, y0, x1, y1))
        im = im.resize((int((x1 - x0) * scale), int((y1 - y0) * scale)), Image.LANCZOS)
        imgs.append(im)
    w, h = imgs[0].size
    rows = (46 + cols - 1) // cols
    canvas = Image.new("RGB", (cols * (w + 4) + 4, rows * (h + 18) + 4), (255, 255, 255))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(canvas)
    for k, im in enumerate(imgs):
        r, c = divmod(k, cols)
        x = 4 + c * (w + 4); y = 4 + r * (h + 18)
        canvas.paste(im, (x, y + 14))
        dr.text((x + 2, y + 1), "p%02d" % (k + 1), fill=(0, 0, 0))
    canvas.save(out)
    return canvas.size

print("header", strip(18, 132, 36, 660, r"D:\Resources\DSH\_probe\va_header_band.png", 5, 0.75))
print("bottom", strip(376, 470, 36, 660, r"D:\Resources\DSH\_probe\va_bottom_band.png", 5, 0.75))

# 背景底图
bg = os.path.join(D, "media", "image1.jpeg")
if os.path.exists(bg):
    im = Image.open(bg)
    print("bg image1.jpeg:", im.size, im.mode, os.path.getsize(bg), "bytes")
    im.convert("RGB").resize((640, 360), Image.LANCZOS).save(r"D:\Resources\DSH\_probe\va_bg_small.png")
else:
    print("bg missing", bg)
    print(os.listdir(os.path.join(D, "media"))[:20])
