import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
def flat(ss):
    for s in ss:
        yield s
        for c in s.get('children',[]) or []: yield from flat([c])
for pg in (15,16,22,24,25,30,31,33):
    print("== P%02d =="%pg)
    for s in flat(d['slides'][pg-1]['shapes']):
        r=(s.get('left') or 0)+(s.get('w') or 0)
        print("   %-14s %-11s (%s,%s) %sx%s 右=%s fill=%s :: %s"%(s['name'][:14],s['type'].split(' ')[0][:10],s['left'],s['top'],s['w'],s['h'],round(r,1) if r else '-',s.get('fill'),(s.get('text') or '')[:44].replace('\n','/')))
