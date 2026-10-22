# -*- coding: utf-8 -*-
"""生成版式图鉴：contact sheet（可视核对）+ 单文件交互 HTML（缩略图/色板/节奏条）。"""
import base64
import io
import json
import os
import statistics
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\Resources\DSH\_specs"
PNG = os.path.join(ROOT, "atlas", "png")
METRICS = os.path.join(ROOT, "_layout_metrics.json")
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"

ARCH_COLORS = {
    "多栏卡片": "#2E6E8F",
    "双栏": "#1C6B60",
    "网格图表": "#A8812F",
    "单栏": "#3B4B57",
    "大标题/扉页": "#B4552F",
    "全幅/通栏图": "#614FB3",
    "空页": "#D3D7D6",
}
GROUP_OF = lambda slug: "styles" if slug.startswith(("bw--", "dark--", "light--", "mixed--", "vivid--", "warm--")) else (
    "web" if slug.startswith("web--") else "ours")


def palette_of(path, n=5):
    im = Image.open(path).convert("RGB").resize((120, 68))
    q = im.quantize(colors=n, method=Image.MEDIANCUT).convert("RGB")
    counts = Counter(q.getdata())
    return ["#%02X%02X%02X" % c for c, _ in counts.most_common(n)]


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def sheet(items, out, cols=5, tw=480, th=270, title=""):
    rows = (len(items) + cols - 1) // cols
    pad, lab = 16, 34
    W = cols * (tw + pad) + pad
    H = rows * (th + pad + lab) + pad + 52
    canvas = Image.new("RGB", (W, H), "#11161C")
    d = ImageDraw.Draw(canvas)
    d.text((pad, 16), title, font=font(26, True), fill="#EAF0F4")
    for i, (slug, path, caption) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = 52 + pad + r * (th + pad + lab)
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        canvas.paste(im, (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline="#2A3542")
        d.text((x, y + th + 6), caption[:46], font=font(17), fill="#B9C9D4")
    canvas.save(out, "JPEG", quality=86, optimize=True)
    return canvas.size, os.path.getsize(out)


def main():
    metrics = {os.path.basename(os.path.dirname(m["file"])): m for m in
               json.load(open(METRICS, encoding="utf-8"))}
    bydir = {os.path.basename(m["file"]): m for m in metrics.values()}

    groups = {}
    for slug in sorted(os.listdir(PNG)):
        d = os.path.join(PNG, slug)
        if not os.path.isdir(d):
            continue
        pages = sorted(f for f in os.listdir(d) if f.endswith(".png"))
        groups[slug] = [os.path.join(d, p) for p in pages]

    # 1) contact sheets
    styles = [(s, p[0], f"{s}") for s, p in groups.items() if GROUP_OF(s) == "styles"]
    print("styles sheet", sheet(styles, os.path.join(ROOT, "atlas", "sheet-styles.jpg"),
                                title="样式库 27 套 · 首页（PowerPoint 渲染）"))
    rest = [(s, p[0], f"{s} / {os.path.basename(p[0])}") for s, p in groups.items() if GROUP_OF(s) != "styles"]
    print("web sheet", sheet(rest, os.path.join(ROOT, "atlas", "sheet-web.jpg"), cols=4,
                             title="网络样本 3 份 + 自制两册 · 首页"))

    # 2) html
    cards = []
    for slug, pages in groups.items():
        meta = None
        for name, m in bydir.items():
            if meta is None and (name.startswith(slug) or slug in name):
                meta = m
        pal = palette_of(pages[0])
        thumbs = []
        for p in pages:
            im = Image.open(p).convert("RGB")
            im.thumbnail((480, 480), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=68, optimize=True)
            thumbs.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode())
        slides = [s for s in (meta["slides"] if meta else []) if not s.get("empty")]
        arch = Counter()
        for s in slides:
            t = "网格图表" if (s.get("tables") or s.get("charts")) else (
                "全幅/通栏图" if s.get("pic_area_ratio", 0) > 0.25 else (
                    "多栏卡片" if (s.get("cols", 1) >= 3 and s.get("content", 0) >= 5) else (
                        "双栏" if s.get("cols", 1) == 2 else (
                            "大标题/扉页" if ((s.get("chars") or 0) < 60 and s.get("content", 0) <= 3) else "单栏"))))
            arch[t] += 1
        ws = round(statistics.median([s["whitespace"] for s in slides]), 2) if slides else 0
        cards.append({
            "slug": slug, "group": GROUP_OF(slug), "thumbs": thumbs, "pal": pal,
            "pages": len(slides), "ws": ws, "arch": dict(arch.most_common()),
            "cols": Counter(s["cols"] for s in slides).most_common(1)[0][0] if slides else 0,
            "chars": round(statistics.median([s["chars"] for s in slides])) if slides else 0,
            "els": round(statistics.median([s["els"] for s in slides]), 1) if slides else 0,
            "ratio": round(statistics.median([s["ratio"] for s in slides if s.get("ratio")]), 2) if any(s.get("ratio") for s in slides) else None,
            "seq": [next((k for k, v in ARCH_COLORS.items() if v == ARCH_COLORS.get(k)), "单栏") for _ in []],
        })

    # 节奏条：按 metrics 里的每页原型
    rhythm = {}
    for m in metrics.values():
        name = os.path.basename(os.path.dirname(m["file"])) + "/" + os.path.basename(m["file"])
        seq = []
        for s in m["slides"]:
            if s.get("empty"):
                seq.append("空页")
                continue
            if s.get("tables") or s.get("charts"):
                seq.append("网格图表")
            elif s.get("pic_area_ratio", 0) > 0.25:
                seq.append("全幅/通栏图")
            elif s.get("cols", 1) >= 3 and s.get("content", 0) >= 5:
                seq.append("多栏卡片")
            elif s.get("cols", 1) == 2:
                seq.append("双栏")
            elif (s.get("chars") or 0) < 60 and s.get("content", 0) <= 3:
                seq.append("大标题/扉页")
            else:
                seq.append("单栏")
        rhythm[name] = seq

    data = {"cards": cards, "rhythm": rhythm, "colors": ARCH_COLORS}
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    out = os.path.join(ROOT, "layout-atlas.html")
    io.open(out, "w", encoding="utf-8").write(html)
    print("html:", out, os.path.getsize(out), "bytes")


