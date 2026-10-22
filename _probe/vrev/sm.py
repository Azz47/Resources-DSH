import json, collections
for lbl, p in (("OURS","ours.json"),("FRIEND","friend.json")):
    d=json.load(open(rf"D:\Resources\DSH\_probe\vrev\{p}",encoding="utf-8"))
    c=collections.Counter(); n=0
    for pg in d["pages"]:
        for s in pg["shapes"]:
            if s.get("kind")!="text": continue
            for z in (s.get("sizes") or []):
                c[z]+=1
                if z<18: n+=1
                if z<15: n+=1
    tot=sum(c.values())
    print(f"{lbl}: run总={tot}  <18pt={sum(v for k,v in c.items() if k<18)} ({sum(v for k,v in c.items() if k<18)/tot:.1%})  <15pt={sum(v for k,v in c.items() if k<15)} ({sum(v for k,v in c.items() if k<15)/tot:.1%})")
    print("   全部字号:", ", ".join(f"{k}pt×{v}" for k,v in sorted(c.items(), reverse=True)))
