import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
def flat(ss):
    for s in ss:
        yield s
        for c in s.get('children',[]) or []: yield from flat([c])
def rect(s): return (s['left'],s['top'],s['left']+s['w'],s['top']+s['h'])
def inter(a,b):
    x=max(0,min(a[2],b[2])-max(a[0],b[0])); y=max(0,min(a[3],b[3])-max(a[1],b[1])); return x*y
print("== 同页形状重叠（面积>500pt²，排除图片与其它图片） ==")
for sl in d['slides']:
    S=[s for s in flat(sl['shapes']) if s.get('left') is not None and s.get('w')]
    out=[]
    for i in range(len(S)):
        for j in range(i+1,len(S)):
            a,b=S[i],S[j]
            ai,bi=inter(rect(a),rect(b)),0
            if ai<=500: continue
            ta=(a.get('text') or '').strip(); tb=(b.get('text') or '').strip()
            if ta and tb: kind="文×文"
            elif ta or tb: kind="文×形"
            else: kind="形×形"
            out.append((ai,kind,a['name'][:12],ta[:16].replace('\n','/'),b['name'][:12],tb[:16].replace('\n','/')))
    if out:
        print(" p%02d"%sl['idx'])
        for o in sorted(out,reverse=True)[:6]:
            print("    %6.0f %s [%s]%s × [%s]%s"%(o[0],o[1],o[2],o[3],o[4],o[5]))
# picture vs text overlap
print("\n== 图片 × 文字框 重叠 ==")
for sl in d['slides']:
    S=[s for s in flat(sl['shapes']) if s.get('left') is not None and s.get('w')]
    for a in S:
        if not a.get('img'): continue
        for b in S:
            if b is a or not (b.get('text') or '').strip(): continue
            ov=inter(rect(a),rect(b))
            if ov>500:
                print("  p%02d 图片%s(r=%s) × 文字[%s](%s) 重叠%.0fpt²"%(sl['idx'],a['img']['sha'],round(a['left']+a['w']),b['name'][:12],(b.get('text') or '')[:14].replace('\n','/'),ov))
print("\n== P13 全形状 ==")
for s in flat(d['slides'][12]['shapes']):
    print("   %-14s %-12s (%s,%s) %sx%s fill=%s :: %s"%(s['name'][:14],s['type'].split(' ')[0][:11],s['left'],s['top'],s['w'],s['h'],s.get('fill'),(s.get('text') or '')[:40].replace('\n','/')))
