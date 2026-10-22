# -*- coding: utf-8 -*-
"""参赛版第二稿设计系统：**黑板 × 粉笔擦卡**。

口径（本文件是全册唯一取色/取字号的地方）：
- 底：沿用底稿的黑板照片（`media/image1.jpeg`，母版继承），版式母题取自源稿（双色块 + 渐隐横线）。
- 一切承载文字的面，一律坐在**不透明浅色卡**上 → 文字永不直接压在照片上（H3 达标）。
- 字号严格落在 **14–24 pt**（用户硬约束⑥）：标题 24 / 小节 18 / 卡标 17 / 正文 16 / 注 14。
- 内容走廊 x ∈ [44, 640]；右侧 1/3 只放**不承载信息**的装饰（竖分栏线 + 竖排标识 + 页码），
  中段 y 200–430 全空作讲师站位。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import kit  # noqa: E402
from kit import T, S, grad, Ln, Img, need_h, tw, wrap, justify  # noqa: E402

W, H = 960, 540
L, R, CW = 44, 640, 596
TOP, BOT, BOT_SAFE = 122, 470, 452
RB_X = 652                 # 右侧装饰带左缘
RB_TAGX = 866              # 右侧竖排标识左缘
RB_TAGW = 74               # 标识/页码宽

BOARD_SAFE = "#3A5542"     # 黑板板面实测中位色（仅作文档注释，元素不引用）
PANEL = "#E9EFE9"          # 冷调粉笔擦卡
PANEL_W = "#F0E8D8"        # 暖调粉笔擦卡（引文/人文页）
INK = "#1D2B23"            # 卡上主文本（vs #E9EFE9 ≈ 12.6:1）
SOFT = "#2E4438"           # 卡上次级文本（≈ 9.4:1）
MUTED = "#465C4D"          # 卡上三级文本（≈ 6.6:1）
CHALK = "#F4F8F4"          # 直接写在板上的标题（vs #3A5542 ≈ 8.0:1）
CHALK_DIM = "#BFD2C2"      # 板上级信息行（≈ 5.4:1）
CHALK_FAINT = "#A9C0AE"    # 板上来源注（≈ 4.6:1）
RULE = "#7E9A85"
SHADOW = "#0E1A12"

SZ_TITLE, SZ_SUB, SZ_CARD, SZ_BODY, SZ_SMALL = 24, 18, 17, 16, 14

SEC = {
    "intro": ("#7FD6B0", "#1F6B4F"),
    "s1":    ("#E8C15A", "#8A6A1E"),
    "s2":    ("#6FC7E8", "#1F6383"),
    "s3":    ("#EE8A72", "#8E3F2E"),
    "end":   ("#B9A7E8", "#584C86"),
}
SEC_LABEL = {
    "intro": "导引 · 从一次策展邀请开始",
    "s1":    "子任务一 · 观展选品——感悟新时代",
    "s2":    "子任务二 · 撰写解说——解码新成就",
    "s3":    "子任务三 · 拓展策展——循迹盐湖行",
    "end":   "收束 · 小结·评价·练习",
}
KAI, HEI = "楷体", "黑体"
KICKER = "九年级道德与法治（统编版）· 第二单元 进入新时代"
BG = '{"type": "image", "src": "media/image1.jpeg", "fit": "cover"}'

# 让 kit 的旧常量与取色表跟本文件保持一致（T() 会查 kit.DARK）
kit.L, kit.R, kit.CW = L, R, CW
kit.TOP, kit.BOT, kit.BOT_SAFE = TOP, BOT, BOT_SAFE
kit.PANEL, kit.CHALK, kit.SOFT, kit.DIM, kit.FAINT = PANEL, INK, SOFT, MUTED, MUTED
kit.SEC = SEC
kit.SEC_LABEL = SEC_LABEL
kit.DARK = {}   # 本稿是「深底黑板 + 浅卡」：不再把浅色强调色改写成同族深色，
                # 否则封面/页码这类直接写在板上的浅色文字会被改暗到看不见。

# 全局收紧文本度量 8%：引擎的换行比本模块保守，放宽后量画一致、不再出现"算得下、渲染却溢出"
_wch0 = kit.wch
kit.wch = lambda c: _wch0(c) * 1.08


# ------------------------------------------------------------------ 页面骨架
def rband(els, num, sec, total=42):
    """右侧 1/3 装饰带：竖分栏线 + 顶部小色块 + 竖排单元标识 + 页码。中段留空。"""
    c1, c2 = SEC[sec]
    els.append(Ln("rb_rule", [[RB_X, 112], [RB_X, 448]], RULE, 1.5))
    els.append(S("rb_chip_a", [648, 96, 12, 12], "rect", grad(c1, c2, 135),
                 role="decoration", reason="右侧分栏线顶端母题（呼应页眉双色块）"))
    els.append(S("rb_chip_b", [652, 120, 8, 8], "rect", c2,
                 role="decoration", reason="右侧分栏线顶端母题（小方块叠压）"))
    els.append(T("rb_tag1", [RB_TAGX, 128, RB_TAGW, 22], "第二单元", SZ_SMALL, CHALK_DIM, HEI,
                 align="center", width=RB_TAGW, wrap_on=True))
    els.append(T("rb_tag2", [RB_TAGX, 150, RB_TAGW, 22], "进入新时代", SZ_SMALL, CHALK_DIM, HEI,
                 align="center", width=RB_TAGW, wrap_on=True))
    els.append(Ln("rb_tagrule", [[RB_TAGX + 18, 178], [RB_TAGX + RB_TAGW - 18, 178]], RULE, 1))
    els.append(T("rb_num", [RB_TAGX, 190, RB_TAGW, 22], "%02d / %d" % (num, total), SZ_SMALL, c1,
                 HEI, bold=True, align="center", width=RB_TAGW, wrap_on=True))


def hd(els, sec, title, num, kicker=None, title_size=SZ_TITLE):
    """页眉（紧凑版）：环节色标药丸 + 24pt 板书标题 + 渐隐横线，收在 y≤92，正文从 100 起。

    黑板上沿 y≈23、下沿 y≈460：页眉越矮，正文可用带越高，卡片才不会落到木框上。
    """
    c1, c2 = SEC[sec]
    lab = SEC_LABEL[sec]
    pw = tw(lab, SZ_SMALL) + 44
    els.append(dict(S("hd_secbg", [L, 22, pw, 24], "roundRect", grad(PANEL, PANEL, 0, 96),
                      role="decoration", reason="环节标签衬底"),
                    contains=["hd_sec", "hd_secbar"]))
    els.append(S("hd_secbar", [L + 4, 25, 3.5, 18], "rect", grad(c2, c1, 90),
                 role="decoration", reason="环节标签左侧色标（母题）"))
    els.append(T("hd_sec", [L + 14, 25, pw - 22, 18], lab, SZ_SMALL, c2, HEI, bold=True,
                 width=pw - 22, wrap_on=True))
    els.append(T("hd_title", [L, 50, CW, 38], title, title_size, CHALK, HEI, bold=True, width=CW))
    els.append(S("hd_rule2", [L, 90, 128, 3.5], "rect", grad(c2, c1, 0)))
    els.append(S("hd_rule", [L + 134, 91.2, CW - 134, 1.5], "rect", {"color": c1, "alpha": 40}))


def page(sec, title, notes, num, kicker=None, title_size=SZ_TITLE):
    els = []
    hd(els, sec, title, num, kicker, title_size)
    rband(els, num, sec)
    return els, {"notes": notes}


# ------------------------------------------------------------------ 版式组件
def ecard(pid, x, y, w, h, accent, fill=None, pad=14):
    """粉笔擦卡：投影 + 不透明浅卡 + 左侧渐隐色边。返回垫底层元素列表。"""
    fill = fill or PANEL
    return [
        S(pid + "_sh", [x + 2, y + 4, w - 4, h], "roundRect", grad(SHADOW, SHADOW, 90, 52),
          role="decoration", reason="卡片接地投影（融合：卡片与板面之间加一层过渡）"),
        dict(S(pid, [x, y, w, h], "roundRect", fill, {"color": accent, "width": 1.25}),
             contains=[pid + "_le"]),
        S(pid + "_le", [x + 2, y + 9, 3.5, max(10, h - 18)], "rect",
          grad(accent, accent, 90, 0), role="decoration",
          reason="卡片左侧渐隐色边（母题）"),
    ]


def card2(pid, x, y, w, accent, title, body, tsize=SZ_CARD, bsize=SZ_BODY, pad=12,
          fill=None, min_h=0, title_color=None, body_color=None, align="left"):
    tw_ = w - 2 * pad
    th_ = need_h(title, tw_, tsize, 1.38) if title else 0
    bh_ = need_h(body, tw_, bsize, 1.42) if body else 0
    content = pad * 2 + th_ + (10 if title and body else 0) + bh_
    h = max(min_h, content)
    dy = (h - content) / 2.0 if h > content else 0.0
    els = ecard(pid, x, y, w, h, accent, fill, pad)
    if title:
        els[1]["contains"].append(pid + "_t")
    if body:
        els[1]["contains"].append(pid + "_b")
    cy = y + pad - 3 + dy
    if title:
        els.append(T(pid + "_t", [x + pad, cy, tw_, th_], title, tsize, title_color or accent,
                     HEI, bold=True, width=tw_, align=align))
        cy += th_ + 10
    if body:
        els.append(T(pid + "_b", [x + pad, cy, tw_, bh_], body, bsize,
                     body_color or SOFT, KAI, width=tw_, align=align))
    return els, h


def row2(spec, y, accent, x0=L, total=CW, gap=12, min_h=0, prefix="r", **kw):
    n = len(spec)
    w = (total - gap * (n - 1)) // n
    hs = []
    for i, (t, b) in enumerate(spec):
        _, h = card2("%sc%d" % (prefix, i), x0 + i * (w + gap), y, w, accent, t, b,
                     min_h=min_h, **kw)
        hs.append(h)
    h = max(hs) if hs else 0
    out = []
    for i, (t, b) in enumerate(spec):
        e, _ = card2("%sc%d" % (prefix, i), x0 + i * (w + gap), y, w, accent, t, b,
                     min_h=h, **kw)
        out.extend(e)
    return out, h


def bar2(eid, x, y, w, accent, text, size=SZ_BODY, fill=None, color=INK, pad=12, h=None,
         bold=False, align="left"):
    """横条：浅底 + 左侧书签色标；宽度内自动换行。"""
    fill = fill or PANEL
    if h is None:
        h = need_h(text, w - 2 * pad, size, 1.42) + 20
    els = [
        S(eid + "_sh", [x + 2, y + 4, w - 4, h], "roundRect", grad(SHADOW, SHADOW, 90, 46),
          role="decoration", reason="横条接地投影"),
        dict(S(eid, [x, y, w, h], "roundRect", fill, {"color": accent, "width": 1.25}),
             contains=[eid + "_cap", eid + "_t"]),
        S(eid + "_cap", [x + 7, y + 6, 4, max(8, h - 12)], "rect",
          grad(accent, accent, 90, 10), role="decoration", reason="横条左侧书签色标（母题）"),
        T(eid + "_t", [x + pad, y + 7, w - 2 * pad, h - 14], text, size, color,
          HEI if bold else KAI, bold=bold, width=w - 2 * pad, align=align),
    ]
    return els, h


def imgcard(eid, x, y, w, h, src, accent, cap=None, pad=9, cap_size=SZ_SMALL):
    """图片卡：浅衬卡 + 图 + 图下注释（三件都严格落在衬卡内）。返回 (els, 总高)。"""
    ch = need_h(cap, w + 2 * pad - 12, cap_size, 1.4) if cap else 0
    total = h + 2 * pad + (3 + ch if cap else 0)
    els = ecard(eid + "_bg", x - pad, y - pad, w + 2 * pad, total, accent, fill=PANEL, pad=pad)
    els[1]["contains"].append(eid)
    els.append(Img(eid, [x, y, w, h], src, fit="cover"))
    if cap:
        els[1]["contains"].append(eid + "_cap")
        els.append(T(eid + "_cap", [x - pad, y + h + pad + 3, w + 2 * pad, ch], cap, cap_size,
                     MUTED, KAI, width=w + 2 * pad))
    return els, total


def numhero(eid, x, y, w, accent, big, label, big_size=SZ_TITLE):
    """数字锚点：浅卡 + 大数字 + 小标签（数字上限 24pt，靠色块与字号保持冲击力）。"""
    bh = big_size * 1.3
    lh = need_h(label, w, SZ_SMALL, 1.4)
    h = 6 + bh + 4 + lh + 8
    els = [
        dict(S(eid + "_pl", [x, y, w, h], "roundRect", PANEL, {"color": accent, "width": 1.5}),
             contains=[eid + "_t", eid + "_l"]),
        T(eid + "_t", [x, y + 6, w, bh], big, big_size, accent, HEI, bold=True,
          align="center", width=w, wrap_on=True, lineHeight=1.2),
        T(eid + "_l", [x, y + 6 + bh + 4, w, lh], label, SZ_SMALL, SOFT, KAI,
          align="center", width=w, wrap_on=True),
    ]
    return els, h


def srcnote(els, text, y=460, x=L, w=CW):
    ch = need_h(text, w, SZ_SMALL, 1.4)
    els.append(T("sn", [x, y, w, ch], text, SZ_SMALL, CHALK_FAINT, KAI, width=w))


def bullets(prefix, items, y, accent, size=SZ_BODY, gap=8, width=CW, x0=L, on_board=False):
    """编号条目：浅卡横条 + 序号块。items=[(标题, 说明)]。"""
    els, cy = [], y
    for i, it in enumerate(items):
        t = it[0] if isinstance(it, (list, tuple)) else it
        b = it[1] if isinstance(it, (list, tuple)) and len(it) > 1 else ""
        eid = "%sb%d" % (prefix, i)
        tw_ = width - 62
        th_ = need_h(t, tw_, size, 1.45)
        bh_ = need_h(b, tw_, size - 2, 1.5) if b else 0
        h = max(36, th_ + (6 + bh_ if b else 0) + 18)
        els.append(S(eid + "_sh", [x0 + 2, cy + 4, width - 4, h], "roundRect",
                     grad(SHADOW, SHADOW, 90, 46), role="decoration", reason="条目接地投影"))
        els.append(dict(S(eid, [x0, cy, width, h], "roundRect", PANEL,
                          {"color": accent, "width": 1.25}),
                        contains=[eid + "_n", eid + "_nt", eid + "_t"] + ([eid + "_b"] if b else [])))
        els.append(S(eid + "_n", [x0 + 10, cy + 9, 30, 30], "roundRect", grad(accent, accent, 135, 55),
                     role="decoration", reason="序号块"))
        els.append(T(eid + "_nt", [x0 + 10, cy + 14, 30, 20], "%02d" % (i + 1), SZ_SMALL,
                     INK, HEI, bold=True, align="center", width=30, wrap_on=True))
        els.append(T(eid + "_t", [x0 + 50, cy + 8, tw_, th_], t, size, INK, HEI, bold=True,
                     width=tw_))
        if b:
            els.append(T(eid + "_b", [x0 + 50, cy + 8 + th_ + 4, tw_, bh_], b, size - 2, SOFT,
                         KAI, width=tw_))
        cy += h + gap
    return els, cy - y - gap


def table2(eid, x, y, w, cols, rows, row_h=None, size=SZ_SMALL):
    """表格（DSL 原生 table：字段只有 cols / rows / header）。返回 (els, 估算高)。"""
    n = len(cols)
    col_w = w / n
    rh = row_h or (size * 1.5 + 18)
    els = [{"elementId": eid, "elementType": "table", "bounds": [x, y, w, rh * len(rows)],
            "cols": list(cols), "rows": [list(r) for r in rows], "header": True}]
    return els, rh * len(rows)


def dump(path, els, notes=None, extra=None):
    import io
    p = {"pageType": "content", "notes": notes}
    if extra:
        p.update(extra)
    io.open(path, "w", encoding="utf8").write(kit.dump_yaml(p, els))
