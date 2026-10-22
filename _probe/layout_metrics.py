# -*- coding: utf-8 -*-
"""版式度量 v2：覆盖率网格算留白、裁剪边距、正确识别图片/表格/图表、按文字面积定标题与正文。

输出：_specs/_layout_metrics.json、_specs/_layout_summary.md
"""
import glob
import io
import json
import os
import statistics
import sys
from collections import Counter

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

sys.stdout.reconfigure(encoding="utf-8")

EMU_CM = 360000.0
OUT_JSON = r"D:\Resources\DSH\_specs\_layout_metrics.json"
OUT_MD = r"D:\Resources\DSH\_specs\_layout_summary.md"
GX, GY = 120, 68


def kind_of(sh):
    try:
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            return "PIC"
        if sh.shape_type == MSO_SHAPE_TYPE.PLACEHOLDER:
            try:
                if sh.placeholder_format.type is not None and "PICTURE" in str(sh.placeholder_format.type):
                    return "PIC"
            except Exception:
                pass
        if getattr(sh, "has_table", False) and sh.has_table:
            return "TBL"
        if getattr(sh, "has_chart", False) and sh.has_chart:
            return "CHT"
    except Exception:
        pass
    if getattr(sh, "has_text_frame", False) and sh.has_text_frame and sh.text_frame.text.strip():
        return "TXT"
    return "SHP"


def walk(shapes, out):
    for sh in shapes:
        try:
            if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                walk(sh.shapes, out)
                continue
            if sh.left is None or sh.top is None:
                continue
            w = (sh.width or 0) / EMU_CM
            h = (sh.height or 0) / EMU_CM
            if w <= 0.05 or h <= 0.05:
                continue
            item = {
                "k": kind_of(sh),
                "x": round(sh.left / EMU_CM, 2),
                "y": round(sh.top / EMU_CM, 2),
                "w": round(w, 2),
                "h": round(h, 2),
            }
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                txt = sh.text_frame.text.strip()
                sizes = []
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.size:
                            sizes.append(round(r.font.size.pt, 1))
                item["chars"] = len(txt)
                item["sizes"] = sizes
                item["size"] = round(statistics.median(sizes), 1) if sizes else 0
                item["text"] = txt[:40]
            out.append(item)
        except Exception:
            continue


def coverage(items, W, H):
    grid = [[0] * GX for _ in range(GY)]
    for i in items:
        x0 = max(0.0, i["x"])
        y0 = max(0.0, i["y"])
        x1 = min(W, i["x"] + i["w"])
        y1 = min(H, i["y"] + i["h"])
        if x1 <= x0 or y1 <= y0:
            continue
        c0, c1 = int(x0 / W * GX), min(GX - 1, int(x1 / W * GX))
        r0, r1 = int(y0 / H * GY), min(GY - 1, int(y1 / H * GY))
        for r in range(r0, r1 + 1):
            row = grid[r]
            for c in range(c0, c1 + 1):
                row[c] = 1
    covered = sum(sum(r) for r in grid)
    return 1 - covered / (GX * GY)


def clusters(values, gap):
    if not values:
        return []
    vals = sorted(values)
    groups = [[vals[0]]]
    for v in vals[1:]:
        if v - groups[-1][-1] > gap:
            groups.append([v])
        else:
            groups[-1].append(v)
    return groups


