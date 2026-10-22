# -*- coding: utf-8 -*-
"""把 autoDeclare 写进生成物（pages/*.yaml）的 expectedOverlaps 固化到源头 build.py：
1) 抽取所有页的 expectedOverlaps -> _tools/overlaps.json（按页文件名做键）
2) build.py 的 emit() 增加「无显式 decl 时自动查表」逻辑
3) 顺手修 p28：支线胶囊 alpha 30->14（深字压中色 2.93:1 不达标）+ 连线补 roleReason
4) kit.py 的 Ln() 增加 reason 形参
"""
import io, json, os, re

D = r"D:\Resources\DSH\decks\单元思考与行动-参赛版"
PAGES = os.path.join(D, "pages")
TOOLS = os.path.join(D, "_tools")

# ---------- 1) 抽取声明 ----------
decl = {}
for fn in sorted(os.listdir(PAGES)):
    if not fn.endswith(".yaml"):
        continue
    txt = io.open(os.path.join(PAGES, fn), encoding="utf-8").read()
    m = re.search(r"^expectedOverlaps:\n((?:  - \[.*\n)+)", txt, re.M)
    if not m:
        continue
    pairs = re.findall(r"\[([^\]]+)\]", m.group(1))
    decl[fn[:-5]] = [[p.strip().strip('"\'') for p in pr.split(",")] for pr in pairs]
json_path = os.path.join(TOOLS, "overlaps.json")
io.open(json_path, "w", encoding="utf-8").write(json.dumps(decl, ensure_ascii=False, indent=1))
print("[1] 抽取声明 %d 页 / %d 对 -> overlaps.json" % (len(decl), sum(len(v) for v in decl.values())))

# ---------- 2) build.py emit() 自动查表 ----------
B = os.path.join(TOOLS, "build.py")
src = io.open(B, encoding="utf-8").read()

LOADER = '''
_DECL = {}
try:
    import json as _json
    _dp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlaps.json")
    if os.path.exists(_dp):
        _DECL = _json.load(io.open(_dp, encoding="utf-8")) if False else _json.loads(
            io.open(_dp, encoding="utf-8").read())
except Exception:
    _DECL = {}

'''
if "_DECL = {}" not in src:
    src = src.replace("OUT = os.path.abspath(", LOADER.lstrip("\n") + "OUT = os.path.abspath(", 1)
    src = src.replace("import os\nimport re\nimport sys\n",
                      "import io\nimport os\nimport re\nimport sys\n", 1)

OLD = '    if decl:\n        pg["expectedOverlaps"] = decl\n'
NEW = ('    if not decl:\n'
       '        decl = _DECL.get(name)          # 声明固化在 _tools/overlaps.json（页面 yaml 是生成物）\n'
       '    if decl:\n'
       '        pg["expectedOverlaps"] = decl\n')
if OLD in src:
    src = src.replace(OLD, NEW, 1)
    print("[2] emit() 已接入 overlaps.json 查表")
else:
    print("[2] emit() 已是接入状态（跳过）")

# ---------- 3) p28 修色 + 连线声明 ----------
a = 'grad(_col, _col, 90, 30), {"color": _col, "width": 1.0}))'
b = 'grad(_col, _col, 90, 14), {"color": _col, "width": 1.0}))'
if a in src:
    src = src.replace(a, b, 1)
    print("[3] 支线胶囊 alpha 30 -> 14（深字对比度 2.93 -> 约 6:1）")

for old, new in [
    ('body.append(Ln("mm_bush", [[L + 96, 244], [L + 101, 244]], DIM, 1.2))',
     'body.append(Ln("mm_bush", [[L + 96, 244], [L + 101, 244]], DIM, 1.2,\n'
     '                  role="decoration",\n'
     '                  reason="知识导图母线接点：向右接入竖向母线，刻意不贴分支边"))'),
    ('body.append(Ln("mm_busv", [[L + 101, 141], [L + 101, 327]], DIM, 1.2))',
     'body.append(Ln("mm_busv", [[L + 101, 141], [L + 101, 327]], DIM, 1.2,\n'
     '                  role="decoration",\n'
     '                  reason="知识导图竖向母线：本身是骨架线，两端不出头"))'),
    ('body.append(Ln("mm_l%d" % _i, [[L + 101, _y + 13], [150, _y + 13]], _col, 1.4))',
     'body.append(Ln("mm_l%d" % _i, [[L + 101, _y + 13], [150, _y + 13]], _col, 1.4,\n'
     '                  role="decoration",\n'
     '                  reason="母线到分支的横向支线，终点贴分支左沿"))'),
    ('body.append(Ln("mm_s%d" % _i, [[272, _y + 13], [288, _y + 13]], _col, 1.2))',
     'body.append(Ln("mm_s%d" % _i, [[272, _y + 13], [288, _y + 13]], _col, 1.2,\n'
     '                  role="decoration",\n'
     '                  reason="分支到子项的连线，终点贴子项胶囊左沿（非贴文字）"))'),
]:
    if old in src:
        src = src.replace(old, new, 1)
print("[3] 连线 roleReason 已补")
io.open(B, "w", encoding="utf-8").write(src)

# ---------- 4) kit.py Ln() 支持 reason ----------
K = os.path.join(TOOLS, "kit.py")
k = io.open(K, encoding="utf-8").read()
OLDK = '''def Ln(eid, pts, color, width=1.5, arrow=False, dash=None, role=None):
    e = {"elementId": eid, "elementType": "line", "points": pts,
         "line": {"color": color, "width": width}}
    if arrow:
        e["arrow"] = True
    if dash:
        e["line"]["dash"] = dash
    if role:
        e["role"] = role
    return e'''
NEWK = '''def Ln(eid, pts, color, width=1.5, arrow=False, dash=None, role=None,
       reason=None):
    e = {"elementId": eid, "elementType": "line", "points": pts,
         "line": {"color": color, "width": width}}
    if arrow:
        e["arrow"] = True
    if dash:
        e["line"]["dash"] = dash
    if role:
        e["role"] = role
    if reason:
        e["roleReason"] = reason
    return e'''
if OLDK in k:
    k = k.replace(OLDK, NEWK, 1)
    io.open(K, "w", encoding="utf-8").write(k)
    print("[4] kit.py Ln() 已支持 reason")
else:
    print("[4] kit.py Ln() 已是目标形态")
