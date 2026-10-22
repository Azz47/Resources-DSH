import json, sys, math

def load(p):
    return json.load(open(p, encoding='utf-8'))

def luma(hexs):
    h = hexs.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contrast(a, b):
    la, lb = luma(a), luma(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def mode(sizes):
    if not sizes:
        return None
    c = {}
    for s in sizes:
        c[s] = c.get(s, 0) + 1
    return max(c.items(), key=lambda kv: kv[1])[0]

def main(path, label, W=960.0):
    d = load(path)
    print('=' * 76)
    print(f'{label}: {d["n"]} pages, design space {W:.0f}x{540}')
    print('=' * 76)

    # A. horizontal extent in DESIGN space (960 wide). 2/3 line = 640
    line = W * 2 / 3
    print(f'\n[A] 页面横向占位（设计空间 {W:.0f} 宽，2/3 线 = {line:.0f}）')
    xs = []
    over = []
    for pg in d['pages']:
        mx = 0; mn = 1e9
        for s in pg['shapes']:
            if s.get('x') is None or s.get('w') is None:
                continue
            mn = min(mn, s['x'])
            mx = max(mx, s['x'] + s['w'])
        xs.append((pg['page'], round(mn, 1) if mn < 1e9 else None, round(mx, 1)))
        if mx > line + 1:
            over.append((pg['page'], round(mx, 1)))
    allmx = [x[2] for x in xs]
    print(f'  右边界 max={max(allmx):.0f}  min={min(allmx):.0f}  median={sorted(allmx)[len(allmx)//2]:.0f}')
    print(f'  右边界跨过 2/3 线的页: {len(over)}/{d["n"]}  ->  {over[:12]}{"..." if len(over)>12 else ""}')
    lefts = [x[1] for x in xs if x[1] is not None]
    if lefts:
        print(f'  左边界 min={min(lefts):.1f} max={max(lefts):.1f}（左边距一致性）')

    # B. font mode per page
    print(f'\n[B] 每页正文字号众数 / 最小字号')
    modes = {}
    mn_all = []
    for pg in d['pages']:
        sz = []
        for s in pg['shapes']:
            if s.get('kind') == 'text':
                sz += (s.get('sizes') or [])
        body = [x for x in sz if x < 26]
        m = mode(body)
        modes[m] = modes.get(m, 0) + 1
        mn_all.append((pg['page'], min(sz) if sz else None, m))
    print('  众数分布:', ', '.join(f'{k}pt×{v}页' for k, v in sorted(modes.items(), key=lambda kv: -kv[1])))
    small = [(p, m) for p, m, mm in mn_all if m is not None and m <= 14]
    print(f'  最小字号 <=14pt 的页: {len(small)}/{d["n"]}')
    from collections import Counter
    print('  最小字号分布:', dict(Counter(m for _, m, _ in mn_all)))

    # C. 30pt / big repeated blocks
    print(f'\n[C] 每页最大号文本块前 3 条（找"每页都有"的重复元素）')
    for pg in d['pages'][:2]:
        tb = [s for s in pg['shapes'] if s.get('kind') == 'text' and (s.get('sizes') or [])]
        tb.sort(key=lambda s: -max(s['sizes']))
        print(f'  --- p{pg["page"]}')
        for s in tb[:3]:
            t = (s.get('text') or '').replace('\n', '⏎')
            print(f'    {max(s["sizes"])}pt @({s["x"]:.0f},{s["y"]:.0f}) {s["w"]:.0f}x{s["h"]:.0f} : {t[:70]}')

    # D. contrast of text colours vs mint bg
    print(f'\n[D] 文字色 / 背景色 对比度（WCAG 2.x）')
    bg = '#7FD6B0'
    cols = ['#17251D', '#12241B', '#2E4438', '#3E574A', '#46604F', '#2F7A5C', '#8A6A1E', '#8E3F2E', '#584C86',
            '#7FD6B0', '#E8C15A', '#EE8A72', '#6FC7E8', '#B9A7E8', '#3A5542', '#126839']
    print(f'  背景 mint {bg}')
    for c in cols:
        cr = contrast(bg, c)
        flag = 'PASS-AA' if cr >= 4.5 else ('LARGE-ONLY' if cr >= 3 else 'FAIL')
        print(f'    {c}  contrast={cr:5.2f}  {flag}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 960.0)
