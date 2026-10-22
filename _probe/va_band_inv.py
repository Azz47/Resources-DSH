# -*- coding: utf-8 -*-
"""注记带系统的全页清点（不加 y 过滤）+ p14/p16 解剖"""
import json, io, collections

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
P = lay["pages"]

o = ["=== 全页清点：宽>=500 的横带元件（任意 y）、竖轨(w<=6)、脚注 sn ==="]
band_pages, rail_pages, sn_pages = [], [], []
for i, p in enumerate(P):
    pg = i + 1
    bands, rails, sns, extras = [], [], [], []
    for e in p.get("elements", []):
        b = e["bounds"]
        t = (e.get("text") or "").replace("\n", " ")[:40]
        if b["w"] >= 500 and 18 <= b["h"] <= 62:
            bands.append("%s(y%.0f h%.0f)%s" % (e.get("id"), b["y"], b["h"], ("【" + t + "】") if t else ""))
        if b["w"] <= 7 and b["h"] >= 18:
            rails.append("%s@y%.0f" % (e.get("id"), b["y"]))
        if e.get("id") == "sn" or (t.startswith(("图片与素材来源", "资料依据", "配图为", "凡引用", "数据来源"))):
            sns.append("%s(y%.0f)%s" % (e.get("id"), b["y"], "【" + t + "】"))
    if bands: band_pages.append(pg)
    if rails: rail_pages.append(pg)
    if sns: sn_pages.append(pg)
    o.append("p%-3d 带:%-3d %s | 轨:%s | 脚注:%s" % (pg, len(bands), " ; ".join(bands) if bands else "-",
                                                    ",".join(rails) if rails else "-", " ; ".join(sns) if sns else "-"))

o += ["", "有横带的页(%d): %s" % (len(band_pages), band_pages),
      "无横带的页(%d): %s" % (46 - len(band_pages), [x for x in range(1, 47) if x not in band_pages]),
      "有竖轨的页(%d): %s" % (len(rail_pages), rail_pages),
      "有脚注的页(%d): %s" % (len(sn_pages), sn_pages)]

o += ["", "=== p14 全部元件 ==="]
for e in P[13].get("elements", []):
    b = e["bounds"]
    o.append("  %-16s %-6s x%-7.1f y%-7.1f w%-7.1f h%-6.1f %s" % (e.get("id"), e.get("kind"), b["x"], b["y"], b["w"], b["h"], (e.get("text") or "").replace("\n", " / ")[:52]))
o += ["", "=== p16 y>=340 元件 ==="]
for e in P[15].get("elements", []):
    b = e["bounds"]
    if b["y"] >= 340:
        o.append("  %-16s %-6s x%-7.1f y%-7.1f w%-7.1f h%-6.1f %s" % (e.get("id"), e.get("kind"), b["x"], b["y"], b["w"], b["h"], (e.get("text") or "").replace("\n", " / ")[:52]))
io.open(r"D:\Resources\DSH\_probe\va_band_inv.txt", "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o[:50]))
print("...")
print("\n".join(o[-30:]))
