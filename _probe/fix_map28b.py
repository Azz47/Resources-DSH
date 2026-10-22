# -*- coding: utf-8 -*-
"""修正 fix_map28.py 里用到的常量名：build.py 只 import 了
L/R/CW/TOP/BOT/CH/BOT_SAFE/PANEL/CHALK/SOFT/DIM/FAINT/SEC/SEC_LABEL/KAI/HEI...
没有 GOLD/CYAN/CORAL/LAV/INK —— 改用 SEC 取值，避免 NameError。"""
import io

P = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
src = io.open(P, encoding="utf-8").read()

rep = [
    ('GOLD),',   'SEC["s1"][0]),'),
    ('CYAN),',   'SEC["s2"][0]),'),
    ('CORAL),',  'SEC["s3"][0]),'),
    ('LAV),',    'SEC["end"][0]),'),
    ('{"type": "solid", "color": INK}, None))',
     'grad(CHALK, CHALK), None))'),
]
n = 0
for a, b in rep:
    if a in src:
        src = src.replace(a, b); n += 1
    else:
        print("  [warn] 未命中：%s" % a)
io.open(P, "w", encoding="utf-8").write(src)
print("[OK] 替换 %d 处" % n)

# 回读自证：新块里不应再出现未定义的常量名
import re
blk = src[src.index("# 知识导图：原生矢量重绘"): src.index('emit("p26_map"')]
bad = [w for w in ("GOLD", "CYAN", "CORAL", "LAV", "INK") if re.search(r"\b%s\b" % w, blk)]
print("  未定义常量残留 = %s" % (bad or "无"))
print("  新块元素数 = %d" % blk.count("body.append"))
print("  image19 引用 = %s" % ("仍在" if "image19" in src else "已移除"))
