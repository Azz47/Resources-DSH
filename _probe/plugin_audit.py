# -*- coding: utf-8 -*-
"""插件盘点：装了哪些、哪些启用、功能是否重叠、每轮注入多少上下文。

关键事实（本机实测得出，别再用别的方法猜）：
  - 插件注册系统提示段的 API 是 `ctx.systemPrompt.section({ name, order, text })`
    （cordis 服务注入，`export const inject = [... 'systemPrompt']`）
  - `text` 可以是字符串，也可以是 `({ agent }) => string` 的函数 —— 后者**必须跑起来
    才知道占多少**，静态分析量不到。所以本表对函数型的标注「动态」，并给出其数据源。

用法: python plugin_audit.py
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROFILE = r"C:\Users\Administrator\.dsh\profiles\desktop"
NM = os.path.join(PROFILE, "node_modules")
PKG = os.path.join(PROFILE, "package.json")
PATCH = os.path.join(PROFILE, "cordis.patch.yml")

deps = json.load(open(PKG, encoding="utf-8"))["dependencies"]

# 插件 id -> 是否在 patch 里启用（patch 里的条目形如 `- id: xxx` 或 name: dsh-xxx）
patch_txt = ""
if os.path.exists(PATCH):
    patch_txt = open(PATCH, encoding="utf-8", errors="replace").read()

# 功能重叠的判定：把插件名映射到能力标签
TAGS = [
    ("技能管理", [r"skill-explorer", r"skill-panel", r"skill-mcp-manager", r"skills-manager",
                  r"run2skill", r"skill"]),
    ("上下文/压缩", [r"billion-context", r"dsh-context", r"simplify"]),
    ("教学/课件", [r"education", r"textbook", r"ppt-studio", r"openmaic", r"teaching-board", r"animations"]),
    ("界面增强", [r"better-sidebar", r"codex-ui", r"genui", r"whale-widget", r"hotspots", r"market"]),
    ("内容生成", [r"image-generation", r"mindmap", r"archive-manager"]),
    ("工程辅助", [r"code-review", r"automation", r"session-cleaner", r"im-connect", r"btw"]),
]


def tags_of(name):
    out = []
    low = name.lower()
    for tag, pats in TAGS:
        if any(re.search(p, low) for p in pats):
            out.append(tag)
    return out


def section_info(pkg_dir):
    """找 systemPrompt.section 调用，返回 (段名, 静态字符数 or None, 来源文件)。"""
    found = []
    for dirpath, dirnames, files in os.walk(pkg_dir):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git", "test", "tests", "docs")]
        for f in files:
            if not f.endswith((".js", ".mjs", ".cjs")):
                continue
            p = os.path.join(dirpath, f)
            try:
                if os.path.getsize(p) > 4_000_000:
                    continue
                src = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if "systemPrompt.section(" not in src:
                continue
            for m in re.finditer(r"systemPrompt\.section\(\s*\{", src):
                seg = src[m.end(): m.end() + 3000]
                nm = re.search(r"name\s*:\s*['\"]([^'\"]+)['\"]", seg)
                nmv = nm.group(1) if nm else "?"
                # text: '...' / "..." 静态
                st = re.search(r"""text\s*:\s*(['"])(.*?)\1""", seg, re.S)
                if st:
                    found.append((nmv, len(st.group(2)), os.path.relpath(p, pkg_dir)))
                else:
                    found.append((nmv, None, os.path.relpath(p, pkg_dir)))
    return found


rows = []
for name in sorted(deps):
    d = os.path.join(NM, name)
    ver = ""
    desc = ""
    pj = os.path.join(d, "package.json")
    if os.path.exists(pj):
        try:
            j = json.load(open(pj, encoding="utf-8"))
            ver = j.get("version", "")
            desc = (j.get("description") or "").strip()
        except Exception:
            pass
    secs = section_info(d) if os.path.isdir(d) else []
    short = name.split("/")[-1]
    enabled = bool(re.search(rf"(^|\s)(id|name)\s*:\s*['\"]?{re.escape(short)}['\"]?\s*$",
                             patch_txt, re.M)) or bool(
        re.search(rf"['\"]{re.escape(name)}['\"]", patch_txt))
    rows.append(dict(name=name, short=short, ver=ver, desc=desc, secs=secs,
                     enabled=enabled, tags=tags_of(name)))

# ---- 打印 ----
print("=" * 108)
print("一、已装插件总览")
print("=" * 108)
print(f"{'插件':<44}{'版本':<10}{'注册提示段':<26}{'功能标签'}")
print("-" * 108)
for r in sorted(rows, key=lambda r: (r["tags"][0] if r["tags"] else "zz", r["name"])):
    sec = ""
    if r["secs"]:
        s0 = r["secs"][0]
        sec = s0[0] + (f" ({s0[1]}字)" if s0[1] is not None else " (动态)")
        if len(r["secs"]) > 1:
            sec += f" +{len(r['secs'])-1}"
    print(f"{r['short']:<44}{r['ver']:<10}{sec:<26}{','.join(r['tags']) or '—'}")
print("-" * 108)
print(f"共 {len(rows)} 个依赖；其中 {sum(1 for r in rows if os.path.isdir(os.path.join(NM,r['name'])))} 个已落盘")

print()
print("=" * 108)
print("二、功能重叠（同一能力被多个插件覆盖 → 整合候选）")
print("=" * 108)
from collections import defaultdict
bytag = defaultdict(list)
for r in rows:
    for t in r["tags"]:
        bytag[t].append(r["short"])
for t, ns in sorted(bytag.items(), key=lambda kv: -len(kv[1])):
    flag = "  ⚠ 重叠" if len(ns) >= 2 else ""
    print(f"  {t:<12}({len(ns)})  {' / '.join(sorted(ns))}{flag}")

print()
print("=" * 108)
print("三、注册了系统提示段的插件（每轮都占上下文）")
print("=" * 108)
for r in rows:
    for nmv, n, src in r["secs"]:
        amt = f"{n:,} 字符（静态）" if n is not None else "动态（跑起来才知道）"
        print(f"  {r['short']:<34} section={nmv:<22}{amt:<24}{src}")

print()
print("=" * 108)
print("四、没注册提示段、也没找到明显工具声明的（可能是纯前端/待确认）")
print("=" * 108)
for r in rows:
    d = os.path.join(NM, r["name"])
    if not os.path.isdir(d):
        continue
    has_tool = False
    for dirpath, dirnames, files in os.walk(d):
        dirnames[:] = [x for x in dirnames if x not in ("node_modules", ".git", "test", "docs")]
        for f in files:
            if f.endswith((".js", ".mjs", ".cjs")):
                try:
                    s = open(os.path.join(dirpath, f), encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                if "tools.register(" in s or ".tool(" in s:
                    has_tool = True
                    break
        if has_tool:
            break
    if not has_tool and not r["secs"]:
        print(f"  {r['short']:<34}{r['ver']:<10}{r['desc'][:56]}")
