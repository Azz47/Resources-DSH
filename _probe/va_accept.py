# -*- coding: utf-8 -*-
"""视觉验收量测：把软要求转成可判定硬阈值，逐页取数。

输出 va_accept.json + 控制台摘要。
口径：
  H1/H2 右侧留白：内容元素 right<=640；装饰元素允许但需满足"低对比+小面积"
  H3    压图/对比度：WCAG 相对亮度比（前景字色 vs 该元素实际像素底）
  H6    字号：正文/标题 >=14pt（用户硬约束），页脚注记可 12pt
"""
import json, io, os, collections, math, re
from PIL import Image, ImageFilter

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")
W, H = 960, 540
CLEAR_X = 640.0      # H1 右边界
SAFE = {"top": 24, "bottom": 48, "left": 36, "right": 320}   # deck.yaml safeArea

# ---------- 颜色工具 ----------
def parse_color(c):
    if not isinstance(c, str):
        return None
    c = c.strip()
    m = re.match(r"^#([0-9A-Fa-f]{6})$", c)
    if m:
        v = int(m.group(1), 16)
        return ((v >> 16) & 255, (v >> 8) & 255, v & 255)
    m = re.match(r"^#([0-9A-Fa-f]{3})$", c)
    if m:
        s = m.group(1)
        return tuple(int(ch * 2, 16) for ch in s)
    return None

def lin(x):
    x = x / 255.0
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

