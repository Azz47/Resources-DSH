# -*- coding: utf-8 -*-
"""
kit3 —— 「蓝图 × 盐晶」视觉系统（2026-10-17 全新设计，不继承任何旧模板）

设计基准 960×540（1px = 1pt），内容区 x ∈ [48, 640]，右侧 1/3 为讲师站位带。
所有样式常量集中在此；页面文件只描述内容与位置。
"""
import io
import json
import os

# ---------------------------------------------------------------- 画布
W, H = 960, 540
L, R = 48, 640
CW = R - L                    # 592
TOP = 142                     # 正文起点
BOT = 462                     # 正文底线

# ---------------------------------------------------------------- 色
PAPER = "#F6F3EC"
CARD = "#FFFFFF"
INK = "#17242E"
INK2 = "#3B4B57"
MUTED = "#3B4B57"   # 注释色：实测纸面 #E0E8E8–#F0E8E0 上 7.2:1（原 #5F6F7A 仅 4.2:1）
RULE = "#D3D7D6"

NAVY = "#0E2A47"
STEEL = "#2E6E8F"
GOLD = "#A8812F"
RUST = "#B4552F"
TEAL = "#1C6B60"

WHITE = "#FFFFFF"
ONDARK = "#EAF0F4"
ONDARK2 = "#B9C9D4"

F_T = "微软雅黑"      # 标题
F_B = "微软雅黑"      # 正文
F_Q = "宋体"          # 引文

# 环节：(主色, 标签, 深底图)
SEC = {
    "intro": (NAVY, "单元导览", "media/bg_d_navy.png"),
    "s1": (STEEL, "环节一 · 观展选品", "media/bg_d_steel.png"),
    "s2": (RUST, "环节二 · 撰写解说", "media/bg_d_rust.png"),
    "s3": (TEAL, "环节三 · 拓展策展", "media/bg_d_teal.png"),
    "end": (NAVY, "收束 · 我们的答卷", "media/bg_d_navy.png"),
}
BG_PAPER = "media/bg_paper.png"
BG_D_NAVY = "media/bg_d_navy.png"
BG_D_STEEL = "media/bg_d_steel.png"
BG_D_RUST = "media/bg_d_rust.png"
BG_D_TEAL = "media/bg_d_teal.png"
SEC_BG = {"intro": BG_D_NAVY, "s1": BG_D_STEEL, "s2": BG_D_RUST, "s3": BG_D_TEAL, "end": BG_D_NAVY}
# 2022 版课标五大核心素养：政治认同 / 道德修养 / 法治观念 / 健全人格 / 责任意识
CORE = {
    "intro": "政治认同 · 责任意识",
    "s1": "政治认同",
    "s2": "政治认同 · 健全人格",
    "s3": "责任意识 · 法治观念",
    "end": "政治认同 · 责任意识",
}
# 浅底页：按环节用不同纸面（同一套网格语言，母题随环节变化）
PAPER_BY_SEC = {
    "intro": "media/bg_p_intro.png",
    "s1": "media/bg_p_s1.png",
    "s2": "media/bg_p_s2.png",
    "s3": "media/bg_p_s3.png",
    "end": "media/bg_p_intro.png",
}
CUR_SEC = ["intro"]

# 字号阶梯（正文只取 16/18，注释 14，标题 28）
SZ_T = 28
SZ_C = 18
SZ_B = 16
SZ_N = 14
SZ_TAG = 14


# ---------------------------------------------------------------- 文字度量
def chw(c):
    if c == " ":
        return 0.30
    if ord(c) < 128:
        return 0.56
    return 1.0


def tw(t, size, fam=F_B):
    k = 1.055 if fam == F_Q else 1.03
    return sum(chw(c) for c in t) * size * k


def wrap(t, width, size, fam=F_B):
    out, cur = [], ""
    for ch in t:
        if ch == "\n":
            out.append(cur)
            cur = ""
            continue
        if tw(cur + ch, size, fam) <= width - 3:
            cur += ch
        else:
            out.append(cur)
            cur = ch
    out.append(cur)
    return out


def nh(t, width, size, lh=1.55, fam=F_B, pad=0):
    return len(wrap(t, width, size, fam)) * size * lh + pad


# ---------------------------------------------------------------- 元素
def T(eid, b, t, size=SZ_B, color=INK, fam=F_B, bold=False, align="left", lh=1.55):
    return {
        "elementId": eid,
        "elementType": "text",
        "bounds": [round(v, 2) for v in b],
        "content": {
            "text": t,
            "fontSize": size,
            "color": color,
            "fontFamily": fam,
            "bold": bold,
            "align": align,
            "lineHeight": lh,
        },
    }


