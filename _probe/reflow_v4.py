# -*- coding: utf-8 -*-
"""v4：在 v2 的基础上修两个具体缺陷，其余不动。

v2 实测效果最好（字号中位 0.92），但有两处硬伤：
  A. 把内容强行顶到页顶 → 封面标题撞上页眉
  B. 文本框变窄后没长高 → 标题断行溢出、压到下个元素

v4 只改这两点：
  · 保留原始 top（不整体位移），只压横向
  · 文本按重排后的估算高度**长高**
  · 从大到小试字号档位，取能塞进页面的最大档
（v3 的"按列避让"已证明不可行：横向区间普遍重叠，会把全页当成一列整体下推）

用法: python reflow_v4.py <src.pptx> <out-dir> [--right 8.75]
"""
import argparse
import math
import os

from pptx import Presentation
from pptx.util import Emu

EMU = 914400


def cjk_w(c):
    """字符宽度（以字号为单位）。中文标点、破折号、省略号都是全角 —— 之前漏判 em dash 导致标题算窄半格。"""
    o = ord(c)
    if o > 0x2E80:                 # CJK 汉字与部首
        return 1.0
    if 0x2010 <= o <= 0x203B:      # – — ‘ ’ “ ” … ※ 等
        return 1.0
    if 0x3000 <= o <= 0x303F:      # 、 。 《 》 【 】 等
        return 1.0
    if 0xFF00 <= o <= 0xFFEF:      # 全角标点与字母
        return 1.0
    return 0.55


def est_h(text, width_in, pt, spacing=1.3):
    if not text or not text.strip():
        return 0.0
    char_w = pt / 72.0
    cpl = max(1, int(width_in / char_w))
    n = 0
    for para in text.replace("\u000b", "\n").split("\n"):
        wide = sum(cjk_w(c) for c in para)
        n += max(1, math.ceil(wide / cpl))
    return n * (pt / 72.0) * spacing


def max_pt(sh, default=18.0):
    s = []
    if getattr(sh, "has_text_frame", False):
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    s.append(r.font.size.pt)
    return max(s) if s else default


def is_bg(sh, SW, SH):
    try:
        l, w, h = sh.left / EMU, sh.width / EMU, sh.height / EMU
    except Exception:
        return False
    txt = getattr(sh, "has_text_frame", False) and bool(sh.text_frame.text.strip())
    return (not txt) and w >= 0.85 * SW and h >= 0.85 * SH and l <= 0.08 * SW


ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out_dir")
ap.add_argument("--left", type=float, default=0.30)
ap.add_argument("--right", type=float, default=8.75)
ap.add_argument("--bottom", type=float, default=7.35)
ap.add_argument("--min-font-scale", type=float, default=0.80)
ap.add_argument("--grow", type=float, default=1.0, help="文本框长高系数，1=按估算长高，0=保持原高")
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)

prs = Presentation(a.src)
SW, SH = prs.slide_width / EMU, prs.slide_height / EMU
LIM = SW * 2 / 3

report = []
for idx, slide in enumerate(prs.slides, 1):
    geo = []
    for sh in slide.shapes:
        if is_bg(sh, SW, SH):
            continue
        try:
            geo.append((sh, sh.left / EMU, sh.top / EMU, sh.width / EMU, sh.height / EMU))
        except Exception:
            pass
    if not geo:
        continue
    x0 = min(g[1] for g in geo)
    x1 = max(g[1] + g[3] for g in geo)
    kx = min(1.0, (a.right - a.left) / max(0.01, x1 - x0))

    def plan(fs):
        items, bottom = [], 0.0
        for sh, l, t, w, h in geo:
            nl = (l - x0) * kx + a.left
            nw = max(0.05, w * kx)
            pt = max_pt(sh) * fs
            txt = sh.text_frame.text if getattr(sh, "has_text_frame", False) else ""
            is_pic = sh.__class__.__name__ == "Picture" or sh.shape_type == 13
            # 规则A：原本是「单行」的文本框（高 ≤ 1.6 行）不跟着整体压缩宽度，
            # 放它撑到右边界为止——否则标题会被挤成两行（实测页眉「环节一：策展——感悟新时代」断行）
            if (not is_pic) and txt.strip() and "\n" not in txt and "\u000b" not in txt:
                one_line_h = (pt / 72.0) * 1.8    # 含上下内边距，单行框通常略高于一行
                if h <= one_line_h:
                    em = sum(cjk_w(c) for c in txt)          # 整行需要的"字号倍数"
                    avail = a.right - nl
                    # 规则B：单行文字在 2/3 宽度里放不下时，**只给这一条降字号**保持单行，
                    # 而不是让它换行压到下方元素（整页降字号是 v2 的做法，牺牲太大）
                    fit_pt = ((avail - 0.12) * 72.0) / max(0.1, em)   # 留 0.12in 边距，避免末字掉行
                    if fit_pt < pt:
                        pt = max(fit_pt, max_pt(sh) * 0.65)           # 下限：原字号的 65%
                    nw = max(nw, min(em * (pt / 72.0) + 0.12, a.right - nl))
                    h_eff = h if h <= one_line_h else one_line_h
            if is_pic:
                nh = h * kx
            else:
                nh = max(h, h + (est_h(txt, nw, pt) - h) * a.grow) if txt.strip() else h
            items.append([sh, nl, t, nw, nh, pt])
            bottom = max(bottom, t + nh)
        return items, bottom

    chosen, bottom, used_fs = None, None, 1.0
    for fs in [1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, a.min_font_scale]:
        if fs < a.min_font_scale - 1e-9:
            continue
        it, b = plan(fs)
        if b <= a.bottom:
            chosen, bottom, used_fs = it, b, fs
            break
    if chosen is None:
        chosen, bottom = plan(a.min_font_scale)
        used_fs = a.min_font_scale

    for sh, nl, nt, nw, nh, pt_final in chosen:
        sh.left = Emu(int(nl * EMU))
        sh.top = Emu(int(nt * EMU))          # 保留原始 top，不做整体位移
        sh.width = Emu(int(nw * EMU))
        if nh > 0:
            sh.height = Emu(int(nh * EMU))
        # 字号：整页档位 × 该形状的单独修正（规则B）
        orig_pt = max_pt(sh)
        scale = used_fs * (pt_final / orig_pt if orig_pt > 0 else 1.0)
        if abs(scale - 1.0) > 1e-9 and getattr(sh, "has_text_frame", False):
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        r.font.size = r.font.size * scale

    report.append((idx, round(kx, 3), round(used_fs, 3), round(bottom, 2)))

print(f"{'页':>3} {'横向kx':>8} {'字号':>6} {'底部':>6}")
for r in report:
    print(f"{r[0]:>3} {r[1]:>8} {r[2]:>6} {r[3]:>6}" + ("  ←超界" if r[3] > a.bottom + 0.02 else ""))
fss = sorted(r[2] for r in report)
print(f"\n字号中位 {fss[len(fss)//2]:.3f}  (v1=0.660 / v2=0.920 / v3=0.800)")

out = os.path.join(a.out_dir, os.path.basename(a.src).replace(".pptx", "_左2-3_v4.pptx"))
prs.save(out)
print(f"输出: {out}")
chk = Presentation(out)
bad = [(i, round(max((s2.left + s2.width) / EMU for s2 in s.shapes), 2))
       for i, s in enumerate(chk.slides, 1)
       if max((s2.left + s2.width) / EMU for s2 in s.shapes) > LIM + 0.02]
print(f"右边界超 {LIM:.2f} in: {bad if bad else '无'}")
