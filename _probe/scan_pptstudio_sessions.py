#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""紧凑报告：哪些会话真的把 ppt-studio-* 当技能加载过（skill 注入 vs 只是被 grep/文档提到）。"""
import sys, os, re, json, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SESS = Path(r"C:\Users\Administrator\.dsh\storages\session_projcache\sessions")
CUR = "d9803f89"   # 当前会话 id 前缀

rows = []
for p in sorted(SESS.glob("*.json"), key=lambda x: -x.stat().st_mtime):
    raw = p.read_bytes()
    txt = raw.decode("utf-8", errors="replace")
    if "ppt-studio" not in txt:
        continue
    injects = {}
    for m in re.finditer(r'"sub"\s*:\s*"skill"\s*,\s*"name"\s*:\s*"([^"]+)"\s*,\s*"tokens"\s*:\s*(\d+)', txt):
        injects[m.group(1)] = int(m.group(2))
    for m in re.finditer(r'"tool"\s*:\s*"skill"\s*,\s*"skill"\s*:\s*"([^"]+)"', txt):
        injects.setdefault(m.group(1), None)
    ppt = {k: v for k, v in injects.items() if k.startswith("ppt-studio")}
    presets = sorted(set(re.findall(r'"([a-zA-Z0-9_-]*preset[a-zA-Z0-9_-]*)"', txt)))
    marks = [s for s in ("PPT 工作室", "ppt-studio-scope", "agentPreset", "presetIds") if s in txt]
    rows.append(dict(
        sid=p.stem.replace("session-", "")[:8],
        file=p.name, kb=len(raw) // 1024,
        mt=time.strftime("%m-%d %H:%M", time.localtime(p.stat().st_mtime)),
        ppt_skills=ppt, n_ppt=len(ppt),
        n_all_skills=len(injects), presets=presets[:4], marks=marks,
        cur=(CUR in p.name), title=(re.search(r'"title"\s*:\s*"([^"]{0,60})"', txt) or [None, ""])[1],
    ))

print(f"共 {len(rows)} 个会话提到 ppt-studio\n")
print(f"{'会话':<10}{'大小':>7}  {'改时间':<12}{'技能注入(ppt)':<34}{'全部技能':>8}  标记")
print("-" * 108)
for r in rows:
    tag = " ←当前" if r["cur"] else ""
    names = ",".join(f"{k.replace('ppt-studio-','')}:{v}" for k, v in sorted(r["ppt_skills"].items()))
    print(f"{r['sid']:<10}{r['kb']:>5}KB  {r['mt']:<12}{names[:33]:<34}{r['n_all_skills']:>8}  {'|'.join(r['marks'])}{tag}")

print("\n--- 被加载过的 ppt-studio 技能（按出现次数）---")
cnt = {}
for r in rows:
    for k, v in r["ppt_skills"].items():
        cnt[k] = cnt.get(k, 0) + 1
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print(f"  {v:>2} 个会话  {k}")

print("\n--- 当前会话是否加载过 ppt-studio 技能 ---")
cur = [r for r in rows if r["cur"]]
print("  当前会话文件:", cur[0]["file"] if cur else "(未在候选中)")
print("  当前会话 ppt 技能注入:", cur[0]["ppt_skills"] if cur else "-")
print("  当前会话全部技能注入:", cur[0]["n_all_skills"] if cur else "-")
print("  当前会话 preset 标记:", cur[0]["marks"] if cur else "-")
