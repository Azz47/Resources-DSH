from PIL import Image, ImageDraw
import os
src = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots"
out = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_probe\contact_all.png"
files = [os.path.join(src, "%02d.png" % i) for i in range(1, 47)]
cols, rows, tw, th = 6, 8, 320, 180
W, H = cols*tw, rows*th
sheet = Image.new("RGB", (W, H), (18, 22, 20))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    if not os.path.exists(f):
        continue
    im = Image.open(f).convert("RGB").resize((tw-4, th-4), Image.LANCZOS)
    x, y = (i % cols)*tw, (i // cols)*th
    sheet.paste(im, (x+2, y+2))
    d.text((x+6, y+4), str(i+1), fill=(255, 220, 60))
sheet.save(out)
print("wrote", out, sheet.size)
