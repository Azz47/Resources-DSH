# -*- coding: utf-8 -*-
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
s = io.open(K, encoding="utf-8").read()
old = '{"pos": 100, "color": c1, "alpha": 10}]},\n          {"color": c1, "width": 1.0}'
new = '{"pos": 100, "color": c1, "alpha": 10}]},\n          {"color": c2, "width": 1.2}'
print("hero.outline " + ("OK" if old in s else "MISS"))
io.open(K, "w", encoding="utf-8").write(s.replace(old, new, 1))
