"""Palette / colour-discipline audit from RENDERED pixels (the honest measure):
how many distinct hues are actually used, how saturated, and how much of the
canvas is the page's own background."""
import sys, os, collections, colorsys
from PIL import Image

def analyze(shots, pages, label, stride=4):
    print('=' * 78)
    print(f'{label}  目录: {shots}')
    print('=' * 78)
    all_px = []
    per_page_bg = []
    hues = collections.Counter()
    sat_hist = collections.Counter()
    for i in pages:
        cand = [f'{i:02d}.png', f'{i: 4d}.png'.strip(), f'page-{i:04d}.png']
        p = next((os.path.join(shots, c) for c in cand if os.path.exists(os.path.join(shots, c))), None)
        if p is None:
            continue
        im = Image.open(p).convert('RGB')
        W, H = im.size
        # page body = drop the outer frame (wooden border / dark band) to judge the content field
        box = (int(W * .04), int(H * .05), int(W * .96), int(H * .92))
        crop = im.crop(box)
        px = list(crop.getdata())[::stride]
        all_px += px
        bg = collections.Counter(px).most_common(1)[0][0]
        share = collections.Counter(px).most_common(1)[0][1] / len(px)
        # how many pixels are within +-12 of the page background colour
        near = sum(1 for c in px if max(abs(c[0]-bg[0]), abs(c[1]-bg[1]), abs(c[2]-bg[2])) <= 12) / len(px)
        per_page_bg.append((i, '#%02X%02X%02X' % bg, round(share, 3), round(near, 3)))

    # palette: quantise to 5-bit/channel and count
    q = collections.Counter((c[0] // 8, c[1] // 8, c[2] // 8) for c in all_px)
    print(f'\n  采样像素 = {len(all_px)}')
    print(f'  量化色（5bit/通道）去重数 = {len(q)}')
    print(f'  占前 90% 的色数 = ', end='')
    tot = sum(q.values()); acc = 0
    for k, (col, cnt) in enumerate(q.most_common(), 1):
        acc += cnt
        if acc / tot >= .90:
            print(k)
            break
    print('\n  前 10 色:')
    for col, cnt in q.most_common(10):
        r, g, b = (v * 8 + 4 for v in col)
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        print(f'    #{r:02X}{g:02X}{b:02X}  {cnt/len(all_px):6.2%}  H={h*360:5.1f}° S={s:.2f} V={v:.2f}')
        if s > .10:
            hues[int(h * 360) // 15 * 15] += cnt
    # saturation distribution
    for c in all_px[::3]:
        _, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
        sat_hist[round(s, 1)] += 1
    print('\n  饱和度分布（占比）:')
    tot2 = sum(sat_hist.values())
    for k in sorted(sat_hist):
        if sat_hist[k] / tot2 > .02:
            print(f'    S={k:.1f}: {sat_hist[k]/tot2:6.2%}')
    print('\n  有效色相桶（每 15°，S>.10）:')
    for k, v in sorted(hues.items()):
        print(f'    {k:3d}-{k+14:3d}° : {v/sum(hues.values()):6.2%}')
    print(f'\n  每页主色与"接近主色"占比（背景纯度）:')
    for i, bg, share, near in per_page_bg:
        print(f'    p{i:02d} bg={bg} 主色占比={share:.1%} 近主色像素={near:.1%}')

if __name__ == '__main__':
    pages = range(int(sys.argv[3]), int(sys.argv[4]) + 1)
    analyze(sys.argv[1], pages, sys.argv[2])
