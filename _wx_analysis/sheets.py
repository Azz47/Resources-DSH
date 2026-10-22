import sys, os, json, math
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
R=r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_probe\friend_render"
OUT=r"D:\Resources\DSH\_wx_analysis"
d=json.load(open(r'D:\Resources\DSH\_wx_analysis\wx_dump.json',encoding='utf-8'))
# ---- contact sheets 4x2 ----
os.makedirs(os.path.join(OUT,'sheets'),exist_ok=True)
CW,CH=470,264; cols,rows=4,2; pad=8
for s in range(0,40,8):
    sheet=Image.new('RGB',(cols*CW+ (cols+1)*pad, rows*CH + (rows+1)*pad + 18*rows),'#202020')
    dr=ImageDraw.Draw(sheet)
    for k in range(8):
        idx=s+k
        if idx>=40: break
        im=Image.open(os.path.join(R,'page-%04d.png'%(idx+1))).convert('RGB').resize((CW,CH))
        r,c=divmod(k,cols)
        x=pad+c*(CW+pad); y=pad+r*(CH+pad+18)
        sheet.paste(im,(x,y)); dr.text((x+3,y+CH+3),"P%02d"%(idx+1),fill='#ffcc00')
    p=os.path.join(OUT,'sheets','sheet-%02d-%02d.png'%(s+1,min(s+8,40)))
    sheet.save(p); print("sheet",p, sheet.size)
# ---- seam metric ----
def mean(im,box):
    c=im.crop(box); px=list(c.getdata()); n=len(px)
    return tuple(sum(v[i] for v in px)/n for i in range(3))
print("\n== 图片-背景 接缝度量 (越亮/越彩色=越像贴图) ==")
def flat(ss):
    for sh in ss:
        yield sh
        for c in sh.get('children',[]) or []: yield from flat([c])
res=[]
for sl in d['slides']:
    idx=sl['idx']
    pics=[s for s in flat(sl['shapes']) if s.get('img')]
    if not pics: continue
    im=Image.open(os.path.join(R,'page-%04d.png'%idx)).convert('RGB')
    W,H=im.size
    for p in pics:
        sx=W/960.0; sy=H/540.0
        L=int(p['left']*sx); T=int(p['top']*sy); Rt=int((p['left']+p['w'])*sx); B=int((p['top']+p['h'])*sy)
        if L<3 or T<3 or Rt>W-3 or B>H-3: 
            res.append((idx,p['img']['sha'],p['w'],p['h'],None,None,None)); continue
        W_=Rt-L; H_=B-T
        outer=[(L-6,T-6,L,T),(L-6,B,Rt-6,B+6),(L-6,T-6,L+6,B),(Rt-6,T-6,Rt,min(B+6,H))]  # left,top,right,bottom rings outside
        inner=[(L+3,T+3,L+9,B-3),(L+3,T+3,Rt-3,T+9),(Rt-9,T+3,Rt-3,B-3),(L+3,B-9,Rt-3,B-3)]
        def ring(boxes):
            tot=[0,0,0]; n=0
            for b in boxes:
                c=im.crop(b); px=list(c.getdata())
                for v in px:
                    tot[0]+=v[0]; tot[1]+=v[1]; tot[2]+=v[2]; n+=1
            return tuple(t/n for t in tot) if n else None
        o=ring(outer); i=ring(inner)
        if o and i:
            dl=math.dist(o,i)
            # aspect distortion
            ow,oh=p['img']['px']
            target=p['w']/p['h']; orig=ow/oh
            dist=abs(target-orig)/orig*100
            res.append((idx,p['img']['sha'],round(p['w'],1),round(p['h'],1),round(dist,1),round(dl,1),"%.0f,%.0f,%.0f / %.0f,%.0f,%.0f"%(o+i)))
        else:
            res.append((idx,p['img']['sha'],round(p['w'],1),round(p['h'],1),"offscreen",None,None))
for r in sorted(res):
    print("  p%02d %s %sx%s 比例失真=%s%% 接缝Δ=%s  %s"%(r[0],r[1],r[2],r[3],r[4],r[5],r[6]))
