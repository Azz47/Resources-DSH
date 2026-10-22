import json,io,collections
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
out=[]
# 1) 空白字形元素（ratio=1.00）探测：框内"与框内众数色明显不同的像素"占比
probe=[(1,"cv_r1a"),(12,"i3b"),(14,"qb3"),(17,"spq0"),(17,"spq1"),(20,"n2t0"),(20,"n2b0"),(25,"Db2"),
       (26,"Eb1"),(27,"k_tg0"),(27,"k_bb1"),(32,"qm"),(33,"dxc0"),(36,"Rt2"),(39,"sbRb"),(39,"sbbar_t"),
       (41,"pjb1"),(43,"sub0"),(44,"lvt0"),(45,"sct0"),(7,"fc0_b"),(41,"pjb0"),(41,"pjb3")]
byid={}
for P in lay["pages"]:
    for e in P["elements"]:
        byid.setdefault((P["pageNo"],e.get("id")),e)
out.append("=== 空白字形元素复核（框内非底色像素占比）===")
for n,eid in probe:
    e=byid.get((n,eid))
    if not e: out.append("p%-3d %-10s 未找到"%(n,eid)); continue
    st=e.get("style") or {}; b=e["bounds"]
    im=Image.open(D+r"\preview\shots\%02d.png"%n).convert("RGB"); px=im.load()
    x0,y0,x1,y1=int(b["x"]),int(b["y"]),int(b["x"]+b["w"]),int(b["y"]+b["h"])
    reg=[px[x,y] for y in range(max(0,y0),min(540,y1)) for x in range(max(0,x0),min(960,x1))]
    cnt=collections.Counter(reg); modal=cnt.most_common(1)[0][0]
    ink=sum(v for c,v in cnt.items() if abs(lum(c)-lum(modal))>0.05)
    out.append("p%-3d %-10s %2spt 声明%-8s 众数%s(%d) 非底色像素=%d/%d (%.1f%%) 文本=%r"%(
        n,eid,st.get("fontSize"),st.get("color"),hx(modal),cnt.most_common(1)[0][1],ink,len(reg),
        ink*100.0/max(1,len(reg)),(e.get("text") or "")[:18]))
out.append("")
out.append("=== 页眉/页脚固定件 声明色 vs 实拍底色 ===")
for n in (2,10,16,20,28,33,40,45):
    for eid in ("hd_info","hd_num","sn"):
        e=byid.get((n,eid))
        if not e: continue
        st=e.get("style") or {}; b=e["bounds"]
        im=Image.open(D+r"\preview\shots\%02d.png"%n).convert("RGB"); px=im.load()
        # 只取框内偏上 2/3，避开下方其它元素
        x0,y0=int(b["x"]),int(b["y"]); x1,y1=int(b["x"]+b["w"]),int(b["y"]+b["h"])
        reg=[px[x,y] for y in range(max(0,y0),min(540,y1)) for x in range(max(0,x0),min(960,x1))]
        cnt=collections.Counter(reg)
        bg=cnt.most_common(1)[0][0]
        fg=pc(st.get("color"))
        r=cr(fg,bg) if fg else None
        out.append("p%-3d %-8s %2spt%-3s 声明字%-8s 众数底%-8s 比=%s  文本=%r"%(
            n,eid,st.get("fontSize"),"粗" if st.get("bold") else "",st.get("color"),hx(bg),
            ("%.2f"%r) if r else "-",(e.get("text") or "")[:26]))
io.open(r"D:\Resources\DSH\_probe\va_blank.txt","w",encoding="utf-8").write("\n".join(out))
