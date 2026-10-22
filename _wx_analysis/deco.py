import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
def flat(ss):
    for s in ss:
        yield s
        for c in s.get('children',[]) or []: yield from flat([c])
print("== 标题装饰组（细横线+方块组合+两个小方块）的落点，全片比对 ==")
for sl in d['slides']:
    S=list(flat(sl['shapes']))
    ln=[s for s in S if s['type'].startswith('LINE')]
    grp=[s for s in S if s['type'].startswith('GROUP') and s.get('w') and 30<s['w']<40]
    sq=[s for s in S if s['type'].startswith('AUTO_SHAPE') and s.get('w')==28.62]
    if ln or sq:
        print("  p%02d 线=(%s,%s) 组合=(%s,%s) 方块=%s x=%s"%(sl['idx'],
            ln[0]['left'],ln[0]['top'] if ln else '-',
            grp[0]['left'] if grp else '-', grp[0]['top'] if grp else '-',
            len(sq), [s['left'] for s in sq]))
print("\n== 零高度/零宽 形状（隐形残留） ==")
n=0
for sl in d['slides']:
    z=[s for s in flat(sl['shapes']) if s.get('w')==0 or s.get('h')==0 or s.get('w') is None]
    if z:
        n+=len(z)
        print("  p%02d %d 个: %s"%(sl['idx'],len(z),[(s['name'],s['w'],s['h']) for s in z][:5]))
print("  合计零尺寸形状:",n)
print("\n== P25 / P22 / P23 溢出复算 ==")
def em(t):
    return sum(2.0 if c=='—' else (0.55 if ord(c)<0x2E80 else 1.0) for c in t)
for pg in (22,23,25,30,36):
    for s in flat(d['slides'][pg-1]['shapes']):
        if not (s.get('text') or '').strip() or not s.get('w'): continue
        szs=[r['sz'] for r in s.get('runs',[]) if r['sz']]
        sz=max(szs) if szs else 18
        avail=s['w']-14.4
        lines=em(s['text'])*sz*1.03/avail
        need=lines*sz*1.29*1.03
        print("  p%02d [%s] %d字 %dpt 框%.0fx%.0f → 需%.0fpt (%.2f行) 比值%.2f"%(pg,s['name'][:10],len(s['text']),sz,s['w'],s['h'],need,lines,need/s['h']))
