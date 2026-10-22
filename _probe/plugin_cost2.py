# -*- coding: utf-8 -*-
"""精确盘点插件「每轮注入上下文」的占用。

上一版把插件自带的**文档/参考资料**也算了进去（billion-context 报出 2300 万字符，
明显是它 bundle 的文档），不能用来排序。这版只抓**真正注册为系统提示段的字符串**：

  systemPrompt.section({ name: ..., order: ..., text: `...` })
  prompt.section({ ..., text: `...` })

做法：定位 `.section(` 调用，在它的括号范围内找 `text:` 后的模板字符串/引号字符串，
量长度。模板插值 `${...}` 按 20 字符估（实际渲染值通常不大）。

用法: python plugin_cost2.py [--top N]
"""
import json
import os
import re
import sys

PROFILE = r"C:\Users\Administrator\.dsh\profiles\desktop"
PKG = os.path.join(PROFILE, "package.json")

# 注册段的调用点
CALL = re.compile(r"\.\s*(?:section|registerSection|addSection)\s*\(", re.I)
# text: `...`  或  text: "..." / text: '...'
TEXT_TMPL = re.compile(r"\btext\s*:\s*`", re.I)
TEXT_QUOT = re.compile(r"""\btext\s*:\s*(['"])""", re.I)


def read_template(src, i):
    """i 指向反引号位置，返回模板内容（处理 \` 转义）。"""
    j = i + 1
    out = []
    while j < len(src):
        c = src[j]
        if c == "\\":
            out.append(src[j + 1] if j + 1 < len(src) else "")
            j += 2
            continue
        if c == "`":
            break
        out.append(c)
        j += 1
    return "".join(out)


def read_quoted(src, i):
    q = src[i]
    j = i + 1
    out = []
    while j < len(src):
        c = src[j]
        if c == "\\":
            out.append(src[j + 1] if j + 1 < len(src) else "")
            j += 2
            continue
        if c == q or c == "\n":
            break
        out.append(c)
        j += 1
    return "".join(out)


def measure(src):
    """返回该文件里所有 section 注册的 text 长度之和。"""
    total = 0
    hits = []
    for m in CALL.finditer(src):
        # 只看足够近的 text: —— 2500 字符内
        window = src[m.end(): m.end() + 2500]
        best = None
        tm = TEXT_TMPL.search(window)
        if tm:
            body = read_template(window, tm.end() - 1)
            best = (len(body), body[:60])
        else:
            tq = TEXT_QUOT.search(window)
            if tq:
                body = read_quoted(window, tq.end() - 1)
                if len(body) >= 40:
                    best = (len(body), body[:60])
        if best:
            total += best[0]
            hits.append(best)
    return total, hits


def walk(pkg_dir):
    total = 0
    files = []
    for dirpath, dirnames, fs in os.walk(pkg_dir):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git", "test", "tests", "docs", "examples")]
        for f in fs:
            if not f.endswith((".js", ".mjs", ".cjs", ".ts")):
                continue
            p = os.path.join(dirpath, f)
            try:
                if os.path.getsize(p) > 4_000_000:
                    continue
                src = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if ".section(" not in src and ".registerSection(" not in src:
                continue
            n, hits = measure(src)
            if n:
                total += n
                files.append((os.path.relpath(p, pkg_dir), n, len(hits)))
    return total, files


deps = json.load(open(PKG, encoding="utf-8"))["dependencies"]
rows = []
for name in sorted(deps):
    d = os.path.join(PROFILE, "node_modules", name)
    if not os.path.isdir(d):
        rows.append((name, -1, []))
        continue
    n, files = walk(d)
    rows.append((name, n, files))

rows.sort(key=lambda r: -r[1])
print(f"{'插件':<46}{'注入字符':>10}  {'段数':>4}  主要来源")
print("-" * 100)
tot = 0
for name, n, files in rows:
    if n <= 0:
        print(f"{name:<46}{('—' if n < 0 else '0'):>10}")
        continue
    tot += n
    segs = sum(f[2] for f in files)
    files.sort(key=lambda f: -f[1])
    top = ", ".join(f"{f[0]}({f[1]:,})" for f in files[:2])
    print(f"{name:<46}{n:>10,}  {segs:>4}  {top}")
print("-" * 100)
print(f"{'合计':<46}{tot:>10,}  约 {tot/3.2:,.0f} tokens/轮")
print()
print("注：`text:` 里的 ${...} 插值按字面计，实际渲染略有差异；未注册为 section 的")
print("    工具描述（tools 的 description）不计入本表。")
