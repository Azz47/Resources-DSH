# -*- coding: utf-8 -*-
"""课件页面语料分析器 —— 把拼接预览图切成单页，逐页提取可量化的设计特征，
再跨语料汇总成「课件设计规范」的实证依据。

用法:
    python corpus_analyze.py <corpus-dir> [--out <out-dir>]

产出:
    <out>/slides/*.png        切出的单页（供人眼复核与拼图）
    <out>/pages.jsonl         逐页特征
    <out>/summary.json        汇总统计
"""
import argparse
import json
import math
import os
import statistics
from collections import Counter

from PIL import Image, ImageFilter, ImageStat

TILE_W = 750  # 预览图统一宽度


def split_tall(path, out_dir, tag):
    """把 750xN 的纵向拼接图按 16:9 切成单页。返回切出的路径列表。"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    th = round(w * 9 / 16)
    n = max(1, round(h / th))
    out = []
    for i in range(n):
        top = i * th
        if top + th > h + 2:
            break
        tile = im.crop((0, top, w, min(h, top + th)))
        p = os.path.join(out_dir, f"{tag}_p{i + 1:02d}.png")
        tile.save(p)
        out.append(p)
    return out


def colorfulness(im):
    """Hasler-Süsstrunk 色彩丰富度，衡量配图/配色强度。"""
    import numpy as np
    a = np.asarray(im.resize((160, 90)), dtype=float)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    rg = R - G
    yb = 0.5 * (R + G) - B
    return float(np.sqrt(rg.std() ** 2 + yb.std() ** 2)
                 + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))


def band_profile(im, bands=10):
    """把页面按横向 10 条带，算每条带的内容占比（非背景像素）。"""
    g = im.convert("L")
    w, h = g.size
    bg = Counter(g.getdata()).most_common(1)[0][0]
    prof = []
    px = g.load()
    for k in range(bands):
        y0, y1 = int(h * k / bands), int(h * (k + 1) / bands)
        tot = hit = 0
        for y in range(y0, y1, 3):
            for x in range(0, w, 3):
                tot += 1
                if abs(px[x, y] - bg) > 28:
                    hit += 1
        prof.append(round(hit / max(1, tot), 3))
    return prof, bg


def analyze_page(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    gray = im.convert("L")
    st = ImageStat.Stat(gray)
    mean = st.mean[0]
    std = st.stddev[0]
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0]
    prof, bg = band_profile(im)
    # 主色：量化到 4 位/通道
    small = im.resize((80, 45))
    q = small.quantize(colors=8, method=Image.MEDIANCUT).convert("RGB")
    pal = Counter(q.getdata()).most_common(6)
    total = sum(c for _, c in pal) or 1
    return {
        "file": os.path.basename(path),
        "w": w, "h": h,
        "mean_lum": round(mean, 1),
        "contrast": round(std, 1),
        "edge_density": round(edge_mean, 2),
        "colorfulness": round(colorfulness(im), 1),
        "bg_lum": bg,
        "light_bg": bg > 127,
        "coverage": round(sum(prof) / len(prof), 3),
        "bands": prof,
        "palette": [{"rgb": "#%02x%02x%02x" % rgb, "pct": round(c / total, 3)} for rgb, c in pal],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(a.corpus, "_analysis")
    slides_dir = os.path.join(out, "slides")
    os.makedirs(slides_dir, exist_ok=True)

    # 兼容两种命名：带扩展名，以及早先版本被洗掉点号留下的 _jpg 结尾
    imgs = sorted(f for f in os.listdir(a.corpus)
                  if f.lower().endswith((".jpg", "_jpg", ".jpeg", ".png")))
    # 只要"整册拼接图"（命名里的 _2_）——它包含多页
    tall = [f for f in imgs if "_2_" in f]
    print(f"corpus images: {len(imgs)}, stitched previews: {len(tall)}")

    rows = []
    for f in tall:
        tag = os.path.splitext(f)[0][:40]
        for p in split_tall(os.path.join(a.corpus, f), slides_dir, tag):
            try:
                rows.append(analyze_page(p))
            except Exception as e:
                print("  page fail", p, repr(e)[:80])

    with open(os.path.join(out, "pages.jsonl"), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    if not rows:
        print("no pages"); return
    pal_all = Counter()
    for r in rows:
        for p in r["palette"][:3]:
            pal_all[p["rgb"]] += p["pct"]
    summary = {
        "pages": len(rows),
        "courseware": len(tall),
        "median_coverage": round(statistics.median(r["coverage"] for r in rows), 3),
        "median_contrast": round(statistics.median(r["contrast"] for r in rows), 1),
        "median_edge_density": round(statistics.median(r["edge_density"] for r in rows), 2),
        "median_colorfulness": round(statistics.median(r["colorfulness"] for r in rows), 1),
        "light_bg_ratio": round(sum(1 for r in rows if r["light_bg"]) / len(rows), 3),
        "top_colors": [{"rgb": k, "weight": round(v, 2)} for k, v in pal_all.most_common(12)],
        "band_profile_mean": [round(sum(r["bands"][i] for r in rows) / len(rows), 3) for i in range(10)],
        "coverage_hist": {
            "稀疏<0.10": sum(1 for r in rows if r["coverage"] < 0.10),
            "适中0.10-0.25": sum(1 for r in rows if 0.10 <= r["coverage"] < 0.25),
            "密集0.25-0.45": sum(1 for r in rows if 0.25 <= r["coverage"] < 0.45),
            "极密>=0.45": sum(1 for r in rows if r["coverage"] >= 0.45),
        },
        "colorfulness_hist": {
            "素<25": sum(1 for r in rows if r["colorfulness"] < 25),
            "中25-45": sum(1 for r in rows if 25 <= r["colorfulness"] < 45),
            "艳>=45": sum(1 for r in rows if r["colorfulness"] >= 45),
        },
    }
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2)[:2000])
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
