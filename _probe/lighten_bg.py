# -*- coding: utf-8 -*-
"""亮底化 v1：把黑板绿 -> 淡薄荷白，木框/木托/书堆/粉笔保持原样。
   只做背景图；不覆盖原图，输出 image1.light.jpeg 供对比。"""
from PIL import Image, ImageFilter
import numpy as np, sys

SRC = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.jpeg"
OUT = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media\image1.light.jpeg"

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.float32)
H, W, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]
lum = 0.299 * r + 0.587 * g + 0.114 * b

# 绿系像素：G 明显高于 R/B，且整体偏暗（黑板/绿墙），排除白粉笔、木框、书
green = (g > r * 1.04) & (g > b * 1.02) & (lum < 175)
# 保护：右侧书堆、底部用具带（y>680 且 x<200 或 x>620 的已成物区域）不动
yy = np.arange(H)[:, None] * np.ones((1, W))
guard = (yy > 676) & ((np.arange(W)[None, :] < 210) | (np.arange(W)[None, :] > 610))
mask = green & ~guard

# 暗->亮线性重映射：保留纹理与明暗层次，只把整体抬到大亮区
lo, hi = np.percentile(lum[mask], 2), np.percentile(lum[mask], 98)
t = np.clip((lum - lo) / max(hi - lo, 1.0), 0, 1)
target = 208.0 + t * 34.0            # 208..242 淡薄荷白
scale = (target / np.maximum(lum, 1.0))[..., None]
out = a * scale
# 轻微向暖白收一点色（黑板绿留 14% 色相，避免死灰）
out = out * 0.86 + np.array([252.0, 253.0, 250.0]) * 0.14
res = np.where(mask[..., None], np.clip(out, 0, 255), a)

# 边界羽化，防硬边
m = (mask * 255).astype(np.uint8)
m = np.asarray(Image.fromarray(m).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255.0
final = a * (1 - m[..., None]) + res * m[..., None]
Image.fromarray(final.astype(np.uint8)).save(OUT, quality=92)

chk = np.asarray(Image.open(OUT).convert("RGB")).astype(np.float32)
L2 = 0.299*chk[...,0] + 0.587*chk[...,1] + 0.114*chk[...,2]
print("SRC 平均亮度 %.1f -> OUT %.1f" % (lum.mean(), L2.mean()))
print("亮底占比(>=200): SRC %.3f -> OUT %.3f" % ((lum>=200).mean(), (L2>=200).mean()))
print("输出:", OUT)
