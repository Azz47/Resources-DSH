# -*- coding: utf-8 -*-
"""PPT Studio 中间层（deck.yaml + pages/*.yaml）搭建工具箱。

几何：960x540 px（1px = 1pt），内容走廊 x ∈ [44, 640] —— 右侧 1/3（640–960）留空给讲师站位。
"""
import itertools

I = itertools.count(1)

W, H = 960, 540
L = 44                      # 左边距
R = 640                     # 内容右边界（= 960 * 2/3）
CW = R - L                  # 596 内容宽
TOP = 122                   # 内容区顶（页眉横线之下）
BOT = 480                   # 内容区底
CH = BOT - TOP              # 358 内容高
BOT_SAFE = 456              # 色块/文本下沿软上限：背景图里板书用具（剪贴板/粉笔）上沿在 456pt，
                            # 内容压在这条线以内，底部的解说词条与素材来源注就不会与用具打架。

PANEL = "#FFFFFF"           # 卡片底板：亮底方案用纯白卡片
PANEL2 = "#F2F7F0"
CHALK = "#17251D"           # 主文本：亮底上改用深墨
SOFT = "#2E4438"            # 次级文本
DIM = "#3E574A"             # 三级文本
FAINT = "#46604F"           # 最小注记（对比度 4.8:1 达标）

def rel_lum(hexcolor):
    """WCAG 相对亮度（0 = 黑 / 1 = 白）。用于「深底自动翻白字」这类自适应取色。"""
    c = hexcolor.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)



# 板块配色：(主色, 辅色)
SEC = {
    "intro": ("#7FD6B0", "#1F5C42"),
    "s1":    ("#E8C15A", "#8A6A1E"),
    "s2":    ("#6FC7E8", "#1F6383"),
    "s3":    ("#EE8A72", "#8E3F2E"),
    "end":   ("#B9A7E8", "#584C86"),
}
DARK = {v[0]: v[1] for v in SEC.values()}   # 亮底：浅色环节色不可作文字色，统一换同族深色
SEC_LABEL = {
    "intro": "导入 · 从一次策展邀请开始",
    "s1":    "环节一 · 策展——感悟新时代",
    "s2":    "环节二 · 归因——解码新成就",
    "s3":    "环节三 · 力行——循迹盐湖行",
    "end":   "收束 · 课堂小结与作业",
}
KAI = "楷体"
HEI = "黑体"

CLOSE = "，。、；：？！）》」』”’·…"
OPEN = "（《「『“‘"


# ---------------------------------------------------------------- 文本度量
def wch(c):
    """字符宽度（以字号为单位）；全角标点按 1 计。"""
    o = ord(c)
    if o > 0x2E80 or 0x2010 <= o <= 0x203B or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return 1.0
    return 0.55


# ---------------------------------------------------------------- 字号换算
# 精品课口径：标题 30 / 正文不小于 24 / 每页不超过 8 行。
# fs() 是**唯一**的字号换算点：度量（tw/wrap/need_h）与渲染（T）都走它，
# 因此上层组件算出的框高天然等于实际排版高度，不会出现量画不一致的溢出。
# CHROME[0]=True 时暂时停用换算：页眉信息行 / 来源注属于**版式 chrome**，
# 不是正文，精品课口径的「正文不小于 24 号」不适用；放大它们只会把页眉挤爆。
CHROME = [False]


def fs(s):
    # 2026-10 收口：正文回退原稿字号。放大正文与「每页不超过 8 行」的精品课口径
    # 在本册内容密度下互相冲突（字号变大 -> 行数再增 -> 高度约 2.25x 膨胀），
    # 只会把版面挤爆。标题 30 号由 header() 单独保证，那是口径里唯一的硬性字号。
    return int(round(s))


def tw(text, size):
    return sum(wch(c) for c in text) * fs(size)


