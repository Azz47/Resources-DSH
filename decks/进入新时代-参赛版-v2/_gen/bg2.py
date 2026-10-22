# -*- coding: utf-8 -*-
"""生成四张环节版纸面背景（1920x1080 = 960x540pt 的 2 倍）。
设计约束：内容区 (48..640, 142..462) 保持干净；纹理与母题只落在外圈
（顶部 y<140 / 底部 y>468 / 右侧 x>660），因此不会压在文字上。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
W, H = 1920, 1080


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def base_canvas(top, bottom):
    """竖向柔和渐变底（上浅下略深），1px 渐变足够。"""
    c1 = np.array(hex2rgb(top), float)
    c2 = np.array(hex2rgb(bottom), float)
    t = np.linspace(0, 1, H)[:, None] ** 1.15
    arr = c1[None, None, :] * (1 - t[:, :, None]) + c2[None, None, :] * t[:, :, None]
    arr = np.repeat(arr, W, axis=1)
    return Image.fromarray(arr.astype("uint8"), "RGB").convert("RGBA")


def add_grid(img, step, color, alpha, offset=0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = hex2rgb(color) + (alpha,)
    for x in range(offset, W, step):
        d.line([(x, 0), (x, H)], fill=c, width=1)
    for y in range(offset, H, step):
        d.line([(0, y), (W, y)], fill=c, width=1)
    return Image.alpha_composite(img, ov)


def add_noise(img, amount=2600, alpha=9, seed=7):
    rng = np.random.default_rng(seed)
    arr = np.array(img)
    xs = rng.integers(0, W, amount)
    ys = rng.integers(0, H, amount)
    for x, y in zip(xs, ys):
        v = arr[y, x]
        arr[y, x] = [max(0, int(v[0]) - 12), max(0, int(v[1]) - 12), max(0, int(v[2]) - 12), 255]
    return Image.fromarray(arr, "RGBA")


def add_wash(img, cx, cy, r, color, alpha, blur=180):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hex2rgb(color) + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img, ov)


def add_vignette(img, strength=16):
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    d = np.sqrt(dx ** 2 * 0.55 + dy ** 2)
    a = np.clip((d - 0.62) / 0.9, 0, 1) ** 1.6 * strength
    ov = np.zeros((H, W, 4), dtype="uint8")
    ov[:, :, 3] = a.astype("uint8")
    ov[:, :, 0:3] = 30
    return Image.alpha_composite(img, Image.fromarray(ov, "RGBA"))


def motif_arcs(img, color, cx, cy, radii, alpha=26, width=2):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for r in radii:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=340,
              fill=hex2rgb(color) + (alpha,), width=width)
    return Image.alpha_composite(img, ov.filter(ImageFilter.GaussianBlur(0.6)))


def motif_contour(img, color, alpha=24):
    """左下等高线：同心不规则波纹。"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k, r in enumerate(range(120, 640, 62)):
        pts = []
        for i in range(0, 721, 6):
            a = i * 3.14159 / 180
            rr = r + 9 * np.sin(a * 3 + k * 0.7)
            pts.append((120 + rr * np.cos(a), 1080 + rr * np.sin(a) * 0.5))
        d.line(pts, fill=hex2rgb(color) + (alpha,), width=2)
    ov = fade_h(ov.filter(ImageFilter.GaussianBlur(0.7)), 560, 150)
    return Image.alpha_composite(img, ov)


