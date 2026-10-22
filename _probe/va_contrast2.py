# -*- coding: utf-8 -*-
"""确定性对比度：渲染用色（YAML 声明） vs 实拍底色（截图采样）
前提：DSH 预览链路对 16 进制色是精确渲染（已用 #7FD6B0 采样值逐字节验证）
"""
import json, io, os, collections, math
from PIL import Image

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")
W, H = 960, 540

def lum(c):
    def f(x):
        x = x / 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
def cr(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)
def hx(c): return "#%02X%02X%02X" % c
def pc(s):
    if isinstance(s, str) and len(s) == 7 and s[0] == "#":
        try: return tuple(int(s[i:i+2], 16) for i in (1, 3, 5))
        except Exception: return None
    return None

lay = json.loads(io.open(os.path.join(D, "preview", "layout.json"), "rb").read().decode("gbk", "replace"))
imgs = {n: Image.open(os.path.join(SH, "%02d.png" % n)).convert("RGB") for n in range(1, 47)}

def flat(el, out=None):
    if out is None: out = []
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"], out)
    return out

def bg_at(n, x0, y0, x1, y1):
    im = imgs[n]; px = im.load()
    x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(W, int(x1)), min(H, int(y1))
    if x1 <= x0 or y1 <= y0: return None
    cnt = collections.Counter(px[x, y] for y in range(y0, y1) for x in range(x0, x1))
    return cnt.most_common(1)[0][0]

def ring_bg(n, x0, y0, x1, y1, pad=2):
    im = imgs[n]; px = im.load()
    cnt = collections.Counter()
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    for y in (y0 - pad, y0 - pad - 1, y1 + pad, y1 + pad + 1):
        if 0 <= y < H:
            for x in range(max(0, x0), min(W, x1)): cnt[px[x, y]] += 1
    for x in (x0 - pad, x0 - pad - 1, x1 + pad, x1 + pad + 1):
        if 0 <= x < W:
            for y in range(max(0, y0), min(H, y1)): cnt[px[x, y]] += 1
    return cnt.most_common(1)[0][0] if cnt else None

rows = []
for idx in range(46):
    n = idx + 1
    for e in flat(lay["pages"][idx].get("elements")):
        if e.get("kind") != "text": continue
        t = (e.get("text") or "").strip()
        if not t: continue
        st = e.get("style") or {}; b = e.get("bounds") or {}
        fg = pc(st.get("color"))
        if fg is None: continue
        x0, y0 = b.get("x", 0), b.get("y", 0); w, h = b.get("w", 0), b.get("h", 0)
        bg = bg_at(n, x0, y0, x0 + w, y0 + h) or ring_bg(n, x0, y0, x0 + w, y0 + h)
        if bg is None: continue
        ring = ring_bg(n, x0, y0, x0 + w, y0 + h)
        fs = st.get("fontSize") or 0
        big = (fs >= 18) or (fs >= 14 and st.get("bold"))
        r_in = cr(fg, bg); r_out = cr(fg, ring) if ring else None
        rows.append({"n": n, "id": e.get("id"), "fs": fs, "bold": bool(st.get("bold")),
                     "fg": hx(fg), "bg": hx(bg), "ring": hx(ring) if ring else None,
                     "r": round(r_in, 2), "r_ring": round(r_out, 2) if r_out else None,
                     "need": 3.0 if big else 4.5, "txt": t[:22]})

fail = [r for r in rows if r["r"] < r["need"]]
o = []
o.append("=== 确定性对比度：声明字色 vs 实测底色（WCAG 2.x）===")
o.append("文本元素 %d 个；未达 AA = %d 个" % (len(rows), len(fail)))
o.append("")
o.append("--- 未达 AA 明细（按比值升序）---")
for r in sorted(fail, key=lambda r: r["r"]):
    o.append("p%-3d %-13s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f (需%.1f)  「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["need"], r["txt"]))
o.append("")
o.append("--- 未达投影从严线 7:1（仅统计，不判死）前 30 ---")
lt7 = sorted([r for r in rows if r["r"] < 7.0], key=lambda r: r["r"])
o.append("  合计 %d / %d (%.0f%%)" % (len(lt7), len(rows), len(lt7) * 100.0 / len(rows)))
for r in lt7[:30]:
    o.append("p%-3d %-13s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f  「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["txt"]))
o.append("")
o.append("--- 同元素跨页色不一致（系统性不一致 = 观感割裂源）---")
byid = collections.defaultdict(list)
for r in rows: byid[r["id"]].append(r)
for k, v in sorted(byid.items()):
    fs = set(x["fg"] for x in v); bs = set(x["bg"] for x in v)
    if len(fs) > 1:
        o.append("  %-12s 出现%d页  字色%2d种 %s" % (k, len(v), len(fs), sorted(fs)))
o.append("")
o.append("--- 底色种类统计（跨页背景一致性）---")
bgs = collections.Counter(r["bg"] for r in rows)
for c, v in bgs.most_common(14):
    o.append("  底 %s  出现 %d 次" % (c, v))
o.append("")
o.append("--- 最弱 20 个（含通过）---")
for r in sorted(rows, key=lambda r: r["r"])[:20]:
    o.append("p%-3d %-13s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f 环%s  「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["ring"], r["txt"]))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_contrast2.txt", "w", encoding="utf-8").write(txt)
json.dump(rows, io.open(r"D:\Resources\DSH\_probe\va_contrast2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(txt)
