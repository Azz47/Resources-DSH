#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐字节对比本地文件与 GitHub raw 上游文件，定位差异性质（换行符/编码/内容）。"""
import hashlib
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dsh-cmp"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cmp(local_path, url, label):
    up = fetch(url)
    with open(local_path, "rb") as fh:
        lo = fh.read()
    print(f"\n=== {label}")
    print(f"  本地 {len(lo):8d} B sha={blob_sha(lo)[:12]}  CRLF={lo.count(b'\\r\\n'):4d} LF={lo.count(b'\\n'):4d}")
    print(f"  上游 {len(up):8d} B sha={blob_sha(up)[:12]}  CRLF={up.count(b'\\r\\n'):4d} LF={up.count(b'\\n'):4d}")
    if lo == up:
        print("  -> 完全一致")
        return
    n = min(len(lo), len(up))
    i = next((k for k in range(n) if lo[k] != up[k]), n)
    print(f"  首个差异字节偏移 {i}")
    lo_ctx = lo[max(0, i - 60): i + 60]
    up_ctx = up[max(0, i - 60): i + 60]
    print(f"  本地: {lo_ctx!r}")
    print(f"  上游: {up_ctx!r}")


CASES = [
    (r"C:\Users\Administrator\.dsh\skills\ask-matt\SKILL.md",
     "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/ask-matt/SKILL.md",
     "mattpocock ask-matt/SKILL.md"),
    (r"C:\Users\Administrator\.dsh\skills\ask-matt\agents\openai.yaml",
     "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/ask-matt/agents/openai.yaml",
     "mattpocock ask-matt/agents/openai.yaml"),
    (r"C:\Users\Administrator\.dsh\skills\ui-ux-pro-max\SKILL.md",
     "https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/.claude/skills/ui-ux-pro-max/SKILL.md",
     "ui-ux-pro-max/SKILL.md"),
]

if __name__ == "__main__":
    for path, url, label in CASES:
        try:
            cmp(path, url, label)
        except Exception as exc:  # noqa: BLE001
            print(f"\n=== {label} 失败: {exc}")
