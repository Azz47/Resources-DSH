#!/usr/bin/env python3
"""deck2motion — 把 Office/文本资料一键转成可播放的动效演示（单文件 HTML）。

用法:
    python deck2motion.py <input.pptx|.md|.txt> <out_dir> [--title "总标题"] [--theme dark-tech]

做法:
    1) .pptx 用 python-pptx 抽每页标题/正文/备注/图片 → outline.json
    2) .md/.txt 按 `#` 标题或空行分页 → outline.json
    3) 生成 index.html：16:9 固定舞台、翻页后元素依次缓入、键盘/滚轮/点击翻页、进度条、页码

这一步只做「确定性搬运 + 动效骨架」，视觉精修交给 ppt-animation / frontend-slides 技能。
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import sys

THEMES = {
    "dark-tech": {"bg": "#0B1020", "fg": "#E8ECF8", "muted": "#9AA6C4", "a1": "#5B8CFF", "a2": "#B06BFF", "ink": "#121A33"},
    "warm-paper": {"bg": "#F4EEE2", "fg": "#2A2318", "muted": "#6B5F4B", "a1": "#B4622D", "a2": "#7A6A3F", "ink": "#E7DCC8"},
    "clean-white": {"bg": "#FFFFFF", "fg": "#111827", "muted": "#6B7280", "a1": "#2563EB", "a2": "#DB2777", "ink": "#F3F4F6"},
}


def from_pptx(path: str, out_dir: str) -> list[dict]:
    from pptx import Presentation  # 延迟导入，md 路径不需要

    prs = Presentation(path)
    assets = os.path.join(out_dir, "assets")
    os.makedirs(assets, exist_ok=True)
    slides: list[dict] = []
    for idx, slide in enumerate(prs.slides):
        item = {"number": idx + 1, "title": "", "bullets": [], "notes": "", "images": []}
        title_shape = slide.shapes.title
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = "\n".join(p.text for p in shape.text_frame.paragraphs).strip()
                if not text:
                    continue
                if title_shape is not None and shape.shape_id == title_shape.shape_id:
                    item["title"] = text.splitlines()[0]
                else:
                    item["bullets"].extend([ln.strip() for ln in text.splitlines() if ln.strip()])
            if shape.shape_type == 13:  # PICTURE
                img = shape.image
                name = f"slide{idx + 1}_{len(item['images']) + 1}.{img.ext}"
                with open(os.path.join(assets, name), "wb") as fh:
                    fh.write(img.blob)
                item["images"].append(f"assets/{name}")
        if slide.has_notes_slide:
            item["notes"] = (slide.notes_slide.notes_text_frame.text or "").strip()
        if not item["title"]:
            item["title"] = f"第 {idx + 1} 页"
        slides.append(item)
    return slides


def from_text(path: str) -> list[dict]:
    raw = io.open(path, encoding="utf-8").read()
    blocks: list[tuple[str, list[str]]] = []
    cur_title, cur_body = "", []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            if cur_title or cur_body:
                blocks.append((cur_title or "概述", cur_body))
            cur_title, cur_body = s.lstrip("# ").strip(), []
        elif s.startswith(("- ", "* ", "1. ")) or re.match(r"^\d+[.)]", s):
            cur_body.append(re.sub(r"^([-*]\s+|\d+[.)]\s+)", "", s))
        else:
            cur_body.append(s)
    if cur_title or cur_body:
        blocks.append((cur_title or "概述", cur_body))
    if not blocks:
        blocks = [("概述", [raw.strip()])]
    return [{"number": i + 1, "title": t, "bullets": b[:8], "notes": "", "images": []} for i, (t, b) in enumerate(blocks)]


def render(slides: list[dict], title: str, theme: dict) -> str:
    pages = []
    for s in slides:
        parts = [f'<h2 class="t">{esc(s["title"])}</h2>']
        if s["bullets"]:
            parts.append('<ul class="b">' + "".join(f'<li style="--i:{i + 1}">{esc(x)}</li>' for i, x in enumerate(s["bullets"][:8])) + "</ul>")
        for im in s["images"][:2]:
            parts.append(f'<figure class="fig" style="--i:9"><img src="{im}" alt=""></figure>')
        if s["notes"]:
            parts.append(f'<p class="n" style="--i:10">{esc(s["notes"][:180])}</p>')
        pages.append('<section class="slide">' + "".join(parts) + "</section>")

    dots = "".join(f'<i data-i="{i}"></i>' for i in range(len(slides)))
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--bg:{theme['bg']};--fg:{theme['fg']};--muted:{theme['muted']};--a1:{theme['a1']};--a2:{theme['a2']};--ink:{theme['ink']}}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;background:var(--bg);color:var(--fg);font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;overflow:hidden}}
#stage{{position:fixed;inset:0;display:grid;place-items:center}}
.slide{{grid-area:1/1;width:min(100vw,177.78vh);aspect-ratio:16/9;padding:6% 7%;display:flex;flex-direction:column;justify-content:center;gap:2.2vh;
  opacity:0;visibility:hidden;pointer-events:none;transition:opacity .45s ease,visibility .45s;position:relative}}
.slide::before{{content:"";position:absolute;inset:0;background:
  radial-gradient(60% 55% at 12% 18%,color-mix(in srgb,var(--a1) 26%,transparent),transparent 70%),
  radial-gradient(55% 50% at 88% 82%,color-mix(in srgb,var(--a2) 22%,transparent),transparent 72%);
  opacity:.55;pointer-events:none}}
.slide.active{{opacity:1;visibility:visible;pointer-events:auto}}
.slide>*{{opacity:0;transform:translateY(18px);transition:opacity .5s ease,transform .5s cubic-bezier(.2,.7,.2,1);transition-delay:calc(var(--i,0)*90ms)}}
.slide.active>*{{opacity:1;transform:none}}
.t{{font-size:clamp(24px,4.4vw,64px);line-height:1.15;letter-spacing:.02em;font-weight:800;
  background:linear-gradient(100deg,var(--fg),color-mix(in srgb,var(--a1) 70%,var(--fg)));-webkit-background-clip:text;background-clip:text;color:transparent}}
.b{{list-style:none;display:flex;flex-direction:column;gap:1.4vh;max-width:62ch}}
.b li{{position:relative;padding-left:1.1em;font-size:clamp(13px,1.55vw,25px);line-height:1.6;color:var(--fg)}}
.b li::before{{content:"";position:absolute;left:0;top:.72em;width:.42em;height:.42em;border-radius:2px;background:linear-gradient(135deg,var(--a1),var(--a2))}}
.fig img{{max-height:32vh;border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.45)}}
.n{{font-size:clamp(11px,1.1vw,17px);color:var(--muted);border-left:3px solid var(--a1);padding-left:.8em}}
#bar{{position:fixed;left:0;bottom:0;height:3px;background:linear-gradient(90deg,var(--a1),var(--a2));transition:width .35s ease;z-index:5}}
#no{{position:fixed;right:18px;bottom:14px;font-size:13px;color:var(--muted);z-index:5;font-variant-numeric:tabular-nums}}
#dots{{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;z-index:5}}
#dots i{{width:7px;height:7px;border-radius:50%;background:color-mix(in srgb,var(--fg) 22%,transparent);cursor:pointer;transition:.25s}}
#dots i.on{{width:22px;border-radius:4px;background:linear-gradient(90deg,var(--a1),var(--a2))}}
@media (prefers-reduced-motion:reduce){{.slide>*{{transition:none!important}}}}
</style></head><body>
<div id="stage">
{chr(10).join(pages)}
</div>
<div id="bar"></div><div id="dots">{dots}</div><div id="no"></div>
<script>
const S=[...document.querySelectorAll('.slide')],bar=document.getElementById('bar'),no=document.getElementById('no'),dots=[...document.querySelectorAll('#dots i')];
let cur=0;const show=n=>{{cur=Math.max(0,Math.min(S.length-1,n));S.forEach((s,i)=>s.classList.toggle('active',i===cur));
dots.forEach((d,i)=>d.classList.toggle('on',i===cur));bar.style.width=((cur+1)/S.length*100)+'%';no.textContent=(cur+1)+' / '+S.length;}};
addEventListener('keydown',e=>{{if(['ArrowRight','ArrowDown',' ','PageDown','Enter'].includes(e.key)){{e.preventDefault();show(cur+1)}}if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){{e.preventDefault();show(cur-1)}}}});
addEventListener('wheel',e=>{{if(Math.abs(e.deltaY)<18)return;show(cur+(e.deltaY>0?1:-1));}},{{passive:true}});
addEventListener('click',e=>{{if(e.target.closest('#dots'))return;const x=e.clientX/innerWidth;show(cur+(x>0.5?1:-1));}});
dots.forEach((d,i)=>d.addEventListener('click',()=>show(i)));
show(0);
</script></body></html>
"""


