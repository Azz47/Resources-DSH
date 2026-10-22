# -*- coding: utf-8 -*-
"""注记条底色 vs 条内文字色的 WCAG 对比度（逐条采样）"""
from PIL import Image
import collections, io, os

SH = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
BARS = {2: (44, 416, 640, 456), 3: (44, 400, 640, 456), 9: (44, 418, 640, 456),
        17: (44, 418, 640, 456), 18: (44, 404, 640, 442), 21: (44, 418, 640, 456),
        33: (44, 377, 640, 414), 35: (44, 418, 640, 456), 37: (44, 414, 640, 451),
        38: (44, 385, 640, 423), 41: (44, 403, 640, 456), 43: (44, 418, 640, 456),
        44: (44, 126, 640, 164), 27: (44, 419, 640, 456), 6: (44, 419, 640, 456)}


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hx(t):
    return "#%02X%02X%02X" % t


o = ["页  条底(众数)      条内文字(最暗5%均) 条内文字(最亮5%均) 对比(暗字) 对比(亮字) 判定"]
for pg, (x0, y0, x1, y1) in sorted(BARS.items()):
    im = Image.open(os.path.join(SH, "%02d.png" % pg)).convert("RGB")
    cnt = collections.Counter()
    px = []
    for y in range(y0 + 4, y1 - 2):
        for x in range(x0 + 8, x1 - 8):
            c = im.getpixel((x, y))
            px.append((lum(c), c))
            cnt[(c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)] += 1
    bg = cnt.most_common(1)[0][0]
    px.sort()
    n = max(1, len(px) // 20)
    dark = tuple(sum(c[i] for _, c in px[:n]) // n for i in range(3))
    light = tuple(sum(c[i] for _, c in px[-n:]) // n for i in range(3))
    rd, rl = ratio(bg, dark), ratio(bg, light)
    best = "暗字 %.2f" % rd if rd >= rl else "亮字 %.2f" % rl
    verdict = "OK" if max(rd, rl) >= 4.5 else ("偏低" if max(rd, rl) >= 3.0 else "★不可读")
    o.append("p%-3d %-10s(#%02X%02X%02X)  %-10s  %-10s      %-6.2f   %-6.2f   %s" % (
        pg, hx(bg), bg[0], bg[1], bg[2], hx(dark), hx(light), rd, rl, best + " " + verdict))

# 白卡上的正文 & 薄荷底上的裸字
o.append("")
for pg, box, label in [(17, (58, 254, 318, 358), "白卡正文"), (27, (58, 210, 150, 300), "白卡正文"),
                       (16, (44, 160, 350, 310), "薄荷底裸字"), (33, (44, 418, 640, 456), "裸字脚注")]:
    im = Image.open(os.path.join(SH, "%02d.png" % pg)).convert("RGB")
    cnt = collections.Counter(); px = []
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            c = im.getpixel((x, y)); px.append((lum(c), c))
            cnt[(c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)] += 1
    bg = cnt.most_common(1)[0][0]
    px.sort(); n = max(1, len(px) // 20)
    dark = tuple(sum(c[i] for _, c in px[:n]) // n for i in range(3))
    o.append("p%-3d %-10s 底=%-9s 字=%-9s 对比=%.2f" % (pg, label, hx(bg), hx(dark), ratio(bg, dark)))

io.open(r"D:\Resources\DSH\_probe\va_contrast.txt", "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o))
