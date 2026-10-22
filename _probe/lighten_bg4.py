# -*- coding: utf-8 -*-
"""亮底化 v4：压一档。v3 平均亮度 207 偏亮，目标回到 185 上下（朋友版 192）。"""
from PIL import Image, ImageFilter
import numpy as np

SRC = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.jpeg"
OUT = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.light.jpeg"

a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
lum = 0.299 * r + 0.587 * g + 0.114 * b
green = (g > r * 1.03) & (g > b * 1.01) & (lum < 178)

lo, hi = np.percentile(lum[green], 2), np.percentile(lum[green], 98)
t = np.clip((lum - lo) / max(hi - lo, 1.0), 0, 1)
target = 182.0 + t * 34.0          # 182..216（v3 是 206..242）
out = a * (target / np.maximum(lum, 1.0))[..., None]
out = out * 0.92 + np.array([250.0, 251.0, 247.0]) * 0.08
res = np.where(green[..., None], np.clip(out, 0, 255), a)
m = np.asarray(Image.fromarray((green * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255.0
final = a * (1 - m[..., None]) + res * m[..., None]
Image.fromarray(final.astype(np.uint8)).save(OUT, quality=92)

L2 = 0.299*final[...,0] + 0.587*final[...,1] + 0.114*final[...,2]
print("EMU mean %.1f -> %.1f   light_ratio %.3f" % (lum.mean(), L2.mean(), (L2>=200).mean()))
for y0 in (700, 752, 790):
    bd = L2[y0:y0+20, :]
    print("  y%-3d L/M/R %.0f/%.0f/%.0f" % (y0, bd[:, :400].mean(), bd[:, 400:1000].mean(), bd[:, 1000:].mean()))
print("board_sample %.0f" % L2[300:400, 300:500].mean())
