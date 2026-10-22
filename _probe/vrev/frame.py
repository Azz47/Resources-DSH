"""Frame footprint + vertical density profile from rendered pixels."""
import sys, os, collections
from PIL import Image

def main(shots, pages, label):
    print('=' * 78)
    print(f'{label} — 版面框架占位与竖向密度')
    print('=' * 78)
    prof = [0] * 100          # occupancy per 1% band
    frame_bottom = []          # y where content field ends (dark wood band)
    n = 0
    for i in pages:
        cand = [f'{i:02d}.png', f'page-{i:04d}.png']
        p = next((os.path.join(shots, c) for c in cand if os.path.exists(os.path.join(shots, c))), None)
        if p is None:
            continue
        im = Image.open(p).convert('RGB')
        W, H = im.size
        px = im.load()
        n += 1
        # vertical density: for each 1% band, share of pixels that are NOT the
        # page background colour (#A2E6B5-ish) and NOT white card (#FCFCFC)
        for y in range(H):
            band = int(y / H * 100)
            step = max(1, W // 320)
            xs = range(0, W, step)
            row = 0
            cnt = 0
            for x in xs:
                r, g, b = px[x, y]
                cnt += 1
                if abs(r - 162) > 26 or abs(g - 230) > 26 or abs(b - 181) > 26:
                    row += 1
            prof[band] += (row / cnt)
        frame_bottom.append(H)
    prof = [min(v / max(n, 1), 1.0) for v in prof]
    print(f'  样本页数 = {n}')
    print(f'\n  竖向密度（每 1% 高度带，"非背景"像素占比）:')
    for b in range(0, 100, 2):
        bar = '█' * int(prof[b] * 46)
        print(f'    {b:>3}%  {prof[b]:5.1%} {bar}')
    # highlight the two heavy bands from the reference standard
    if n:
        hdr = sum(prof[0:11]) / 11
        mid = sum(prof[49:61]) / 12
        print(f'\n  第1带(0-10%)均值 = {hdr:.1%}')
        print(f'  第6带(50-60%)均值 = {mid:.1%}')

if __name__ == '__main__':
    main(sys.argv[1], range(int(sys.argv[2]), int(sys.argv[3]) + 1), sys.argv[4])
