import json, sys, collections

def load(p):
    return json.load(open(p, encoding='utf-8'))

def txt_of(s):
    return (s.get('text') or '').strip()

def dig(path, label, pages=None):
    d = load(path)
    print('#' * 78)
    print(f'# {label}  ({d["n"]} pages)')
    print('#' * 78)
    for pg in d['pages']:
        p = pg['page']
        if pages and p not in pages:
            continue
        tb = [s for s in pg['shapes'] if s.get('kind') == 'text' and txt_of(s)]
        imgs = [s for s in pg['shapes'] if s.get('kind') == 'image']
        # largest font text = likely title
        def maxsz(s):
            return max(s.get('sizes') or [0])
        ttl = max(tb, key=maxsz) if tb else None
        # smallest fonts
        mn = sorted(tb, key=maxsz)
        print(f"\n--- p{p:02d}  textblocks={len(tb)} imgs={len(imgs)}")
        if ttl:
            print(f"  TITLE {maxsz(ttl)}pt @({ttl['x']},{ttl['y']}) w{ttl['w']}h{ttl['h']}: {txt_of(ttl)[:60]}")
        # font size set
        sz = collections.Counter()
        for s in tb:
            for z in s.get('sizes') or []:
                sz[z] += 1
        print('  sizes:', ','.join(f'{k}:{v}' for k, v in sorted(sz.items(), key=lambda kv: -kv[0])))
        small = [s for s in tb if maxsz(s) <= 13]
        if small:
            print(f"  SMALL(<=13pt) x{len(small)}:", ' | '.join(txt_of(s)[:26] for s in small[:4]))
        for s in imgs:
            print(f"  IMG @({s['x']},{s['y']}) {s['w']}x{s['h']}")
        # right third occupancy
        W = 1280
        r3 = [s for s in pg['shapes'] if (s.get('x') or 0) + (s.get('w') or 0) > W * 2 / 3 and (s.get('w') or 0) > 2]
        if r3:
            print(f"  RIGHT1/3 elements: {len(r3)} -> " +
                  ' ; '.join(f"{s.get('kind')}@x{s['x']}w{s['w']}" + (f" '{txt_of(s)[:14]}'" if txt_of(s) else '')
                             for s in r3[:4]))

if __name__ == '__main__':
    dig(sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else None)
