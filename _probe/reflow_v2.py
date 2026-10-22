# -*- coding: utf-8 -*-
"""把 PPT 重排到「左侧 2/3」——只压横向，**字号不缩**，用满纵向空间。

与上一版的根本区别：
  上一版：x/y/字号 全乘 0.66 → 整份课件变小，投影后字号不够看。
  本版  ：只压横向；字号保持原样；逐框估算重排后的高度，若顶到页底再统一微调字号。

用法: python reflow_v2.py <src.pptx> <out-dir> [--right 8.75] [--top 0.30] [--bottom 7.20]
     [--keep-font] [--min-font-scale 0.72]
"""
import argparse
import math
import os

from pptx import Presentation
from pptx.util import Emu

EMU = 914400


def est_lines(text, width_in, font_pt):
    """估算中文文本在给定宽度下的行数。中文字宽 ≈ 字号（1 em），英文按 0.55 em。"""
    if not text:
        return 0
    char_w = font_pt / 72.0
    cpl = max(1, int(width_in / char_w))
    n = 0
    for para in text.split("\n"):
        wide = sum(1.0 if ord(c) > 0x2E80 else 0.55 for c in para)
        n += max(1, math.ceil(wide / cpl))
    return n


def shape_font_pt(sh, default=18.0):
    sizes = []
    if getattr(sh, "has_text_frame", False):
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    sizes.append(r.font.size.pt)
    return max(sizes) if sizes else default


def is_background(sh, SW, SH):
    """满版且无文字 = 页面底色，保留整幅。"""
    try:
        l, t, w, h = sh.left / EMU, sh.top / EMU, sh.width / EMU, sh.height / EMU
    except Exception:
        return False
    has_text = getattr(sh, "has_text_frame", False) and bool(sh.text_frame.text.strip())
    return (not has_text) and w >= 0.85 * SW and h >= 0.85 * SH and l <= 0.08 * SW


ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out_dir")
ap.add_argument("--right", type=float, default=8.75, help="内容右边界（英寸），2/3 线=8.89")
ap.add_argument("--left", type=float, default=0.30)
ap.add_argument("--top", type=float, default=0.30)
ap.add_argument("--bottom", type=float, default=7.20)
ap.add_argument("--min-font-scale", type=float, default=0.72)
a = ap.parse_args()

os.makedirs(a.out_dir, exist_ok=True)
prs = Presentation(a.src)
SW, SH = prs.slide_width / EMU, prs.slide_height / EMU
print(f"原尺寸 {SW:.2f}x{SH:.2f} in；目标内容区 x∈[{a.left},{a.right}] y∈[{a.top},{a.bottom}]")

report = []
for idx, slide in enumerate(prs.slides, 1):
    content, bg = [], 0
    for sh in slide.shapes:
        if is_background(sh, SW, SH):
            bg += 1
        else:
            content.append(sh)
    if not content:
        continue

    # 内容包围盒
    xs0, xs1 = [], []
    for sh in content:
        try:
            l, w = sh.left / EMU, sh.width / EMU
        except Exception:
            continue
        if w > 0:
            xs0.append(l)
            xs1.append(l + w)
    if not xs0:
        continue
    x0, x1 = min(xs0), max(xs1)
    span = max(0.01, x1 - x0)
    kx = min(1.0, (a.right - a.left) / span)
    ys = [sh.top / EMU for sh in content if sh.width > 0]
    y0 = min(ys) if ys else 0.0

    # 找一个能塞下的字号比例
    best = None
    for fs in [1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, a.min_font_scale]:
        if fs < a.min_font_scale - 1e-9:
            continue
        bottom = a.top
        for sh in content:
            try:
                t = sh.top / EMU
                w2 = (sh.width / EMU) * kx
            except Exception:
                continue
            txt = sh.text_frame.text if getattr(sh, "has_text_frame", False) else ""
            if not txt.strip():
                continue
            pt = shape_font_pt(sh) * fs
            lines = est_lines(txt.replace("\u000b", "\n"), w2, pt)
            h2 = lines * (pt / 72.0) * 1.35
            bottom = max(bottom, a.top + t + h2)
        if bottom <= a.bottom:
            best = (fs, bottom)
            break
    if best is None:
        best = (a.min_font_scale, a.bottom)
    fs = best[0]

    for sh in content:
        try:
            l, t, w, h = sh.left / EMU, sh.top / EMU, sh.width / EMU, sh.height / EMU
        except Exception:
            continue
        if w <= 0:
            continue
        sh.left = Emu(int(((l - x0) * kx + a.left) * EMU))
        sh.width = Emu(int(max(0.05, w * kx) * EMU))
        # 纵向：整体把内容块顶到 a.top（y0 在循环前算好，避免边改边取值）
        sh.top = Emu(int((a.top + (t - y0)) * EMU))
        if h > 0:
            sh.height = Emu(int(h * EMU))
        # 图片等比（只缩宽会让图片变形）
        if h > 0 and (sh.__class__.__name__ == "Picture" or sh.shape_type == 13):
            sh.height = Emu(int(h * kx * EMU))
        if fs != 1.0 and getattr(sh, "has_text_frame", False):
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        r.font.size = r.font.size * fs

    report.append((idx, round(kx, 3), round(fs, 3), bg, len(content)))

print(f"\n{'页':>3} {'横向压缩kx':>10} {'字号比例':>9} {'背景':>5} {'内容形状':>8}")
for r in report:
    print(f"{r[0]:>3} {r[1]:>10} {r[2]:>9} {r[3]:>5} {r[4]:>8}")
kx_all = [r[1] for r in report]
fs_all = [r[2] for r in report]
print(f"\n横向压缩：中位 {sorted(kx_all)[len(kx_all)//2]:.3f}（上一版固定 0.66）")
print(f"字号比例：中位 {sorted(fs_all)[len(fs_all)//2]:.3f}（上一版固定 0.66 —— 这就是变小的根源）")

out = os.path.join(a.out_dir, os.path.basename(a.src).replace(".pptx", "_左2-3版.pptx"))
prs.save(out)
print(f"\n输出: {out}")

# 复检
chk = Presentation(out)
lim = SW * 2 / 3
bad = []
for i, s in enumerate(chk.slides, 1):
    x = max(((sh.left + sh.width) / EMU) for sh in s.shapes)
    if x > lim + 0.02:
        bad.append((i, round(x, 2)))
print(f"复检：右边界超 {lim:.2f} in 的页 = {bad if bad else '无'}")
