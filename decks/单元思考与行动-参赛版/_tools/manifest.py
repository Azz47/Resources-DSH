# -*- coding: utf-8 -*-
"""极简 YAML 扫描器：只为把导入后的 pages/slide_*.yaml 变成可读内容清单（不依赖 pyyaml）。"""
import io
import os
import re

BASE = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
OUT = os.path.join(BASE, "_tools", "content_manifest.txt")

def parse(path):
    d = {"elements": [], "notes": "", "background": ""}
    cur = None
    in_notes = False
    notes = []
    for raw in io.open(path, encoding="utf8"):
        line = raw.rstrip("\n")
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        if in_notes:
            if line.startswith("  ") or line.startswith("\t"):
                notes.append(s)
                continue
            in_notes = False
        if s.startswith("pageType:") or s.startswith("version:"):
            continue
        if s.startswith("notes:"):
            v = s[len("notes:"):].strip()
            if v in ("|", ">", "|-"):
                in_notes = True
                notes = []
            else:
                d["notes"] = v.strip('"')
            continue
        if s.startswith("background:"):
            m = re.search(r"src:\s*([^,}]+)", s)
            d["background"] = (m.group(1).strip().strip('"').split("/")[-1] if m else s)
            continue
        if s.startswith("- elementId:"):
            cur = {"id": s.split(":", 1)[1].strip().strip('"')}
            d["elements"].append(cur)
            continue
        if cur is None:
            continue
        for key in ("elementType", "kind", "src", "fit", "fill", "align", "fontFamily", "fontSize", "color", "bold"):
            if s.startswith(key + ":"):
                cur[key] = s.split(":", 1)[1].strip().strip('"')
        if s.startswith("bounds:"):
            cur["bounds"] = s.split(":", 1)[1].strip()
        if s.startswith("line:"):
            cur["line"] = s.split(":", 1)[1].strip()
        if s.startswith("text:"):
            cur["text"] = s.split(":", 1)[1].strip().strip('"')
    d["notes"] = " ".join(notes) if notes else d["notes"]
    return d

lines = []
summary = []
for i in range(1, 41):
    p = os.path.join(BASE, "pages", "slide_%02d.yaml" % i)
    d = parse(p)
    els = d["elements"]
    lines.append("")
    lines.append("### P%02d  bg=%s  notes=%r" % (i, d["background"], d["notes"][:70]))
    nT = nI = nS = nL = 0
    for e in els:
        t = (e.get("elementType") or "").lower()
        b = e.get("bounds", "")
        if t == "text":
            nT += 1
            lines.append("  T   %-26s %-24s sz=%-4s %-8s %-7s | %s"
                         % (e["id"], b, e.get("fontSize", ""), e.get("fontFamily", ""), e.get("align", ""), e.get("text", "")))
        elif t == "image":
            nI += 1
            lines.append("  IMG %-26s %-24s %s" % (e["id"], b, e.get("src", "")))
        elif t == "line":
            nL += 1
            lines.append("  LN  %-26s %-24s %s" % (e["id"], b, e.get("line", "")))
        else:
            nS += 1
            lines.append("  SHP %-26s %-24s kind=%-10s fill=%s" % (e["id"], b, e.get("kind", ""), e.get("fill", "")))
    summary.append("P%02d text=%-3d img=%-2d shp=%-3d line=%-2d bg=%s" % (i, nT, nI, nS, nL, d["background"]))

io.open(OUT, "w", encoding="utf8").write("\n".join(lines))
print("\n".join(summary))
print("manifest -> %s  (%d lines)" % (OUT, len(lines)))