def S(eid, b, kind="rect", fill=None, line=None, radius=None, deco=False):
    e = {
        "elementId": eid,
        "elementType": "shape",
        "kind": kind,
        "bounds": [round(v, 2) for v in b],
    }
    if fill is not None:
        e["fill"] = fill
    if line is not None:
        e["line"] = line
    if radius is not None:
        e["radius"] = radius
    if deco:
        e["role"] = "decoration"
    return e


def LN(eid, pts, color=RULE, width=1, dash=None, arrow=False, deco=True):
    c = {"color": color, "width": width}
    if dash:
        c["dash"] = dash
    e = {
        "elementId": eid,
        "elementType": "line",
        "points": [[round(x, 2), round(y, 2)] for x, y in pts],
        "line": c,
    }
    if arrow:
        e["arrow"] = True
    if deco:
        e["role"] = "decoration"
    return e


def IMG(eid, b, src, fit="cover"):
    return {
        "elementId": eid,
        "elementType": "image",
        "bounds": [round(v, 2) for v in b],
        "src": src,
        "fit": fit,
    }


def TB(els, eid, b, cols, rows, header=True):
    els.append({
        "elementId": eid,
        "elementType": "table",
        "bounds": [round(v, 2) for v in b],
        "cols": cols,
        "rows": rows,
        "header": header,
    })


# ---------------------------------------------------------------- 右侧讲师带
def rband(els, num, acc, dark=False, total=44):
    """虚线分栏 + 顶部色块 + 竖排单元名 + 页码。此带只放可遮挡信息。"""
    x = 648
    els.append(LN("rb_rule", [[x, 96], [x, BOT]], color=(ONDARK2 if dark else "#D9D6CB"),
                  width=1, dash="dash"))
    els.append(S("rb_mark", [x - 1, 96, 10, 4], "rect", fill=acc, deco=True))
    vt = "\n".join(list("第二单元 进入新时代"))
    els.append(T("rb_vt", [x + 14, 112, 22, 210], vt, 13,
                 (ONDARK2 if dark else MUTED), F_B, lh=1.42))
    els.append(T("rb_num", [x + 14, 400, 60, 24],
                 "%02d / %d" % (num, total), 13, (ONDARK2 if dark else MUTED), F_B, lh=1.5))


# ---------------------------------------------------------------- 页眉（浅底）
def hd(els, sec, title, num, total=44):
    CUR_SEC[0] = sec
    acc, label, _ = SEC[sec]
    els.append(S("hd_sq", [L, 56, 4, 16], "rect", fill=acc, deco=True))
    els.append(T("hd_tag", [L + 12, 52, 300, 22], label, SZ_TAG, acc, F_B, bold=True))
    els.append(T("hd_core", [R - 236, 52, 236, 22], "核心素养 · " + CORE[sec],
                 SZ_TAG, MUTED, F_B, align="right"))
    els.append(T("hd_tt", [L, 78, CW, 40], title, SZ_T, INK, F_T, bold=True, lh=1.25))
    els.append(LN("hd_ru", [[L, 128], [R, 128]], RULE, 1))
    els.append(LN("hd_ac", [[L, 128], [L + 64, 128]], acc, 2))
    rband(els, num, acc, dark=False, total=total)


# ---------------------------------------------------------------- 页眉（深底）
def ophead(els, sec):
    """深底环节页的页眉：环节标签 + 核心素养（与浅底 hd() 对齐同一套语义）。"""
    _acc, label, _ = SEC[sec]
    els.append(S("op_sq", [L, 48, 4, 16], "rect", fill=SEC[sec][0], deco=True))
    els.append(T("op_tag", [L + 12, 44, 300, 22], label, SZ_TAG, ONDARK2, F_B, bold=True))
    els.append(T("op_core", [R - 236, 44, 236, 22], "核心素养 · " + CORE[sec],
                 SZ_TAG, ONDARK2, F_B, align="right"))


def hd_dark(els, sec, title, num, total=44):
    acc, label, _ = SEC[sec]
    els.append(T("hd_tag", [L, 78, 300, 22], label, SZ_TAG, ONDARK2, F_B, bold=True))
    els.append(T("hd_core", [R - 236, 78, 236, 22], "核心素养 · " + CORE[sec],
                 SZ_TAG, ONDARK2, F_B, align="right"))
    els.append(T("hd_tt", [L, 104, CW, 44], title, 30, WHITE, F_T, bold=True, lh=1.24))
    els.append(LN("hd_ac", [[L, 156], [L + 88, 156]], acc if acc != NAVY else GOLD, 3))
    rband(els, num, GOLD, dark=True, total=total)


