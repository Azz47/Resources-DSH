import json,io,collections,os
from PIL import Image
D=r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay=json.loads(io.open(D+r"\preview\layout.json","rb").read().decode("gbk","replace"))
def lum(c):
    def f(x):
        x=x/255.0
        return x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4
    return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])
out=[]
out.append("=== 各页元素类型盘点 ===")
kinds=collections.Counter()
imgpages={}
for P in lay["pages"]:
    n=P["pageNo"]
    for e in P["elements"]:
        kinds[e.get("kind")]+=1
        if e.get("kind")=="image":
            b=e["bounds"]
            imgpages.setdefault(n,[]).append((e.get("id"),round(b["x"]),round(b["y"]),round(b["w"]),round(b["h"]),(e.get("src") or e.get("href") or "")[-28:]))
out.append("  元素类型: %s"%kinds.most_common())
out.append("  含 image 元素的页: %d 页"%len(imgpages))
tot=0
for n,v in sorted(imgpages.items()):
    tot+=len(v)
    out.append("   p%-3d %d 张: %s"%(n,len(v),[(a,b,c,d,e,f) for a,b,c,d,e,f in v][:6]))
out.append("  图片元素合计 %d 张"%tot)
out.append("")
out.append("=== 图片元素框内的底色离散度（H3：文字/图形 与 背景图 是否打架）===")
for n,v in sorted(imgpages.items()):
    im=Image.open(D+r"\preview\shots\%02d.png"%n).convert("RGB"); px=im.load()
    for eid,x,y,w,h,s in v:
        reg=[px[xx,yy] for yy in range(max(0,y),min(540,y+h),3) for xx in range(max(0,x),min(960,x+w),3)]
        if len(reg)<40: continue
        Ls=[lum(c) for c in reg]
        mean=sum(Ls)/len(Ls)
        sd=(sum((v2-mean)**2 for v2 in Ls)/len(Ls))**0.5
        Ls.sort()
        out.append("   p%-3d %-10s 区域(%d,%d,%d,%d) 亮度sd=%.3f  P5=%.3f P95=%.3f 对比跨度=%.2f"%(
            n,eid,x,y,w,h,sd,Ls[int(len(Ls)*0.05)],Ls[int(len(Ls)*0.95)],
            (max(Ls)+0.05)/(min(Ls)+0.05)))
io.open(r"D:\Resources\DSH\_probe\va_images.txt","w",encoding="utf-8").write("\n".join(out))
