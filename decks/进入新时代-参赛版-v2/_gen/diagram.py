# -*- coding: utf-8 -*-
"""黄河几字弯示意图（自绘，示意非地理实测）"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 600, 440
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")

INK = (23, 36, 46, 255)
RUST = (156, 67, 39, 255)
STEEL = (42, 100, 128, 255)
FAINT = (120, 138, 148, 255)

FONT = None
for p in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc",
          r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\Deng.ttf"):
    if os.path.exists(p):
        FONT = p
        break


def f(sz, bold=False):
    cands = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"] if bold else [FONT]
    for c in cands:
        if c and os.path.exists(c):
            try:
                return ImageFont.truetype(c, sz)
            except Exception:
                pass
    return ImageFont.load_default()


img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 河道（示意走向：源头→兰州→河套→几字弯→河口镇→壶口→三门峡→利津→入海）
pts = [(44, 300), (120, 296), (196, 288), (252, 268), (286, 214), (300, 150),
       (306, 108), (360, 100), (404, 108), (416, 160), (418, 226), (430, 286),
       (462, 330), (512, 344), (562, 350)]
d.line(pts, fill=STEEL, width=7, joint="curve")
for p in pts:
    d.ellipse([p[0] - 3.5, p[1] - 3.5, p[0] + 3.5, p[1] + 3.5], fill=STEEL)

# 断流段（利津以下，虚线）
x0, y0 = 468, 332
x1 = 566
xx = x0
while xx < x1:
    nx = min(xx + 10, x1)
    d.line([(xx, 332 + (xx - x0) * 0.18), (nx, 332 + (nx - x0) * 0.18)], fill=RUST, width=5)
    xx += 19
d.ellipse([x0 - 6, 326, x0 + 6, 338], fill=RUST)

# 节点
nodes = [(44, 300, "源头", "center", -26),
         (196, 288, "兰州", "center", 14),
         (352, 100, "河套", "center", -24),
         (418, 226, "河口镇", "left", 6),
         (430, 286, "壶口", "left", 14)]


def put(x, y, name, anchor, dy):
    ft = f(17, True)
    tw = d.textlength(name, font=ft)
    tx = x - tw / 2 if anchor == "center" else x + 10
    d.text((tx, y + dy), name, font=ft, fill=INK)


for (x, y, name, anchor, dy) in nodes:
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, 255), outline=INK, width=2)
    put(x, y, name, anchor, dy)

# 断流标注
ft = f(15, True)
d.text((286, 372), "利津断面 1972—1999 年间有 22 年断流", font=ft, fill=RUST)
d.line([(430, 366), (470, 340)], fill=RUST, width=1)

# 图注
ft2 = f(13)
d.text((30, 36), "黄河干流走向 · 示意图（非地理实测）", font=ft2, fill=FAINT)

img.save(os.path.join(OUT, "doc_yellowriver.png"))
print("wrote doc_yellowriver.png", os.path.getsize(os.path.join(OUT, "doc_yellowriver.png")))
