# -*- coding: utf-8 -*-
"""逐页盘点：元素数 / 图片数 / 字数 / 纵向占用 / 是否裸文本为主。"""
import json
from collections import Counter

DECK = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.load(open(DECK + r"\preview\layout.json", encoding="utf-8"))
print(f"{'页':>3} {'文件':<26} {'元素':>4} {'图':>3} {'方块':>4} {'字数':>5} {'y范围':>13} {'最低':>5} 视觉密度")
tot_txt = 0; noimg = []
for pg in lay["pages"]:
    els = pg["elements"]
    imgs = [e for e in els if e.get("kind") == "image"]
    txts = [e for e in els if e.get("kind") == "text"]
    shps = [e for e in els if e.get("kind") == "shape"]
    nchar = sum(len(e.get("text", "")) for e in txts)
    tot_txt += nchar
    ymin = min(e["bounds"]["y"] for e in els if e.get("bounds"))
    ymax = max(e["bounds"]["y"] + e["bounds"]["h"] for e in els if e.get("bounds"))
    # 视觉面积占比（图片+实心形状）
    area = 0.0
    for e in els:
        if e.get("kind") in ("image",) or (e.get("kind") == "shape" and e.get("fill")):
            b = e.get("bounds")
            if b: area += b["w"] * b["h"]
    dens = area / (960 * 540) * 100
    if not imgs: noimg.append(pg["pageNo"])
    print(f"{pg['pageNo']:>3} {pg['file'].split('/')[-1]:<26} {len(els):>4} {len(imgs):>3} {len(shps):>4} {nchar:>5} "
          f"{ymin:>5.0f}-{ymax:<7.0f} {nchar/max(1,len(els)):>5.0f} {dens:>5.1f}%")
print(f"\n总字数 {tot_txt}，平均每页 {tot_txt/46:.0f}")
print(f"无图页 {len(noimg)}: {noimg}")
# 色/字号统计
col = Counter(); fsz = Counter()
for pg in lay["pages"]:
    for e in pg["elements"]:
        if e.get("kind") == "text" and e.get("style"):
            col[e["style"].get("color")] += 1; fsz[e["style"].get("fontSize")] += 1
print("\n颜色使用:", dict(col.most_common()))
print("字号使用:", dict(sorted(fsz.items(), key=lambda kv: -kv[1])))
