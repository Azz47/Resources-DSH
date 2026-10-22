# -*- coding: utf-8 -*-
"""课件几何体检：python _check_deck.py <deck.pptx> [--max-right 640] [--max-bottom 496]

输出：页数 / 画布 / 备注覆盖 / 字号分布 / 越界元素 / 对比度提示（需人工对照 checklist.md B3）。
只依赖 python-pptx。
"""
import sys

try:  # Windows 控制台默认 GBK，强制 UTF-8 输出，避免中文乱码
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from collections import Counter

from pptx import Presentation
from pptx.util import Emu


def pt(v):
    return round(Emu(v).pt, 2) if v is not None else None


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    max_right = 640.0
    max_bottom = 496.0
    for i, a in enumerate(argv):
        if a == "--max-right" and i + 1 < len(argv):
            max_right = float(argv[i + 1])
        if a == "--max-bottom" and i + 1 < len(argv):
            max_bottom = float(argv[i + 1])

    p = Presentation(path)
    slides = list(p.slides)
    print("file          :", path)
    print("slides        :", len(slides))
    print("canvas(pt)    :", pt(p.slide_width), "x", pt(p.slide_height))
    notes = [i for i, s in enumerate(slides, 1)
             if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip()]
    print("notes         : %d / %d" % (len(notes), len(slides)))
    if len(notes) != len(slides):
        print("  missing notes pages:", [i for i in range(1, len(slides) + 1) if i not in notes])

    sizes = Counter()
    right_over, bottom_over, textless_over = [], [], []
    for i, s in enumerate(slides, 1):
        for sh in s.shapes:
            right = pt(sh.left + sh.width) if sh.width is not None and sh.left is not None else None
            bottom = pt(sh.top + sh.height) if sh.height is not None and sh.top is not None else None
            has_text = sh.has_text_frame and sh.text_frame.text.strip() != ""
            left = pt(sh.left) if sh.left is not None else None
            if right is not None and right > max_right + 0.5:
                # 右侧带（整块都在 640 右边）是允许的装饰：竖排单元名 + 页码
                if left is not None and left >= max_right:
                    textless_over.append((i, sh.shape_type, right))
                elif has_text:
                    right_over.append((i, sh.shape_type, right))
                else:
                    textless_over.append((i, sh.shape_type, right))
            if bottom is not None and bottom > max_bottom + 0.5:
                bottom_over.append((i, sh.shape_type, bottom))
            if has_text:
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        if run.text.strip() and run.font.size:
                            sizes[run.font.size.pt] += 1

    print("font sizes(pt):", dict(sorted(sizes.items())))
    small = {k: v for k, v in sizes.items() if k < 14}
    print("  below 14pt  :", small if small else "none")
    print("text beyond x=%.1f :" % max_right, right_over if right_over else "none")
    print("decoration beyond x=%.1f (allowed if non-informational):" % max_right,
          len(textless_over), textless_over[:8])
    print("below y=%.1f       :" % max_bottom, bottom_over if bottom_over else "none")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