def analyze(path):
    prs = Presentation(path)
    W = prs.slide_width / EMU_CM
    H = prs.slide_height / EMU_CM
    slides = []
    for idx, slide in enumerate(prs.slides, 1):
        items = []
        walk(slide.shapes, items)
        if not items:
            slides.append({"n": idx, "empty": True})
            continue
        # 承载信息 = 文字 / 图 / 表 / 图（排除纯装饰小色块）
        content = [i for i in items if i["k"] in ("TXT", "PIC", "TBL", "CHT")]
        xs = [min(max(i["x"], 0), W) for i in content] or [0]
        ys = [min(max(i["y"], 0), H) for i in content] or [0]
        rs = [min(max(i["x"] + i["w"], 0), W) for i in content] or [W]
        bs = [min(max(i["y"] + i["h"], 0), H) for i in content] or [H]
        cols = clusters([min(max(i["x"], 0), W) for i in content if i["w"] > 0.8], W * 0.07)
        text_items = [i for i in content if i["k"] == "TXT"]
        chars = sum(i.get("chars") or 0 for i in text_items)
        text_area = sum(i["w"] * i["h"] for i in text_items)
        pic_area = sum(i["w"] * i["h"] for i in content if i["k"] == "PIC")
        tables = sum(1 for i in content if i["k"] == "TBL")
        charts = sum(1 for i in content if i["k"] == "CHT")
        # 标题 = 面积不小于画布 1.5% 的文字块里最大字号；正文 = 字数≥8 的块的字号中位数
        title = body = None
        tbox = None
        big = [(i["w"] * i["h"], i.get("size") or 0, i) for i in text_items
               if (i.get("size") or 0) > 0 and i["w"] * i["h"] >= 0.015 * W * H]
        if big:
            _, title, tbox = max(big, key=lambda t: (t[1], t[0]))
        body_sizes = [(i.get("chars") or 0, i.get("size") or 0) for i in text_items
                      if (i.get("size") or 0) > 0 and (i.get("chars") or 0) >= 8]
        if body_sizes:
            expanded = []
            for c, s in body_sizes:
                expanded.extend([s] * max(1, min(c, 60)))
            body = statistics.median(expanded)
        ws_content = coverage(content, W, H)
        ws_all = coverage(items, W, H)
        overflow = any(i["x"] < -0.2 or i["y"] < -0.2 or i["x"] + i["w"] > W + 0.2 or i["y"] + i["h"] > H + 0.2
                       for i in items)
        slides.append({
            "n": idx,
            "els": len(items),
            "content": len(content),
            "boxes": [[i["x"], i["y"], i["w"], i["h"], i["k"], i.get("size") or 0] for i in items],
            "margins": [round(xs and min(xs) or 0, 2), round(ys and min(ys) or 0, 2),
                        round(W - (max(rs) if rs else W), 2), round(H - (max(bs) if bs else H), 2)],
            "cols": len(cols),
            "whitespace": round(ws_content, 3),
            "deco_cover": round(max(0.0, ws_all - ws_content) and (1 - ws_all) - (1 - ws_content), 3),
            "chars": chars,
            "text_area_ratio": round(min(text_area, W * H) / (W * H), 3),
            "pic_area_ratio": round(min(pic_area, W * H) / (W * H), 3),
            "has_pic": 1 if pic_area > 0 else 0,
            "tables": tables,
            "charts": charts,
            "body": body,
            "title": title,
            "ratio": round(title / body, 2) if (title and body) else None,
            "title_frac": [round(tbox["x"] / W, 3), round(tbox["y"] / H, 3),
                           round(tbox["w"] / W, 3), round(tbox["h"] / H, 3)] if tbox else None,
            "overflow": overflow,
        })
    return {"file": path, "W": round(W, 2), "H": round(H, 2), "slides": slides}


def archetype(s):
    if s.get("empty"):
        return "空页"
    if s["tables"] or s["charts"]:
        return "网格图表"
    if s["pic_area_ratio"] > 0.25:
        return "全幅/通栏图"
    if s["cols"] >= 3 and s["content"] >= 5:
        return "多栏卡片"
    if s["cols"] == 2:
        return "双栏"
    if s["chars"] < 60 and s["content"] <= 3:
        return "大标题/扉页"
    return "单栏"


