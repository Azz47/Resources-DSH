#!/usr/bin/env python3
"""统计用户技能根规模 + 第二批 13 个技能的体积（用于文档同步）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"C:\Users\Administrator\.dsh\skills"
NEW = {
    "ppt-master", "morph-ppt", "morph-ppt-3d", "officecli", "officecli-docx",
    "officecli-xlsx", "officecli-pptx", "officecli-academic-paper",
    "officecli-data-dashboard", "officecli-financial-model",
    "officecli-pitch-deck", "officecli-word-form", "human-writing",
}


def du(path):
    total = 0
    count = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
                count += 1
            except OSError:
                pass
    return total, count


def main():
    dirs = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    missing = [d for d in dirs if not os.path.isfile(os.path.join(ROOT, d, "SKILL.md"))]
    total = 0
    rows = []
    for d in dirs:
        size, count = du(os.path.join(ROOT, d))
        total += size
        rows.append((d, size, count))
    print(f"user_root_dirs={len(dirs)}  no_skill_md={len(missing)}  total_bytes={total} ({total/1048576:.2f} MB)")
    if missing:
        print("missing:", ", ".join(missing))
    print("\n-- 第二批 13 个 --")
    for d, size, count in rows:
        if d in NEW:
            print(f"{d}\t{size}\t{count}")
    print("\n-- 体积 Top 8 --")
    for d, size, count in sorted(rows, key=lambda r: -r[1])[:8]:
        print(f"{d}\t{size}\t{count}")


if __name__ == "__main__":
    main()
