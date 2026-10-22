# -*- coding: utf-8 -*-
"""PPT 库全量学习：语料指标聚合 + 27 个样式模板解剖。

python learn_ppt_library.py  ->  写 _specs/_learn_dump.md（UTF-8）
数据源：
  - D:\\Resources\\DSH\\corpus\\corpus.jsonl（23 条本机模板/成品指标）
  - D:\\Resources\\DSH\\corpus\\contest.jsonl（62 条参赛/优质课样本指标）
  - C:\\Users\\Administrator\\.dsh\\skills\\morph-ppt\\reference\\styles\\**\\*.pptx（27 个样式模板）
"""
import glob
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CORPUS = r"D:\Resources\DSH\corpus"
STYLES = r"C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles"
OUT = r"D:\Resources\DSH\_specs\_learn_dump.md"

NS_P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def load_jsonl(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def agg_corpus(rows, title, out):
    out.append(f"\n## {title}（{len(rows)} 条）\n")
    if not rows:
        return
    pages = [r.get("slides") or 0 for r in rows]
    pages_nz = [p for p in pages if p]
    out.append(f"- 有页数的样本：{len(pages_nz)}；页数中位 **{sorted(pages_nz)[len(pages_nz)//2] if pages_nz else 0}**，"
               f"范围 {min(pages_nz) if pages_nz else 0}–{max(pages_nz) if pages_nz else 0}")
    subj = Counter()
    for r in rows:
        s = r.get("subject") or r.get("学科") or "未标"
        subj[s] += 1
    out.append(f"- 学科分布：{dict(subj.most_common(8))}")
    fs = Counter()
    for r in rows:
        for k, v in (r.get("font_sizes") or {}).items():
            fs[k] += v if isinstance(v, int) else 1
    top_fs = sorted(fs.items(), key=lambda kv: -kv[1])[:10]
    out.append(f"- 字号频次 Top10（pt:次数）：{top_fs}")
    fonts = Counter()
    for r in rows:
        for k, v in (r.get("fonts") or {}).items():
            fonts[k] += v if isinstance(v, int) else 1
    out.append(f"- 字体频次 Top8：{fonts.most_common(8)}")
    colors = Counter()
    for r in rows:
        for k, v in (r.get("colors") or {}).items():
            colors[k] += v if isinstance(v, int) else 1
    out.append(f"- 颜色频次 Top10：{colors.most_common(10)}")
    ratios = [r.get("image_ratio") for r in rows if isinstance(r.get("image_ratio"), (int, float))]
    if ratios:
        ratios_sorted = sorted(ratios)
        out.append(f"- 图片页占比：中位 **{ratios_sorted[len(ratios_sorted)//2]:.2f}**，均值 {sum(ratios)/len(ratios):.2f}，"
                   f"范围 {min(ratios):.2f}–{max(ratios):.2f}")
    chars = [r.get("avg_chars_per_slide") for r in rows if isinstance(r.get("avg_chars_per_slide"), (int, float)) and r.get("avg_chars_per_slide")]
    if chars:
        out.append(f"- 每页字数：中位 {sorted(chars)[len(chars)//2]:.0f}，均值 {sum(chars)/len(chars):.0f}")
    blocks = [r.get("avg_blocks_per_slide") for r in rows if isinstance(r.get("avg_blocks_per_slide"), (int, float)) and r.get("avg_blocks_per_slide")]
    if blocks:
        out.append(f"- 每页块数：中位 {sorted(blocks)[len(blocks)//2]:.1f}")
    out.append(f"- 表格合计 {sum(r.get('tables_total') or 0 for r in rows)} 个；图表合计 {sum(r.get('charts_total') or 0 for r in rows)} 个")


def theme_of(path):
    """返回 (dk1, lt1, accent1..6, majorFont, minorFont)。"""
    with zipfile.ZipFile(path) as z:
        themes = [n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml$", n)]
        if not themes:
            return None
        xml = z.read(sorted(themes)[0]).decode("utf-8", "ignore")
    res = {}
    for key in ["dk1", "lt1", "dk2", "lt2"] + [f"accent{i}" for i in range(1, 7)]:
        m = re.search(r"<a:%s>.*?val=\"([0-9A-Fa-f]{6})\"" % key, xml, re.S)
        if not m:
            m = re.search(r"<a:%s[^>]*>.*?<a:srgbClr val=\"([0-9A-Fa-f]{6})\"" % key, xml, re.S)
        res[key] = ("#" + m.group(1).upper()) if m else None
    for key, tag in (("major", "majorFont"), ("minor", "minorFont")):
        m = re.search(r"<a:%s>.*?<a:latin typeface=\"([^\"]*)\"" % tag, xml, re.S)
        e = re.search(r"<a:%s>.*?<a:ea typeface=\"([^\"]*)\"" % tag, xml, re.S)
        res[key] = (m.group(1) if m else "") + (" / " + e.group(1) if e and e.group(1) else "")
    return res


def deck_of(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        slides = sorted(n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n))
        media = [n for n in names if n.startswith("ppt/media/")]
        trans = Counter()
        for s in slides:
            xml = z.read(s).decode("utf-8", "ignore")
            for m in re.finditer(r"<p:transition([^>]*)>(.*?)</p:transition>|<p:transition([^>]*)/>", xml, re.S):
                attrs = (m.group(1) or m.group(3) or "")
                body = m.group(2) or ""
                kind = "fade"
                for cand in ("morph", "push", "wipe", "dissolve", "zoom", "uncover", "cover", "split"):
                    if (f'<p:{cand}' in body) or (f'p14:{cand}' in body):
                        kind = cand
                        break
                spd = re.search(r'spd="(\w+)"', attrs)
                adv = re.search(r'advTm="(\d+)"', attrs)
                trans[(kind, spd.group(1) if spd else "-", "auto" if adv else "click")] += 1
    return {"slides": len(slides), "media": len(media), "trans": trans}


def style_family(name):
    m = re.match(r"(dark|light|bw|vivid|warm|mixed)--(.+)", os.path.basename(os.path.dirname(name)))
    return (m.group(1), m.group(2)) if m else ("?", os.path.basename(os.path.dirname(name)))


def main():
    out = ["# PPT 库学习 · 原始指标（脚本生成，勿手改）",
           f"\n生成时间：{__import__('datetime').datetime.now():%Y-%m-%d %H:%M}；脚本：`_probe/learn_ppt_library.py`"]
    c1 = load_jsonl(os.path.join(CORPUS, "corpus.jsonl"))
    c2 = load_jsonl(os.path.join(CORPUS, "contest.jsonl"))
    agg_corpus(c1, "corpus.jsonl（本机模板/成品）", out)
    agg_corpus(c2, "contest.jsonl（参赛/优质课样本）", out)

    out.append("\n## 27 个样式模板（morph-ppt/reference/styles）\n")
    out.append("| 家族 | 样式 | 页数 | 媒体 | 主题主色（accent1/2/3） | 主题字体（latin/ea） | 转场 |")
    out.append("|---|---|---|---|---|---|---|")
    fam_count = Counter()
    trans_all = Counter()
    for p in sorted(glob.glob(os.path.join(STYLES, "*", "*.pptx"))):
        fam, style = style_family(p)
        fam_count[fam] += 1
        try:
            th = theme_of(p) or {}
            dk = deck_of(p)
        except Exception as exc:  # 损坏文件不阻塞整体
            out.append(f"| {fam} | {style} | err | | | {exc} |")
            continue
        acc = "/".join(x for x in [th.get("accent1"), th.get("accent2"), th.get("accent3")] if x)
        tt = trans = ", ".join(f"{k[0]}×{v}" for k, v in dk["trans"].most_common(3)) or "无"
        for k, v in dk["trans"].items():
            trans_all[k[0]] += v
        out.append(f"| {fam} | {style} | {dk['slides']} | {dk['media']} | {acc} | {th.get('major','')} | {tt} |")
    out.append(f"\n- 家族计数：{dict(fam_count)}")
    out.append(f"- 转场类型合计：{dict(trans_all)}")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("written:", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
