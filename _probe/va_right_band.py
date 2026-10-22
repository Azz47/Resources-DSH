# -*- coding: utf-8 -*-
"""右侧净空带（640-960pt）像素级实测 + 逐页体质（留白率/内容量/色数）
标定：960x540 pt ↔ 1920x1080 px（shots 若为其它尺寸按比例换算）"""
import json, io, os, collections, math
from PIL import Image

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
SH = os.path.join(D, "preview", "shots")
W, H = 960.0, 540.0
CLEAR = 640.0

lay = json.loads(io.open(os.path.join(D, "preview", "layout.json"), "rb").read().decode("gbk", "replace"))
cards = {}
for i in range(1, 47):
    fn = os.path.join(SH, "%02d.png" % i)
    cards[i] = Image.open(fn).convert("RGB")
print("shot size sample:", cards[1].size, " expected ratio", cards[1].size[0] / cards[1].size[1])

def rect(n, x0, y0, x1, y1):
    im = cards[n]
    sx = im.size[0] / W
    sy = im.size[1] / H
    return (int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy))

def stats(n, x0, y0, x1, y1, step=2):
    """返回 众数色/亮度均值/标准差/暗像素占比/色数/边缘(局部方差)强度"""
    im = cards[n]
    bx = rect(n, x0, y0, x1, y1)
    px = []
    for y in range(bx[1], bx[3], step):
        for x in range(bx[0], bx[2], step):
            px.append(im.getpixel((x, y)))
    if not px:
        return None
    def lum(c):
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    L = [lum(c) for c in px]
    mean = sum(L) / len(L)
    var = sum((v - mean) ** 2 for v in L) / len(L)
    cnt = collections.Counter((c[0] // 12 * 12, c[1] // 12 * 12, c[2] // 12 * 12) for c in px)
    top, topn = cnt.most_common(1)[0]
    dark = sum(1 for v in L if v < 110) / len(L)
    return {
        "mean": round(mean, 1), "sd": round(math.sqrt(var), 1),
        "dom": "#%02X%02X%02X" % top, "dom_share": round(topn / len(px), 3),
        "dark_pct": round(dark * 100, 1), "colors": len(cnt), "n": len(px),
    }

rows = []
for n in range(1, 47):
    full = stats(n, 0, 0, W, H, 4)
    right = stats(n, CLEAR, 0, W, H, 2)
    left = stats(n, 0, 0, CLEAR, H, 2)
    rows.append({"n": n, "right": right, "left": left, "full": full})

# 全页留白率：以 left+right 众数色为"底"，统计"非底色像素"占比（内容覆盖率近似）
def coverage(n):
    im = cards[n]
    sx = im.size[0] / W
    step = 3
    px = [im.getpixel((x, y)) for y in range(0, im.size[1], step)
          for x in range(0, im.size[0], step)]
    cnt = collections.Counter((c[0] // 12 * 12, c[1] // 12 * 12, c[2] // 12 * 12) for c in px)
    # 取出现最多的前 2 色当"底"
    base = set(c for c, _ in cnt.most_common(2))
    ink = sum(v for c, v in cnt.items() if c not in base)
    return round(ink / len(px), 3), len(cnt)

cov = {n: coverage(n) for n in range(1, 47)}

o = []
o.append("=== 右侧净空带 640-960pt 像素实测（46 页）===")
o.append("页  mean   sd   dom色     dom占比 暗像素%  色数")
for r in rows:
    g = r["right"]
    o.append("p%-3d %-6s %-5s %-8s %-7s %-8s %s" % (
        r["n"], g["mean"], g["sd"], g["dom"], g["dom_share"], g["dark_pct"], g["colors"]))

o.append("")
o.append("=== 右侧带一致性（H6 融合相关性）===")
doms = collections.Counter(r["right"]["dom"] for r in rows)
o.append("  右侧带众数色分布: %s" % doms.most_common())
sds = [r["right"]["sd"] for r in rows]
o.append("  右侧带亮度标准差 range = %.1f ~ %.1f, 均值 %.1f" % (min(sds), max(sds), sum(sds) / len(sds)))
o.append("  右侧带 vs 左侧带 众数色相同页数 = %d/46" % sum(1 for r in rows if r["right"]["dom"] == r["left"]["dom"]))
o.append("  右侧带色数 range = %d ~ %d" % (min(r["right"]["colors"] for r in rows), max(r["right"]["colors"] for r in rows)))

o.append("")
o.append("=== 全页内容覆盖率（非底色像素占比，粗筛）===")
o.append("  逐页: " + " ".join("%.2f" % cov[n][0] for n in range(1, 47)))
o.append("  全册均值 = %.3f  中位 = %.3f" % (
    sum(cov[n][0] for n in range(1, 47)) / 46, sorted(cov[n][0] for n in range(1, 47))[23]))
o.append("  最低 8 页: %s" % sorted([(round(cov[n][0], 3), n, cov[n][1]) for n in range(1, 47)])[:8])
o.append("  最高 8 页: %s" % sorted([(round(cov[n][0], 3), n, cov[n][1]) for n in range(1, 47)], reverse=True)[:8])
o.append("  全页色数(12级量化) 逐页: " + " ".join("%d" % cov[n][1] for n in range(1, 47)))

txt = "\n".join(o)
io.open(r"D:\Resources\DSH\_probe\va_right_band.txt", "w", encoding="utf-8").write(txt)
json.dump({"band": rows, "cov": {str(k): v for k, v in cov.items()}},
          io.open(r"D:\Resources\DSH\_probe\va_right_band.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(txt)
