import json, io
D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.loads(io.open(D + r"\preview\layout.json", "rb").read().decode("gbk", "replace"))


def flat(el, out=None):
    if out is None:
        out = []
    for e in el or []:
        out.append(e)
        if e.get("children"):
            flat(e["children"], out)
    return out


rows = []
for P in lay["pages"]:
    n = P["pageNo"]
    title = ""
    sec = ""
    tx = [e for e in flat(P.get("elements")) if e.get("kind") == "text"]
    for e in tx:
        if e.get("id") == "hd_title":
            title = (e.get("text") or "").strip()
        if e.get("id") == "hd_sec":
            sec = (e.get("text") or "").strip()
    if not title:
        best = None
        for e in tx:
            st = e.get("style") or {}
            fs = st.get("fontSize") or 0
            if fs >= 26 and (best is None or fs > best[0]):
                best = (fs, (e.get("text") or "").strip())
        if best:
            title = "[" + "no header" + "] " + best[1]
    rows.append((n, sec, title))

io.open(r"D:\Resources\DSH\_probe\va_pageindex2.txt", "w", encoding="utf-8").write(
    "\n".join("p%-3d | %-26s | %s" % (n, s, t) for n, s, t in rows))
print("written", len(rows))
