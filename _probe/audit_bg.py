# -*- coding: utf-8 -*-
"""背景图审计：黑板可视区 / 装饰物占位 / 内容压背景 / WCAG 对比度。"""
import json, sys, itertools
from collections import defaultdict
from PIL import Image
import numpy as np

DECK = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
BG   = DECK + r"\media\image1.jpeg"
LAY  = DECK + r"\preview\layout.json"
W_PT, H_PT = 960.0, 540.0

img = Image.open(BG).convert("RGB")
IW, IH = img.size
a = np.asarray(img).astype(np.int16)
SX, SY = IW / W_PT, IH / H_PT            # pt -> px
print(f"[bg] {BG}  {IW}x{IH}px  1pt={SX}px")

# ---------- 1. 分类：木框 / 黑板 ----------
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
wood = (r > g + 12) & (g >= b) & (r > 70)                 # 棕木
board_ref = np.array([46, 74, 61])                         # 黑板绿参考
d = np.abs(a - board_ref).sum(axis=2)
board = d < 60
print(f"[class] wood {wood.mean()*100:.1f}%  board {board.mean()*100:.1f}%")

# 逐行最长 board 连续段（取含中心的那段更稳，这里取最长段并记录起止）
best_rows = []
for y in range(IH):
    row = board[y]
    idx = np.flatnonzero(row)
    if idx.size == 0:
        best_rows.append(None); continue
    # 找最长连续 run
    splits = np.flatnonzero(np.diff(idx) > 1)
    segs = np.split(idx, splits + 1)
    s = max(segs, key=len)
    best_rows.append((len(s), int(s[0]), int(s[-1])))

runs = [x for x in best_rows if x and x[0] > 800]
# 黑板行 = 段起点 > 0 的行
board_rows = [y for y in range(IH) if best_rows[y] and best_rows[y][0] > 800 and best_rows[y][1] > 5]
by0, by1 = min(board_rows), max(board_rows)
xs0 = min(best_rows[y][1] for y in board_rows)
xs1 = max(best_rows[y][2] for y in board_rows)
print(f"[board] inner rect px x[{xs0},{xs1}] y[{by0},{by1}]  ->  pt x[{xs0/SX:.1f},{xs1/SX:.1f}] y[{by0/SY:.1f},{by1/SY:.1f}]")

# ---------- 2. 黑板内的“装饰物”连通块（4x4 降采样后 flood fill） ----------
sub = ~board[by0:by1 + 1, xs0:xs1 + 1]
ds = 4
H2, W2 = sub.shape[0] // ds, sub.shape[1] // ds
blk = sub[:H2 * ds, :W2 * ds].reshape(H2, ds, W2, ds).mean(axis=(1, 3)) > 0.45
lab = np.zeros((H2, W2), np.int32); nxt = 0; out = []
for sy in range(H2):
    for sx in range(W2):
        if blk[sy, sx] and lab[sy, sx] == 0:
            nxt += 1; stack = [(sy, sx)]; lab[sy, sx] = nxt
            y0 = y1_ = sy; x0 = x1_ = sx; cnt = 0
            while stack:
                cy, cx = stack.pop(); cnt += 1
                y0 = min(y0, cy); y1_ = max(y1_, cy); x0 = min(x0, cx); x1_ = max(x1_, cx)
                for ny, nx in ((cy+1,cx),(cy-1,cx),(cy,cx+1),(cy,cx-1)):
                    if 0 <= ny < H2 and 0 <= nx < W2 and blk[ny, nx] and lab[ny, nx] == 0:
                        lab[ny, nx] = nxt; stack.append((ny, nx))
            if cnt >= 5:
                px0 = xs0 + x0*ds; px1 = xs0 + (x1_+1)*ds
                py0 = by0 + y0*ds; py1 = by0 + (y1_+1)*ds
                out.append((px0, py0, px1, py1, cnt))
out.sort(key=lambda t: -t[4])
print(f"[decor] {len(out)} blobs inside board:")
for (x0, y0, x1, y1, c) in out[:12]:
    print(f"   px[{x0},{y0}]-[{x1},{y1}] blocks={c}  ->  pt[{x0/SX:.0f},{y0/SY:.0f}]-[{x1/SX:.0f},{y1/SY:.0f}]")

# ---------- 3. 逐元素审计 ----------
def bbox_pt(px0, py0, px1, py1):
    return (px0/SX, py0/SY, px1/SX, py1/SY)

board_rect = bbox_pt(xs0, by0, xs1 + 1, by1 + 1)
decor_rects = [bbox_pt(*o[:4]) for o in out if o[4] >= 8]
print(f"[board_rect_pt] {tuple(round(v,1) for v in board_rect)}")

def ov(a_, b_):  # 交集面积
    ix = max(0.0, min(a_[2], b_[2]) - max(a_[0], b_[0]))
    iy = max(0.0, min(a_[3], b_[3]) - max(a_[1], b_[1]))
    return ix * iy

def lum(c):
    def f(v):
        v /= 255.0
        return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055) ** 2.4
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2])

