# -*- coding: utf-8 -*-
"""无障碍复核实测：#2F7A5C on #A2E6B5（板书底）= 3.57:1，低于 AA 正文 4.5:1，
   命中 p1 封面进度行 / p5 总议题 / p28 收束行 / p32 引语出处 / p34 展墙标题。
   统一压深到 #1F5C42（重新实测对比度），一处改色两处引用（kit.SEC + theme.mint2）。"""
import io
D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools"
OLD, NEW = "#2F7A5C", "#1F5C42"

def rel_lum(h):
    c = h.lstrip("#"); r, g, b = (int(c[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)

def cr(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

BG = "#A2E6B5"
print("对比度  %s on %s = %.2f:1  ->  %s on %s = %.2f:1" % (OLD, BG, cr(OLD, BG), NEW, BG, cr(NEW, BG)))
for f in ("kit.py", "build.py"):
    p = D + "\\" + f
    s = io.open(p, encoding="utf-8").read()
    n = s.count(OLD)
    if n:
        io.open(p, "w", encoding="utf-8").write(s.replace(OLD, NEW))
    print("  %-9s 替换 %d 处" % (f, n))
