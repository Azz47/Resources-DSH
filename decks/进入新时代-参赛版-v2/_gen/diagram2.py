# -*- coding: utf-8 -*-
"""两张自绘示意图：P16 黄河断流时间轴 / P25 盐湖用途演变带。"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "media"))
S = 2  # 超采样倍率（2x）

INK = (23, 36, 46)
MUTED = (59, 75, 87)
RULE = (196, 208, 214)
RUST = (180, 85, 47)
TEAL = (46, 110, 143)
PAPER = (255, 255, 255)

FP = r"C:\Windows\Fonts\msyh.ttc"
FB = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(FB if bold else FP, size * S)
    except Exception:
        return ImageFont.load_default()


def ctext(d, cx, y, txt, size, color, bold=False):
    f = font(size, bold)
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=color)
    return w


# ---------------------------------------------------------------- P16 时间轴
def timeline():
    W, H = 596 * S, 74 * S
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y0 = 40 * S
    # 两段时间条
    d.rectangle([6 * S, y0 - 7 * S, 288 * S, y0 + 7 * S], fill=RUST)
    d.rectangle([288 * S, y0 - 7 * S, 590 * S, y0 + 7 * S], fill=TEAL)
    # 分段标签
    ctext(d, 147 * S, y0 - 30 * S, "1972—1999 ｜ 28 年里有 22 年断流", 12, RUST, True)
    ctext(d, 439 * S, y0 - 30 * S, "1999—2026 ｜ 连续 27 年不断流", 12, TEAL, True)
    # 关键节点
    for x, t, mode in ((44, "1972 首次断流", "l"), (288, "1999.3.1 统一调度", "c"), (552, "2026.8 至今", "r")):
        d.line([x * S, y0 - 12 * S, x * S, y0 + 12 * S], fill=PAPER, width=2 * S)
        f = font(11)
        w = d.textlength(t, font=f)
        tx = x * S if mode == "l" else (x * S - w if mode == "r" else x * S - w / 2)
        d.text((tx, y0 + 14 * S), t, font=f, fill=MUTED)
    img.save(os.path.join(OUT, "doc_timeline.png"))
    print("timeline", os.path.getsize(os.path.join(OUT, "doc_timeline.png")))


# ---------------------------------------------------------------- P25 用途演变
def saltuse():
    W, H = 596 * S, 88 * S
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    nodes = [("4000 余年", "采盐为业", RUST),
             ("2020 年", "停止工业采盐", (138, 106, 34)),
             ("“十四五”以来", "27 项生态修复", TEAL),
             ("今天", "城郊湿地 · 有限游览", (31, 92, 107))]
    n = len(nodes)
    seg = W / n
    y0 = 44 * S
    # 基线
    d.line([10 * S, y0, W - 10 * S, y0], fill=RULE, width=2 * S)
    for i, (when, what, col) in enumerate(nodes):
        cx = int(seg * (i + 0.5))
        d.ellipse([cx - 7 * S, y0 - 7 * S, cx + 7 * S, y0 + 7 * S], fill=col)
        ctext(d, cx, 9 * S, when, 11, MUTED, True)
        ctext(d, cx, y0 + 14 * S, what, 12, INK, True)
    img.save(os.path.join(OUT, "doc_saltuse.png"))
    print("saltuse", os.path.getsize(os.path.join(OUT, "doc_saltuse.png")))


if __name__ == "__main__":
    timeline()
    saltuse()