def wrap(text, width, size):
    """按容器宽度在语义断点处贪婪换行（中文按字断行，避开行首标点）。"""
    size = fs(size)
    out = []
    for para in str(text).split("\n"):
        if not para:
            out.append("")
            continue
        line, cur = "", 0.0
        # 标点悬挂位：仅当本段含可悬挂标点时才预留，悬挂上限 = 真实框宽 width。
        # 旧版一律允许长到 width + size，浏览器按 width 断行 → 多一行（实测档捕获）；
        # 但一律预留又会把纯数字/带分隔符的短行挤下去（如 24.39 → 24.3/9），故按需预留。
        hang = min(size, width * 0.28) if any(c in CLOSE or c in OPEN for c in para) else 0.0
        eff = width - hang
        i = 0
        while i < len(para):
            c = para[i]
            w = wch(c) * size
            if cur + w > eff and line:
                # 行尾标点跟随上一行（悬挂不得超过真实框宽）
                j = i
                while j < len(para) and para[j] in CLOSE and cur + wch(para[j]) * size <= width:
                    line += para[j]
                    cur += wch(para[j]) * size
                    j += 1
                # 行首避免开括号（同样不得超过真实框宽）
                if j < len(para) and para[j] in OPEN and cur + wch(para[j]) * size <= width:
                    line += para[j]
                    cur += wch(para[j]) * size
                    j += 1
                out.append(line)
                line, cur = "", 0.0
                i = j
                continue
            line += c
            cur += w
            i += 1
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- 元素工厂
def need_h(text, width, size, lh=1.35, pad=6):
    """给定宽度与字号，估算文本需要的框高。"""
    return (wrap(text, width, size).count("\n") + 1) * fs(size) * lh + pad


def T(eid, bounds, text, size, color, family=KAI, bold=False, align="left",
      lineHeight=None, wrap_on=False, role=None, width=None):
    color = DARK.get(color, color)   # 亮底收口：浅色环节色 -> 同族深色
    """文本框。默认按 bounds 宽度自动换行（显式 \\n 优先）。"""
    if not wrap_on:
        text = wrap(text, (width if width is not None else bounds[2]) - 6, size)
    c = {"text": text, "fontSize": fs(size), "color": color, "fontFamily": family}
    if bold:
        c["bold"] = True
    if align != "left":
        c["align"] = align
    if lineHeight:
        c["lineHeight"] = lineHeight
    e = {"elementId": eid, "elementType": "text", "bounds": bounds, "content": c}
    if role:
        e["role"] = role
    return e


def S(eid, bounds, kind="rect", fill=None, line=None, role=None, reason=None):
    e = {"elementId": eid, "elementType": "shape", "kind": kind, "bounds": bounds}
    if fill:
        e["fill"] = fill
    if line:
        e["line"] = line
    if role:
        e["role"] = role
    if reason:
        e["roleReason"] = reason
    return e


def grad(c1, c2=None, angle=90, a2=100):
    """形状渐变填充（DSL 只支持形状渐变，文本没有渐变/描边）。"""
    return {"type": "gradient",
            "stops": [{"pos": 0, "color": c1}, {"pos": 100, "color": c2 or c1, "alpha": a2}],
            "angle": angle}


