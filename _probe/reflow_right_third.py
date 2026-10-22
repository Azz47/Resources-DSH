# -*- coding: utf-8 -*-
"""① 把参赛 PPT 的结构+全文导出成 JSON（供按需查阅，不占上下文）
   ② 生成「右侧空出 1/3」的改造版

改造规则：
  · 满版背景（宽 ≥ 90% 且左边距 ≤ 5%）→ 保持不动，只当底色
  · 其余所有形状 → x 与 width 同乘 k，锚定左侧；图片等比缩放避免变形
  · 顶部/高度不变（slides 是 16:9，"压扁"会失真）

用法: python reflow_right_third.py <src.pptx> <out-dir> [--k 0.66] [--font-scale 1.0]
"""
import argparse
import json
import os
import shutil

from pptx import Presentation
from pptx.util import Emu

EMU = 914400
ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out_dir")
ap.add_argument("--k", type=float, default=0.66)
ap.add_argument("--font-scale", type=float, default=1.0)
ap.add_argument("--center-offset", type=float, default=None,
                help="垂直位移（英寸）。默认自动垂直居中缩放后的内容块")
ap.add_argument("--dump-only", action="store_true")
a = ap.parse_args()

os.makedirs(a.out_dir, exist_ok=True)
prs = Presentation(a.src)
SW, SH = prs.slide_width / EMU, prs.slide_height / EMU
TARGET_RIGHT = SW * 2 / 3
if a.center_offset is None:
    a.center_offset = max(0.0, (SH - SH * a.k) / 2)

# ---------- ① 导出结构 ----------
dump = {"file": os.path.basename(a.src), "size_in": [round(SW, 3), round(SH, 3)],
        "right_third_starts_at_in": round(TARGET_RIGHT, 3), "slides": []}
for idx, slide in enumerate(prs.slides, 1):
    s = {"n": idx, "shapes": []}
    for sh in slide.shapes:
        rec = {"kind": sh.shape_type.__str__() if sh.shape_type is not None else "?",
               "name": sh.name}
        try:
            rec.update(left=round(sh.left / EMU, 3), top=round(sh.top / EMU, 3),
                       width=round(sh.width / EMU, 3), height=round(sh.height / EMU, 3))
        except Exception:
            pass
        if getattr(sh, "has_text_frame", False) and sh.text_frame.text.strip():
            rec["text"] = sh.text_frame.text
            try:
                rec["font_sizes"] = sorted({round(r.font.size.pt, 1)
                                            for p in sh.text_frame.paragraphs
                                            for r in p.runs if r.font.size})
            except Exception:
                pass
        if getattr(sh, "has_table", False) and sh.has_table:
            rec["table"] = [[c.text for c in row.cells] for row in sh.table.rows]
        s["shapes"].append(rec)
    dump["slides"].append(s)

dump_path = os.path.join(a.out_dir, "deck-structure.json")
with open(dump_path, "w", encoding="utf-8") as fh:
    json.dump(dump, fh, ensure_ascii=False, indent=1)
print(f"结构已导出: {dump_path}  ({os.path.getsize(dump_path)/1024:.0f} KB)")
if a.dump_only:
    raise SystemExit(0)

# ---------- ② 改造：等比缩放（x/y/字号同乘 k）+ 垂直居中 ----------
# 为什么必须三样同乘 k：
#   只缩 x 会导致文本框变窄 → 文字重排成更多行 → 高度不够 → 溢出错位（第一版就这样炸了）
#   字号同乘 k 后每行字数不变 → 行数不变 → 版面比例完全保留
k = a.k
moved = bg_kept = 0
for slide in prs.slides:
    for sh in slide.shapes:
        try:
            l, t, w, h = sh.left / EMU, sh.top / EMU, sh.width / EMU, sh.height / EMU
        except Exception:
            continue
        if w <= 0:
            continue
        # 注意：水平分隔线的 height 是 0，不能因为 h<=0 就跳过——否则线不会被缩放，
        # 会横穿到讲师站位区（第一版就漏了这类形状）
        has_text = getattr(sh, "has_text_frame", False) and bool(sh.text_frame.text.strip())
        if (not has_text) and w >= 0.90 * SW and l <= 0.05 * SW and h >= 0.90 * SH:
            bg_kept += 1          # 真·满版背景：整页保留，右侧那 1/3 只是底色，不妨碍讲师
            continue
        sh.left = Emu(int(l * k * EMU))
        sh.top = Emu(int((t * k + a.center_offset) * EMU))
        sh.width = Emu(int(w * k * EMU))
        if h > 0:
            sh.height = Emu(int(h * k * EMU))
        moved += 1
        if getattr(sh, "has_text_frame", False):
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        r.font.size = r.font.size * k

out = os.path.join(a.out_dir, os.path.basename(a.src).replace(".pptx", "_右1-3留空.pptx"))
prs.save(out)
print(f"改造版: {out}")
print(f"  形状变换 {moved} 个；满版背景保持 {bg_kept} 个；k={k}")
print(f"  内容右边界目标 ≤ {TARGET_RIGHT:.2f} in")

# ---------- ③ 复检 ----------
chk = Presentation(out)
bad = []
for idx, slide in enumerate(chk.slides, 1):
    x1 = 0
    for sh in slide.shapes:
        try:
            x1 = max(x1, (sh.left + sh.width) / EMU)
        except Exception:
            pass
    if x1 > TARGET_RIGHT + 0.02:
        bad.append((idx, round(x1, 2)))
print(f"  复检：仍有 {len(bad)} 页越界" + (f" → {bad}" if bad else " ✅ 全部在 2/3 内"))
