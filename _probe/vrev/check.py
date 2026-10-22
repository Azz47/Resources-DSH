import json, sys, collections

RGB = 'https://schemas.openxmlformats.org/drawingml/2006/main'

def load(p):
    return json.load(open(p, encoding='utf-8'))

def main(path, label, W=None):
    d = load(path)
    W = W or d['w']
    H = d['h']
    print('=' * 74)
    print(f'{label}: {d["n"]} pages, {W:.0f}x{H:.0f}')
    print('=' * 74)
    # 1. right-third violation, using design space = W*2/3
    line = W * 2 / 3
    print(f'\n[1] 右 1/3 留空检查（2/3 线 = {line:.1f}px）')
    viol = []
    for pg in d['pages']:
        r = [s for s in pg['shapes']
             if (s.get('x') is not None and s.get('w') is not None
                 and s['x'] + s['w'] > line + 0.5)]
        if r:
            viol.append((pg['page'], r))
    if not viol:
        print('  OK 无元素越过 2/3 线')
    for p, r in viol:
        items = []
        for s in r:
            t = (s.get('text') or '').replace('\n', ' ')[:26]
            items.append(f"{s.get('kind')}@x{s['x']:.0f}+w{s['w']:.0f}->{s['x']+s['w']:.0f} '{t}'")
        print(f'  p{p:02d}: {len(r)} 个 -> ' + ' ; '.join(items[:3]))

    # 2. image inventory
    print(f'\n[2] 图片清单')
    tot = 0
    for pg in d['pages']:
        ims = [s for s in pg['shapes'] if s.get('kind') == 'image']
        if ims:
            tot += len(ims)
            a = sum((s['w'] or 0) * (s['h'] or 0) for s in ims)
            print(f"  p{pg['page']:02d}: {len(ims)} 张, 占页 {a/(W*H):.1%}  " +
                  ' '.join(f"{s['w']:.0f}x{s['h']:.0f}" for s in ims))
    print(f'  合计图片 {tot} 张 / {d["n"]} 页 = {tot/d["n"]:.0%} 页含图')
    nimg_pages = sum(1 for pg in d['pages'] if any(s.get('kind') == 'image' for s in pg['shapes']))
    print(f'  含图页数 {nimg_pages}/{d["n"]} = {nimg_pages/d["n"]:.1%}')

    # 3. font discipline per page
    print(f'\n[3] 字号纪律（每页正文级字号集合，排除标题>=26pt）')
    allsz = collections.Counter()
    for pg in d['pages']:
        sz = collections.Counter()
        for s in pg['shapes']:
            if s.get('kind') != 'text':
                continue
            for z in s.get('sizes') or []:
                sz[z] += 1
                allsz[z] += 1
        body = {k: v for k, v in sz.items() if k < 26}
        big = {k: v for k, v in sz.items() if k >= 26}
        bs = ','.join(f'{k}' for k in sorted(big))
        bd = ','.join(f'{k}' for k in sorted(body))
        print(f'  p{pg["page"]:02d} 标题[{bs or "-"}] 正文[{bd or "-"}]')
    print('\n  全册 run 级字号分布:')
    for k, v in sorted(allsz.items(), key=lambda kv: -kv[0]):
        print(f'    {k:>5}pt : {v:>4}')

    # 4. min font / small text census
    print(f'\n[4] 最小字号 / 小字普查')
    mn = min(allsz) if allsz else None
    print(f'  全册最小字号 = {mn}pt')
    for k in sorted(allsz):
        if k <= 13:
            print(f'  {k}pt 出现 {allsz[k]} 次', end='')
            pgs = [pg['page'] for pg in d['pages']
                   if any(k in (s.get('sizes') or []) for s in pg['shapes'] if s.get('kind') == 'text')]
            print(f'，分布在 {len(pgs)} 页: {pgs[:20]}{"..." if len(pgs) > 20 else ""}')

    # 5. title font census
    print(f'\n[5] 每页最大字号（标题字号阶梯）')
    tsz = []
    for pg in d['pages']:
        m = 0
        for s in pg['shapes']:
            if s.get('kind') == 'text' and (s.get('sizes')):
                m = max(m, max(s['sizes']))
        tsz.append((pg['page'], m))
    c = collections.Counter(x[1] for x in tsz)
    print('  最大字号分布:', ', '.join(f'{k}pt×{v}' for k, v in sorted(c.items(), key=lambda kv: -kv[0])))
    print('  逐页:', ' '.join(f'{p}:{s}' for p, s in tsz))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