# ---------------------------------------------------------------- 卡片
def card(els, pid, x, y, w, acc, title, body, ts=SZ_C, bs=SZ_B,
         pad=16, fill=CARD, dark=False, bar=True, minh=0, kick=None):
    tx = x + pad + (3 if bar else 0)
    tw_ = w - pad * 2 - (3 if bar else 0)
    h = pad
    if kick:
        h += nh(kick, tw_, 14, 1.4) + 4
    if title:
        h += nh(title, tw_, ts, 1.35, F_T)
        h += 6
    if body:
        h += nh(body, tw_, bs, 1.55)
    h += pad
    h = max(h, minh)
    els.append(S(pid + "_bg", [x, y, w, h], "roundRect", fill=fill,
                 line={"color": RULE, "width": 1}, radius=6))
    if bar:
        els.append(S(pid + "_bar", [x, y + 10, 3, h - 20], "rect", fill=acc, deco=True))
    cy = y + pad
    if kick:
        kh = nh(kick, tw_, 14, 1.4)
        els.append(T(pid + "_k", [tx, cy, tw_, kh], kick, 14, acc, F_B, bold=True, lh=1.4))
        cy += kh + 4
    if title:
        th = nh(title, tw_, ts, 1.35, F_T)
        els.append(T(pid + "_t", [tx, cy, tw_, th], title, ts,
                     (ONDARK if dark else INK), F_T, bold=True, lh=1.35))
        cy += th + 6
    if body:
        bh = nh(body, tw_, bs, 1.55)
        els.append(T(pid + "_b", [tx, cy, tw_, bh], body, bs,
                     (ONDARK2 if dark else INK2), F_B, lh=1.55))
    return h


# ---------------------------------------------------------------- 横条
def strip(els, pid, x, y, w, acc, text, size=SZ_B, fill=None, color=None,
          h=None, bold=False, dark=False):
    pad = 12
    ih = h or (nh(text, w - pad * 2 - 3, size, 1.5) + pad * 2 - 4)
    els.append(S(pid + "_bg", [x, y, w, ih], "roundRect",
                 fill=(fill or CARD), line={"color": RULE, "width": 1}, radius=4))
    els.append(S(pid + "_bar", [x, y, 3, ih], "rect", fill=acc, deco=True))
    els.append(T(pid + "_t", [x + pad + 3, y + (ih - nh(text, w - pad * 2 - 3, size, 1.5)) / 2,
                              w - pad * 2 - 3, nh(text, w - pad * 2 - 3, size, 1.5)],
                 text, size, (color or (ONDARK if dark else INK)), F_B, bold=bold, lh=1.5))
    return ih


# ---------------------------------------------------------------- 数字块
def kpi(els, pid, x, y, w, num, label, acc, dark=False):
    lh = nh(label, w - 20, 13, 1.45)
    h = 22 + 46 + 4 + lh + 14
    els.append(S(pid + "_bg", [x, y, w, h], "roundRect", fill=CARD,
                 line={"color": RULE, "width": 1}, radius=6))
    els.append(S(pid + "_bar", [x, y, w, 3], "rect", fill=acc, deco=True))
    els.append(T(pid + "_n", [x + 10, y + 20, w - 20, 46], num, 38, acc, F_T,
                 bold=True, align="center", lh=1.15))
    els.append(T(pid + "_l", [x + 10, y + 70, w - 20, lh], label, 13,
                 (ONDARK2 if dark else MUTED), F_B, align="center", lh=1.45))
    return h


# ---------------------------------------------------------------- 图卡
def imcard(els, pid, x, y, w, ih, src, cap, acc, dark=False, cap_size=13):
    pad = 8
    ch = nh(cap, w - pad * 2 - 2, cap_size, 1.45) if cap else 0
    h = pad + ih + (6 + ch if cap else 0) + pad
    els.append(S(pid + "_bg", [x, y, w, h], "roundRect", fill=CARD,
                 line={"color": RULE, "width": 1}, radius=6))
    els.append(IMG(pid + "_im", [x + pad, y + pad, w - pad * 2, ih], src))
    if cap:
        els.append(T(pid + "_cp", [x + pad + 1, y + pad + ih + 6, w - pad * 2 - 2, ch],
                     cap, cap_size, (ONDARK2 if dark else MUTED), F_B, lh=1.45))
    return h


# ---------------------------------------------------------------- 引文
def quote(els, pid, x, y, w, text, cite, acc, size=18):
    pad = 18
    bh = nh(text, w - pad * 2 - 4, size, 1.7, F_Q)
    ch = nh(cite, w - pad * 2 - 4, 13, 1.5) if cite else 0
    h = pad + bh + (10 + ch if cite else 0) + pad
    els.append(S(pid + "_bg", [x, y, w, h], "roundRect", fill="#FBF8F0",
                 line={"color": RULE, "width": 1}, radius=6))
    els.append(S(pid + "_bar", [x, y, 4, h], "rect", fill=acc, deco=True))
    els.append(T(pid + "_t", [x + pad + 4, y + pad, w - pad * 2 - 4, bh],
                 text, size, INK, F_Q, lh=1.7))
    if cite:
        els.append(T(pid + "_c", [x + pad + 4, y + pad + bh + 10, w - pad * 2 - 4, ch],
                     cite, 13, MUTED, F_B, lh=1.5))
    return h


