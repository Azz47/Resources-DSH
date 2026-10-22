# -*- coding: utf-8 -*-
"""出厂口径定稿量测：渲染态对比度（暗/亮中位法）+ 霓虹带 + 粉笔尘底噪 + 覆盖密度"""
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

lay = json.loads(io.open(os.path.join(D, "preview", "layout.json"), "rb").read().decode("gbk", "replace"))
imgs = {n: Image.open(os.path.join(SH, "%02d.png" % n)).convert("RGB") for n in range(1, 47)}

def flat(el, out=None):
    if out is None: out = []
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"], out)
    return out

def measure(n, x0, y0, x1, y1):
    """区内：暗簇中位（字） vs 亮簇中位（底）→ 实测对比"""
    px = imgs[n].load()
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(W, int(x1)), min(H, int(y1))
    reg = [px[x, y] for y in range(y0, y1) for x in range(x0, x1)]
    if len(reg) < 20: return None
    Ls = sorted(lum(c) for c in reg)
    lo, hi = Ls[int(len(Ls) * 0.08)], Ls[int(len(Ls) * 0.92)]
    dark = sorted([c for c in reg if lum(c) <= lo + 0.02], key=lum)
    light = sorted([c for c in reg if lum(c) >= hi - 0.02], key=lum, reverse=True)
    if not dark or not light: return None
    d = dark[len(dark) // 2]; l = light[len(light) // 2]
    return {"dark": d, "light": l, "r": cr(d, l), "n": len(reg)}

rows = []
for idx in range(46):
    n = idx + 1
    mn = 99.0; worst = None
    for e in flat(lay["pages"][idx].get("elements")):
        if e.get("kind") != "text": continue
        t = (e.get("text") or "").strip()
        if not t: continue
        st = e.get("style") or {}; b = e.get("bounds") or {}
        m = measure(n, b.get("x", 0), b.get("y", 0), b.get("x", 0) + b.get("w", 0), b.get("y", 0) + b.get("h", 0))
        if not m: continue
        fs = st.get("fontSize") or 0
        big = (fs >= 18) or (fs >= 14 and st.get("bold"))
        need = 3.0 if big else 4.5
        rec = {"n": n, "id": e.get("id"), "fs": fs, "bold": bool(st.get("bold")),
               "decl": st.get("color"), "fg": hx(m["dark"]), "bg": hx(m["light"]),
               "r": round(m["r"], 2), "need": need, "txt": t[:22]}
        rows.append(rec)
        if m["r"] < mn: mn, worst = m["r"], rec
    rows.append({"n": n, "page_min": round(mn, 2), "worst": worst})

pages = [r for r in rows if "page_min" in r]
texts = [r for r in rows if "r" in r]
o = []
o.append("=== 渲染实拍对比度（暗/亮中位法），文本 %d 个 ===" % len(texts))
o.append("未达 AA(大字3.0/小字4.5) = %d" % len([r for r in texts if r["r"] < r["need"]]))
o.append("未达 7:1 = %d (%.0f%%)" % (len([r for r in texts if r["r"] < 7]), len([r for r in texts if r["r"] < 7]) * 100.0 / len(texts)))
o.append("")
o.append("--- 未达 AA 明细 ---")
for r in sorted([r for r in texts if r["r"] < r["need"]], key=lambda r: r["r"]):
    o.append("  p%-3d %-12s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f 需%.1f 「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["need"], r["txt"]))
o.append("")
o.append("--- 通过但 <4.5 或 <5.5 的边界项（投影边缘）---")
for r in sorted([r for r in texts if 3.0 <= r["r"] < 5.5], key=lambda r: r["r"])[:35]:
    o.append("  p%-3d %-12s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f 需%.1f 「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["fg"], r["bg"], r["r"], r["need"], r["txt"]))
o.append("")
o.append("--- 逐页最低对比度 ---")
for r in pages:
    w = r["worst"] or {}
    o.append("  p%-3d min=%5.2f  %s" % (r["n"], r["page_min"],
             ("%s %spt 「%s」" % (w.get("id"), w.get("fs"), w.get("txt"))) if w else ""))

# ---- 霓虹带 ----
o.append("")
o.append("=== 底部离群带（#40FF9x 霓虹绿）逐页实测 ===")
bad_band = []
for n in range(1, 47):
    px = imgs[n].load()
    ys = [y for y in range(380, 540) if px[500, y][0] < 150 and px[500, y][1] > 210 and px[500, y][2] > 100]
    ytop = ys[0] if ys else None
    # 该带最高点 x 扫描
    xs = []
    if ys:
        for x in range(0, 960, 4):
            if px[x, ys[0] + 2][1] > 210 and px[x, ys[0] + 2][0] < 150: xs.append(x)
    o.append("  p%-3d 带顶 y=%-4s  hue范围 x=%s~%s" % (n, ytop, xs[0] if xs else "-", xs[-1] if xs else "-"))
    if ytop is not None and ytop < 490: bad_band.append((n, ytop))
o.append("  带顶 <490（比标称 494 更早出现）的页: %s" % bad_band)

# ---- 粉笔尘 / 右侧带底噪 ----
o.append("")
o.append("=== 右侧净空带 640-960 的板面底噪（粉笔尘）===")
o.append("页  带宽内亮度sd  尘斑(亮度高于底0.06)占比%  最大尘斑连通近似(px)")
tot = []
for n in range(1, 47):
    px = imgs[n].load()
    Ls = []
    cnt = collections.Counter()
    for y in range(40, 460, 2):
        for x in range(650, 950, 2):
            c = px[x, y]; Ls.append(lum(c)); cnt[c] += 1
    base = cnt.most_common(1)[0][0]
    lb = lum(base)
    nd = sum(1 for v in Ls if v - lb > 0.06)
    mean = sum(Ls) / len(Ls)
    sd = math.sqrt(sum((v - mean) ** 2 for v in Ls) / len(Ls))
    tot.append((n, sd, nd * 100.0 / len(Ls), hx(base)))
    o.append("  p%-3d  sd=%.3f  尘占比=%5.1f%%  底=%s" % (n, sd, nd * 100.0 / len(Ls), hx(base)))
o.append("  底噪 sd 中位 = %.3f ；尘占比 中位 = %.1f%%" % (
    sorted(t[1] for t in tot)[23], sorted(t[2] for t in tot)[23]))

# ---- 内容覆盖密度（页内左 2/3 的非底色像素率）----
o.append("")
o.append("=== 内容覆盖率（左侧内容区 x<640）===")
cvs = []
for n in range(1, 47):
    px = imgs[n].load()
    cnt = collections.Counter()
    for y in range(0, H, 3):
        for x in range(0, 640, 3):
            cnt[px[x, y]] += 1
    base = set(c for c, _ in cnt.most_common(2))
    ink = sum(v for c, v in cnt.items() if c not in base)
    t = len(range(0, H, 3)) * len(range(0, 640, 3))
    cvs.append((n, ink * 1.0 / t))
o.append("  逐页: " + " ".join("%.2f" % v for _, v in cvs))
o.append("  均值 %.3f 中位 %.3f 最低5 %s 最高5 %s" % (
    sum(v for _, v in cvs) / 46, sorted(v for _, v in cvs)[23],
    sorted(cvs, key=lambda p: p[1])[:5], sorted(cvs, key=lambda p: p[1], reverse=True)[:5]))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_final.txt", "w", encoding="utf-8").write(txt)
print(txt[:5200])

