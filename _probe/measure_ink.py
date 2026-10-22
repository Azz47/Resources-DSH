# -*- coding: utf-8 -*-
"""在指定页的指定 y 区间里找"墨迹"（深色像素）的水平范围，用来验证文字实际占多宽。

用法: python measure_ink.py <page.png> <y0_frac> <y1_frac> [dpi]
"""
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

p = sys.argv[1]
y0 = float(sys.argv[2])
y1 = float(sys.argv[3])
dpi = float(sys.argv[4]) if len(sys.argv) > 4 else 110.0

im = Image.open(p).convert("L")
a = np.asarray(im)
h, w = a.shape
band = a[int(h * y0):int(h * y1), :]

# 深色像素 = 墨迹（模板底色是浅灰 #f0f0f0 左右，页眉绿带另算）
dark = band < 110
cols = np.where(dark.sum(axis=0) > 0)[0]
rows = np.where(dark.sum(axis=1) > 0)[0]

print(f"页面 {w}x{h}px  @{dpi}dpi  = {w / dpi:.2f}x{h / dpi:.2f} in")
print(f"y 区间 {y0:.2f}~{y1:.2f}  →  {int(h * y0)}~{int(h * y1)}px")
if len(cols) == 0:
    print("  该区间无墨迹")
else:
    print(f"  墨迹 x: {cols[0]}~{cols[-1]}px  =  {cols[0] / dpi:.2f}~{cols[-1] / dpi:.2f} in   宽 {(cols[-1] - cols[0]) / dpi:.2f} in")
    # 分列：找连续的墨迹段，能看出断行位置
    gaps = np.where(np.diff(cols) > 8)[0]
    if len(gaps):
        segs, s = [], cols[0]
        for g in gaps:
            segs.append((s, cols[g]))
            s = cols[g + 1]
        segs.append((s, cols[-1]))
        print("  横向分段:", " | ".join(f"{x0 / dpi:.2f}~{x1 / dpi:.2f}" for x0, x1 in segs))
    print(f"  墨迹 y: {rows[0]}~{rows[-1]}px  高 {(rows[-1] - rows[0]) / dpi:.2f} in  (区间内相对)")
