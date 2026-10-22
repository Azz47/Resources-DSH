# -*- coding: utf-8 -*-
"""声明由几何自证：在 build.py 的 emit() 里自动推导「承载关系」并写入 expectedOverlaps。
规则：文本框完全落在某个形状（面板/胶囊/色块）之内 → 该对是「面板→文字」的设计意图承载，
      属于可声明重叠（内容互压不在此列，因为互压是文本之间）。
这样声明随页面一起生成，重建永不丢失，也不需要外挂 JSON。
"""
import io, os

B = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
src = io.open(B, encoding="utf-8").read()

# 之前接的 JSON 查表改掉
OLD = ('    if not decl:\n'
       '        decl = _DECL.get(name)          # 声明固化在 _tools/overlaps.json（页面 yaml 是生成物）\n'
       '    if decl:\n'
       '        pg["expectedOverlaps"] = decl\n')
NEW = ('    if not decl:\n'
       '        # 承载关系自证：文本框完整落在某个形状内 = 面板/胶囊→文字的刻意叠层，\n'
       '        # 写入 expectedOverlaps 后审阅会判「✓ 预期重叠」；文本互压不在此列。\n'
       '        _d = []\n'
       '        for _a in els:\n'
       '            if _a.get("elementType") != "shape":\n'
       '                continue\n'
       '            _ab = _a.get("bounds") or []\n'
       '            if len(_ab) != 4:\n'
       '                continue\n'
       '            for _b in els:\n'
       '                if _b.get("elementType") != "text":\n'
       '                    continue\n'
       '                _bb = _b.get("bounds") or []\n'
       '                if len(_bb) != 4:\n'
       '                    continue\n'
       '                if (_bb[0] >= _ab[0] - 2 and _bb[1] >= _ab[1] - 2 and\n'
       '                        _bb[0] + _bb[2] <= _ab[0] + _ab[2] + 2 and\n'
       '                        _bb[1] + _bb[3] <= _ab[1] + _ab[3] + 2):\n'
       '                    _d.append([_a["elementId"], _b["elementId"]])\n'
       '        decl = _d or None\n'
       '    if decl:\n'
       '        pg["expectedOverlaps"] = decl\n')

assert OLD in src, "emit anchor not found"
src = src.replace(OLD, NEW, 1)

# 卸载 JSON loader（已不需要）
i = src.find("_DECL = {}")
if i != -1:
    j = src.find("OUT = os.path.abspath(", i)
    src = src[:i] + src[j:]
    print("[OK] 已卸载 overlaps.json 查表")

io.open(B, "w", encoding="utf-8").write(src)
print("[OK] emit() 现在是几何自证声明")
print("     _DECL 残留 = %s" % ("有" if "_DECL" in src else "无"))
print("     承载自证块 = %s" % ("有" if 'for _a in els:' in src else "无"))
