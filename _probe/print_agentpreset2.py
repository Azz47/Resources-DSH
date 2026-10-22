#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""正确解析 projcache JSON，递归找 agentPreset 的真实取值。"""
import sys, json, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SESS = Path(r"C:\Users\Administrator\.dsh\storages\session_projcache\sessions")
IDS = ["d9803f89", "24588854", "c5432d9c", "2250d60b", "a3f98428",
       "4fd192f0", "68e7b239", "51ca8ec6", "5857488e", "c2f67b1e"]


def walk(node, key, out, depth=0):
    if depth > 12:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                out.append(v)
            walk(v, key, out, depth + 1)
    elif isinstance(node, list):
        for it in node[:4000]:
            walk(it, key, out, depth + 1)


print(f"{'会话':<10}{'改时间':<12}  agentPreset / 预设线索")
print("-" * 96)
for pref in IDS:
    hits = list(SESS.glob(f"*{pref}*.json"))
    if not hits:
        print(f"{pref:<10}未找到")
        continue
    p = hits[0]
    mt = time.strftime("%m-%d %H:%M", time.localtime(p.stat().st_mtime))
    try:
        data = json.loads(p.read_bytes().decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"{pref:<10}{mt:<12}  解析失败: {e}")
        continue
    vals = []
    walk(data, "agentPreset", vals)
    uniq = []
    for v in vals:
        if v not in uniq:
            uniq.append(v)
    shown = json.dumps(uniq[:2], ensure_ascii=False)[:180] if uniq else "(无该键)"
    print(f"{pref:<10}{mt:<12}  {shown}")
