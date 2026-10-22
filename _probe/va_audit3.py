# -*- coding: utf-8 -*-
"""跨页元件覆盖 + 底部注记条识别 + 环节色"""
import json, io, collections
D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
o = []
o.append("=== 1. 逐页跨页元件覆盖矩阵 ===")
KEY = ["hd_chip_a", "hd_chip_b", "hd_info", "hd_num", "hd_secbg", "hd_sec"]
o.append("%-4s %-18s %s" % ("pg", "file", "  ".join(k[:8] for k in KEY)))
miss = collections.defaultdict(list)
for i, p in enumerate(lay["pages"]):
    ids = {e.get("id") for e in p.get("elements", [])}
    marks = []
    for k in KEY:
        has = k in ids
        marks.append("  YES   " if has else "  ---   ")
        if not has: miss[k].append(i + 1)
    o.append("%-4d %-18s %s" % (i + 1, p["file"].split("/")[-1], "".join(marks)))
o.append("")
for k in KEY:
    v = miss[k]
    o.append("  %-10s 缺失页: %s" % (k, v if v else "无"))

o.append("\n=== 2. 各页 hd_info / hd_sec / hd_num 文本内容 ===")
for i, p in enumerate(lay["pages"]):
    d = {}
    for e in p.get("elements", []):
        if e.get("id") in ("hd_info", "hd_sec", "hd_num"):
            d[e["id"]] = (e.get("text") or "").strip()
    o.append("  p%-3d info=%-42s sec=%-18s num=%s" % (
        i + 1, d.get("hd_info", "(缺)")[:42], d.get("hd_sec", "(缺)")[:18], d.get("hd_num", "(缺)")))

o.append("\n=== 3. 多页重复元件（统一“底部注记条”候选） ===")
sig = collections.defaultdict(list)
for i, p in enumerate(lay["pages"]):
    for e in p.get("elements", []):
        b = e["bounds"]
        sig[(e.get("id"), e.get("kind"), round(b["x"]), round(b["y"]), round(b["w"]), round(b["h"]))].append(i + 1)
rep = sorted(sig.items(), key=lambda kv: -len(kv[1]))
for k, v in rep:
    if len(v) >= 8:
        o.append("  %-40s x%-3d 页: %s" % (str(k), len(v), v if len(v) <= 12 else "%s...%s" % (v[:6], v[-3:])))

o.append("\n=== 4. 底部带 (y 380-492) 逐页元件 ===")
for i, p in enumerate(lay["pages"]):
    band = []
    for e in p.get("elements", []):
        b = e["bounds"]
        if 380 <= b["y"] <= 492:
            band.append("%s@y%s h%s" % (e.get("id"), round(b["y"]), round(b["h"])))
    o.append("  p%-3d %s" % (i + 1, ", ".join(band) if band else "(空)"))

io.open(r"D:\Resources\DSH\_probe\va_geom_report3.txt", "w", encoding="utf-8").write("\n".join(o))
print("OK")
