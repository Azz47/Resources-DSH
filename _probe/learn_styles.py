# -*- coding: utf-8 -*-
"""解剖 27 个样式模板：每页形状数、字号集合、显式色板、版式签名。"""
import glob
import io
import os
import re
import sys
import zipfile
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STYLES = r"C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles"
OUT = r"D:\Resources\DSH\_specs\_learn_styles.md"

rows = []
for path in sorted(glob.glob(os.path.join(STYLES, "*", "*.pptx"))):
    fam = os.path.basename(os.path.dirname(path))
    name = os.path.basename(path)
    z = zipfile.ZipFile(path)
    slides = sorted(n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
    per_slide = []
    colors = Counter()
    sizes = Counter()
    fonts = Counter()
    texts = []
    for s in slides:
        xml = z.read(s).decode("utf-8", "ignore")
        per_slide.append((len(re.findall(r"<p:sp>", xml)), len(re.findall(r"<p:pic>", xml))))
        colors.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml))
        sizes.update(re.findall(r'sz="(\d{3,4})"', xml))
        fonts.update(re.findall(r'typeface="([^"+]{2,30})"', xml))
        texts.extend(re.findall(r"<a:t>([^<]{1,60})</a:t>", xml))
    # 主题色（部分模板走主题）
    themes = [n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml$", n)]
    theme_colors = Counter()
    if themes:
        tx = z.read(sorted(themes)[0]).decode("utf-8", "ignore")
        theme_colors.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', tx))
    top_colors = [c for c, _ in colors.most_common(6)]
    rows.append({
        "fam": fam,
        "name": name.replace(".pptx", ""),
        "slides": len(slides),
        "shapes": sum(a for a, _ in per_slide),
        "pics": sum(b for _, b in per_slide),
        "colors": top_colors,
        "theme": [c for c, _ in theme_colors.most_common(5)],
        "sizes": sorted({round(int(v) / 100, 1) for v in sizes if v.isdigit()}),
        "fonts": [f for f, _ in fonts.most_common(3)],
        "texts": texts[:6],
    })

lines = ["# 27 个样式模板 · 版式解剖（脚本生成）", "",
         "| 家族 | 样式 | 页 | 形状/页 | 图 | 显式主色（Top6） | 字号集合(pt) | 字体 |",
         "|---|---|---|---|---|---|---|---|"]
for r in rows:
    per = round(r["shapes"] / max(r["slides"], 1), 1)
    lines.append("| {fam} | {name} | {slides} | {per} | {pics} | {colors} | {sizes} | {fonts} |".format(
        fam=r["fam"], name=r["name"], slides=r["slides"], per=per, pics=r["pics"],
        colors="/".join("#" + c for c in r["colors"]),
        sizes=", ".join(str(x) for x in r["sizes"]),
        fonts="/".join(f for f in r["fonts"] if not f.startswith("+"))))

lines += ["", "## 每套的首页文案（判断叙事骨架）", ""]
for r in rows:
    lines.append(f"- **{r['fam']}/{r['name']}**：" + " ｜ ".join(r["texts"][:5]))

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("written:", OUT, os.path.getsize(OUT))
print("slides per style:", sorted({r["slides"] for r in rows}))
