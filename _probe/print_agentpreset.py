#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""读出每个会话 projcache 里的 agentPreset 取值 —— 判定它属于哪个预设。"""
import sys, re, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SESS = Path(r"C:\Users\Administrator\.dsh\storages\session_projcache\sessions")
IDS = ["d9803f89", "24588854", "c5432d9c", "2250d60b", "a3f98428",
       "4fd192f0", "68e7b239", "51ca8ec6", "5857488e", "c2f67b1e"]

for pref in IDS:
    hits = list(SESS.glob(f"session-{pref}*.json")) or list(SESS.glob(f"{pref}*.json"))
    if not hits:
        print(f"{pref}: 未找到")
        continue
    p = hits[0]
    txt = p.read_bytes().decode("utf-8", errors="replace")
    mt = time.strftime("%m-%d %H:%M", time.localtime(p.stat().st_mtime))
    vals = []
    for m in re.finditer(r'"agentPreset"\s*:\s*("?[^,}\n]{0,40})', txt):
        v = m.group(1).strip()
        if v not in vals:
            vals.append(v)
    vals = vals[:3]
    # 顺带看有没有显式提到 ppt 预设名
    extra = sorted(set(re.findall(r'"(ppt|ppt-studio[a-z-]*)"', txt)))[:4]
    print(f"{pref}  ({mt})  agentPreset={vals}   文本中出现的 presets={extra}")
