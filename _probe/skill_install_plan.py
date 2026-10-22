#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""扫描 _skillinstall 下已克隆仓库的 SKILL.md，给出安装计划（含与现有技能的重名冲突）。

用法: python skill_install_plan.py [--json]
输出:
  1) 每个仓库的候选技能（name / 相对路径 / description 首 60 字）
  2) 与现有 74 个技能的重名
  3) 仓库内部重名（同名多份 -> 必须只挑一份导入）
"""
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STAGE = Path(r"D:\Resources\DSH\_skillinstall")
INVENTORY = Path(r"D:\Resources\DSH\_probe\skills-inventory.json")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
NAME_RE = re.compile(r"^name\s*:\s*(.+?)\s*$", re.M)
DESC_RE = re.compile(r"^description\s*:\s*(.+?)\s*$", re.M)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return None, None
    fm = m.group(1)
    name = NAME_RE.search(fm)
    desc = DESC_RE.search(fm)
    return (
        name.group(1).strip().strip('"\'') if name else None,
        desc.group(1).strip().strip('"\'') if desc else None,
    )


def existing_names():
    if not INVENTORY.exists():
        return set()
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("skills", [])
    return {str(it.get("name", "")).strip() for it in items if it.get("name")}


def main():
    as_json = "--json" in sys.argv
    existing = existing_names()
    repos = sorted([p for p in STAGE.iterdir() if p.is_dir()]) if STAGE.exists() else []
    plan = {}
    report = []
    for repo in repos:
        rows = []
        for skill_md in sorted(repo.rglob("SKILL.md")):
            rel = skill_md.relative_to(repo).as_posix()
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except Exception as e:  # noqa: BLE001
                text = ""
                rel += f"  (read-error {e})"
            name, desc = parse_frontmatter(text)
            rows.append(
                {
                    "path": rel,
                    "dir": skill_md.parent.relative_to(repo).as_posix(),
                    "name": name or skill_md.parent.name,
                    "frontmatter": bool(name),
                    "desc": (desc or "")[:80],
                }
            )
        by_name = {}
        for r in rows:
            by_name.setdefault(r["name"], []).append(r)
        dup = {k: [x["path"] for x in v] for k, v in by_name.items() if len(v) > 1}
        coll = sorted({r["name"] for r in rows} & existing)
        plan[repo.name] = {
            "skill_md": len(rows),
            "unique_names": len(by_name),
            "no_frontmatter_name": [r["path"] for r in rows if not r["frontmatter"]],
            "internal_duplicates": dup,
            "collides_with_existing": coll,
            "skills": rows,
        }
        report.append(
            f"=== {repo.name}: SKILL.md={len(rows)} 唯一名={len(by_name)} "
            f"仓库内重名={len(dup)} 与现有重名={len(coll)} ==="
        )
        for r in rows:
            flag = "  <-- 重名(已存在)" if r["name"] in existing else ""
            report.append(f"  {r['name']:<32} {r['dir']}{flag}")
        if dup:
            report.append("  [仓库内重名]")
            for k, v in dup.items():
                report.append(f"    {k}: " + " | ".join(v))
        if not rows:
            report.append("  (无 SKILL.md)")

    out = "\n".join(report)
    print(out)
    if as_json:
        dest = Path(r"D:\Resources\DSH\_probe\skill-install-plan.json")
        dest.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[written] {dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
