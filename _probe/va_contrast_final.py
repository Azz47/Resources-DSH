# -*- coding: utf-8 -*-
"""定稿对比度：字色取渲染真相（YAML 声明，渲染链路对 16 进制色精确），底色取实拍众数色
校准验证：p6 #7FD6B0 声明 → 实拍 #7FD6B0 逐字节一致（已证）"""
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

rows = []
for idx in range(46):
    n = idx + 1
    P = lay["pages"][idx]
    px = imgs[n].load()
    for e in flat(P.get("elements")):
        if e.get("kind") != "text": continue
        t = (e.get("text") or "").strip()
        if not t: continue
        st = e.get("style") or {}; b = e.get("bounds") or {}
        fg = pc(st.get("color"))
        if fg is None: continue
        x0, y0 = max(0, int(b.get("x", 0))), max(0, int(b.get("y", 0)))
        x1, y1 = min(W, int(b.get("x", 0) + b.get("w", 0))), min(H, int(b.get("y", 0) + b.get("h", 0)))
        reg = [px[x, y] for y in range(y0, y1) for x in range(x0, x1)]
        if len(reg) < 30: continue
        cnt = collections.Counter(reg)
        bg = cnt.most_common(1)[0][0]
        r_bg = cr(fg, bg)
        # 框内是否含多个明显不同的底色（=压在花背景/图片上）
        lf = collections.Counter(c for c in reg if abs(lum(c) - lum(bg)) > 0.12)
        noise = sum(lf.values()) / len(reg)
        fs = st.get("fontSize") or 0
        big = (fs >= 18) or (fs >= 14 and st.get("bold"))
        need = 3.0 if big else 4.5
        rows.append({"n": n, "id": e.get("id"), "fs": fs, "bold": bool(st.get("bold")),
                     "fg": hx(fg), "bg": hx(bg), "r": round(r_bg, 2), "need": need,
                     "noise": round(noise * 100, 1), "txt": t[:24],
                     "page": P.get("name") or P.get("file")})

o = []
o.append("=== 定稿对比度（字色=渲染真相 / 底色=实拍众数）文本 %d 个 ===" % len(rows))
fail = [r for r in rows if r["r"] < r["need"]]
o.append("未达 WCAG AA = %d (%.0f%%)" % (len(fail), len(fail) * 100.0 / len(rows)))
o.append("未达 7:1 = %d (%.0f%%)" % (len([r for r in rows if r["r"] < 7]), len([r for r in rows if r["r"] < 7]) * 100.0 / len(rows)))
o.append("")
o.append("--- 未达 AA 明细（按比值升序）---")
for r in sorted(fail, key=lambda r: r["r"]):
    o.append("  p%-3d %-14s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f≥%.1f 「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["need"], r["txt"]))
o.append("")
o.append("--- 通过但 <6.0（投影边界，建议复核）---")
for r in sorted([r for r in rows if r["need"] <= r["r"] < 6.0], key=lambda r: r["r"])[:40]:
    o.append("  p%-3d %-14s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f 「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["txt"]))
o.append("")
o.append("--- 文字压花背景（框内异色 >25%，H3 压图风险）---")
for r in sorted([r for r in rows if r["noise"] > 25], key=lambda r: -r["noise"])[:40]:
    o.append("  p%-3d %-14s 异色占比=%5.1f%%  比=%5.2f  字%s 底%s 「%s」" % (
        r["n"], r["id"], r["noise"], r["r"], r["fg"], r["bg"], r["txt"]))
o.append("")
o.append("--- 按字号分组统计 ---")
gs = collections.defaultdict(lambda: [0, 0, 9.9])
for r in rows:
    k = r["fs"]; gs[k][0] += 1
    if r["r"] < r["need"]: gs[k][1] += 1
    gs[k][2] = min(gs[k][2], r["r"])
for k in sorted(gs):
    o.append("  %2dpt  共%3d 个  未达AA %2d 个  最低比 %.2f" % (k, gs[k][0], gs[k][1], gs[k][2]))
o.append("")
o.append("--- 同元素跨页色不一致 ---")
byid = collections.defaultdict(list)
for r in rows: byid[r["id"]].append(r)
for k, v in sorted(byid.items()):
    fs = set(x["fg"] for x in v)
    if len(fs) > 1 and len(v) > 3:
        o.append("  %-14s %2d页  字色%2d种: %s" % (k, len(v), len(fs), sorted(fs)))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_contrast_final.txt", "w", encoding="utf-8").write(txt)
json.dump(rows, io.open(r"D:\Resources\DSH\_probe\va_contrast_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
try:
    print(txt[:5000])
except Exception:
    pass
