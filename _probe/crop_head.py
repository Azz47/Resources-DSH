# -*- coding: utf-8 -*-
"""裁出页面顶部区域放大，用来肉眼确认页眉是否断行。"""
import glob
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PAGES = r"D:\Resources\DSH\contest-rework\render-final\pages"
OUT = r"D:\Resources\DSH\contest-rework\render-final"
WANT = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["3"])]
FRAC = float(sys.argv[2]) if len(sys.argv) > 2 else 0.22

fs = sorted(glob.glob(os.path.join(PAGES, "*.png")))
for n in WANT:
    im = Image.open(fs[n - 1])
    w, h = im.size
    crop = im.crop((0, 0, w, int(h * FRAC)))
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
    out = os.path.join(OUT, "head-p%d.png" % n)
    crop.save(out)
    print("saved %s  %s" % (out, crop.size))
