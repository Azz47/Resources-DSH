# -*- coding: utf-8 -*-
"""1) 文字换行/纵向余量  2) 环节标签片底色（验证环节色编码）  3) p41/p27 细节"""
import json, io, os, collections
from PIL import Image

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
P = lay["pages"]

rows = []
for i, p in enumerate(P):
    for e in p.get("elements", []):
        m = e.get("metrics") or {}
        lw = m.get("lineWidths") or []
        if not lw:
            continue
        b = e["bounds"]
        rows.append((i + 1, e.get("id"), e.get("kind"), b["w"], max(lw), b["w"] - max(lw),
                     b["h"], m.get("textH") or 0, b["h"] - (m.get("textH") or 0),
                     (e.get("text") or "").replace("\n", " ")[:24]))

FMT = "  p%-3d %-24s %-6s w=%-6.1f maxLine=%-6.1f slackW=%-5.1f h=%-6.1f textH=%-6.1f slackH=%-6.1f %s"
o = ["=== 横向余量最小 22 个文本元素（slackW 小 = PowerPoint 字体更宽时可能重排）==="]
for r in sorted(rows, key=lambda x: x[5])[:22]:
    o.append(FMT % r)
o += ["", "=== 纵向余量最小 18 个（负数=溢出）==="]
for r in sorted(rows, key=lambda x: x[8])[:18]:
    o.append(FMT % r)
o += ["", "文本元素总数=%d  任一向余量为负=%d" % (len(rows), sum(1 for r in rows if r[5] < 0 or r[8] < 0))]

# 环节标签片底色
def hx(t):
    return "#%02X%02X%02X" % t

o += ["", "=== 环节标签片底色（采样 y45..47，取众数）==="]
chip = {}
for i in range(1, 47):
    im = Image.open(os.path.join(SH, "%02d.png" % i)).convert("RGB")
    c = collections.Counter()
    for y in range(45, 48):
        for x in range(60, 160):
            r, g, b = im.getpixel((x, y))
            c[(r // 8 * 8, g // 8 * 8, b // 8 * 8)] += 1
    chip[i] = hx(c.most_common(1)[0][0])
o.append("  " + "  ".join("p%02d=%s" % (k, v) for k, v in chip.items()))
grp = collections.defaultdict(list)
for k, v in chip.items():
    grp[v].append(k)
o.append("")
for v, ks in sorted(grp.items(), key=lambda kv: -len(kv[1])):
    o.append("  %s  %d 页: %s" % (v, len(ks), ks))

o += ["", "=== p41 y>=390 元素 ==="]
for e in P[40].get("elements", []):
    b = e["bounds"]
    o.append("  %-18s %-6s x%-7.1f y%-7.1f w%-7.1f h%-6.1f  %s" % (
        e.get("id"), e.get("kind"), b["x"], b["y"], b["w"], b["h"], (e.get("text") or "").replace("\n", " / ")[:56]))
o += ["", "=== p27 小元件（h<=5 或 w<=22）==="]
for e in P[26].get("elements", []):
    b = e["bounds"]
    if b["h"] <= 5 or b["w"] <= 22:
        o.append("  %-18s %-6s x%-7.1f y%-7.1f w%-7.1f h%-6.1f" % (
            e.get("id"), e.get("kind"), b["x"], b["y"], b["w"], b["h"]))
io.open(r"D:\Resources\DSH\_probe\va_slack.txt", "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o[:24]))
print("=== 环节色 ===")
print("\n".join(o[o.index("=== 环节标签片底色（采样 y45..47，取众数）==="):][:12]))
print("=== p41/p27 ===")
print("\n".join(o[-24:]))
