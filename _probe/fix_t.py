# -*- coding: utf-8 -*-
"""T() 签名跨两行，上一版正则没命中；改为按行定位签名结尾后插入。"""
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
L = io.open(K, encoding="utf-8").read().split("\n")
if any("DARK.get(color" in x for x in L):
    print("ALREADY DONE")
else:
    i = next(n for n, x in enumerate(L) if x.startswith("def T("))
    j = next(n for n in range(i, i + 8) if L[n].rstrip().endswith("):"))
    L.insert(j + 1, "    color = DARK.get(color, color)   # 亮底收口：浅色环节色 -> 同族深色")
    io.open(K, "w", encoding="utf-8").write("\n".join(L))
    print("INSERTED after line %d: %s" % (j + 1, L[j].strip()[:60]))
