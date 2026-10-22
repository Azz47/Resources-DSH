# -*- coding: utf-8 -*-
"""视觉验收 - 几何审计：逐页取元素包围盒，检查右1/3侵入、越界、贴边、溢出、背景一致性。"""
import json, io, sys
from collections import Counter, defaultdict

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
mea = json.load(io.open(D + r"\preview\measured.json", encoding="utf-8"))

_s = lay["size"]
if isinstance(_s, dict):
    W, H = float(_s.get("w") or _s.get("width")), float(_s.get("h") or _s.get("height"))
else:
    W, H = [float(v) for v in str(_s).replace("x", ",").split(",")[:2]]
W, H = int(W), int(H)
SA = lay["pages"][0]["safeArea"]
LIMIT_R = W - SA["right"]          # 640 内容右界
SAFE_T, SAFE_B = SA["top"], H - SA["bottom"]

out = []
out.append("canvas=%dx%d  safeArea=%s  content-right-limit=%s" % (W, H, SA, LIMIT_R))

# ---- 逐页 ----
rows = []
for p in lay["pages"]:
    els = p.get("elements", []) or []
    name = p["file"].split("/")[-1]
    bg = p.get("background") or {}
    bgdesc = bg.get("type") + ":" + str(bg.get("src") or bg.get("fill") or "")
    maxx = 0.0; minx1e9 = 1e9; maxb = 0.0; mintop = 1e9
    over_right = []      # 侵入右1/3
    off_page = []        # 越出画布
    near_edge = []       # 距画布边 <10px
    text_ovf = []        # 文本溢出
    in_bottom = []       # 落在底部安全带(注记条区)
    for e in els:
        b = e.get("bounds") or {}
        x = float(b.get("x", 0)); y = float(b.get("y", 0))
        w = float(b.get("w", 0)); h = float(b.get("h", 0))
        r = x + w; bot = y + h
        minx1e9 = min(minx1e9, x); maxx = max(maxx, r)
        mintop = min(mintop, y);   maxb = max(maxb, bot)
        eid = e.get("id", "?")
        if r > LIMIT_R + 0.5:
            over_right.append((eid, e.get("kind"), round(x), round(w), round(r), round(r - LIMIT_R)))
        if r > W + 0.5 or bot > H + 0.5 or x < -0.5 or y < -0.5:
            off_page.append((eid, round(x), round(y), round(w), round(h), round(r), round(bot)))
        d = min(x, y, W - r, H - bot)
        if d < 10:
            near_edge.append((eid, round(d, 1)))
        mt = e.get("metrics") or {}
        if (mt.get("overflowY") or 0) > 0.5 or (mt.get("overflowX") or 0) > 0.5:
            text_ovf.append((eid, round(mt.get("overflowY") or 0, 1), round(mt.get("overflowX") or 0, 1), (e.get("text") or "")[:18]))
        if y >= SAFE_B - 1 or bot > SAFE_B:
            in_bottom.append((eid, round(y), round(bot), (e.get("text") or "")[:14]))
    rows.append(dict(name=name, bg=bgdesc, n=len(els), maxx=round(maxx, 1), minx=round(minx1e9, 1),
                     top=round(mintop, 1), bot=round(maxb, 1),
                     over_right=over_right, off_page=off_page, near_edge=near_edge,
                     text_ovf=text_ovf, in_bottom=in_bottom,
                     exp_ov=len(p.get("expectedOverlaps") or []),
                     exp_oos=len(p.get("expectedOutOfSafeArea") or [])))

out.append("\n==== A. 背景来源一致性 (page | bg | elements | maxRight | maxBottom | expOverlap/OutSafe) ====")
for r in rows:
    out.append("%-18s | %-28s | n=%-3d | R=%-6s | B=%-6s | %s/%s" % (
        r["name"], r["bg"][:28], r["n"], r["maxx"], r["bot"], r["exp_ov"], r["exp_oos"]))

bgc = Counter(r["bg"] for r in rows)
out.append("\n==== B. 背景种类统计 ====")
for k, v in bgc.most_common():
    out.append("  %-32s x%d" % (k[:32], v))

out.append("\n==== C. 侵入右1/3 (x+w > %s) ====" % LIMIT_R)
hit = 0
for r in rows:
    if r["over_right"]:
        hit += 1
        out.append("  [%s] %d 个元素越界:" % (r["name"], len(r["over_right"])))
        for e in r["over_right"]:
            out.append("      id=%-14s kind=%-6s x=%-5s w=%-5s right=%-6s 超出=%s" % e)
out.append("  => 共 %d/46 页存在右1/3侵入" % hit)

out.append("\n==== D. 越出画布 (off-page) ====")
c = 0
for r in rows:
    if r["off_page"]:
        c += 1
        out.append("  [%s] %s" % (r["name"], r["off_page"]))
out.append("  => 共 %d 页" % c)

out.append("\n==== E. 距画布边 <10px (贴边风险) ====")
c = 0
for r in rows:
    if r["near_edge"]:
        c += 1
        out.append("  [%s] %s" % (r["name"], r["near_edge"][:8]))
out.append("  => 共 %d 页" % c)

out.append("\n==== F. 文本溢出 (metrics.overflow) ====")
c = 0
for r in rows:
    if r["text_ovf"]:
        c += 1
        for e in r["text_ovf"]:
            out.append("  [%s] id=%-14s ovfY=%-6s ovfX=%-6s text=%s" % (r["name"], e[0], e[1], e[2], e[3]))
out.append("  => 共 %d 页" % c)

out.append("\n==== G. 底部安全带 (y>=%s 或 bottom>%s) 元素 ====" % (SAFE_B, SAFE_B))
for r in rows:
    if r["in_bottom"]:
        out.append("  [%-18s] %s" % (r["name"], r["in_bottom"][:6]))

out.append("\n==== H. 内容底部位置分布 (maxBottom) ====")
import statistics
bs = [r["bot"] for r in rows]
out.append("  min=%s  median=%s  max=%s  (SAFE_B=%s)" % (min(bs), statistics.median(bs), max(bs), SAFE_B))
for r in sorted(rows, key=lambda r: r["bot"]):
    out.append("   %-18s bottom=%s" % (r["name"], r["bot"]))

out.append("\n==== I. 内容右界分布 (maxRight, 目标 640) ====")
xs = [r["maxx"] for r in rows]
out.append("  min=%s  median=%s  max=%s" % (min(xs), statistics.median(xs), max(xs)))
for r in sorted(rows, key=lambda r: r["maxx"]):
    out.append("   %-18s maxRight=%s" % (r["name"], r["maxx"]))

out.append("\n==== J. measured.json (浏览器实测) ====")
out.append("  browser=%s size=%s pages=%d" % (mea.get("browser"), mea.get("size"), len(mea.get("pages") or [])))
if mea.get("pages"):
    p0 = mea["pages"][0]
    out.append("  page[0] keys=%s" % (list(p0.keys()),))

txt = "\n".join(out)
io.open(r"D:\Resources\DSH\_probe\va_geom_report.txt", "w", encoding="utf-8").write(txt)
print("WROTE", len(txt))