# ---------------------------------------------------------------- 条目组
def bullets(els, pid, items, y, acc, size=SZ_B, gap=10, x=L, w=CW, dark=False):
    cy = y
    for i, (lab, txt) in enumerate(items):
        eid = "%s%d" % (pid, i)
        tw_ = w - 14
        lw = min(tw(lab, size) + 8, tw_)
        lh_lab = nh(lab, lw, size, 1.55)
        twt = tw_ - lw - 8
        bh = nh(txt, twt, size, 1.55) if txt else 0
        rh = max(lh_lab, bh)
        els.append(S(eid + "_d", [x, cy + size * 0.42, 6, 6], "rect", fill=acc, deco=True))
        els.append(T(eid + "_l", [x + 14, cy, lw, lh_lab], lab, size,
                     (ONDARK if dark else INK), F_B, bold=True, lh=1.55))
        if txt:
            els.append(T(eid + "_t", [x + 14 + lw + 8, cy, tw_ - lw - 8, bh], txt, size,
                         (ONDARK2 if dark else INK2), F_B, lh=1.55))
        cy += rh + gap
    return cy - y


# ---------------------------------------------------------------- 来源注
def src(els, text, y=None):
    y = BOT if y is None else y
    els.append(T("src_note", [L, y, CW, 20], text, 13, MUTED, F_B, lh=1.4))


# ---------------------------------------------------------------- 输出
def auto_declare(els):
    """把「以 _bg 结尾的衬板 / 卡片底」与其内含元素（同前缀）登记为有意重叠。"""
    pairs = []
    for e in els:
        eid = e.get("elementId", "")
        if not eid.endswith("_bg"):
            continue
        pre = eid[:-3] + "_"
        b = e["bounds"]
        for f in els:
            fid = f.get("elementId", "")
            if fid == eid or not fid.startswith(pre):
                continue
            fb = f["bounds"]
            if (fb[0] >= b[0] - 1 and fb[1] >= b[1] - 1
                    and fb[0] + fb[2] <= b[0] + b[2] + 1
                    and fb[1] + fb[3] <= b[1] + b[3] + 1):
                pairs.append([eid, fid])
    return pairs


def dump(path, els, notes="", page_type="content", bg=BG_PAPER):
    page = {"elements": els}
    if page_type == "cover":
        page["pageType"] = "cover"
    if bg:
        page["background"] = {"type": "image", "src": bg, "fit": "cover"}
    if notes:
        page["notes"] = notes
    ov = auto_declare(els)
    if ov:
        page["expectedOverlaps"] = [{"pair": p, "reason": "色块衬底"} for p in ov]
    with io.open(path, "w", encoding="utf8") as f:
        f.write(json.dumps(page, ensure_ascii=False, indent=1))


def deck_yaml(title, page_files, min_font=14):
    L0 = [
        "# 进入新时代 · 单元思考与行动 —— 参赛版 v2（从零重建，不继承任何旧模板）",
        "version: 1",
        "title: %s" % json.dumps(title, ensure_ascii=False),
        "size: [960, 540]",
        "theme:",
        "  colors:",
        '    ink: "%s"' % INK,
        '    ink2: "%s"' % INK2,
        '    muted: "%s"' % MUTED,
        '    rule: "%s"' % RULE,
        '    card: "%s"' % CARD,
        '    paper: "%s"' % PAPER,
        '    navy: "%s"' % NAVY,
        '    steel: "%s"' % STEEL,
        '    gold: "%s"' % GOLD,
        '    rust: "%s"' % RUST,
        '    teal: "%s"' % TEAL,
        '    ondark: "%s"' % ONDARK,
        '    ondark2: "%s"' % ONDARK2,
        '    white: "%s"' % WHITE,
        '    tint: "#FBF8F0"',
        '    seco1: "#4E7FA6"',
        '    seco2: "#C97B57"',
        '    seco3: "#4F9E92"',
        '    lite2: "#D9A57E"',
        '    lite3: "#7FC0B6"',
        "  textStyles:",
        "    pageTitle: {fontSize: %d, color: $ink, bold: true}" % SZ_T,
        "    cardTitle: {fontSize: %d, color: $ink, bold: true}" % SZ_C,
        "    body: {fontSize: %d, color: $ink2}" % SZ_B,
        "    note: {fontSize: %d, color: $muted}" % SZ_N,
        "  safeArea: {top: 40, bottom: 44, left: 32, right: 48}",
        "  minFontSize: %d" % min_font,
        "pages:",
    ]
    for f in page_files:
        L0.append("  - %s" % f)
    return "\n".join(L0) + "\n"
