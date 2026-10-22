# -*- coding: utf-8 -*-
"""语料库全量统计：560 份课件的页数分布 + 1,100+ 张预览图的视觉指纹。

输出 _specs/_learn_corpus.md（UTF-8）
"""
import glob
import io
import json
import os
import sys
from collections import Counter, defaultdict

from PIL import Image, ImageFilter, ImageStat

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"D:\Resources\DSH\corpus"
OUT = r"D:\Resources\DSH\_specs\_learn_corpus.md"


def quant_color(px, step=16):
    return tuple((v // step) * step for v in px[:3])


def look(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    small = im.resize((160, int(160 * h / max(w, 1)) or 1))
    gray = small.convert("L")
    st = ImageStat.Stat(gray)
    mean = st.mean[0]
    edges = small.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    px = small.load()
    W, H = small.size
    dark = light = 0
    colors = Counter()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            p = px[x, y]
            lum = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
            if lum < 64:
                dark += 1
            elif lum > 235:
                light += 1
            colors[quant_color(p)] += 1
    total = max(1, (W // 2) * (H // 2))
    top = ["#%02X%02X%02X" % c for c, _ in colors.most_common(4)]
    # 色彩丰富度：主色占比越低越花
    greedy = colors.most_common(1)[0][1] / total
    return {
        "w": w, "h": h, "aspect": round(w / max(h, 1), 3),
        "mean_lum": round(mean, 1), "edge": round(edge_mean, 1),
        "dark": round(dark / total, 3), "light": round(light / total, 3),
        "colors": top, "dominant": round(greedy, 3),
    }


def main():
    rows = []
    for d in ("1ppt", "1ppt2"):
        idx = os.path.join(ROOT, d, "index.jsonl")
        if not os.path.exists(idx):
            continue
        for line in io.open(idx, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    seen = set()
    decks = []
    for r in rows:
        key = r.get("url") or r.get("title")
        if key in seen:
            continue
        seen.add(key)
        decks.append(r)

    out = ["# 语料库全量统计（脚本生成）", "", f"- 去重后课件：**{len(decks)} 份**"]
    pages = []
    by_cat = defaultdict(list)
    for r in decks:
        try:
            p = int(r.get("pages") or 0)
        except (TypeError, ValueError):
            p = 0
        if p:
            pages.append(p)
            by_cat[r.get("cat") or "未标"].append(p)
    pages.sort()
    if pages:
        n = len(pages)
        q = lambda f: pages[min(n - 1, int(f * (n - 1)))]
        out += [
            f"- 有页数记录：{n} 份，总页数 **{sum(pages)}**",
            f"- 页数：中位 **{q(0.5)}**，P25 {q(0.25)}，P75 {q(0.75)}，P90 {q(0.9)}，最短 {pages[0]}，最长 {pages[-1]}",
            f"- 分布：1–9 页 {sum(1 for p in pages if p < 10)} 份；10–19 页 {sum(1 for p in pages if 10 <= p < 20)} 份；"
            f"20–34 页 {sum(1 for p in pages if 20 <= p < 35)} 份；35–50 页 {sum(1 for p in pages if 35 <= p <= 50)} 份；"
            f"50 页以上 {sum(1 for p in pages if p > 50)} 份",
        ]
    out += ["", "## 分学科页数与体量", "", "| 学科 | 份数 | 页数中位 | 页数范围 |", "|---|---|---|---|"]
    for cat, ps in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        ps = sorted(ps)
        out.append(f"| {cat} | {len(ps)} | {ps[len(ps)//2]} | {ps[0]}–{ps[-1]} |")

    # 预览图指纹
    imgs = sorted(glob.glob(os.path.join(ROOT, "1ppt", "images", "*")) +
                  glob.glob(os.path.join(ROOT, "1ppt2", "images", "*")))
    looks = []
    for p in imgs:
        try:
            looks.append(look(p))
        except Exception:
            continue
    if looks:
        def med(key):
            vals = sorted(x[key] for x in looks)
            return vals[len(vals) // 2]
        out += ["", "## 预览图视觉指纹", "",
                f"- 样本：**{len(looks)} 张**（每份课件最多 2 张预览页）",
                f"- 宽高比：中位 {med('aspect')}；16:9 占 {sum(1 for x in looks if 1.7 <= x['aspect'] <= 1.82) / len(looks):.0%}",
                f"- 平均亮度：中位 {med('mean_lum')}/255；深色页（<96）占 {sum(1 for x in looks if x['mean_lum'] < 96) / len(looks):.0%}，"
                f"亮色页（>200）占 {sum(1 for x in looks if x['mean_lum'] > 200) / len(looks):.0%}",
                f"- 纯黑占比中位 {med('dark'):.1%}，纯白占比中位 {med('light'):.1%}",
                f"- 边缘密度中位 {med('edge')}（越高信息越密）",
                f"- 主色占比中位 {med('dominant'):.1%}（越高越素）"]
        palette = Counter()
        for x in looks:
            palette.update(x["colors"][:2])
        out.append(f"- 出现最多的主色：{palette.most_common(12)}")
        # 亮/暗页的学科偏好
        cat_lum = defaultdict(list)
        for p, x in zip(imgs, looks):
            name = os.path.basename(p)
            cat = name.split("_")[0]
            cat_lum[cat].append(x["mean_lum"])
        out += ["", "| 学科 | 预览页平均亮度的中位 | 样本 |", "|---|---|---|"]
        for cat, vs in sorted(cat_lum.items(), key=lambda kv: -len(kv[1])):
            vs = sorted(vs)
            out.append(f"| {cat} | {vs[len(vs)//2]:.0f} | {len(vs)} |")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("written:", OUT, os.path.getsize(OUT), "bytes; decks:", len(decks), "images:", len(imgs))


if __name__ == "__main__":
    main()
