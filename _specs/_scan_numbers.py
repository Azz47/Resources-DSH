# -*- coding: utf-8 -*-
"""数字盘点：python _scan_numbers.py <工程目录>  —— 列出 pages\\*.yaml 里所有含数字的文字块及所在页。

可选：--orphans 同时报告「在 pages\\ 但不在 deck.yaml」的孤页。
输出直接可回填 number-bank.md 的 §1 表。
"""
import glob
import json
import os
import re
import sys

try:  # Windows 控制台默认 GBK，强制 UTF-8 输出，避免中文乱码
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

NUM = re.compile(r"\d")


def load_pages(deck_dir):
    pages_dir = os.path.join(deck_dir, "pages")
    files = sorted(glob.glob(os.path.join(pages_dir, "*.yaml")))
    out = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        texts = []
        for el in data.get("elements", []):
            t = (el.get("content") or {}).get("text")
            if t:
                texts.append((el.get("elementId"), t.strip()))
        out.append((os.path.basename(f), texts))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    deck_dir = argv[1]
    show_orphans = "--orphans" in argv

    pages = load_pages(deck_dir)
    print("pages scanned: %d" % len(pages))
    for name, texts in pages:
        hits = [(eid, t) for eid, t in texts if NUM.search(t)]
        if not hits:
            continue
        print("\n## %s" % name)
        for eid, t in hits:
            print("  [%s] %s" % (eid, t.replace("\n", " / ")))

    if show_orphans:
        deck_yaml = os.path.join(deck_dir, "deck.yaml")
        listed = set()
        with open(deck_yaml, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("- pages/"):
                    listed.add(os.path.basename(line.split("pages/", 1)[1].strip()))
        files = {name for name, _ in pages}
        print("\n## page list check")
        print("  deck.yaml: %d | files: %d" % (len(listed), len(files)))
        print("  orphans (file not in deck.yaml): %s" % sorted(files - listed))
        print("  missing (listed but absent):     %s" % sorted(listed - files))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
