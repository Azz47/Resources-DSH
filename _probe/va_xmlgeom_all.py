# -*- coding: utf-8 -*-
"""全册 46 页：pptx XML 几何 vs 设计几何 全等校验（含连线 cxnSp）"""
import zipfile, json, io, os
from xml.etree import ElementTree as ET

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
PPTX = os.path.join(D, "第二单元 进入新时代-单元思考与行动-参赛版.pptx")
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
PAGES = lay["pages"]
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
EMU = 12700.0
z = zipfile.ZipFile(PPTX)


def shapes(n):
    root = ET.fromstring(z.read("ppt/slides/slide%d.xml" % n))
    tree = root.find(".//p:cSld/p:spTree", NS)
    out = {}
    for sp in tree:
        tag = sp.tag.split("}")[1]
        if tag not in ("sp", "pic", "graphicFrame", "cxnSp", "grpSp"):
            continue
        nv = sp.find(".//p:cNvPr", NS)
        if nv is None:
            continue
        name = nv.get("name")
        xfrm = sp.find(".//a:xfrm", NS)
        if xfrm is None:
            continue
        off = xfrm.find("a:off", NS); ext = xfrm.find("a:ext", NS)
        if off is None or ext is None:
            continue
        out[name] = (int(off.get("x")) / EMU, int(off.get("y")) / EMU,
                     int(ext.get("cx")) / EMU, int(ext.get("cy")) / EMU)
    return out


tot_el = tot_miss = tot_bad = 0
lines = []
worst = []
for pg in range(1, 47):
    sh = shapes(pg)
    els = PAGES[pg - 1].get("elements", [])
    miss, bad = [], []
    for e in els:
        k = e.get("id"); b = e["bounds"]
        if k not in sh:
            miss.append(k); continue
        x, y, w, h = sh[k]
        if abs(x - b["x"]) > 1.5 or abs(y - b["y"]) > 1.5 or abs(w - b["w"]) > 2.5 or abs(h - b["h"]) > 2.5:
            bad.append((k, b, (x, y, w, h)))
    tot_el += len(els); tot_miss += len(miss); tot_bad += len(bad)
    extra = [k for k in sh if k not in {e.get("id") for e in els}]
    lines.append("p%-3d 设计元件=%-3d XML形状=%-3d 缺=%-3d 几何不符=%-3d 仅XML有=%s" % (
        pg, len(els), len(sh), len(miss), len(bad), extra if extra else "-"))
    for k, b, a in bad:
        worst.append((pg, k, b, a))
z.close()
rep = ["=== 全册几何一致性（设计 vs pptx XML 形状）===", ""] + lines + [
    "", "合计：设计元件=%d  缺失=%d  几何不符=%d" % (tot_el, tot_miss, tot_bad)]
if worst:
    rep.append("")
    rep.append("几何不符明细：")
    for pg, k, b, a in worst[:40]:
        rep.append("  p%-3d %-22s 设计(x%-6.1f y%-6.1f w%-6.1f h%-6.1f) XML(x%-6.1f y%-6.1f w%-6.1f h%-6.1f)" % (
            pg, k, b["x"], b["y"], b["w"], b["h"], a[0], a[1], a[2], a[3]))
io.open(r"D:\Resources\DSH\_probe\va_xmlgeom_all.txt", "w", encoding="utf-8").write("\n".join(rep))
print("\n".join(rep[:6]))
print("...")
print("\n".join(rep[-30:]))