def Ln(eid, pts, color, width=1.5, arrow=False, dash=None, role=None,
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
    return e


def Img(eid, bounds, src, fit="cover"):
    return {"elementId": eid, "elementType": "image", "bounds": bounds, "src": src, "fit": fit}


# ---------------------------------------------------------------- 页面骨架
def header(els, sec, title, num, title_size=25):
    title_size = 30 if title_size <= 25 else title_size   # 精品课口径：标题 30 号
    CHROME[0] = True
    c1, c2 = SEC[sec]
    els.append(S("hd_chip_a", [L, 28, 22, 22], "rect", grad(c1, c2, 135), role="decoration",
                 reason="页眉双色块母题（取自源稿）：大方块 + 右下角小方块叠压"))
    els.append(S("hd_chip_b", [52, 42, 14, 14], "rect", c2, role="decoration",
                 reason="页眉双色块母题（取自源稿）：大方块 + 右下角小方块叠压"))
    els.append(T("hd_info", [L + 36, 25, 480, 18],
                 "九年级道德与法治（统编版）· 第二单元 进入新时代 · 盐湖区北城初级中学",
                 12, DIM, HEI, width=480))
    els.append(T("hd_num", [566, 24, 74, 18], "%02d" % num, 14, c1, HEI, bold=True,
                 align="right", width=74))
    lab = SEC_LABEL[sec]
    pw = tw(lab, 14) + 44        # tw() 对加粗黑体偏窄，留出余量，否则药丸里的末字会被裁掉
    els.append(dict(S("hd_secbg", [L, 44.5, pw, 22], "roundRect", grad(c1, c1, 0, 78),
                      role="decoration", reason="环节标签药丸衬底（m01136：打破纯文字的单调）"),
                    contains=["hd_sec"]))
    els.append(T("hd_sec", [L + 13, 46.5, pw - 26, 19], lab, 14, "#12241B", HEI, bold=True,
                 width=pw - 26, wrap_on=True))
    els.append(T("hd_title", [L, 71, CW, 42], title, title_size, CHALK, HEI, bold=True,
                 width=CW))
    els.append(S("hd_rule2", [L, 119, 128, 3.5], "rect", grad(c2, c1, 0)))
    els.append(S("hd_rule", [L + 134, 120.2, CW - 134, 1.5], "rect", {"color": c1, "alpha": 42}))
    CHROME[0] = False


def footer(els, num):
    """页脚已并入页眉信息行（安全区底部 48px 容不下底部页脚）。保留空实现以稳定调用点。"""
    return


def srcnote(els, text, y=430):
    CHROME[0] = True
    try:
        _n = text.count("\n") + 1
        _lines = 0
        for _seg in text.split("\n"):
            _lines += wrap(_seg, CW, 12).count(chr(10)) + 1
        _h = max(18 * _n, 6 + 12 * 1.35 * _lines)
        els.append(T("sn", [L, y, CW, _h],
                     text, 12, FAINT, KAI, width=CW, lineHeight=1.35))
    finally:
        CHROME[0] = False


# ---------------------------------------------------------------- 竖向排布
def _yext(e):
    b = e.get("bounds")
    if b:
        return float(b[1]), float(b[1] + b[3])
    pts = e.get("points")
    if pts:
        ys = [float(p[1]) for p in pts]
        return min(ys), max(ys)
    return None


def _shift(e, dy):
    b = e.get("bounds")
    if b:
        b[1] = round(float(b[1]) + dy, 2)
        return
    pts = e.get("points")
    if pts:
        for p in pts:
            p[1] = round(float(p[1]) + dy, 2)


def _grow(e, dh):
    b = e.get("bounds")
    if b:
        b[3] = round(float(b[3]) + dh, 2)


def justify(els, target=None, gap_cap=34.0, grow_cap=120.0, min_gap=4.0):
    """把正文分成的若干「横排」在竖向重新分配，使最后一行底沿落到 target。

    只整体平移行、不动行内相对位置 —— 因此绝不会制造新的元素重叠。
    余量优先塞进行间距（单条最多长 gap_cap）；仍有余量时，把最后一排里
    高度 ≥40 的**形状**（卡片底板）拉高吸收，避免在页底留一条空带。
    """
    if target is None:
        target = BOT_SAFE
    body = [e for e in els
            if not str(e.get("elementId", "")).startswith(("hd_", "ft_"))
            and _yext(e) is not None]
    if len(body) < 2:
        return
    body.sort(key=lambda e: _yext(e)[0])
    rows = []
    for e in body:
        y0, y1 = _yext(e)
        if rows and y0 <= rows[-1][1] + 2.0:
            rows[-1][1] = max(rows[-1][1], y1)
            rows[-1][2].append(e)
        else:
            rows.append([y0, y1, [e]])
    if len(rows) < 2:
        return
    gaps = [rows[i + 1][0] - rows[i][1] for i in range(len(rows) - 1)]
    slack = target - rows[-1][1]

    if slack > 1.0:
        room = [max(0.0, min(gap_cap, g + gap_cap) - max(0.0, g)) for g in gaps]
        total = sum(room)
        add = [min(r, slack * (r / total)) for r in room] if total > 0 else [0.0] * len(gaps)
        rest = slack - sum(add)
    elif slack < -1.0:
        avail = [max(0.0, g - min_gap) for g in gaps]
        total = sum(avail)
        if total <= 0:
            return
        take = min(-slack, total)
        add = [-take * (a / total) for a in avail]
        rest = slack + take          # 仍为负 = 压不下去的余量
    else:
        return

    dy = 0.0
    for i, r in enumerate(rows):
        if i > 0:
            dy += add[i - 1]
        if abs(dy) < 0.01:
            continue
        for e in r[2]:
            _shift(e, dy)
        r[0] += dy
        r[1] += dy

    if rest < -3.0:
        # 压不下：挑一个"能缩"的大形状行（面板/卡片底）缩掉，并把它下面的行整体上移
        best_i, best_h = -1, 0.0
        for i, r in enumerate(rows):
            if i == len(rows) - 1:
                continue
            cand = [float(e["bounds"][3]) for e in r[2]
                    if e.get("elementType") == "shape" and float(e["bounds"][3]) >= 60]
            if cand and max(cand) > best_h:
                best_i, best_h = i, max(cand)
        if best_i >= 0:
            dh = max(rest, -min(20.0, best_h * 0.18))
            if dh < -3:
                for e in rows[best_i][2]:
                    if e.get("elementType") == "shape" and float(e["bounds"][3]) >= 60:
                        _grow(e, dh)
                for j in range(best_i + 1, len(rows)):
                    for e in rows[j][2]:
                        _shift(e, dh)

    if rest > 10.0:
        # 间距吃不下：挑一个"能长高"的形状行（卡片/面板底板）拉高，
        # 并把它下面的所有行整体下移，让页底不再留空带。
        best_i, best_h = -1, 0.0
        for i, r in enumerate(rows):
            cand = [float(e["bounds"][3]) for e in r[2]
                    if e.get("elementType") == "shape" and float(e["bounds"][3]) >= 40]
            if cand and max(cand) > best_h:
                best_i, best_h = i, max(cand)
        if best_i >= 0:
            dh = min(rest, min(grow_cap, best_h * 1.4))
            if dh > 4:
                for e in rows[best_i][2]:
                    if e.get("elementType") == "shape" and float(e["bounds"][3]) >= 40:
                        _grow(e, dh)
                for j in range(best_i + 1, len(rows)):
                    for e in rows[j][2]:
                        _shift(e, dh)


# ---------------------------------------------------------------- 版式组件
def panel(eid, x, y, w, h, accent, fill=None, kind="roundRect"):
    return S(eid, [x, y, w, h], kind, fill or PANEL, {"color": accent, "width": 1.25})


def panelc(eid, x, y, w, h, accent, children, fill=None, kind="roundRect"):
    """带 contains 承载声明的面板（子元素必须严格落在面板内）。"""
    return dict(panel(eid, x, y, w, h, accent, fill, kind), contains=list(children))


def card(pid, x, y, w, accent, title, body, tsize=17, bsize=14, pad=14,
         title_color=None, body_color=None, fill=None, min_h=0):
    """带标题的卡片：面板 + 标题 + 正文（用 contains 声明承载关系）。

    卡片被 min_h / row() / justify() 拉高时，卡内文字**竖向居中**——
    否则高卡片会变成"上面一行字、下面一大片空"，这正是"空间利用不合理"的来源。
    """
    tw_ = w - 2 * pad
    th_ = need_h(title, tw_, tsize, 1.25)
    bh_ = need_h(body, tw_, bsize, 1.4) if body else 0
    content = pad * 2 + th_ + (10 if body else 0) + bh_
    h = max(min_h, content)
    dy = (h - content) / 2.0 if h > content else 0.0
    els = [
        dict(panel(pid, x, y, w, h, accent, fill),
             contains=[pid + "_t", pid + "_b", pid + "_le"]),
        S(pid + "_le", [x + 2, y + 9, 3.5, max(10, h - 18)], "rect",
          grad(accent, accent, 90, 0), role="decoration",
          reason="卡片左侧渐隐色边（m01136：统一视觉母题，避免整页灰面）"),
        T(pid + "_t", [x + pad, y + pad - 4 + dy, tw_, th_], title, tsize, title_color or accent,
          HEI, bold=True, width=tw_),
    ]
    if body:
        els.append(T(pid + "_b", [x + pad, y + pad - 4 + dy + th_ + 10, tw_, bh_], body, bsize,
                     body_color or SOFT, KAI, width=tw_))
    return els, h


def bar(eid, x, y, w, accent, text, size=16, color="#12241B", h=None, pad=14, bold=False,
        align="left"):
    """实色横条 + 条上文字（contains 承载）。"""
    h = h or need_h(text, w - 2 * pad, size, 1.35) + 12
    if isinstance(accent, str):
        _la, _lc = rel_lum(accent), rel_lum(color)
        if (max(_la, _lc) + 0.05) / (min(_la, _lc) + 0.05) < 4.5:
            color = "#FFFFFF"   # 条上文字与条底色对比不足（p37 H2bar_t 实测 1.38:1）自动翻白
    els = [
        dict(S(eid, [x, y, w, h], "roundRect", accent), contains=[eid + "_t", eid + "_cap"]),
        S(eid + "_cap", [x + 7, y + 5.5, 4, max(8, h - 11)], "rect",
          grad("#12241B", "#12241B", 90, 25), role="decoration",
          reason="横条左侧书签色标（m01136）"),
        T(eid + "_t", [x + pad, y + 6, w - 2 * pad, h - 12], text, size, color, HEI if bold else KAI,
          bold=bold, width=w - 2 * pad, align=align),
    ]
    return els, h


def hero(sec, big, sub=None, seal=None, y=TOP, big_size=34, sub_size=16, pad=32):
    """一句话页的仪式版式：渐变衬板 + 左侧渐隐色边 + 大字 + 副句 + 环节印章。

    m01136：「不要让内容看起来很单调」。DSL 的文本没有渐变/描边（只有实色 rPr），
    所以"艺术字"靠 **渐变形状衬板 + 大字 + 印章** 组合实现；`role="decoration"`
    的形状压在文字上由审阅器自动豁免，不会产生 content-collision。
    返回 (els, h)，h 为衬板高度，调用方据此在其下方排横条。
    """
    c1, c2 = SEC[sec]
    iw = CW - 2 * pad
    bh = need_h(big, iw, big_size, 1.32)
    sh = need_h(sub, iw, sub_size, 1.5) if sub else 0
    h = bh + (18 + sh if sub else 0) + 56
    els = [
        S("hr_panel", [L, y, CW, h], "roundRect", {"type": "gradient", "angle": 90, "stops": [{"pos": 0, "color": c1, "alpha": 32}, {"pos": 100, "color": c1, "alpha": 10}]},
          {"color": c2, "width": 1.2}, role="decoration",
          reason="一句话页渐变衬板（m01136：给大字一个版面锚点，避免整页纯文字）"),
        S("hr_edge", [L, y + 10, 5, h - 20], "rect", grad(c2, c2, 90, 22),
          role="decoration", reason="衬板左侧渐隐色边"),
        T("hr_big", [L + pad, y + 26, iw, bh], big, big_size, CHALK, HEI, bold=True,
          width=iw, lineHeight=1.32),
    ]
    if sub:
        # 副句宽度让出右下角印章的位置，否则 hr_sub 会与 hr_sealt 内容互压（不可声明豁免）
        els.append(T("hr_sub", [L + pad, y + 26 + bh + 18, iw - 58, sh], sub, sub_size, SOFT, KAI,
                     width=iw - 58, lineHeight=1.5))
    if seal:
        # 38 < justify() 的「可拉高形状」阈值 40，否则印章会被当成底板拉长
        els.append(S("hr_seal", [R - 64, y + h - 50, 38, 38], "roundRect",
                     {"color": c2, "alpha": 100}, {"color": c2, "width": 1.2},
                     role="decoration", reason="环节印章（母题）"))
        els.append(T("hr_sealt", [R - 64, y + h - 41, 38, 20], seal, 15, "#FFFFFF", HEI, bold=True,
                     align="center", width=38, wrap_on=True))
    return els, h


def row(cards_spec, y, accent, x0=L, total=CW, gap=11, min_h=0, prefix="r", **kw):
    """横排等宽卡片：先量出最高的卡片，再统一高度并让卡内文字竖向居中。"""
    n = len(cards_spec)
    w = (total - gap * (n - 1)) // n
    hs = []
    for i, (t, b) in enumerate(cards_spec):
        _, h = card("%sc%d" % (prefix, i), x0 + i * (w + gap), y, w, accent, t, b,
                    min_h=min_h, **kw)
        hs.append(h)
    h = max(hs) if hs else 0
    out = []
    for i, (t, b) in enumerate(cards_spec):
        e, _ = card("%sc%d" % (prefix, i), x0 + i * (w + gap), y, w, accent, t, b,
                    min_h=h, **kw)
        out.extend(e)
    return out, h


def bullet_rows(prefix, items, y, accent, size=16, gap=10, num=True, width=CW, x0=L):
    """竖向编号条目：编号色块 + 标题 +（可选）说明。items=[(标题, 说明)]"""
    els, cy = [], y
    for i, it in enumerate(items):
        t = it[0] if isinstance(it, (list, tuple)) else it
        b = it[1] if isinstance(it, (list, tuple)) and len(it) > 1 else ""
        tw_ = width - 46
        th_ = need_h(t, tw_, size, 1.25)
        bh_ = need_h(b, tw_, size - 2, 1.4) if b else 0
        h = max(30, th_ + bh_ + 8)
        nid = "%sn%d" % (prefix, i)
        els.append(dict(S(nid, [x0, cy, 34, 30], "ellipse", grad(accent, accent, 135, 58)),
                        contains=[nid + "_t"]))
        els.append(T(nid + "_t", [x0, cy + 5, 34, 20], "%02d" % (i + 1), 14, "#12241B",
                     HEI, bold=True, align="center", width=34, wrap_on=True))
        els.append(T("%st%d" % (prefix, i), [x0 + 46, cy - 1, tw_, th_], t, size, CHALK,
                     HEI, bold=True, width=tw_))
        if b:
            els.append(T("%sb%d" % (prefix, i), [x0 + 46, cy - 1 + th_ + 4, tw_, bh_], b,
                         size - 2, SOFT, KAI, width=tw_))
        cy += h + gap
        if i < len(items) - 1:
            els.append(Ln("%sl%d" % (prefix, i), [[x0 + 6, cy - gap // 2], [x0 + width - 6, cy - gap // 2]],
                          "#3D5A4A", 1, dash="dot"))
    return els, cy - y - gap


def page(sec, title, notes, num, extra_top=None, title_size=25):
    els = []
    header(els, sec, title, num, title_size)
    footer(els, num)
    if extra_top:
        els.extend(extra_top)
    return els


def dump_yaml(page, els):
    """极简 YAML 输出：只覆盖本工程用到的形状。"""
    def f(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
        if isinstance(v, (int, float)):
            return repr(v) if isinstance(v, float) else str(v)
        if isinstance(v, list):
            return "[" + ", ".join(f(x) for x in v) + "]"
        if isinstance(v, dict):
            return "{" + ", ".join("%s: %s" % (k, f(x)) for k, x in v.items()) + "}"
        raise TypeError(repr(v))

    out = []
    out.append('pageType: "%s"' % page.get("pageType", "content"))
    if page.get("subtitle"):
        pass
    out.append('background: {"type": "image", "src": "media/image1.jpeg", "fit": "cover"}')
    if page.get("notes"):
        out.append('notes: ' + f(page["notes"]))
    if page.get("expectedOverlaps"):
        out.append("expectedOverlaps:")
        for o in page["expectedOverlaps"]:
            out.append("  - " + f(o))
    if page.get("expectedOutOfSafeArea"):
        out.append("expectedOutOfSafeArea: " + f(page["expectedOutOfSafeArea"]))
    out.append("elements:")
    for e in els:
        keys = list(e.keys())
        out.append("  - %s: %s" % (keys[0], f(e[keys[0]])))
        for k in keys[1:]:
            out.append("    %s: %s" % (k, f(e[k])))
    return "\n".join(out) + "\n"