def motif_hex(img, color, alpha=26):
    """右下盐晶六边形格。"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    R = 52
    dx = R * 1.5
    dy = R * 1.732
    for col in range(7):
        for row in range(6):
            cx = 1460 + col * dx
            cy = 700 + row * dy + (dy / 2 if col % 2 else 0)
            pts = [(cx + R * np.cos(np.pi / 3 * i - np.pi / 6),
                    cy + R * np.sin(np.pi / 3 * i - np.pi / 6)) for i in range(6)]
            d.polygon(pts, outline=hex2rgb(color) + (alpha,))
    ov = fade_h(ov.filter(ImageFilter.GaussianBlur(0.5)), 1180, 1560)
    return Image.alpha_composite(img, ov)


def motif_blueprint(img, color, alpha=26):
    """右上蓝图：L 形构造线 + 十字角标（不放密集斜线，避免与波纹抢位）。"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = hex2rgb(color) + (alpha,)
    d.line([(1330, 748), (1900, 748)], fill=c, width=2)
    d.line([(1330, 566), (1330, 1080)], fill=c, width=2)
    d.line([(1330, 900), (1900, 900)], fill=hex2rgb(color) + (alpha // 2,), width=1)
    for (cx, cy) in ((1330, 748), (1330, 566), (1330, 900)):
        d.line([(cx - 14, cy), (cx + 14, cy)], fill=c, width=2)
        d.line([(cx, cy - 14), (cx, cy + 14)], fill=c, width=2)
    ov = fade_h(ov.filter(ImageFilter.GaussianBlur(0.5)), 1200, 1500)
    ov = fade_v(ov, 1080, 700)
    return Image.alpha_composite(img, ov)


def frame(img, color, alpha=30):
    """内框：距边 14px 的 1px 细框，让版面像一张被装裱过的纸。"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = hex2rgb(color) + (alpha,)
    d.rectangle([14, 14, W - 15, H - 15], outline=c, width=2)
    d.rectangle([26, 26, W - 27, H - 27], outline=hex2rgb(color) + (alpha // 3,), width=1)
    return Image.alpha_composite(img, ov)


def fade_h(ov, a, b):
    """横向渐隐：alpha 从 x=a 的 0 线性升到 x=b 的 1（避免母题出现硬边界）。"""
    arr = np.array(ov).astype(np.float32)
    ramp = np.clip((np.arange(W) - a) / float(b - a), 0, 1)[None, :]
    arr[:, :, 3] *= ramp
    return Image.fromarray(arr.astype("uint8"), "RGBA")


def fade_v(ov, a, b):
    arr = np.array(ov).astype(np.float32)
    ramp = np.clip((np.arange(H) - a) / float(b - a), 0, 1)[:, None]
    arr[:, :, 3] *= ramp
    return Image.fromarray(arr.astype("uint8"), "RGBA")


def spine(img, color, alpha=225):
    """左侧书脊：一条满高色带，给整册一个稳定的装订边。"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, 26, H], fill=hex2rgb(color) + (alpha,))
    d.rectangle([26, 0, 30, H], fill=hex2rgb(color) + (60,))
    for y in (150, 300, 450):
        d.rectangle([0, y, 26, y + 3], fill=(255, 255, 255, 90))
    return Image.alpha_composite(img, ov)


def bottom_rule(img, color, alpha=34):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = hex2rgb(color) + (alpha,)
    d.line([(96, 1008), (1720, 1008)], fill=c, width=2)
    d.line([(96, 1016), (1180, 1016)], fill=hex2rgb(color) + (alpha // 3,), width=1)
    return Image.alpha_composite(img, ov)


SPECS = {
    # 文件, 上色, 下色, 主网格色, 母题函数, 母题色, 光晕
    "bg_p_intro.png": ("#F8F5EE", "#F3EFE4", "#5C6B7A", "arcs", "#0E2A47", ("#C9DCE6", 20)),
    "bg_p_s1.png":    ("#F2F6F6", "#EAF0F1", "#3D5A6B", "blueprint", "#1F5C6B", ("#CFE2E6", 18)),
    "bg_p_s2.png":    ("#F9F4EA", "#F4EDDF", "#7A6A55", "contour", "#9A5B2E", ("#EBD9C0", 22)),
    "bg_p_s3.png":    ("#F3F7F0", "#ECF2E8", "#4E6A56", "hex", "#2E6B4F", ("#D5E6D4", 18)),
}

for name, (top, bot, grid_c, motif, motif_c, wash) in SPECS.items():
    img = base_canvas(top, bot)
    img = add_wash(img, 1750, 120, 760, wash[0], 26, blur=240)
    img = add_wash(img, 180, 980, 520, wash[0], 22, blur=240)
    img = add_grid(img, 24, grid_c, 9)
    img = add_grid(img, 192, grid_c, 20)
    img = add_noise(img)
    if motif == "arcs":
        img = motif_arcs(img, motif_c, 900, 700, range(520, 1240, 74), alpha=34)
    elif motif == "blueprint":
        img = motif_blueprint(img, motif_c, alpha=30)
        img = motif_arcs(img, motif_c, 1680, 980, range(360, 900, 72), alpha=26)
    elif motif == "contour":
        img = motif_contour(img, motif_c, alpha=38)
    elif motif == "hex":
        img = motif_hex(img, motif_c, alpha=36)
    img = bottom_rule(img, motif_c, alpha=44)
    img = frame(img, motif_c, alpha=34)
    img = spine(img, motif_c)
    img = add_vignette(img, 14)
    p = os.path.join(OUT, name)
    img.convert("RGB").save(p, optimize=True)
    print("wrote", name, os.path.getsize(p))
