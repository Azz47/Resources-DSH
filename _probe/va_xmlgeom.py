# -*- coding: utf-8 -*-
"""真值校验：pptx slide XML 里的形状几何 vs layout.json 设计几何（EMU→pt，1pt=12700EMU）"""
import zipfile, re, json, io, os
from xml.etree import ElementTree as ET

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
PPTX = os.path.join(D, "第二单元 进入新时代-单元思考与行动-参赛版.pptx")
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
PAGES = lay["pages"]

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
EMU_PT = 12700.0
z = zipfile.ZipFile(PPTX)


def slide_shapes(n):
    root = ET.fromstring(z.read("ppt/slides/slide%d.xml" % n))
    out = []
    spTree = root.find(".//p:cSld/p:spTree", NS)
    for sp in spTree:
        tag = sp.tag.split("}")[1]
        if tag not in ("sp", "pic", "graphicFrame"):
            continue
        nv = sp.find(".//p:cNvPr", NS)
        name = nv.get("name") if nv is not None else "?"
        xfrm = sp.find(".//a:xfrm", NS)
        if xfrm is None:
            continue
        off = xfrm.find("a:off", NS); ext = xfrm.find("a:ext", NS)
        if off is None or ext is None:
            continue
        x = int(off.get("x")) / EMU_PT; y = int(off.get("y")) / EMU_PT
        cx = int(ext.get("cx")) / EMU_PT; cy = int(ext.get("cy")) / EMU_PT
        txt = "".join(t.text or "" for t in sp.findall(".//a:t", NS))
        out.append((name, tag, round(x, 1), round(y, 1), round(cx, 1), round(cy, 1), txt[:34]))
    return out


rep = []
for pg in (17, 33, 5):
    rep.append("=" * 70)
    rep.append("幻灯片 %d（=页面 p%02d）XML 形状（pt）" % (pg, pg))
    rep.append("  %-26s %-6s %8s %8s %8s %8s  %s" % ("name", "type", "x", "y", "w", "h", "text"))
    for row in slide_shapes(pg):
        rep.append("  %-26s %-6s %8.1f %8.1f %8.1f %8.1f  %s" % row)
    rep.append("-- 设计（layout.json）--")
    for e in PAGES[pg - 1].get("elements", []):
        b = e["bounds"]
        rep.append("  %-26s %-6s %8.1f %8.1f %8.1f %8.1f  %s" % (
            e.get("id"), e.get("kind"), b["x"], b["y"], b["w"], b["h"], (e.get("text") or "").strip()[:34]))
    # 几何差异
    d = {e.get("id"): e["bounds"] for e in PAGES[pg - 1].get("elements", [])}
    rep.append("-- 差异（设计 id 未找到对应 XML / 或几何不符）--")
    xnames = {}
    for name, tag, x, y, cx, cy, txt in slide_shapes(pg):
        xnames[name] = (x, y, cx, cy)
    miss = [k for k in d if k not in xnames]
    bad = []
    for k, b in d.items():
        if k in xnames:
            x, y, cx, cy = xnames[k]
            if abs(x - b["x"]) > 1.5 or abs(y - b["y"]) > 1.5 or abs(cx - b["w"]) > 2.5 or abs(cy - b["h"]) > 2.5:
                bad.append((k, b, (x, y, cx, cy)))
    rep.append("  设计元件数=%d  XML 形状数=%d  名称未对上=%d" % (len(d), len(xnames), len(miss)))
    rep.append("  名称未对上: %s" % miss)
    rep.append("  几何不符 %d 个:" % len(bad))
    for k, b, a in bad[:12]:
        rep.append("     %-24s 设计(x%.0f y%.0f w%.0f h%.0f)  XML(x%.0f y%.0f w%.0f h%.0f)" % (
            k, b["x"], b["y"], b["w"], b["h"], a[0], a[1], a[2], a[3]))
z.close()
io.open(r"D:\Resources\DSH\_probe\va_xmlgeom.txt", "w", encoding="utf-8").write("\n".join(rep))
print("\n".join(rep[-60:]))