def esc(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def main() -> int:
    args = [a for a in sys.argv[1:]]
    if len(args) < 2:
        print(__doc__)
        return 2
    src, out_dir = args[0], args[1]
    title = "动效演示"
    theme_name = "dark-tech"
    for i, a in enumerate(args):
        if a == "--title" and i + 1 < len(args):
            title = args[i + 1]
        if a == "--theme" and i + 1 < len(args):
            theme_name = args[i + 1]
    os.makedirs(out_dir, exist_ok=True)
    ext = os.path.splitext(src)[1].lower()
    slides = from_pptx(src, out_dir) if ext == ".pptx" else from_text(src)
    if not slides:
        print("no slides extracted:", src)
        return 1
    theme = THEMES.get(theme_name, THEMES["dark-tech"])
    html = render(slides, title, theme)
    with io.open(os.path.join(out_dir, "outline.json"), "w", encoding="utf-8") as fh:
        json.dump({"source": os.path.abspath(src), "title": title, "slides": slides}, fh, ensure_ascii=False, indent=2)
    out_html = os.path.join(out_dir, "index.html")
    with io.open(out_html, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    imgs = sum(len(s["images"]) for s in slides)
    print(f"slides={len(slides)} images={imgs} bytes={os.path.getsize(out_html)}")
    print("html:", os.path.abspath(out_html))
    print("outline:", os.path.abspath(os.path.join(out_dir, "outline.json")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
