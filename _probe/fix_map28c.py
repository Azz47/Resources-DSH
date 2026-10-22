# -*- coding: utf-8 -*-
"""build.py 的 from kit import (...) 里补上 grad 与 Img 之外的所需符号。
grad 在 kit.py:167 有定义，只是没被 import。"""
import io

P = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
src = io.open(P, encoding="utf-8").read()

OLD = "from kit import (L, R, CW, TOP, BOT, CH, BOT_SAFE, PANEL, CHALK, SOFT, DIM, FAINT, SEC,"
NEW = "from kit import (L, R, CW, TOP, BOT, CH, BOT_SAFE, PANEL, CHALK, SOFT, DIM, FAINT, grad, SEC,"
assert OLD in src, "import anchor not found"
src = src.replace(OLD, NEW, 1)
io.open(P, "w", encoding="utf-8").write(src)

line = [l for l in src.splitlines() if l.startswith("from kit import")][0]
print("[OK] import line now:\n   %s" % line)
print("   'grad' in import = %s" % ("grad" in line))