def ratio(c1, c2):
    l1, l2 = lum(c1), lum(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(ch*2 for ch in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

lay = json.load(open(LAY, encoding="utf-8"))
pages = lay["pages"]
print(f"[layout] {len(pages)} pages")

# 背景在元素框下的“有效底色”：取该框内 board 像素的中位数；wood/decor 占比单独报
issues = defaultdict(list)
contrast_rows = []
for pg in pages:
    pno = pg["pageNo"]
    els = pg["elements"]
    fills = []      # (bounds, fill) 按 z 序
    for e in els:
        bd = e.get("bounds")
        if not bd: continue
        box = (bd["x"], bd["y"], bd["x"]+bd["w"], bd["y"]+bd["h"])
        col = e.get("style", {}).get("color")
        kind = e.get("kind")
        # --- 压框/压装饰 ---
        if kind in ("text", "shape", "line", "image"):
            lx = board_rect[0] - box[0]
            ty = board_rect[1] - box[1]
            rx = box[2] - board_rect[2]
            by = box[3] - board_rect[3]
            if max(lx, ty, rx, by) > 0.6:
                issues["压木框"].append((pno, e["id"], kind, tuple(round(v,1) for v in box),
                                        f"左{lx:.1f} 上{ty:.1f} 右{rx:.1f} 下{by:.1f}"))
            for dr in decor_rects:
                A = ov(box, dr)
                if A > 40:
                    issues["压装饰"].append((pno, e["id"], kind, tuple(round(v,1) for v in box),
                                            f"与 pt[{dr[0]:.0f},{dr[1]:.0f}]-[{dr[2]:.0f},{dr[3]:.0f}] 重叠 {A:.0f}pt²"))
        if kind == "shape" and e.get("fill") and not str(e.get("fill")).startswith("none"):
            fills.append((box, e["fill"], e["id"]))
        if kind != "text" or not col:
            continue
        # --- 强调色变体（hd_num / hd_sec 用区块强调色）不算问题；先算对比度 ---
        # 有效底色：优先被 contains 的实心形状
        fg = hex2rgb(col)
        bgc = None; src = "背景图黑板"
        for (fb, fc, fid) in fills:
            if box[0] >= fb[0]-0.5 and box[1] >= fb[1]-0.5 and box[2] <= fb[2]+0.5 and box[3] <= fb[3]+0.5:
                bgc = hex2rgb(fc); src = f"衬底 {fid} {fc}"
        if bgc is None:
            px0, py0 = int(max(0, box[0]*SX)), int(max(0, box[1]*SY))
            px1, py1 = int(min(IW, box[2]*SX)), int(min(IH, box[3]*SY))
            if px1 <= px0 or py1 <= py0: continue
            crop = a[py0:py1, px0:px1].reshape(-1, 3)
            m = board[py0:py1, px0:px1].reshape(-1)
            if m.sum() < 0.3 * m.size:
                issues["底色不纯"].append((pno, e["id"], kind, tuple(round(v,1) for v in box),
                                          f"框内黑板占比仅 {m.mean()*100:.0f}%（压框/压装饰）"))
            if m.sum() > 0:
                med = np.median(crop[m], axis=0)
                var = crop[m].std(axis=0).mean()
                bgc = tuple(int(v) for v in med)
                src = f"背景黑板 #{bgc[0]:02X}{bgc[1]:02X}{bgc[2]:02X}" + (f" σ{var:.0f}" if var > 6 else "")
            else:
                continue
        ct = ratio(fg, bgc)
        fs = e.get("style", {}).get("fontSize", 0)
        need = 3.0 if (fs >= 18 or fs >= 14 and e.get("style", {}).get("bold")) else 4.5
        is_dec = e.get("role") == "decoration"
        contrast_rows.append((pno, e["id"], col, fs, round(ct, 2), need, "PASS" if ct >= need else "FAIL", src, e.get("text","")[:14]))

print("\n===== A. 内容压背景图 =====")
for k in ("压木框", "压装饰", "底色不纯"):
    v = issues.get(k, [])
    print(f"-- {k}: {len(v)}")
    for row in v[:25]:
        print("   p%-2s %-12s %-6s %s  %s" % row)
    if len(v) > 25: print(f"   ... 其余 {len(v)-25} 条")

print("\n===== B. 对比度（WCAG）=====")
fails = [x for x in contrast_rows if x[6] == "FAIL"]
print(f"文本元素 {len(contrast_rows)} 个，未达标 {len(fails)}")
by_col = defaultdict(list)
for x in fails: by_col[(x[2], x[3])].append((x[0], x[1], x[4], x[5], x[7]))
for k, v in sorted(by_col.items(), key=lambda kv: -len(kv[1])):
    print(f"  {k[0]} @{k[1]}号  {len(v)} 处，最低 {min(i[2] for i in v)}: {v[:4]}")

print("\n-- 全部色对（实测）--")
seen = {}
for (pno, eid, col, fs, ct, need, st, src, txt) in contrast_rows:
    key = (col, src.split(' ')[0] if ' ' in src else src)
    if key not in seen or ct < seen[key]: seen[key] = ct
for k in sorted(seen, key=lambda k: seen[k]):
    print(f"   {k[0]:8s} on {k[1]:24s} min {seen[k]:.2f}")

print("\n-- 字号分布 --")
fsd = defaultdict(int)
for x in contrast_rows: fsd[x[3]] += 1
print("   ", dict(sorted(fsd.items())))
