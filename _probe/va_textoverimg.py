import json, io

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
lay = json.loads(io.open(D + r"\preview\layout.json", "rb").read().decode("gbk", "replace"))


def fl(el, o=None):
    o = [] if o is None else o
    for e in el or []:
        o.append(e)
        if e.get("children"):
            fl(e["children"], o)
    return o


r = []
for P in lay["pages"]:
    n = P["pageNo"]
    E = fl(P.get("elements"))
    imgs = [e for e in E if e.get("kind") == "image"]
    if not imgs:
        continue
    for im in imgs:
        b = im.get("bounds") or {}
        x0, y0, w0, h0 = b.get("x", 0), b.get("y", 0), b.get("w", 0), b.get("h", 0)
        hits = []
        for e in E:
            if e.get("kind") not in ("text", "table", "chart"):
                continue
            c = e.get("bounds") or {}
            ix = max(0, min(x0 + w0, c.get("x", 0) + c.get("w", 0)) - max(x0, c.get("x", 0)))
            iy = max(0, min(y0 + h0, c.get("y", 0) + c.get("h", 0)) - max(y0, c.get("y", 0)))
            if ix * iy > 4:
                hits.append("%s(%.0f,%.0f,%.0fx%.0f)" % (e.get("id"), c.get("x", 0), c.get("y", 0), c.get("w", 0), c.get("h", 0)))
        r.append("p%-3d %-8s img(%.0f,%.0f,%.0fx%.0f)  交集元素=%d  %s" % (
            n, im.get("id"), x0, y0, w0, h0, len(hits), ", ".join(hits[:8])))

io.open(r"D:\Resources\DSH\_probe\va_textoverimg.txt", "w", encoding="utf-8").write("\n".join(r))
print("written", len(r))
