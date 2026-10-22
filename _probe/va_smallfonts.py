import json,io,collections
D=r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay=json.loads(io.open(D+r"\preview\layout.json","rb").read().decode("gbk","replace"))
def flat(el,out=None):
    if out is None: out=[]
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"],out)
    return out
out=[]
out.append("=== <14pt 的 103 个文本元素：按元素名归因 ===")
names=collections.Counter(); pages=collections.defaultdict(set)
detail=[]
for P in lay["pages"]:
    n=P["pageNo"]
    for e in flat(P.get("elements")):
        if e.get("kind")!="text": continue
        t=(e.get("text") or "").strip()
        if not t: continue
        st=e.get("style") or {}; fs=st.get("fontSize")
        if fs is None or fs>=14: continue
        names[(fs,e.get("id"))]+=1; pages[e.get("id")].add(n)
        detail.append((n,e.get("id"),fs,len(t),t.replace("\n","/")[:44]))
agg=collections.Counter()
for (fs,i),c in names.items(): agg[fs]+=c
out.append("  12pt 元素名分布: %s"%[(i,c) for (fs,i),c in sorted(names.items()) if fs==12])
out.append("  13pt 元素名分布: %s"%[(i,c) for (fs,i),c in sorted(names.items()) if fs==13])
out.append("")
out.append("=== 非页眉/页脚类的 <14pt 内容元素（真正需要提级的）===")
STRUCT={"hd_info","hd_num","hd_sec","sn"}
for n,i,fs,L,t in detail:
    if i in STRUCT: continue
    out.append("  p%-3d %-12s %2dpt %2d字 「%s」"%(n,i,fs,L,t))
cnt=len([d for d in detail if d[1] not in STRUCT])
out.append("")
out.append("  非结构类 <14pt 元素合计 = %d 个；结构类 = %d 个（hd_info %d / hd_num %d / hd_sec %d / sn %d）"%(
    cnt, len(detail)-cnt,
    sum(1 for d in detail if d[1]=="hd_info"),
    sum(1 for d in detail if d[1]=="hd_num"),
    sum(1 for d in detail if d[1]=="hd_sec"),
    sum(1 for d in detail if d[1]=="sn")))
io.open(r"D:\Resources\DSH\_probe\va_smallfonts.txt","w",encoding="utf-8").write("\n".join(out))
