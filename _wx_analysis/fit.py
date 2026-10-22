import sys, json, math
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
def flat(ss):
    for s in ss:
        yield s
        for c in s.get('children',[]) or []: yield from flat([c])
def em(t):
    w=0.0
    for ch in t:
        o=ord(ch)
        if ch in '——': w+=2.0
        elif o<0x2E80: w+=0.55
        else: w+=1.0
    return w
print("== 文本溢出估算（needed/box 高度比 >1.0 = 会压到下一元素）==")
tot=0
for sl in d['slides']:
    bad=[]
    for s in flat(sl['shapes']):
        if not s.get('text') or not s.get('runs'): continue
        w=s['w']; h=s['h']
        if not w or not h: continue
        avail=max(w-14.4, 1)   # 默认左右内缩各 7.2pt
        need=0.0; maxsz=0
        # group runs by paragraph (approx: split text)
        szs=[r['sz'] for r in s['runs'] if r['sz']]
        sz=max(szs) if szs else 18
        for r in s['runs']:
            if not r['t']: continue
            e=em(r['t']); rs=r['sz'] or sz
            need += e*rs*1.03 / avail * rs*1.29*1.03
        if need/h > 1.02:
            bad.append((round(need/h,2), round(need,1), h, s['name'], (s['text'] or '')[:34].replace('\n','/')))
    if bad:
        tot+=sum(1 for b in bad if b[0]>1.15)
        for b in sorted(bad,reverse=True)[:4]:
            print("  p%02d 比=%.2f 需%.0fpt/框%.0fpt [%s] %s"%(sl['idx'],b[0],b[1],b[2],b[3][:14],b[4]))
print("  严重溢出(>1.15)文本框数:",tot)
