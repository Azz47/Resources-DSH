#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描一个目录下所有 SKILL.md，打印 frontmatter name/description/大小与合计体积。

用法： python inspect_skills.py <root> [--depth-from <子目录>]
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
KV = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")


def frontmatter(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = FM.match(text)
    data = {}
    if m:
        for line in m.group(1).splitlines():
            mm = KV.match(line)
            if mm:
                data[mm.group(1)] = mm.group(2).strip().strip('"').strip("'")
    return data, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    found = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if fn == "SKILL.md":
                found.append(os.path.join(dirpath, fn))
    found.sort()
    for p in found:
        data, text = frontmatter(p)
        rel = os.path.relpath(os.path.dirname(p), root).replace("\\", "/")
        desc = (data.get("description") or "").replace("\n", " ")
        print(f"  {rel:<34} name={data.get('name') or '-'!s:<30} {len(text.encode()):>7} B  {desc[:70]}")
    total = 0
    count = 0
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            total += os.path.getsize(os.path.join(dirpath, fn))
            count += 1
    print(f"SKILL.md 命中 {len(found)}  目录内文件 {count}  合计 {round(total/1048576, 2)} MB")


if __name__ == "__main__":
    main()
