# -*- coding: utf-8 -*-
"""上一版只判 #12241B；p37 的 H2bar 传的是 SOFT(#2E4438)，没命中。
   改成通用判据：条上文字与条底色的对比度 < 4.5 就翻白字。"""
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
s = io.open(K, encoding="utf-8").read()
log = []

old = '    if color == "#12241B" and isinstance(accent, str) and rel_lum(accent) < 0.42:\n        color = "#FFFFFF"      # 深色横条上深字不可读（p37 H2bar_t 实测 1.38:1），自动翻白\n'
new = ('    if isinstance(accent, str):\n'
       '        _la, _lc = rel_lum(accent), rel_lum(color)\n'
       '        if (max(_la, _lc) + 0.05) / (min(_la, _lc) + 0.05) < 4.5:\n'
       '            color = "#FFFFFF"   # 条上文字与条底色对比不足（p37 H2bar_t 实测 1.38:1）自动翻白\n')
if old in s:
    s = s.replace(old, new, 1); log.append("bar.contrast OK")
else:
    log.append("MISS")
io.open(K, "w", encoding="utf-8").write(s)
print("PATCH " + " | ".join(log))
