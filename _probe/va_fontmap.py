import json,io,collections
D=r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay=json.loads(io.open(D+r"\preview\layout.json","rb").read().decode("gbk","replace"))
def flat(el,out=None):
    if out is None: out=[]
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"],out)
    return out
buckets=collections.defaultdict(list)
for P in lay["pages"]:
    n=P["pageNo"]
    for e in flat(P.get("elements")):
        if e.get("kind")!="text": continue
        t=(e.get("text") or "").strip()
        if not t: continue
        st=e.get("style") or {}
        fs=st.get("fontSize")
        if fs is None: continue
        buckets[fs].append((n,e.get("id"),t,st.get("bold"),len(t)))
out=[]
out.append("=== 各字号用途画像（判定 14-24pt 约束的适用面）===")
for fs in sorted(buckets):
    v=buckets[fs]
    lens=[x[4] for x in v]
    ids=collections.Counter(x[1] for x in v)
    out.append("")
    out.append("--- %spt  共 %d 个  平均字数 %.1f  最长 %d ---"%(fs,len(v),sum(lens)/len(lens),max(lens)))
    out.append("    元素名TOP: %s"%ids.most_common(8))
    for n,i,t,b,L in v[:8]:
        out.append("    p%-3d %-14s %-3s %2d字 「%s」"%(n,i,"粗" if b else "",L,t.replace("\n","/")[:38]))
io.open(r"D:\Resources\DSH\_probe\va_fontmap.txt","w",encoding="utf-8").write("\n".join(out))
