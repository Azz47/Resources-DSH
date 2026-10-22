# -*- coding: utf-8 -*-
"""像素级采样：底部注记条底色/页背景/卡片底色，逐页取色，判定跨页一致性。"""
from PIL import Image
import os, io, collections, json

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")


def px(im, x, y):
    return im.getpixel((x, y))


def mode_color(im, box):
    """区域内出现最多的颜色（量化到 8 级以抗压缩噪声）"""
    c = collections.Counter()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = im.getpixel((x, y))
            c[(r // 8 * 8, g // 8 * 8, b // 8 * 8)] += 1
    return c.most_common(3)


def hx(t):
    return "#%02X%02X%02X" % t


rows = []
for i in range(1, 47):
    im = Image.open(os.path.join(SH, "%02d.png" % i)).convert("RGB")
    # 背景采样：内容列左外侧留白 + 右 1/3 讲师区 + 上留白
    bg_left = mode_color(im, (300, 300, 330, 330))[0][0]
    bg_right = mode_color(im, (760, 300, 800, 340))[0][0]
    bg_right2 = mode_color(im, (860, 430, 900, 470))[0][0]
    # 底部注记区：横条底色（避开左侧 caption chip，取右半）
    bar = mode_color(im, (420, 440, 560, 452))[0][0]
    bar2 = mode_color(im, (480, 424, 600, 436))[0][0]
    # caption chip 区域
    cap = mode_color(im, (46, 424, 170, 440))[0][0]
    # 卡片白底样本（中上部）
    card = mode_color(im, (300, 200, 340, 230))[0][0]
    rows.append(dict(pg=i, bgL=hx(bg_left), bgR=hx(bg_right), bgR2=hx(bg_right2),
                     bar=hx(bar), bar2=hx(bar2), cap=hx(cap), card=hx(card)))

o = []
o.append("pg  | 背景(内容列外) | 背景(右1/3 300h) | 背景(右1/3 430h) | 底条色(440行) | 底条色(424行) | caption片 | 卡片样本")
for r in rows:
    o.append("p%-3d| %-15s | %-15s | %-16s | %-13s | %-13s | %-9s | %s" % (
        r["pg"], r["bgL"], r["bgR"], r["bgR2"], r["bar"], r["bar2"], r["cap"], r["card"]))

o.append("\n==== 统计 ====")
for k, label in [("bgL", "背景(内容列外)"), ("bgR", "背景(右1/3,300h)"), ("bgR2", "背景(右1/3,430h)"),
                 ("bar", "底条色(y440)"), ("bar2", "底条色(y424)"), ("cap", "caption片"), ("card", "卡片样本")]:
    c = collections.Counter(r[k] for r in rows)
    o.append("  %-18s 种类=%d  %s" % (label, len(c), c.most_common(8)))

o.append("\n==== 视觉上不可辨的近似簇（ΔRGB<=24 视为同族）====")
def cluster(vals):
    groups = []
    for v, n in collections.Counter(vals).most_common():
        t = tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
        for g in groups:
            if all(abs(t[j] - g[0][j]) <= 24 for j in range(3)):
                g[1].append((v, n)); g[0] = tuple(sum(x[0][j] * x[1] for x in g[1]) // sum(x[1] for x in g[1]) for j in range(3)); break
        else:
            groups.append([t, [(v, n)]])
    return groups
for k, label in [("bgR2", "背景(右1/3)"), ("bar", "底条色(y440)"), ("cap", "caption片")]:
    gs = cluster([r[k] for r in rows])
    o.append("  %s → %d 个色族:" % (label, len(gs)))
    for g in gs:
        pgs = [r["pg"] for r in rows if r[k] in [x[0] for x in g[1]]]
        o.append("     %-9s 页数=%-3d %s" % (hx(g[0]), len(pgs), pgs))
io.open(r"D:\Resources\DSH\_probe\va_color_report.txt", "w", encoding="utf-8").write("\n".join(o))
json.dump(rows, io.open(r"D:\Resources\DSH\_probe\va_color.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK")
