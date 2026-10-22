import sys, json, re

def summarize(path, label):
    d = json.load(open(path, encoding='utf-8'))
    W, H = d['w'], d['h']
    print('=' * 70)
    print(f"{label}: {d['n']} pages, {W}x{H}px  ({d['path']})")
    print('=' * 70)
    total_sizes = {}
    all_rows = []
    for pg in d['pages']:
        shp = pg['shapes']
        sizes = {}
        text_chars = 0
        text_area = 0.0
        img_area = 0.0
        n_text = n_img = n_shape = 0
        inks = []
        for s in shp:
            k = s.get('kind')
            w = s.get('w') or 0
            h = s.get('h') or 0
            if k == 'text':
                n_text += 1
                text_chars += s.get('tlen', 0)
                text_area += w * h
                for z in s.get('sizes', []):
                    sizes[z] = sizes.get(z, 0) + 1
                    total_sizes[z] = total_sizes.get(z, 0) + 1
            elif k == 'image':
                n_img += 1
                img_area += w * h
                inks.append('IMG')
            else:
                n_shape += 1
                f = s.get('fill')
                if f:
                    inks.append('#' + f)
        cover = (text_area / (W * H))
        row = {
            'p': pg['page'], 'nt': n_text, 'ni': n_img, 'ns': n_shape,
            'chars': text_chars, 'txtcov': round(cover, 3),
            'imgcov': round(img_area / (W * H), 3),
            'sizes': sizes,
            'notes': len(pg.get('notes') or ''),
        }
        all_rows.append(row)

    print('\n-- per page --')
    print(f"{'pg':>3} {'#txt':>4} {'#img':>4} {'#shp':>4} {'chars':>6} {'txtcov':>7} {'imgcov':>7}  sizes")
    for r in all_rows:
        szs = ','.join(f"{k}:{v}" for k, v in sorted(r['sizes'].items(), key=lambda kv: -kv[0]))
        print(f"{r['p']:>3} {r['nt']:>4} {r['ni']:>4} {r['ns']:>4} {r['chars']:>6} "
              f"{r['txtcov']:>7} {r['imgcov']:>7}  {szs[:70]}")

    n = len(all_rows)
    import statistics as st
    def agg(f):
        return round(st.median([f(r) for r in all_rows]), 3)
    print('\n-- medians --')
    print('text blocks/page :', agg(lambda r: r['nt']))
    print('images/page      :', agg(lambda r: r['ni']))
    print('shapes/page      :', agg(lambda r: r['ns']))
    print('chars/page       :', agg(lambda r: r['chars']))
    print('text coverage    :', agg(lambda r: r['txtcov']))
    print('image coverage   :', agg(lambda r: r['imgcov']))
    print('\n-- font size histogram (runs) --')
    for k, v in sorted(total_sizes.items(), key=lambda kv: -kv[0]):
        print(f'  {k:>5}pt : {v:>5}')
    return all_rows

if __name__ == '__main__':
    summarize(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'deck')
