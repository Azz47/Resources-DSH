# -*- coding: utf-8 -*-
"""亮底化 v2：用精确用具包围盒保护，代替 v1 的粗粒度 y>676 切分（v1 在底部留下色块补丁）。"""
from PIL import Image, ImageFilter
import numpy as np

SRC = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.jpeg"
OUT = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.light.jpeg"

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.float32)
H, W, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]
lum = 0.299 * r + 0.587 * g + 0.114 * b
X = np.arange(W)[None, :]; Y = np.arange(H)[:, None]

# 用具精确包围盒（实测）：记事本簇 / 粉笔 / 书堆，各留 10px 余量
props = [(-8, 676, 168, 806), (665, 674, 806, 746), (1283, 592, 1440, 766)]
guard = np.zeros((H, W), bool)
for x0, y0, x1, y1 in props:
    guard |= (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)

green = (g > r * 1.03) & (g > b * 1.01) & (lum < 178)
mask = green & ~guard

lo, hi = np.percentile(lum[mask], 2), np.percentile(lum[mask], 98)
t = np.clip((lum - lo) / max(hi - lo, 1.0), 0, 1)
target = 206.0 + t * 36.0
out = a * (target / np.maximum(lum, 1.0))[..., None]
out = out * 0.88 + np.array([252.0, 253.0, 250.0]) * 0.12
res = np.where(mask[..., None], np.clip(out, 0, 255), a)

m = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255.0
final = a * (1 - m[..., None]) + res * m[..., None]
Image.fromarray(final.astype(np.uint8)).save(OUT, quality=92)

chk = np.asarray(Image.open(OUT).convert("RGB")).astype(np.float32)
L2 = 0.299*chk[...,0] + 0.587*chk[...,1] + 0.114*chk[...,2]
print("平均亮度 %.1f -> %.1f" % (lum.mean(), L2.mean()))
print("亮底占比(>=200) %.3f -> %.3f" % ((lum>=200).mean(), (L2>=200).mean()))
# 底部条带单独体检：整条亮度是否均匀（防再次出现补丁）
band = L2[752:800, :]
print("底部墙带 y752-800 亮度 左/中/右 = %.0f / %.0f / %.0f" % (band[:, :400].mean(), band[:, 400:1000].mean(), band[:, 1000:].mean()))
