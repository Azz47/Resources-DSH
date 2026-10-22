# -*- coding: utf-8 -*-
"""背景贴合审计 v2：精确黑板可用区 + 装饰物占位 + 裸文本/衬底分类。"""
import json, sys
from collections import defaultdict
from PIL import Image
import numpy as np

DECK = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
a = np.asarray(Image.open(DECK + r"\media\image1.jpeg").convert("RGB")).astype(np.int16)
IH, IW = a.shape[:2]
SX = IW / 960.0
d = np.abs(a - np.array([46, 74, 61])).sum(axis=2)
board = d < 90

# --- 精确边界：中列/中行扫描 ---
col = board[:, 700]
y0 = next(y for y in range(200) if col[y])
y1 = max(y for y in range(IH - 1, 0, -1) if col[y] and y < 740)
row = board[400, :]
x0 = next(x for x in range(IW) if row[x])
x1 = max(x for x in range(IW - 1, 0, -1) if row[x])
print(f"[board] px x[{x0},{x1}] y[{y0},{y1}] -> pt x[{x0/SX:.1f},{x1/SX:.1f}] y[{y0/SX:.1f},{y1/SX:.1f}]")
BR = (x0 / SX, y0 / SX, x1 / SX, y1 / SX)

# --- 装饰物连通块（整个黑板范围内） ---
sub = ~board[y0:y1 + 1, x0:x1 + 1]
ds = 4
H2, W2 = sub.shape[0] // ds, sub.shape[1] // ds
blk = sub[:H2*ds, :W2*ds].reshape(H2, ds, W2, ds).mean(axis=(1, 3)) > 0.35
lab = np.zeros((H2, W2), np.int32); n = 0; blobs = []
for sy in range(H2):
    for sx in range(W2):
        if blk[sy, sx] and lab[sy, sx] == 0:
            n += 1; st = [(sy, sx)]; lab[sy, sx] = n
            ay0 = ay1 = sy; ax0 = ax1 = sx; cnt = 0
            while st:
                cy, cx = st.pop(); cnt += 1
                ay0 = min(ay0, cy); ay1 = max(ay1, cy); ax0 = min(ax0, cx); ax1 = max(ax1, cx)
                for ny, nx in ((cy+1,cx),(cy-1,cx),(cy,cx+1),(cy,cx-1)):
                    if 0 <= ny < H2 and 0 <= nx < W2 and blk[ny, nx] and lab[ny, nx] == 0:
                        lab[ny, nx] = n; st.append((ny, nx))
            if cnt >= 3:
                blobs.append(((x0+ax0*ds)/SX, (y0+ay0*ds)/SX, (x0+(ax1+1)*ds)/SX, (y0+(ay1+1)*ds)/SX, cnt))
blobs.sort(key=lambda t: -t[4])
print(f"[decor] {len(blobs)} blobs:")
for bl in blobs[:14]:
    print(f"   pt[{bl[0]:.0f},{bl[1]:.0f}]-[{bl[2]:.0f},{bl[3]:.0f}]  blocks={bl[4]}")

def ov(A, B):
    ix = max(0.0, min(A[2], B[2]) - max(A[0], B[0])); iy = max(0.0, min(A[3], B[3]) - max(A[1], B[1]))
    return ix * iy

lay = json.load(open(DECK + r"\preview\layout.json", encoding="utf-8"))
ONWOOD, ONDEC, ONDEC_BARE = [], [], []
for pg in lay["pages"]:
    pno = pg["pageNo"]; els = pg["elements"]
    backed = set()
    for e in els:
        if e.get("kind") == "shape" and e.get("contains"):
            backed.update(e["contains"])
    fillboxes = [(e["bounds"], e.get("fill"), e["id"]) for e in els
                 if e.get("kind") == "shape" and e.get("fill") and e.get("bounds")]
    for e in els:
        bd = e.get("bounds")
        if not bd or e.get("kind") not in ("text", "shape", "image"): continue
        B = (bd["x"], bd["y"], bd["x"]+bd["w"], bd["y"]+bd["h"])
        bare = e["kind"] == "text" and e["id"] not in backed
        # 是否被某个实心衬底完全覆盖
        covered = any(B[0] >= f[0]["x"]-0.6 and B[1] >= f[0]["y"]-0.6 and
                      B[2] <= f[0]["x"]+f[0]["w"]+0.6 and B[3] <= f[0]["y"]+f[0]["h"]+0.6
                      for f in fillboxes if f[0])
        over_bottom = B[3] - BR[3]; over_top = BR[1] - B[1]
        left = BR[0] - B[0]; right = B[2] - BR[2]
        if max(over_bottom, over_top, left, right) > 1.0:
            ONWOOD.append((round(max(over_bottom, over_top, left, right), 1), pno, e["id"], e["kind"],
                           "衬底" if covered else ("裸文本" if bare else "—"),
                           tuple(round(v, 1) for v in B),
                           f"下越界{over_bottom:.1f} 上{over_top:.1f} 左{left:.1f} 右{right:.1f}"))
        for bl in blobs:
            A = ov(B, bl[:4])
            if A > 30:
                (ONDEC_BARE if bare else ONDEC).append((round(A), pno, e["id"], e["kind"],
                    tuple(round(v) for v in B), f"pt[{bl[0]:.0f},{bl[1]:.0f}]-[{bl[2]:.0f},{bl[3]:.0f}] 交{A:.0f}"))
                break

ONWOOD.sort(reverse=True)
print(f"\n===== 越出黑板可视区（> pt{B[3]:.0f} 即压木框/木条）: {len(ONWOOD)} =====")
for r in ONWOOD[:30]:
    print(f"  {r[0]:6.1f}pt p{r[1]:<2} {r[2]:<12} {r[3]:<6} {r[4]:<5} {r[5]}  {r[6]}")
print(f"  其中 裸文本 {sum(1 for r in ONWOOD if r[4]=='裸文本')} / 衬底 {sum(1 for r in ONWOOD if r[4]=='衬底')}")
print(f"\n===== 压装饰物：裸文本 {len(ONDEC_BARE)} / 有衬底 {len(ONDEC)} =====")
for r in ONDEC_BARE[:30]:
    print(f"  p{r[1]:<2} {r[2]:<12} {r[3]:<6} {r[4]} 交{r[0]}pt²  {r[5]}")
print("  --- 有衬底（视觉遮挡，非可读性）样本 ---")
for r in ONDEC[:10]:
    print(f"  p{r[1]:<2} {r[2]:<12} {r[3]:<6} {r[4]} 交{r[0]}pt²  {r[5]}")
