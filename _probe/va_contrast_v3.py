import json,io,collections,os
from PIL import Image
D=r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay=json.loads(io.open(D+r"\preview\layout.json","rb").read().decode("gbk","replace"))
def lum(c):
    def f(x):
        x=x/255.0
        return x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4
    return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])
def cr(a,b):
    la,lb=lum(a),lum(b); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def hx(c): return "#%02X%02X%02X"%c
def pc(s):
    if isinstance(s,str) and len(s)==7 and s[0]=="#":
        return tuple(int(s[i:i+2],16) for i in (1,3,5))
    return None
def flat(el,out=None):
    if out is None: out=[]
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"],out)
    return out
# 背景候选：整页众数色（=该页真正的大面积底）；以及元素四周环
PAGEBG={}
for P in lay["pages"]:
    n=P["pageNo"]
    im=Image.open(D+r"\preview\shots\%02d.png"%n).convert("RGB"); px=im.load()
    c=collections.Counter(px[x,y] for y in range(0,540,4) for x in range(0,960,4))
    PAGEBG[n]=c.most_common(3)
out=[]
out.append("=== 每页全局底色候选（前3）===")
for n in sorted(PAGEBG):
    out.append("  p%-3d %s"%(n,[(hx(c),v) for c,v in PAGEBG[n]]))
out.append("")
out.append("=== 元素级对比度（底=框内众数；若框内众数=字色占比最高，则改用页面前3底色中与字色对比最低者）===")
rows=[]
for P in lay["pages"]:
    n=P["pageNo"]
    im=Image.open(D+r"\preview\shots\%02d.png"%n).convert("RGB"); px=im.load()
    for e in flat(P.get("elements")):
        if e.get("kind")!="text": continue
        t=(e.get("text") or "").strip()
        if not t: continue
        st=e.get("style") or {}; b=e.get("bounds") or {}
        fg=pc(st.get("color"))
        if fg is None: continue
        x0,y0=max(0,int(b.get("x",0))),max(0,int(b.get("y",0)))
        x1,y1=min(960,int(b.get("x",0)+b.get("w",0))),min(540,int(b.get("y",0)+b.get("h",0)))
        reg=[px[x,y] for y in range(y0,y1) for x in range(x0,x1)]
        if len(reg)<30: continue
        cnt=collections.Counter(reg); modal=cnt.most_common(1)[0][0]
        cands=[modal]
        if cr(fg,modal)<2.0:   # 众数色≈字色 → 换底
            cands=[c for c,_ in PAGEBG[n]]
        best=None
        for c in cands:
            r=cr(fg,c)
            if best is None or r<best[0]: best=(r,c)
        r,bg=best
        fs=st.get("fontSize") or 0
        big=(fs>=18) or (fs>=14 and st.get("bold"))
        need=3.0 if big else 4.5
        rows.append({"n":n,"id":e.get("id"),"fs":fs,"bold":bool(st.get("bold")),
                     "fg":hx(fg),"bg":hx(bg),"r":round(r,2),"need":need,"txt":t.replace("\n","/")[:22]})
fail=[r for r in rows if r["r"]<r["need"]]
out.append("文本 %d 个；未达 AA = %d"%(len(rows),len(fail)))
out.append("")
out.append("--- 未达 AA 明细 ---")
for r in sorted(fail,key=lambda r:r["r"]):
    out.append("  p%-3d %-14s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f≥%.1f 「%s」"%(r["n"],r["id"],r["fs"],"粗" if r["bold"] else "",r["fg"],r["bg"],r["r"],r["need"],r["txt"]))
out.append("")
out.append("--- 通过但 <6.0（投影边缘，建议提亮/加深）---")
for r in sorted([r for r in rows if r["need"]<=r["r"]<6.0],key=lambda r:r["r"]):
    out.append("  p%-3d %-14s %2dpt%-3s 字%-8s 底%-8s 比=%5.2f 「%s」"%(r["n"],r["id"],r["fs"],"粗" if r["bold"] else "",r["fg"],r["bg"],r["r"],r["txt"]))
io.open(r"D:\Resources\DSH\_probe\va_contrast_v3.txt","w",encoding="utf-8").write("\n".join(out))
json.dump(rows,io.open(r"D:\Resources\DSH\_probe\va_contrast_v3.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
