# -*- coding: utf-8 -*-
"""1ppt.com 课件「预览图」采集器 —— 只抓公开的列表页/详情页与其公开预览图，
不触碰带反爬保护的下载端点（/plus/download.php）。

产出:
    <out>/images/*.jpg        预览图（真实课件页面设计）
    <out>/index.jsonl         每条: 详情页URL / 标题 / 所属 / 页数 / 图片URL列表

用法:
    python crawl_1ppt.py <out-dir> [--cats zhengzhi,daode,yuwen] [--pages 3] [--delay 0.6]
"""
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE = "https://www.1ppt.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}

DETAIL_RE = re.compile(r'href="(/kejian/\d+\.html)"[^>]*>([^<]{2,120})<')
IMG_RE = re.compile(r'(https://img\.1ppt\.com/uploads/allimg/[^"\'\s<>]+\.(?:jpg|jpeg|png))')
PAGES_RE = re.compile(r'共\s*(\d+)\s*页')


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("gbk", errors="replace")


def collect_details(cats, pages, delay):
    seen, out = set(), []
    for cat in cats:
        for p in range(1, pages + 1):
            url = f"{BASE}/kejian/{cat}/" if p == 1 else f"{BASE}/kejian/{cat}/list_{p}.html"
            try:
                html = get(url)
            except Exception as e:
                print(f"  [list] {url} -> {e!r}"[:120])
                continue
            n = 0
            for m in DETAIL_RE.finditer(html):
                href, title = m.group(1), m.group(2).strip()
                if href in seen:
                    continue
                seen.add(href)
                out.append({"cat": cat, "url": BASE + href, "title": title})
                n += 1
            print(f"  [list] {cat} p{p}: +{n} (total {len(out)})")
            time.sleep(delay)
    return out


def enrich(item, delay):
    try:
        html = get(item["url"])
    except Exception as e:
        item["error"] = repr(e)[:100]
        return item
    # 只取正文预览区（#contentbox）里的图；排除"相关课件"缩略图
    m = re.search(r'id="contentbox"(.*?)</div>', html, re.S)
    region = m.group(1) if m else html
    imgs = []
    for u in IMG_RE.findall(region):
        if u not in imgs:
            imgs.append(u)
    pm = PAGES_RE.search(html)
    item["pages"] = int(pm.group(1)) if pm else None
    item["images"] = imgs
    time.sleep(delay)
    return item


def download(url, dest, referer):
    """图片 CDN 强制校验 Referer，缺失会 403。"""
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return os.path.getsize(dest)
    hdrs = dict(HEADERS)
    hdrs["Referer"] = referer
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--cats", default="zhengzhi,daode")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--delay", type=float, default=0.6)
    ap.add_argument("--max-details", type=int, default=0)
    a = ap.parse_args()

    img_dir = os.path.join(a.out, "images")
    os.makedirs(img_dir, exist_ok=True)
    cats = [c.strip() for c in a.cats.split(",") if c.strip()]

    details = collect_details(cats, a.pages, a.delay)
    if a.max_details:
        details = details[:a.max_details]
    print(f"\ndetails collected: {len(details)}")

    idx = open(os.path.join(a.out, "index.jsonl"), "a", encoding="utf-8")
    n_img = 0
    for i, it in enumerate(details, 1):
        it = enrich(it, a.delay)
        saved = []
        for j, u in enumerate(it.get("images", []), 1):
            base = u.split("/")[-1]
            stem_name, ext = os.path.splitext(base)
            name = re.sub(r"[^0-9A-Za-z_]+", "_", stem_name) + (ext.lower() or ".jpg")
            stem = re.sub(r"[^0-9A-Za-z]+", "", it["url"].split("/")[-1].replace(".html", ""))
            dest = os.path.join(img_dir, f"{it['cat']}_{stem}_{j}_{name}")
            try:
                download(u, dest, it["url"])
                saved.append(os.path.basename(dest))
                n_img += 1
            except Exception as e:
                it.setdefault("errors", []).append(repr(e)[:80])
        it["saved"] = saved
        idx.write(json.dumps(it, ensure_ascii=False) + "\n")
        idx.flush()
        if i % 10 == 0:
            print(f"  [{i}/{len(details)}] images so far: {n_img}")
    idx.close()
    print(f"\nDONE: {len(details)} courseware pages, {n_img} preview images -> {a.out}")


if __name__ == "__main__":
    main()