def main():
    decks = []
    for pattern in (r"D:\Resources\DSH\corpus\_web\**\*.pptx",
                    r"C:\Users\Administrator\.dsh\skills\morph-ppt\reference\styles\*\*.pptx",
                    r"D:\Resources\DSH\decks\**\*.pptx"):
        decks.extend(sorted(glob.glob(pattern, recursive=True)))
    results = []
    for p in decks:
        try:
            results.append(analyze(p))
        except Exception as exc:
            print("SKIP", os.path.basename(p), exc)
    io.open(OUT_JSON, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False))
    print("decks:", len(results), "->", OUT_JSON)

    lines = ["# 版式度量汇总（脚本生成）", "",
             "留白 = 内容元素（文字/图/表）未覆盖的画布比例；文字区/图区 = 占画布面积比中位数。",
             "",
             "| 样本 | 页 | 画布 cm | 左 | 上 | 右 | 下 | 栏数众数 | 留白 | 文字区 | 图解 | 图区均值 | 标题/正文 | 溢出页 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    all_arch = Counter()
    buckets = {}
    for r in results:
        ss = [s for s in r["slides"] if not s.get("empty")]
        if not ss:
            continue
        med = lambda k: round(statistics.median([s[k] for s in ss]), 2)
        for s in ss:
            buckets.setdefault(archetype(s), []).append(s)
            all_arch[archetype(s)] += 1
        name = os.path.basename(os.path.dirname(r["file"])) + "/" + os.path.basename(r["file"])
        ratios = [s["ratio"] for s in ss if s.get("ratio")]
        lines.append("| {name} | {n} | {w}×{h} | {l} | {t} | {rr} | {b} | {cols} | {ws} | {tr} | {pic} | {pr} | {ratio} | {of} |".format(
            name=name[:42], n=len(ss), w=r["W"], h=r["H"],
            l=round(statistics.median([s["margins"][0] for s in ss]), 2),
            t=round(statistics.median([s["margins"][1] for s in ss]), 2),
            rr=round(statistics.median([s["margins"][2] for s in ss]), 2),
            b=round(statistics.median([s["margins"][3] for s in ss]), 2),
            cols=Counter(s["cols"] for s in ss).most_common(1)[0][0],
            ws=med("whitespace"), tr=med("text_area_ratio"),
            pic=round(sum(s["has_pic"] for s in ss) / len(ss), 2),
            pr=round(statistics.mean([s["pic_area_ratio"] for s in ss]), 2),
            ratio=round(statistics.median(ratios), 2) if ratios else "-",
            of=sum(1 for s in ss if s["overflow"]),
        ))
    lines += ["", "## 版式原型 · 几何中位", "",
              "| 原型 | 页数 | 左边距 | 上边距 | 右边距 | 下边距 | 标题x% | 标题y% | 栏数 | 留白 | 文字区 | 图区 | 字数 | 元素 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arch, ss in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        m = lambda k: round(statistics.median([s[k] for s in ss]), 2)
        lines.append("| {a} | {n} | {l} | {t} | {r} | {b} | {ty} | {tz} | {c} | {w} | {tx} | {p} | {ch} | {e} |".format(
            a=arch, n=len(ss),
            l=m("margins") if False else round(statistics.median([s["margins"][0] for s in ss]), 2),
            t=round(statistics.median([s["margins"][1] for s in ss]), 2),
            r=round(statistics.median([s["margins"][2] for s in ss]), 2),
            b=round(statistics.median([s["margins"][3] for s in ss]), 2),
            ty=round(statistics.median([s["title_frac"][0] for s in ss if s.get("title_frac")]), 3),
            tz=round(statistics.median([s["title_frac"][1] for s in ss if s.get("title_frac")]), 3),
            c=round(statistics.median([s["cols"] for s in ss]), 1),
            w=m("whitespace"), tx=m("text_area_ratio"),
            p=round(statistics.mean([s["pic_area_ratio"] for s in ss]), 2),
            ch=round(statistics.median([s["chars"] for s in ss])),
            e=round(statistics.median([s["els"] for s in ss]), 1),
        ))
    lines += ["", "## 版式原型分布（全部页）", "", str(dict(all_arch.most_common()))]
    io.open(OUT_MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("summary:", os.path.getsize(OUT_MD), "bytes")


if __name__ == "__main__":
    main()
