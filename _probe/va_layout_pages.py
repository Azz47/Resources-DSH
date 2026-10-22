import json,io,collections
D=r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay=json.loads(io.open(D+r"\preview\layout.json","rb").read().decode("gbk","replace"))
def flat(el,out=None):
    if out is None: out=[]
    for e in el or []:
        out.append(e)
        if e.get("children"): flat(e["children"],out)
    return out
TARGET={27,28,30,33,36,41,44}
out=[]
for P in lay["pages"]:
    n=P["pageNo"]
    if n not in TARGET: continue
    out.append("=========== p%d  %s ==========="%(n,P.get("name")))
    els=[e for e in flat(P.get("elements"))]
    els.sort(key=lambda e:(round(e.get("bounds",{}).get("y",0)),e.get("bounds",{}).get("x",0)))
    for e in els:
        b=e.get("bounds") or {}
        t=(e.get("text") or "").strip().replace("\n","/")[:26]
        st=e.get("style") or {}
        out.append("  %-13s %-6s x=%6.1f y=%6.1f w=%6.1f h=%5.1f r=%6.1f %s%s %s"%(
            e.get("id"),e.get("kind"),b.get("x",0),b.get("y",0),b.get("w",0),b.get("h",0),
            b.get("x",0)+b.get("w",0),
            ("%gpt "%st["fontSize"]) if st.get("fontSize") else "",
            ("F"+str(st.get("fill"))+" ") if st.get("fill") else "",
            t))
json.dump(1,io.open(r"D:\Resources\DSH\_probe\_x.json","w"))
io.open(r"D:\Resources\DSH\_probe\va_layout_pages.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
