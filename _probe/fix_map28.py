# -*- coding: utf-8 -*-
"""P0 修复：p28（emit id p26_map）原本直接嵌入 media/image19.jpg —— 一张第三方
思维导图软件的窗口截图（macOS 红黄蓝圆点 / 7:07 时钟 / 撤销重做缩放工具条 /
品牌图标），对参赛课件的「原创性」是直接反证，且窗口小字投屏不可读。
改为用原生矢量元素重绘知识导图（圆角矩形 + 正交连线 + 本册环节色）。
"""
import io, re, sys

P = r"D:\Resources\DSH\decks\单元思考与行动-参赛版\_tools\build.py"
src = io.open(P, encoding="utf-8").read()

OLD = '''body = [
    Img("map", [L, 122, 452, 280], "media/image19.jpg", "contain"),
    T("mapt", [L, 406, CW, 20],
      "找找今天用上了哪些——把说过的话放回这张图，知识连成网才记得住、用得上。",
      14, c1, KAI, width=CW),
]'''

assert OLD in src, "anchor not found"

NEW = '''# 知识导图：原生矢量重绘（替代原第三方软件窗口截图 —— 参赛原创性硬伤）
body = []
_MM = [
    ("新的历史方位", "社会主要矛盾的变化", "进入新时代的意义", GOLD),
    ("新时代的思想旗帜", "系统科学的理论体系", "必须长期坚持的指导思想", CYAN),
    ("中国腾飞谱新篇", "经济实力大幅跃升（经济）", "民主政治不断发展（政治）", CORAL),
    ("五位一体总体布局", "文化建设·社会建设", "生态文明建设（生态）", LAV),
]
_MMY = [128, 190, 252, 314]
body.append(S("mm_root", [L, 222, 96, 44], "roundRect",
              {"type": "solid", "color": INK}, None))
body.append(T("mm_root_t", [L, 233, 96, 22], "进入新时代", 14, "#FFFFFF", HEI,
              bold=True, align="center", width=96))
body.append(Ln("mm_bush", [[L + 96, 244], [L + 101, 244]], DIM, 1.2))
body.append(Ln("mm_busv", [[L + 101, 141], [L + 101, 327]], DIM, 1.2))
for _i, (_n, _s1, _s2, _col) in enumerate(_MM):
    _y = _MMY[_i]
    body.append(Ln("mm_l%d" % _i, [[L + 101, _y + 13], [150, _y + 13]], _col, 1.4))
    body.append(S("mm_b%d" % _i, [150, _y, 122, 26], "roundRect",
                  grad(_col, _col, 90, 30), {"color": _col, "width": 1.0}))
    body.append(T("mm_bt%d" % _i, [150, _y + 4, 122, 18], _n, 12.5, _col, HEI,
                  bold=True, align="center", width=122))
    body.append(Ln("mm_s%d" % _i, [[272, _y + 13], [288, _y + 13]], _col, 1.2))
    body.append(S("mm_s1%d" % _i, [288, _y - 1, 200, 21], "roundRect",
                  grad(_col, _col, 90, 14), {"color": _col, "width": 0.75}))
    body.append(T("mm_s1t%d" % _i, [294, _y + 2, 188, 16], _s1, 11.5, DIM, KAI,
                  width=188))
    body.append(S("mm_s2%d" % _i, [288, _y + 24, 200, 21], "roundRect",
                  grad(_col, _col, 90, 14), {"color": _col, "width": 0.75}))
    body.append(T("mm_s2t%d" % _i, [294, _y + 27, 188, 16], _s2, 11.5, DIM, KAI,
                  width=188))
body.append(T("mapt", [L, 406, CW, 20],
              "找找今天用上了哪些——把说过的话放回这张图，知识连成网才记得住、用得上。",
              14, c1, KAI, width=CW))'''

src = src.replace(OLD, NEW)

# 图片来源行也要改（不再是第三方素材）
src = src.replace('src="图片来源：本课原稿素材（《进入新时代》单元知识导图）"',
                  'src="知识导图：本课按《进入新时代》单元结构自绘"')

io.open(P, "w", encoding="utf-8").write(src)

# 常量名核对
for n in ("GOLD", "CYAN", "CORAL", "LAV", "INK", "DIM", "grad", "Ln"):
    print("  %-6s 定义/引用 = %s" % (n, ("有" if re.search(r"\b%s\b" % n, src) else "缺失")))
print("[OK] build.py patched")
