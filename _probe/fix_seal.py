# -*- coding: utf-8 -*-
"""环节印章：fill 的 alpha 在渲染端未生效（实底就是 c1 浅色），深色印字压浅底只有 2.94。
   改成 c2 实底 + 白字（各环节 c2 都是深色，白字一律 7:1 以上）。"""
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
s = io.open(K, encoding="utf-8").read()
log = []
for old, new, tag in [
    ('{"color": c1, "alpha": 14}, {"color": c1, "width": 1.6}',
     '{"color": c2, "alpha": 100}, {"color": c2, "width": 1.2}', "seal.fill"),
    ('T("hr_sealt", [R - 64, y + h - 41, 38, 20], seal, 15, c1, HEI, bold=True,',
     'T("hr_sealt", [R - 64, y + h - 41, 38, 20], seal, 15, "#FFFFFF", HEI, bold=True,', "seal.text"),
]:
    if old in s:
        s = s.replace(old, new, 1); log.append(tag + " OK")
    else:
        log.append("MISS:" + tag)
io.open(K, "w", encoding="utf-8").write(s)
print("PATCH " + " | ".join(log))
