"""Contrast audit: sample the real rendered PNG behind each text run's box,
and keep only the darkest cluster (the ink) vs the lightest (the ground).
Using only pixels actually present avoids guessing backgrounds."""
import sys, collections, json, os
from pptx import Presentation
from PIL import Image

DES_W, DES_H = 960.0, 540.0   # ours: design space == preview png px
EMU_W, EMU_H = 12192000.0, 6858000.0

def luma(c):
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])

def contrast(a, b):
    la, lb = luma(a), luma(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def main(pptx, shots_dir, prefix, scale_x, scale_y, label, out_json):
    prefix = '' if prefix == '-' else prefix
    prs = Presentation(pptx)
    rows = []
    for i, sl in enumerate(prs.slides, 1):
        cand = [f'{prefix}{i:02d}.png', f'{prefix}{i:04d}.png', f'page-{i:04d}.png',
                f'{prefix}{i}.png', f'{i:02d}.png']
        p = next((os.path.join(shots_dir, c) for c in cand
                  if os.path.exists(os.path.join(shots_dir, c))), None)
        if p is None:
            continue
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        W, H = im.size
        for sh in sl.shapes:
            if not sh.has_text_frame or sh.left is None or sh.width is None:
                continue
            x0 = sh.left / EMU_W * DES_W * scale_x
            y0 = sh.top / EMU_H * DES_H * scale_y
            x1 = (sh.left + sh.width) / EMU_W * DES_W * scale_x
            y1 = (sh.top + sh.height) / EMU_H * DES_H * scale_y
            x0, y0 = max(0, int(x0)), max(0, int(y0))
            x1, y1 = min(W, int(x1)), min(H, int(y1))
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            szs = [r.font.size.pt for para in sh.text_frame.paragraphs for r in para.runs
                   if r.text.strip() and r.font.size]
            if not szs:
                continue
            sz = min(szs)
            txt = sh.text_frame.text.strip().replace('\n', ' ')[:34]
            crop = im.crop((x0, y0, x1, y1))
            nw, nh = crop.size
            # inset 15%: skip box padding/rounded corners and any neighbouring ink
            ix0, iy0 = int(nw * .15), int(nh * .15)
            ix1, iy1 = int(nw * .85), int(nh * .85)
            if ix1 - ix0 < 3 or iy1 - iy0 < 3:
                ix0, iy0, ix1, iy1 = 0, 0, nw, nh
            px = list(crop.crop((ix0, iy0, ix1, iy1)).getdata())
            n = len(px)
            if n < 12:
                continue
            # background = the single most common exact colour (text can never
            # outnumber its own ground inside a text box)
            hist = collections.Counter(px)
            ground = hist.most_common(1)[0][0]
            ground_share = hist.most_common(1)[0][1] / n
            # ink = darkest 3% of pixels, ignored if the crop is nearly monochrome
            L = sorted(px, key=luma)
            ink = L[max(0, int(n * 0.03)) // 2]
            cr = contrast(ink, ground)
            # how many pixels actually look like glyphs against the ground?
            ink_like = sum(1 for c in px if contrast(c, ground) >= 2.0)
            ink_share = ink_like / n
            dist = sum(abs(ink[k] - ground[k]) for k in range(3))
            if ground_share < 0.30:
                mark = '? 底色不可靠'      # photo / gradient behind text
            elif ink_share < 0.04 or dist < 30:
                mark = '~ 未采到字'        # crop contains no glyphs: unusable
            else:
                mark = ''
            if mark:
                rows.append({'page': i, 'size': sz, 'contrast': round(cr, 2),
                             'ink': '#%02X%02X%02X' % ink,
                             'ground': '#%02X%02X%02X' % ground,
                             'ground_share': round(ground_share, 2),
                             'ink_share': round(ink_share, 3), 'mark': mark,
                             'unusable': True, 'text': txt})
                continue
            rows.append({'page': i, 'size': sz, 'contrast': round(cr, 2),
                         'ink': '#%02X%02X%02X' % ink, 'ground': '#%02X%02X%02X' % ground,
                         'ground_share': round(ground_share, 2),
                         'ink_share': round(ink_share, 3), 'mark': mark,
                         'unusable': False, 'text': txt})
    json.dump(rows, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('=' * 78)
    print(f'{label}: {len(rows)} 个文本块按实测像素算对比度')
    print('=' * 78)
    unused = [r for r in rows if r.get('unusable')]
    rows = [r for r in rows if not r.get('unusable')]
    if unused:
        print(f'  （另有 {len(unused)} 块因底色不可靠/未采到字形被排除，不计入下面统计）')
    band = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        need = 3.0 if r['size'] >= 18 else 4.5
        ok = r['contrast'] >= need
        b = ('>=18pt' if r['size'] >= 18 else ('15-17pt' if r['size'] >= 15 else
             ('13-14pt' if r['size'] >= 13 else '<=12pt')))
        band[b][0] += 1
        band[b][1] += 0 if ok else 1
    for b in ('>=18pt', '15-17pt', '13-14pt', '<=12pt'):
        t, bad = band[b]
        if t:
            print(f'  {b:>8}: {t:>3} 块, 不达标 {bad:>3} ({bad/t:.0%})')
    fails = [r for r in rows if r['contrast'] < (3.0 if r['size'] >= 18 else 4.5)]
    fails.sort(key=lambda r: r['contrast'])
    print(f'\n  最差 16 块:')
    for r in fails[:16]:
        print(f"    p{r['page']:02d} {r['size']:>4}pt cr={r['contrast']:>4} "
              f"{r['ink']} on {r['ground']}  {r['text']}")
    print(f'\n  按页统计不达标块数:')
    c = collections.Counter(r['page'] for r in fails)
    print('   ', ', '.join(f'p{p}×{n}' for p, n in sorted(c.items())))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3],
         float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], sys.argv[7])