TEMPLATE = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>版式图鉴 · layout atlas</title>
<style>
:root{--bg:#0E141A;--panel:#151D25;--line:#26313D;--ink:#E8EEF4;--dim:#93A4B3;--acc:#2E6E8F}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 "Microsoft YaHei",system-ui,sans-serif}
header{padding:28px 32px 12px}h1{margin:0;font-size:24px;letter-spacing:.5px}
.sub{color:var(--dim);font-size:13px;margin-top:6px}
.bar{position:sticky;top:0;z-index:9;background:rgba(14,20,26,.94);backdrop-filter:blur(6px);padding:14px 32px;border-bottom:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button{background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:6px 14px;border-radius:999px;cursor:pointer;font-size:13px}
button.on{background:var(--acc);border-color:var(--acc)}
.wrap{padding:20px 32px 60px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;cursor:zoom-in}
.card img{width:100%;display:block;aspect-ratio:16/9;object-fit:cover}
.meta{padding:10px 12px}.nm{font-size:13px;font-weight:600;word-break:break-all}
.kv{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;color:var(--dim);font-size:12px}
.pal{display:flex;gap:3px;margin-top:8px}.pal i{width:16px;height:16px;border-radius:3px;border:1px solid rgba(255,255,255,.15)}
h2{font-size:16px;margin:34px 0 12px;padding-left:10px;border-left:3px solid var(--acc)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left}
th{color:var(--dim);font-weight:500}
.rhythm{display:flex;align-items:center;gap:10px;margin:6px 0}
.rname{width:260px;color:var(--dim);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.seq{display:flex;gap:2px;flex:1;flex-wrap:nowrap;overflow:hidden}
.seq i{flex:1;min-width:4px;height:14px;border-radius:2px;opacity:.9}
#lb{position:fixed;inset:0;background:rgba(5,8,11,.94);display:none;align-items:center;justify-content:center;z-index:99;cursor:zoom-out}
#lb img{max-width:94vw;max-height:88vh;box-shadow:0 20px 60px rgba(0,0,0,.6)}
.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--dim);font-size:12px;margin-top:8px}
.legend span{display:flex;align-items:center;gap:5px}.legend i{width:12px;height:12px;border-radius:3px}
</style></head><body>
<header><h1>版式图鉴 · layout atlas</h1>
<div class="sub">76 页 PowerPoint 真实渲染 · 27 套样式库 + 3 份网络样本 + 自制两册 · 度量由 python-pptx 逐盒计算</div></header>
<div class="bar" id="filters"></div>
<div class="wrap">
<h2>版式卡片（点开看大图）</h2><div class="grid" id="grid"></div>
<h2>整册节奏条（每格一页，颜色=版式原型）</h2><div class="legend" id="legend"></div><div id="rhythm"></div>
</div>
<div id="lb"><img id="lbimg"></div>
<script>
const D=__DATA__;
const NAMES={styles:"样式库",web:"网络样本",ours:"自制两册"};
let cur="all";
const bar=document.getElementById("filters");
function mkBtn(k,t){const b=document.createElement("button");b.textContent=t;b.onclick=()=>{cur=k;render();};b.dataset.k=k;return b;}
bar.append(mkBtn("all","全部"),mkBtn("styles","样式库 27"),mkBtn("web","网络样本 3"),mkBtn("ours","自制两册"));
const grid=document.getElementById("grid");
function render(){
 [...bar.children].forEach(b=>b.classList.toggle("on",b.dataset.k===cur));
 grid.innerHTML="";
 D.cards.filter(c=>cur==="all"||c.group===cur).forEach((c,idx)=>{
  const d=document.createElement("div");d.className="card";
  const arch=Object.entries(c.arch).slice(0,2).map(([k,v])=>k+" "+v).join(" · ");
  d.innerHTML=`<img src="${c.thumbs[0]}" loading="lazy"><div class="meta"><div class="nm">${c.slug}</div>
   <div class="kv"><span>${c.pages} 页</span><span>栏 ${c.cols}</span><span>留白 ${Math.round(c.ws*100)}%</span><span>${c.els} 元素/页</span><span>${c.chars} 字/页</span></div>
   <div class="kv">${arch}</div><div class="pal">${c.pal.map(p=>`<i style="background:${p}" title="${p}"></i>`).join("")}</div></div>`;
  d.onclick=()=>open(c.thumbs[0]);grid.append(d);
 });
}
function open(src){const lb=document.getElementById("lb");document.getElementById("lbimg").src=src;lb.style.display="flex";}
document.getElementById("lb").onclick=()=>document.getElementById("lb").style.display="none";
const lg=document.getElementById("legend");
for(const[k,v] of Object.entries(D.colors)){const s=document.createElement("span");s.innerHTML=`<i style="background:${v}"></i>${k}`;lg.append(s);}
const rh=document.getElementById("rhythm");
for(const[name,seq] of Object.entries(D.rhythm)){
 const row=document.createElement("div");row.className="rhythm";
 row.innerHTML=`<div class="rname" title="${name}">${name}</div><div class="seq">${seq.map((a,i)=>`<i title="第${i+1}页 · ${a}" style="background:${D.colors[a]||'#444'}"></i>`).join("")}</div>`;
 rh.append(row);
}
render();
</script></body></html>"""

if __name__ == "__main__":
    main()
