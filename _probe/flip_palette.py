# -*- coding: utf-8 -*-
"""亮底调色板翻转：把 5 个调色板常量由「深底白字」翻成「亮底深字」。
   透明/半透明元素（环节胶囊 78% alpha、编号徽章 58% alpha、卡片左沿渐隐）本来就是
   半透明的，在亮底上自动仍成立 —— 只翻实色常量，不动版式。"""
import io, os, shutil

K = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\kit.py"
src = io.open(K, encoding="utf-8").read()
pairs = [
    ('PANEL = "#2A4436"           # 卡片底板（黑板底色加深一档）',
     'PANEL = "#FFFFFF"           # 卡片底板：亮底方案用纯白卡片'),
    ('PANEL2 = "#234536"', 'PANEL2 = "#F2F7F0"'),
    ('CHALK = "#FFFFFF"', 'CHALK = "#17251D"           # 主文本：亮底上改用深墨'),
    ('SOFT = "#E4EEE2"',  'SOFT = "#2E4438"            # 次级文本'),
    ('DIM = "#C2D8C2"',   'DIM = "#3E574A"             # 三级文本'),
    ('FAINT = "#BCD0BC"', 'FAINT = "#46604F"           # 最小注记（对比度 4.8:1 达标）'),
]
hit = []
for old, new in pairs:
    if old in src:
        src = src.replace(old, new, 1); hit.append(old.split("=")[0].strip())
    else:
        hit.append("MISS:" + old.split("=")[0].strip())
io.open(K, "w", encoding="utf-8").write(src)

B = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
tb = io.open(B, encoding="utf-8").read()
tpairs = [
    ('    board: "#2E4A3D"', '    board: "#CDDACF"'),
]
for old, new in tpairs:
    if old in tb:
        tb = tb.replace(old, new, 1); hit.append("build.board")
    else:
        hit.append("MISS:build.board")
io.open(B, "w", encoding="utf-8").write(tb)

# 背景图换新（原深底图留档）
M = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\media"
if not os.path.exists(os.path.join(M, "image1.dark.jpeg")):
    shutil.copy2(os.path.join(M, "image1.jpeg"), os.path.join(M, "image1.dark.jpeg"))
shutil.copy2(os.path.join(M, "image1.light.jpeg"), os.path.join(M, "image1.jpeg"))
print("PATCH " + " | ".join(hit))
print("BG 已换为亮底；深底原图留档 media/image1.dark.jpeg")
