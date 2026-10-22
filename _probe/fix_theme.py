# -*- coding: utf-8 -*-
"""修两处根因：
   ① 主题色板的 chalk/soft 仍是硬编码白系 -> 改成引用同一批常量（241 个 theme-conformance 错误的总根因）
   ② 亮底上任何用「浅色环节色」当文字色的地方都不可读（#7FD6B0 on #FFFFFF = 1.73）
      -> 在唯一的文字工厂 T() 里统一把浅色环节色换成同族深色，一处收口，46 页全覆盖"""
import io, re

K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
B = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
log = []

k = io.open(K, encoding="utf-8").read()
if "DARK = {v[0]: v[1]" not in k:
    k = k.replace("SEC_LABEL = {", "DARK = {v[0]: v[1] for v in SEC.values()}   # 亮底：浅色环节色不可作文字色，统一换同族深色\nSEC_LABEL = {", 1)
    log.append("kit.DARK added")
m = re.search(r"\ndef T\(([^\n]*)\):", k)
if m and "DARK.get(color" not in k:
    head = m.group(0)
    args = [a.strip().split("=")[0].strip() for a in m.group(1).split(",")]
    if "color" in args:
        k = k.replace(head, head + "\n    color = DARK.get(color, color)   # 亮底收口：浅色 -> 同族深色", 1)
        log.append("kit.T swap added")
    else:
        log.append("MISS: T has no color arg -> " + m.group(1)[:80])
io.open(K, "w", encoding="utf-8").write(k)

b = io.open(B, encoding="utf-8").read()
for old, new, tag in [
    ('    chalk: "#FFFFFF"', '    chalk: "%s"' % "#17251D", "theme.chalk"),
    ('    soft: "#E4EEE2"',  '    soft: "%s"' % "#2E4438", "theme.soft"),
]:
    if old in b:
        b = b.replace(old, new, 1); log.append(tag)
    else:
        log.append("MISS:" + tag)
io.open(B, "w", encoding="utf-8").write(b)
print("PATCH " + " | ".join(log))
