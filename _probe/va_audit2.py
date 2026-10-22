# -*- coding: utf-8 -*-
"""1) 判定 metrics.overflowX 语义  2) 自算内容互压（text/table/chart 之间的部分重叠）"""
import json, io
D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.load(io.open(D + r"\preview\layout.json", encoding="utf-8"))
W, H = 960, 540
LIMIT_R = 640

o = []
o.append("=== 1. overflow 语义判定 ===")
o.append("样本: id | box.w | textW | maxLineW | overflowX | overflowY | lines")
bad = []
for p in lay["pages"][:8]:
    for e in p.get("elements", []):
        mt = e.get("metrics") or {}
        if not mt: continue
        if abs(mt.get("overflowX") or 0) > 20:
            o.append("  %-14s | w=%-6s | textW=%-7s | maxLine=%-7s | ovfX=%-6s | ovfY=%-4s | lines=%s" % (
                e.get("id"), e["bounds"]["w"], round(mt.get("textW", 0), 1),
                round(max(mt.get("lineWidths") or [0]), 1), mt.get("overflowX"), mt.get("overflowY"), mt.get("lines")))
o.append("")
# 结论判定：ovfX 是否等于「单行最宽 - 框宽」的剩余还是超出
e0 = None
for p in lay["pages"]:
    for e in p.get("elements", []):
        if (e.get("metrics") or {}).get("overflowX"):
            e0 = e; break
    if e0: break
mt = e0["metrics"]
o.append("  取样元素 %s: w=%s, textW=%s, maxLineW=%s, ovfX=%s" % (
    e0["id"], e0["bounds"]["w"], mt.get("textW"), max(mt.get("lineWidths") or [0]), mt.get("overflowX")))
o.append("  → 若 ovfX ≈ w - maxLineW = %.1f ：表示【剩余空间】" % (e0["bounds"]["w"] - max(mt.get("lineWidths") or [0])))
o.append("  → 若 ovfX ≈ maxLineW - w = %.1f ：表示【真实溢出】" % (max(mt.get("lineWidths") or [0]) - e0["bounds"]["w"]))
o.append("")

o.append("=== 2. 自算内容互压 (text/image/table/chart 两两交叠) ===")
o.append("  规则: 一方完全包含于另一方 = 承载(忽略); 部分交叠 或 text×text = 记为风险")
def inter(a, b):
    x1 = max(a["x"], b["x"]); y1 = max(a["y"], b["y"])
    x2 = min(a["x"] + a["w"], b["x"] + b["w"]); y2 = min(a["y"] + a["h"], b["y"] + b["h"])
    if x2 <= x1 or y2 <= y1: return 0.0
    return (x2 - x1) * (y2 - y1)

KINDS = {"text", "image", "table", "chart", "icon"}
risk_total = 0
for p in lay["pages"]:
    els = [e for e in p.get("elements", []) if e.get("kind") in KINDS and e.get("bounds")]
    if len(els) < 2: continue
    found = []
    for i in range(len(els)):
        for j in range(i + 1, len(els)):
            a, b = els[i], els[j]
            A, B = a["bounds"], b["bounds"]
            ov = inter(A, B)
            if ov <= 1: continue
            aa = A["w"] * A["h"]; ab = B["w"] * B["h"]
            contains = (ov >= 0.92 * min(aa, ab))
            both_text = (a.get("kind") == "text" and b.get("kind") == "text")
            if contains and not both_text:
                continue                      # 承载关系：面板/图片内嵌文字，忽略
            found.append((a.get("id"), a.get("kind"), b.get("id"), b.get("kind"),
                          round(ov), round(ov / max(1, min(aa, ab)) * 100, 1),
                          "TEXT-TEXT" if both_text else ("contain" if contains else "partial")))
    if found:
        risk_total += len(found)
        o.append("  [%s] %d 对:" % (p["file"].split("/")[-1], len(found)))
        for f in found:
            o.append("      %s(%s) × %s(%s)  交叠=%spx² 占小者=%s%%  %s" % f)
o.append("  => 风险对总数 = %d" % risk_total)
o.append("")

o.append("=== 3. 页眉/页脚/页码 等跨页元件识别 ===")
import collections
sig = collections.defaultdict(list)
for p in lay["pages"]:
    n = p["file"].split("/")[-1]
    for e in p.get("elements", []):
        b = e["bounds"]; y = b["y"]; x = b["x"]
        if y < 70 or y > 470 or x > 560:
            sig[(e.get("id"), e.get("kind"), round(x), round(y), round(b["w"]), round(b["h"]))].append(n)
o.append("  页顶(y<70)/页底(y>470)/右侧(x>560) 且 id 在 >=20 页重复出现的元件:")
cnt = 0
for k, v in sorted(sig.items(), key=lambda kv: -len(kv[1])):
    if len(v) >= 20:
        cnt += 1
        o.append("   %-34s 出现 %d 页" % (str(k), len(v)))
o.append("  => 共 %d 个跨页固定元件" % cnt)
io.open(r"D:\Resources\DSH\_probe\va_geom_report2.txt", "w", encoding="utf-8").write("\n".join(o))
print("OK")
