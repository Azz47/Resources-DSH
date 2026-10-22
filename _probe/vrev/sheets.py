"""Build labeled side-by-side comparison sheets: ours | friend."""
import sys, os
from PIL import Image, ImageDraw

OURS = r'D:\Resources\DSH\decks\单元思考与行动-参赛版\preview\shots'
FRI = r'D:\Resources\DSH\_probe\vrev\friend-render'
OUT = r'D:\Resources\DSH\_probe\vrev\sheets'
os.makedirs(OUT, exist_ok=True)

PAIRS = [(1, 1), (2, 2), (3, 3)]
CELL_W = 700
PAD = 10
LBL = 30

def load(p, idx, pref):
    fn = os.path.join(p, f'{pref}{idx:04d}.png' if pref == 'page-' else f'{idx:02d}.png')
    if not os.path.exists(fn):
        return None
    return Image.open(fn).convert('RGB')

def sheet(name, pairs):
    rows = []
    for a, b in pairs:
        ia = load(OURS, a, '')
        ib = load(FRI, b, 'page-')
        ims = [i for i in (ia, ib) if i]
        if not ims:
            continue
        h = int(ims[0].height * CELL_W / ims[0].width)
        row = Image.new('RGB', (CELL_W * 2 + PAD, h + LBL + PAD), 'white')
        dr = ImageDraw.Draw(row)
        for k, im in enumerate(ims):
            im = im.resize((CELL_W, h))
            row.paste(im, (k * (CELL_W + PAD), LBL))
        dr.text((6, 8), f'OURS p{a}', fill='red')
        dr.text((CELL_W + PAD + 6, 8), f'FRIEND p{b}', fill='blue')
        rows.append(row)
    if not rows:
        print('no rows for', name)
        return
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + PAD * (len(rows) - 1)
    out = Image.new('RGB', (W, H), 'white')
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + PAD
    p = os.path.join(OUT, name)
    out.save(p)
    print(p, out.size)

if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'a':
        sheet('cmp_01_02_03.png', PAIRS)
    elif which == 'b':
        sheet('cmp_08_16_31.png', [(8, 6), (16, 15), (31, 26)])
    elif which == 'c':
        sheet('cmp_cover_end.png', [(1, 1), (46, 40), (44, 38)])
