import sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
def flat(ss):
    for s in ss:
        yield s
        for c in s.get('children',[]) or []: yield from flat([c])
print("== 手拖痕迹：横坐标未落在 5pt 网格上的形状占比 ==")
tot=0; off=0
percount={}
for sl in d['slides']:
    S=[s for s in flat(sl['shapes']) if s.get('left') is not None]
    bad=sum(1 for s in S if abs(s['left']/5-round(s['left']/5))>0.02 or abs(s['top']/5-round(s['top']/5))>0.02)
    perc=bad/max(len(S),1)
    percount[sl['idx']]=(len(S),bad,round(perc*100))
    tot+=len(S); off+=bad
print("  全片 %d/%d = %.0f%% 的形状横纵起点不在 5pt 网格上"%(off,tot,off/tot*100))
print("  最严重的页:", sorted(percount.items(), key=lambda kv:-kv[1][2])[:10])
print("\n== 每页左边界（内容起点）种类数 ==")
for sl in d['slides']:
    S=[s for s in flat(sl['shapes']) if s.get('left') is not None and (s.get('text') or '').strip()]
    ls=sorted({round(s['left'],1) for s in S})
    if len(ls)>3: print("  p%02d 左起点 %d 种: %s"%(sl['idx'],len(ls),ls[:12]))
print("\n== P17 详情 ==")
for s in flat(d['slides'][16]['shapes']):
    print("   %-16s %-16s (%s,%s) %sx%s fill=%s line=%s :: %s"%(s['name'][:16],s['type'].split(' ')[0][:15],s['left'],s['top'],s['w'],s['h'],s.get('fill'),s.get('line'),(s.get('text') or '')[:34].replace('\n','/')))
print("\n== 用了流程图接点/任意多边形/自由曲线的页 ==")
for sl in d['slides']:
    hits=[s['name'] for s in flat(sl['shapes']) if any(k in s['name'] for k in ('流程图','任意多边形','自由曲线','手绘'))]
    if hits: print("  p%02d %d 个: %s"%(sl['idx'],len(hits),hits[:6]))
