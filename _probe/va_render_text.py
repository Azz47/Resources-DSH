# -*- coding: utf-8 -*-
"""渲染实测对比度 + 底部霓虹带 + 右侧粉笔尘实测（H3/H6 取证）"""
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
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def hx(c):
    return "#%02X%02X%02X" % c

lay = json.loads(io.open(os.path.join(D, "preview", "layout.json"), "rb").read().decode("gbk", "replace"))
imgs = {n: Image.open(os.path.join(SH, "%02d.png" % n)).convert("RGB") for n in range(1, 47)}

def flat(elems, out=None):
    if out is None: out = []
    for e in elems or []:
        out.append(e)
        if e.get("children"): flat(e["children"], out)
    return out

o = []
o.append("=== A. 渲染实测：正文/标题 视觉可读性（字色取框内极端值，底色取框内众数）===")
o.append("页  元素        声明字号  声明色    实测字色  实测底色  实测比  声明比")
rows = []
for idx in range(46):
    n = idx + 1
    im = imgs[n]
    px = im.load()
    for e in flat((lay["pages"][idx].get("elements"))):
        if e.get("kind") != "text": continue
        t = (e.get("text") or "").strip()
        if not t: continue
        st = e.get("style") or {}
        b = e.get("bounds") or {}
        fs = st.get("fontSize") or 0
        x0, y0 = int(b.get("x", 0)), int(b.get("y", 0))
        x1, y1 = int(x0 + b.get("w", 0)), int(y0 + b.get("h", 0))
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
        if x1 - x0 < 4 or y1 - y0 < 4: continue
        cnt = collections.Counter(px[x, y] for y in range(y0, y1) for x in range(x0, x1))
        bg = cnt.most_common(1)[0][0]
        lb = lum(bg)
        # 字色 = 与底亮度距离最大的高频色（取 top40 里的极值）
        best = None; bd = -1
        for c, v in cnt.most_common(40):
            if v < 3: continue
            d = abs(lum(c) - lb)
            if d > bd: bd, best = d, c
        if best is None: continue
        fd = st.get("color")
        dec = None
        if isinstance(fd, str) and fd.startswith("#") and len(fd) == 7:
            dc = tuple(int(fd[i:i+2], 16) for i in (1, 3, 5))
            dec = cr(dc, bg)
        ratio = cr(best, bg)
        big = (fs >= 18) or (fs >= 14 and st.get("bold"))
        need = 3.0 if big else 4.5
        rows.append({"n": n, "id": e.get("id"), "fs": fs, "bold": bool(st.get("bold")),
                     "declared": fd, "measured_fg": hx(best), "measured_bg": hx(bg),
                     "ratio": round(ratio, 2), "declared_ratio": round(dec, 2) if dec else None,
                     "need": need, "text": t[:20]})

bad = [r for r in rows if r["ratio"] < r["need"]]
o.append("文本元素总数 %d ；实测未达 AA = %d" % (len(rows), len(bad)))
for r in sorted(bad, key=lambda r: r["ratio"]):
    o.append("p%-3d %-12s %2dpt%-4s 声明%-8s 实测字%-8s 底%-8s 比=%5.2f 需%.1f  「%s」" % (
        r["n"], r["id"], r["fs"], "粗" if r["bold"] else "", r["declared"] or "-",
        r["measured_fg"], r["measured_bg"], r["ratio"], r["need"], r["text"]))
o.append("")
o.append("实测比 < 4.5 的全部（含大字）共 %d" % len([r for r in rows if r["ratio"] < 4.5]))
for r in sorted([r for r in rows if r["ratio"] < 4.5], key=lambda r: r["ratio"])[:40]:
    o.append("  p%-3d %-12s %2dpt 比=%5.2f  字%s 底%s  「%s」" % (
        r["n"], r["id"], r["fs"], r["ratio"], r["measured_fg"], r["measured_bg"], r["text"]))
o.append("")
o.append("声明色 vs 实测字色 偏差（|ΔL| > 0.05 视为渲染/字体替换）")
dev = [r for r in rows if r["declared_ratio"] and abs(r["declared_ratio"] - r["ratio"]) > 0.8]
o.append("  偏差>0.8 的元素数 = %d / %d" % (len(dev), len(rows)))
for r in dev[:25]:
    o.append("  p%-3d %-12s 声明比%5.2f 实测比%5.2f  声明%s 实测字%s 底%s" % (
        r["n"], r["id"], r["declared_ratio"], r["ratio"], r["declared"], r["measured_fg"], r["measured_bg"]))

o.append("")
o.append("=== B. 底部霓虹绿带（离群色）实测 ===")
for n in (1, 10, 20, 30, 40, 46):
    im = imgs[n]; px = im.load()
    ys = []
    for y in range(400, 540):
        c = px[500, y]
        if c[1] > 200 and c[0] < 140 and c[2] > 120:  # 霓虹绿判据
            ys.append(y)
    o.append("  p%-3d 霓虹带 x=500 行范围 = %s ~ %s  (高度 %d px)" % (
        n, ys[0] if ys else "-", ys[-1] if ys else "-", len(ys)))
im = imgs[20]; px = im.load()
o.append("  霓虹带色值样本 p20: " + " ".join("y%d=%s" % (y, hx(px[500, y])) for y in (500, 505, 510, 515, 520, 530, 539)))
o.append("  带下木框缺失：x=500,y=530 与 x=920,y=530 色 %s / %s" % (hx(px[500, 530]), hx(px[920, 530])))

o.append("")
o.append("=== C. 右侧净空带 640-960 粉笔尘/装饰 实测（H2 讲师站位区可用度）===")
o.append("页  尘斑色   尘斑亮度  板底亮度  亮度差  尘斑面积%  右侧带亮度sd")
for n in (1, 6, 20, 28, 36, 46):
    im = imgs[n]; px = im.load()
    cnt = collections.Counter()
    for y in range(40, 450, 2):
        for x in range(660, 930, 2):
            cnt[px[x, y]] += 1
    base = cnt.most_common(1)[0][0]
    dust = None
    for c, v in cnt.most_common(6):
        if lum(c) - lum(base) > 0.08: dust = c; break
    nd = nun = 0
    Ls = []
    for y in range(40, 450, 2):
        for x in range(660, 930, 2):
            c = px[x, y]; Ls.append(lum(c)); nun += 1
            if lum(c) - lum(base) > 0.08: nd += 1
    mean = sum(Ls) / len(Ls)
    sd = math.sqrt(sum((v - mean) ** 2 for v in Ls) / len(Ls))
    o.append("p%-3d %-8s %-9.3f %-9.3f %-8.3f %-10.1f %.3f" % (
        n, hx(dust) if dust else "-", lum(dust) if dust else 0, lum(base), 
        (lum(dust) - lum(base)) if dust else 0, nd * 100.0 / nun, sd))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_render_text.txt", "w", encoding="utf-8").write(txt)
json.dump(rows, io.open(r"D:\Resources\DSH\_probe\va_render_text.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(txt[:7000])
