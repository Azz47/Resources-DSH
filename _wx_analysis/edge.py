import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
MED=r'D:\Resources\DSH\_wx_analysis\media'
im=Image.open(os.path.join(MED,'image3.jpeg')).convert('RGB')
W,H=im.size
col=[im.getpixel((W//2,y)) for y in range(H)]
def grn(p): return abs(p[0]-59)<25 and abs(p[1]-86)<25 and abs(p[2]-67)<25
ys=[y for y,p in enumerate(col) if grn(p)]
print("image3 green rows:", ys[0], "..", ys[-1] if ys else None, " groups:")
prev=None; segs=[]
for y in ys:
    if prev is None or y!=prev+1: segs.append([y,y])
    else: segs[-1][1]=y
    prev=y
print("  segments:",[(a,round(a/H*100,1),b,round(b/H*100,1)) for a,b in segs])
print("  body color at center:", col[H//2], " top band:", col[40], " at 12%:", col[int(H*0.12)])
print()
R=r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_probe\friend_render"
print("== 每页：贴边墨迹（右/下）与内容包围盒 ==")
def inkrow(px): return any(abs(p[0]-242)>18 or abs(p[1]-242)>18 or abs(p[2]-242)>18 for p in px)
for i in range(1,41):
    im=Image.open(os.path.join(R,'page-%04d.png'%i)).convert('RGB'); W,H=im.size
    # ignore the background's own green bands when judging: only look at body region y>0.20H
    body_top=int(H*0.21)
    right=[im.getpixel((W-2,y)) for y in range(body_top,H-2)]
    bot =[im.getpixel((x,H-2)) for x in range(2,W-2)]
    rin = sum(1 for p in right if inkrow([p]))
    bin_= sum(1 for p in bot if inkrow([p]))
    # content bbox inside body
    px=im.load()
    minx,maxx,miny,maxy=W,0,H,0
    step=4
    for y in range(body_top,H-2,step):
        for x in range(2,W-2,step):
            p=px[x,y]
            if abs(p[0]-242)>18 or abs(p[1]-242)>18 or abs(p[2]-242)>18:
                if x<minx:minx=x
                if x>maxx:maxx=x
                if y<miny:miny=y
                if y>maxy:maxy=y
    print("  p%02d 右贴边=%3d/%d 下贴边=%3d/%d  内容bbox x[%.3f,%.3f] y[%.3f,%.3f] 覆盖率=%.3f"%(
        i,rin,len(right),bin_,len(bot), minx/W,maxx/W, miny/H,maxy/H,
        ((maxx-minx)*(maxy-miny))/(W*H) if maxx>minx else 0))
