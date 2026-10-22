# -*- coding: utf-8 -*-
"""亮底化 v3：不要矩形保护框（v2 在底部留下 3 块深绿补丁）；纯靠颜色掩膜，
   用具本身（白/木/彩）不是绿系，天然不受影响。"""
from PIL import Image, ImageFilter
import numpy as np

SRC = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.jpeg"
OUT = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.light.jpeg"

a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]
lum = 0.299 * r + 0.587 * g + 0.114 * b

green = (g > r * 1.03) & (g > b * 1.01) & (lum < 178)
lo, hi = np.percentile(lum[green], 2), np.percentile(lum[green], 98)
t = np.clip((lum - lo) / max(hi - lo, 1.0), 0, 1)
target = 206.0 + t * 36.0
out = a * (target / np.maximum(lum, 1.0))[..., None]
out = out * 0.88 + np.array([252.0, 253.0, 250.0]) * 0.12
res = np.where(green[..., None], np.clip(out, 0, 255), a)

m = np.asarray(Image.fromarray((green * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255.0
final = a * (1 - m[..., None]) + res * m[..., None]
Image.fromarray(final.astype(np.uint8)).save(OUT, quality=92)

chk = np.asarray(Image.open(OUT).convert("RGB")).astype(np.float32)
L2 = 0.299*chk[...,0] + 0.587*chk[...,1] + 0.114*chk[...,2]
print("平均亮度 %.1f -> %.1f   亮底占比 %.3f -> %.3f" % (lum.mean(), L2.mean(), (lum>=200).mean(), (L2>=200).mean()))
for y0 in (700, 752, 790):
    band = L2[y0:y0+20, :]
    print("  y%-3d 左/中/右 = %.0f / %.0f / %.0f" % (y0, band[:, :400].mean(), band[:, 400:1000].mean(), band[:, 1000:].mean()))
