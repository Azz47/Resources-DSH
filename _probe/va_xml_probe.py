# -*- coding: utf-8 -*-
"""1) 直读 pptx XML：画布尺寸与真实字号  2) 真渲染右 1/3 区域裁图"""
import zipfile, re, os
from PIL import Image, ImageDraw

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
PPTX = os.path.join(D, "第二单元 进入新时代-单元思考与行动-参赛版.pptx")
z = zipfile.ZipFile(PPTX)
pres = z.read("ppt/presentation.xml").decode("utf-8", "ignore")
m = re.search(r'<p:sldSz[^>]*/>', pres)
print("sldSz:", m.group(0) if m else "NOT FOUND")
names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
print("slides:", len(names))

# 第 5 页（=p05）字号分布
s5 = z.read("ppt/slides/slide5.xml").decode("utf-8", "ignore")
sizes = [int(x) for x in re.findall(r'sz="(\d+)"', s5)]
from collections import Counter
print("slide5 字号分布(sz, 百分之一磅):", sorted(Counter(sizes).items()))
# 字体名
print("字体:", sorted(set(re.findall(r'typeface="([^"]+)"', s5))))
# 段落文本
for t in re.findall(r"<a:t>([^<]*)</a:t>", s5)[:14]:
    print("   txt:", t[:60])
# 图片关系
rels = z.read("ppt/slides/_rels/slide5.xml.rels").decode("utf-8", "ignore")
print("slide5 图片rels:", re.findall(r'Target="([^"]*media[^"]*)"', rels))
# 背景：查 slide5 是否用 blipFill 铺底
print("slide5 有 blipFill:", "blipFill" in s5, " 有 bg:", "<p:bg>" in s5)
print("slide5 ext (图片/形状尺寸) 前 6 个:", re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"/>', s5)[:6])
z.close()

# ---- 真渲染右 1/3 裁图 ----
T = r"D:\Resources\DSH\_probe\va_true"
pairs = [("p17", "page-0004.png"), ("p33", "page-0006.png"), ("p44", "page-0009.png"), ("p08", "page-0003.png")]
box = (640, 150, 960, 420)
cs = []
for pg, fn in pairs:
    im = Image.open(os.path.join(T, fn)).convert("RGB").resize((960, 540), Image.LANCZOS).crop(box)
    cs.append((pg, im))
w, h = cs[0][1].size
canvas = Image.new("RGB", (len(cs) * (w + 10) + 10, h + 40), (255, 255, 255))
dr = ImageDraw.Draw(canvas)
for i, (pg, im) in enumerate(cs):
    x = 10 + i * (w + 10)
    dr.text((x, 6), "%s 右1/3 (pptx真渲染)" % pg, fill=(180, 0, 0))
    canvas.paste(im, (x, 30))
    # 采样点统计
    from collections import Counter
    c = Counter(im.getdata())
    dr.text((x, h + 32 - 12), "主色: %s" % str(c.most_common(2)), fill=(0, 0, 0))
canvas.save(r"D:\Resources\DSH\_probe\va_rightthird.png")
print("saved", canvas.size)
