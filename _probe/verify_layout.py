# -*- coding: utf-8 -*-
"""Verify the exported contest deck: slide geometry, right-third emptiness, notes."""
from pptx import Presentation

p = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\第二单元 进入新时代-单元思考与行动-参赛版.pptx"
pr = Presentation(p)
W = pr.slide_width

def max_right(slide):
    m = 0
    for sh in slide.shapes:
        try:
            if sh.left is None:
                continue
            m = max(m, sh.left + (sh.width or 0))
        except Exception:
            pass
    return m

print(f"slides={len(pr.slides)}  W={W}  safeRight(640pt)={int(640/960*W)}")
over = []
for i, s in enumerate(pr.slides, 1):
    r = max_right(s)
    if r > 640 / 960 * W:
        over.append((i, round(r / 12700, 1)))
print("pages whose rightmost shape exceeds 640pt:", len(over))
for i, r in over[:12]:
    print(f"   p{i}: right edge = {r} pt")

# first slide text
print("--- p1 shapes ---")
for sh in pr.slides[0].shapes:
    if sh.has_text_frame and sh.text_frame.text.strip():
        print("   ", sh.text_frame.text.strip().replace("\n", " | ")[:90])
print("--- p2 shapes ---")
for sh in pr.slides[1].shapes:
    if sh.has_text_frame and sh.text_frame.text.strip():
        print("   ", sh.text_frame.text.strip().replace("\n", " | ")[:90])