def rel_lum(rgb):
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def contrast(rgb1, rgb2):
    l1, l2 = rel_lum(rgb1), rel_lum(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def hexs(rgb):
    return "#%02X%02X%02X" % rgb

# ---------- 读布局 ----------
raw = io.open(os.path.join(D, "preview", "layout.json"), "rb").read()
for enc in ("utf-8", "gbk", "utf-8-sig"):
    try:
        lay = json.loads(raw.decode(enc))
        break
    except Exception:
        continue
P = lay["pages"]
THEME = lay.get("theme", {})
MINS = (THEME.get("minFontSize") or 0)

def flat(elems, out=None, depth=0):
    """展开 groups 嵌套"""
    if out is None:
        out = []
    for e in elems or []:
        out.append((e, depth))
        if e.get("children"):
            flat(e["children"], out, depth + 1)
    return out

def norm(e):
    """统一取 bounds / style / metrics"""
    b = e.get("bounds") or {}
    st = e.get("style") or {}
    mt = e.get("metrics") or {}
    return {
        "id": e.get("id"), "kind": e.get("kind"), "role": e.get("role"),
        "x": b.get("x", 0), "y": b.get("y", 0), "w": b.get("w", 0), "h": b.get("h", 0),
        "fontSize": st.get("fontSize"), "color": st.get("color"),
        "bold": st.get("bold"), "align": st.get("align"),
        "text": (e.get("text") or "").replace("\n", " "),
        "lines": mt.get("lines"), "lineWidths": mt.get("lineWidths") or [],
        "textH": mt.get("textH"), "textW": mt.get("textW"),
        "contains": e.get("contains") or [],
        "fill": e.get("fill"),
    }

# ---------- 采样底色的像素工具 ----------
_cache = {}
def page_img(n):
    if n not in _cache:
        _cache[n] = Image.open(os.path.join(SH, "%02d.png" % n)).convert("RGB")
    return _cache[n]

def sample_ring(im, x0, y0, x1, y1, pad=3):
    """取元素四周一圈像素的众数色 = 该元素实际压着的底色"""
    Wp, Hp = im.size
    cnt = collections.Counter()
    def add(px):
        cnt[(px[0] // 6 * 6, px[1] // 6 * 6, px[2] // 6 * 6)] += 1
    xs = range(max(0, int(x0)), min(Wp, int(x1)))
    for y in (int(y0) - pad, int(y1) + pad - 1):
        if 0 <= y < Hp:
            for x in xs:
                add(im.getpixel((x, y)))
    ys = range(max(0, int(y0)), min(Hp, int(y1)))
    for x in (int(x0) - pad, int(x1) + pad - 1):
        if 0 <= x < Wp:
            for y in ys:
                add(im.getpixel((x, y)))
    if not cnt:
        return None
    return cnt.most_common(1)[0][0]

def bright_share(im, x0, y0, x1, y1):
    """框内"与暗字对比不足"的像素占比（底偏暗/偏花 → 文字会糊）"""
    Wp, Hp = im.size
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(Wp, int(x1)), min(Hp, int(y1))
    if x1 <= x0 or y1 <= y0:
        return None, None
    n = 0
    tot = 0
    mn, mx = 999, -999
    step = max(1, (x1 - x0) // 60)
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            r, g, b = im.getpixel((x, y))
            L = rel_lum((r, g, b))
            mn = min(mn, L); mx = max(mx, L)
            n += 1
            if L < 0.35:      # 偏暗像素
                tot += 1
    return (tot / n if n else 0), (mx - mn)

# ---------- 逐页 ----------
rows = []
for idx, p in enumerate(P):
    n = idx + 1
    els = [norm(e) for e, d in flat(p.get("elements"))]
    texts = [e for e in els if e["kind"] == "text" and (e["text"] or "").strip()]
    im = page_img(n)

    rec = {
        "n": n, "file": p.get("file"), "name": p.get("name"),
        "bg": (p.get("background") or {}).get("type"),
        "bg_src": (p.get("background") or {}).get("src"),
        "n_el": len(els), "n_text": len(texts),
        "expectedOverlaps": len(p.get("expectedOverlaps") or []),
        "expectedOutOfSafeArea": len(p.get("expectedOutOfSafeArea") or []),
    }

    # --- H1 右边界 ---
    right_edges = [(e["x"] + e["w"], e) for e in els if e["w"] or e["h"]]
    rec["max_right"] = round(max([r for r, _ in right_edges], default=0), 1)
    rec["over_640"] = sorted(
        [{"id": e["id"], "kind": e["kind"], "role": e["role"], "right": round(r, 1),
          "area": round(e["w"] * e["h"], 1), "text": e["text"][:28]}
         for r, e in right_edges if r > CLEAR_X + 0.01],
        key=lambda d: -d["right"])
    rec["n_over_640"] = len(rec["over_640"])

    # 右侧净空带里的"装饰"面积占比（H6 的合法交集判定）
    band_area = (W - CLEAR_X) * H
    dec_area = sum((min(e["x"] + e["w"], W) - CLEAR_X) * e["h"]
                   for e in els if e["x"] + e["w"] > CLEAR_X and e["kind"] != "text")
    rec["right_band_deco_area_pct"] = round(dec_area / band_area * 100, 2)

    # --- H6 字号 ---
    sizes = collections.Counter()
    small = []
    for e in texts:
        fs = e["fontSize"]
        if fs is None:
            continue
        sizes[fs] += 1
        if fs < 14:
            small.append({"id": e["id"], "fs": fs, "t": e["text"][:24]})
    rec["font_min"] = min(sizes) if sizes else None
    rec["font_hist"] = dict(sorted(sizes.items()))
    rec["font_lt14"] = small
    rec["n_font_lt14"] = len(small)

    # --- 文本溢出（布局器自算）---
    ovf = []
    for e in texts:
        lw = e["lineWidths"]
        slackW = e["w"] - max(lw) if lw else None
        slackH = (e["h"] - (e["textH"] or 0)) if e["textH"] is not None else None
        if (slackW is not None and slackW < 0) or (slackH is not None and slackH < 0):
            ovf.append({"id": e["id"], "slackW": round(slackW, 1) if slackW is not None else None,
                        "slackH": round(slackH, 1) if slackH is not None else None,
                        "t": e["text"][:24]})
    rec["overflow"] = ovf
    rec["n_overflow"] = len(ovf)
    # 紧余量（PowerPoint 字体更宽时会重排的候选）
    tight = [{"id": e["id"], "slackW": round(e["w"] - max(e["lineWidths"]), 1), "t": e["text"][:22]}
             for e in texts if e["lineWidths"] and 0 <= e["w"] - max(e["lineWidths"]) < 3]
    rec["tight_w"] = tight
    rec["n_tight_w"] = len(tight)

    # --- H3 文字压图 / 对比度 ---
    crows = []
    for e in texts:
        col = parse_color(e["color"])
        if col is None:
            continue
        bd = sample_ring(im, e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"])
        if bd is None:
            continue
        c = contrast(col, bd)
        dark_share, lrange = bright_share(im, e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"])
        crows.append({"id": e["id"], "fs": e["fontSize"], "bold": bool(e["bold"]),
                      "fg": hexs(col), "bg_sample": hexs(bd), "ratio": round(c, 2),
                      "txt": e["text"][:22]})
    rec["contrast"] = crows
    # AA 阈值：>=18pt 或 >=14pt粗体 = 大字(3.0)，否则 4.5
    def need(r):
        return 3.0 if ((r["fs"] or 0) >= 18 or ((r["fs"] or 0) >= 14 and r["bold"])) else 4.5
    bad = [dict(r, need=need(r)) for r in crows if r["ratio"] < need(r)]
    rec["contrast_fail"] = sorted(bad, key=lambda d: d["ratio"])
    rec["n_contrast_fail"] = len(bad)
    rec["contrast_min"] = round(min([r["ratio"] for r in crows], default=0), 2)
    # 投影级从严线（大屏环境光）7:1 只统计、不判死
    rec["contrast_lt7"] = len([r for r in crows if r["ratio"] < 7.0])

    # --- 出界（页面边界 / 安全区）---
    oob_page = [e["id"] for e in els
                if e["x"] < -0.01 or e["y"] < -0.01 or e["x"] + e["w"] > W + 0.01 or e["y"] + e["h"] > H + 0.01]
    oob_safe = [e["id"] for e in els
                if e["x"] < SAFE["left"] - 0.01
                or e["x"] + e["w"] > W - SAFE["right"] + 0.01
                or e["y"] < SAFE["top"] - 0.01
                or e["y"] + e["h"] > H - SAFE["bottom"] + 0.01]
    rec["oob_page"] = oob_page
    rec["oob_safe"] = oob_safe
    rec["n_oob_page"] = len(oob_page)
    rec["n_oob_safe"] = len(oob_safe)

    # --- 底部安全带：内容是否压到讲师/字幕区 ---
    rec["bottom_used"] = round(max([e["y"] + e["h"] for e in els if e["kind"] != "text" or True], default=0), 1)
    rows.append(rec)

json.dump(rows, io.open(r"D:\Resources\DSH\_probe\va_accept.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---------- 摘要 ----------
o = []
o.append("=== 1. 右侧 1/3 净空（H1/H2 硬约束：内容 right<=640）===")
bad = [r for r in rows if r["n_over_640"]]
o.append("  越界页数 = %d / 46" % len(bad))
for r in bad:
    o.append("  p%-3d max_right=%-7.1f 越界元素%d个: %s" % (
        r["n"], r["max_right"], r["n_over_640"],
        "; ".join("%s(%s,right=%.1f)" % (d["id"], d["kind"], d["right"]) for d in r["over_640"][:6])))
o.append("  逐页 max_right: " + " ".join("%.0f" % r["max_right"] for r in rows))
o.append("  右侧净空带内装饰面积占比>0 的页: %s" % (
    [(r["n"], r["right_band_deco_area_pct"]) for r in rows if r["right_band_deco_area_pct"] > 0]))

o.append("")
o.append("=== 2. 字号（H6：正文/标题 >=14pt）===")
o.append("  deck minFontSize = %s" % MINS)
allh = collections.Counter()
for r in rows:
    allh.update(r["font_hist"])
o.append("  全册字号直方图: %s" % dict(sorted(allh.items())))
lt = [(r["n"], r["n_font_lt14"], r["font_min"]) for r in rows if r["n_font_lt14"]]
o.append("  含 <14pt 文本的页数 = %d" % len(lt))
for n, c, mn in lt:
    r = rows[n - 1]
    o.append("  p%-3d 最小=%-5s 小于14pt的文本%d处" % (n, mn, c))

o.append("")
o.append("=== 3. 文本溢出 / 紧余量 ===")
o.append("  溢出元素总数 = %d（分布页：%s）" % (
    sum(r["n_overflow"] for r in rows), [r["n"] for r in rows if r["n_overflow"]]))
o.append("  横向余量<3pt 的文本（重排风险）总数 = %d（页：%s）" % (
    sum(r["n_tight_w"] for r in rows), [r["n"] for r in rows if r["n_tight_w"]]))

o.append("")
o.append("=== 4. 对比度（H3）===")
o.append("  未达 WCAG AA 的文本元素总数 = %d（分布页：%s）" % (
    sum(r["n_contrast_fail"] for r in rows), [r["n"] for r in rows if r["n_contrast_fail"]]))
o.append("  对比度 <7:1（投影从严线未达）合计 = %d" % sum(r["contrast_lt7"] for r in rows))
for r in rows:
    if r["contrast_fail"]:
        o.append("  p%-3d 最低=%.2f  %s" % (
            r["n"], r["contrast_min"],
            "; ".join("%s(%s,%spt,%s) %.2f<%.1f" % (d["id"], d["fg"], d["fs"], d["bold"], d["ratio"], d["need"])
                      for d in r["contrast_fail"][:8])))

o.append("")
o.append("=== 5. 出界 ===")
o.append("  超页面边界元素 = %d（页：%s）" % (
    sum(r["n_oob_page"] for r in rows), [r["n"] for r in rows if r["n_oob_page"]]))
o.append("  超 safeArea 元素 = %d（页：%s）" % (
    sum(r["n_oob_safe"] for r in rows), [r["n"] for r in rows if r["n_oob_safe"]]))
for r in rows[:3] if False else []:
    pass

o.append("")
o.append("=== 6. 内容底部 / 页型 ===")
o.append("  逐页内容底部 y: " + " ".join("%.0f" % r["bottom_used"] for r in rows))
o.append("  背景为 image 的页: %s" % [r["n"] for r in rows if r["bg"] == "image"])
o.append("  预期重叠声明数: " + " ".join("%d" % r["expectedOverlaps"] for r in rows))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_accept.txt", "w", encoding="utf-8").write(txt)
print(txt[:6000])
