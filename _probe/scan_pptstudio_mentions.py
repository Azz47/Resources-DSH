#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""定位「ppt-studio-craft / copy / data / diagram」这些名字出现在哪些对话与文件里。

输出有界：每个文件最多 3 段上下文（各 ±140 字符），文件级别最多 20 个。
同时核实 ppt-studio 插件里的 SKILL.md 实名与预设隔离声明。
"""
import sys, os, re, json, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOME = Path(r"C:\Users\Administrator\.dsh")
WS = Path(r"D:\Resources\DSH")
KEYWORDS = ["ppt-studio-craft", "ppt-studio-copy", "ppt-studio-data",
            "ppt-studio-diagram", "ppt-studio-manual"]

print("=" * 78)
print("A. ppt-studio 插件里的 SKILL.md 实名（磁盘事实）")
print("=" * 78)
plug = HOME / "profiles" / "desktop" / "node_modules" / "dsh-ppt-studio"
skdirs = sorted(p for p in plug.rglob("SKILL.md"))
roots = {}
for p in skdirs:
    try:
        rel = p.relative_to(plug)
    except ValueError:
        rel = p
    top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    roots.setdefault(str(top), []).append(str(rel))
for top in sorted(roots):
    print(f"\n-- {top}  ({len(roots[top])} 个 SKILL.md)")
    for rel in roots[top][:24]:
        print("   ", rel)
print(f"\n合计 {len(skdirs)} 个 SKILL.md")

def show_iso(fp, patterns, label, maxlines=14):
    print("\n" + "-" * 78)
    print(f"B. {label}: {fp}")
    print("-" * 78)
    if not fp.exists():
        print("   (不存在)")
        return
    txt = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    hits = 0
    for i, ln in enumerate(txt):
        if any(re.search(pat, ln) for pat in patterns):
            print(f"   {i+1:>4}| {ln.strip()[:230]}")
            hits += 1
            if hits >= maxlines:
                print("   ... (更多略)")
                break
    if hits == 0:
        print("   (无匹配行)")

show_iso(plug / "cordis.patch.yml",
         [r"skill", r"preset", r"scope", r"isolat|隔离"], "插件 patch 自述")
show_iso(plug / "agent-presets" / "ppt" / "agent.cordis.yml",
         [r"skill", r"filesystem|tool-skill", r"scope"], "PPT 预设 agent.cordis.yml")

print("\n" + "=" * 78)
print("C. 谁提到过这四个名字（对话 / 文档全域扫描）")
print("=" * 78)

cands = []
for base in [HOME / "storages", HOME / "sessions", HOME / "projects",
             WS / "_probe", WS / "_skilltest", WS]:
    if not base.exists():
        continue
    for dp, dn, fn in os.walk(base):
        dn[:] = [d for d in dn if d not in ("node_modules", ".git", "__pycache__")]
        for f in fn:
            if not f.lower().endswith((".json", ".jsonl", ".md", ".txt", ".log")):
                continue
            p = Path(dp) / f
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size < 200:
                continue
            cands.append((st.st_size, st.st_mtime, p))

seen = set()
cands = [c for c in cands if not (str(c[2]) in seen or seen.add(str(c[2])))]
cands.sort(key=lambda x: -x[1])
print(f"候选文件 {len(cands)} 个（按修改时间倒序，跳过 node_modules）\n")

reported = 0
for size, mtime, p in cands:
    if reported >= 20:
        break
    if size > 80 * 1024 * 1024:
        print(f"[skip >80MB] {p}  {size/1048576:.1f}MB")
        continue
    try:
        raw = p.read_bytes()
    except OSError:
        continue
    txt = raw.decode("utf-8", errors="replace")
    found = [k for k in KEYWORDS if k in txt]
    if not found:
        continue
    reported += 1
    ts = time.strftime("%m-%d %H:%M", time.localtime(mtime))
    print(f"\n### [{reported}] {p}")
    print(f"     {size/1024:.0f} KB · mtime {ts} · 命中 {found}")
    for k in found[:2]:
        idxs = [m.start() for m in re.finditer(re.escape(k), txt)][:2]
        for n, i in enumerate(idxs):
            seg = txt[max(0, i - 140): i + 140].replace("\n", " ⏎ ")
            print(f"     · {k} #{n+1}: …{seg}…")

print(f"\n共 {reported} 个文件提到这些名字")
