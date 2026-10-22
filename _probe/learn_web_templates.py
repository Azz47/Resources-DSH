# -*- coding: utf-8 -*-
"""解剖网络高收藏样本（GitHub stars）与本地下载的 pptx。"""
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

ROOTS = [r"D:\Resources\DSH\corpus\_web"]
OUT = r"D:\Resources\DSH\_specs\_learn_web.md"

rows = []
for root in ROOTS:
    for path in sorted(glob.glob(os.path.join(root, "**", "*.pptx"), recursive=True)):
        name = os.path.relpath(path, root)
        try:
            z = zipfile.ZipFile(path)
            bad = z.testzip()
            slides = sorted(n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
            media = [n for n in z.namelist() if n.startswith("ppt/media/")]
            sizes, colors, fonts = Counter(), Counter(), Counter()
            shapes, pics, texts = 0, 0, []
            trans = Counter()
            layouts = set()
            for s in slides:
                xml = z.read(s).decode("utf-8", "ignore")
                shapes += len(re.findall(r"<p:sp>", xml))
                pics += len(re.findall(r"<p:pic>", xml))
                sizes.update(re.findall(r'sz="(\d{3,4})"', xml))
                colors.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml))
                fonts.update(re.findall(r'typeface="([^"+]{2,30})"', xml))
                texts.extend(re.findall(r"<a:t>([^<]{1,40})</a:t>", xml))
                for m in re.finditer(r'<p:transition[^>]*(?:/>|>(.*?)</p:transition>)', xml, re.S):
                    body = m.group(1) or ""
                    kind = "fade"
                    for cand in ("morph", "push", "wipe", "dissolve", "zoom", "uncover", "cover", "split"):
                        if f"<p:{cand}" in body:
                            kind = cand
                            break
                    trans[kind] += 1
                for m in re.finditer(r'<p:sldLayoutId[^>]*r:id="[^"]*"', xml):
                    layouts.add(m.group(0))
            rows.append({
                "name": name, "slides": len(slides), "media": len(media),
                "shapes": shapes, "pics": pics, "bad": bad,
                "colors": [c for c, _ in colors.most_common(8)],
                "sizes": sorted({round(int(v) / 100, 1) for v in sizes if v.isdigit()}),
                "fonts": [f for f, _ in fonts.most_common(4)],
                "trans": dict(trans), "texts": texts[:12],
            })
        except Exception as exc:
            rows.append({"name": name, "err": str(exc)[:100]})

lines = ["# 网络高收藏样本解剖（脚本生成）", ""]
for r in rows:
    if "err" in r:
        lines.append(f"## {r['name']}\n\n- 读取失败：{r['err']}\n")
        continue
    lines.append(f"## {r['name']}")
    lines.append(f"- 页数 {r['slides']}，媒体 {r['media']}，形状合计 {r['shapes']}（{r['shapes']/max(r['slides'],1):.1f}/页），"
                 f"图片元素 {r['pics']}，zip 坏块 {r['bad']}")
    lines.append(f"- 字号集合：{', '.join(str(x) for x in r['sizes'])}")
    lines.append(f"- 字体 Top4：{r['fonts']}")
    lines.append(f"- 显式色 Top8：{'/'.join('#'+c for c in r['colors'])}")
    lines.append(f"- 转场：{r['trans'] or '无'}")
    lines.append(f"- 文案样本：{' ｜ '.join(t for t in r['texts'][:10] if t.strip())}")
    lines.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("written:", OUT, os.path.getsize(OUT), "| decks:", len(rows))
