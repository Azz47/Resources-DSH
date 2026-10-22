# -*- coding: utf-8 -*-
"""hero 底板亮底化：grad(c2,c2,90,3) 的语义是「实色 c2 渐变到透明」，最上层实底就是 c2 深色
   -> 亮底方案下深字压深板不可读（#17251D on #1F6383 = 2.40 / #2E4438 on #1F6383 = 1.59）。
   改成浅色 c1 低透明度渐变板 + c2 描边，深字自然可读，同时保留「衬板」的仪式感。"""
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
s = io.open(K, encoding="utf-8").read()
log = []
pairs = [
    ('"roundRect", grad(c2, c2, 90, 3),',
     '"roundRect", {"type": "gradient", "angle": 90, "stops": [{"pos": 0, "color": c1, "alpha": 32}, {"pos": 100, "color": c1, "alpha": 10}]},',
     "hero.panel"),
    ('grad(c2, c2, 90, 3),\n          {"color": c1, "width": 1.0}',
     'grad(c2, c2, 90, 3),\n          {"color": c2, "width": 1.0}',
     "hero.outline"),
    ('S("hr_edge", [L, y + 10, 5, h - 20], "rect", grad(c1, c1, 90, 12),',
     'S("hr_edge", [L, y + 10, 5, h - 20], "rect", grad(c2, c2, 90, 22),',
     "hero.edge"),
]
for old, new, tag in pairs:
    if old in s:
        s = s.replace(old, new, 1); log.append(tag + " OK")
    else:
        log.append("MISS:" + tag)
io.open(K, "w", encoding="utf-8").write(s)
print("PATCH " + " | ".join(log))
