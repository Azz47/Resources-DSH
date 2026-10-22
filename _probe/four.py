# -*- coding: utf-8 -*-
from PIL import Image
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
pages = ["01", "24", "28", "34"]
tw = 700
ims = [Image.open(S + "\\" + p + ".png").convert("RGB") for p in pages]
th = int(ims[0].height * tw / ims[0].width)
cols, pad = 2, 8
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols*tw + (cols+1)*pad, rows*th + (rows+1)*pad), (20,20,20))
for i, im in enumerate(ims):
    r, c = divmod(i, cols)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + c*(tw+pad), pad + r*(th+pad)))
out = r"D:\Resources\DSH\_probe\fix4.png"
sheet.save(out)
print("pages", pages, "->", out, sheet.size)
