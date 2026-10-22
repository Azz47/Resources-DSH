# -*- coding: utf-8 -*-
"""p37 H2bar_t：#2E4438 深字压在 #3D5A4A 深条上 = 1.38:1（接近不可读）。
   根因是 bar() 的文字色写死为深墨，但条底色可能是深色（如 theme 的 rule 色）。
   加一个 WCAG 相对亮度判据：深条自动翻白字，一处收口。"""
import io
K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
s = io.open(K, encoding="utf-8").read()
log = []

helper = '''
def rel_lum(hexcolor):
    """WCAG 相对亮度（0 = 黑 / 1 = 白）。用于「深底自动翻白字」这类自适应取色。"""
    c = hexcolor.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


'''
anchor = 'FAINT = "#46604F"           # 最小注记（对比度 4.8:1 达标）\n'
if "def rel_lum(" not in s and anchor in s:
    s = s.replace(anchor, anchor + helper, 1); log.append("rel_lum OK")
else:
    log.append("MISS:rel_lum")

old = '''    h = h or need_h(text, w - 2 * pad, size, 1.35) + 12
    els = ['''
new = '''    h = h or need_h(text, w - 2 * pad, size, 1.35) + 12
    if color == "#12241B" and isinstance(accent, str) and rel_lum(accent) < 0.42:
        color = "#FFFFFF"      # 深色横条上深字不可读（p37 H2bar_t 实测 1.38:1），自动翻白
    els = ['''
if old in s:
    s = s.replace(old, new, 1); log.append("bar.auto OK")
else:
    log.append("MISS:bar.auto")
io.open(K, "w", encoding="utf-8").write(s)
print("PATCH " + " | ".join(log))
