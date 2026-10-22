# -*- coding: utf-8 -*-
from PIL import Image
import os
S = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
OUT = r"D:\Resources\DSH\_probe\contact_light.png"
files = sorted([f for f in os.listdir(S) if f.endswith(".png") and f[:2].isdigit()])
cols, tw = 6, 300
ims = [Image.open(os.path.join(S, f)).convert("RGB") for f in files]
th = int(ims[0].height * tw / ims[0].width)
rows = (len(ims) + cols - 1) // cols
pad, bg = 6, (24, 24, 24)
W = cols * tw + (cols + 1) * pad
H = rows * th + (rows + 1) * pad
sheet = Image.new("RGB", (W, H), bg)
for i, im in enumerate(ims):
    r, c = divmod(i, cols)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + c * (tw + pad), pad + r * (th + pad)))
sheet.save(OUT)
print("contact sheet %dx%d  pages=%d -> %s" % (W, H, len(ims), OUT))
