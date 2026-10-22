#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测本机已装技能与 GitHub 上游仓库最新树的差异。

要点：
  * 上游用 GitHub tree API（curl 取，绕开本机对 raw.github 的间歇性掐断），
    每个文件带 blob SHA-1；本机按 git 的 blob 定义（sha1(b"blob <len>\\0"+data)）算同一哈希。
  * **换行归一**：本机若曾用 git clone 安装，core.autocrlf 会把 LF 变 CRLF，
    导致「每个文件都像被改过」。因此先比原始字节，再比归一化（\\r\\n -> \\n）字节，
    二者只差换行的记为「仅换行差异」，不算真实更新。
  * 允许别名：上游目录名与本机技能目录名不同（如 agent-reach 上游叫 skill/）。

用法：
  python check_skill_updates.py                 # 全部登记仓库（走本地树缓存）
  python check_skill_updates.py --refresh       # 重新抓树
  python check_skill_updates.py --repo owner/repo
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILLS_ROOT = r"C:\Users\Administrator\.dsh\skills"
CACHE = r"D:\Resources\DSH\_probe\upstream-trees"

REPOS = [
    ("mattpocock/skills", ["main", "master"]),
    ("nextlevelbuilder/ui-ux-pro-max-skill", ["main", "master"]),
    ("leonxlnx/taste-skill", ["main", "master"]),
    ("blader/humanizer", ["main", "master"]),
    ("panniantong/agent-reach", ["main", "master"]),
    ("Egonex-AI/Understand-Anything", ["main", "master"]),
    ("zarazhangrui/frontend-slides", ["main", "master"]),
    ("hugohe3/ppt-master", ["main", "master"]),
    ("iOfficeAI/OfficeCLI", ["main", "master"]),
    ("KKKKhazix/human-writing", ["main", "master"]),
]

# (repo, 上游目录 basename) -> 本机技能目录名
ALIASES = {
    ("panniantong/agent-reach", "skill"): "agent-reach",
}
# 上游根目录的 SKILL.md 与某个子技能重复时跳过（本机按打包态安装）
SKIP_DIRS = {
    ("zarazhangrui/frontend-slides", "(root)"),
}


def blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def file_shas(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return blob_sha(raw), blob_sha(raw.replace(b"\r\n", b"\n"))


def curl_get(url, timeout=300):
    proc = subprocess.run(
        ["curl.exe", "-sL", "--connect-timeout", "20", "--max-time", str(timeout),
         "-H", "User-Agent: dsh-skill-update-check",
         "-H", "Accept: application/vnd.github+json", url],
        capture_output=True,
    )
    return proc.stdout


def fetch_tree(slug, branches, refresh=False):
    os.makedirs(CACHE, exist_ok=True)
    cache_file = os.path.join(CACHE, slug.replace("/", "__") + ".json")
    if not refresh and os.path.exists(cache_file) and os.path.getsize(cache_file) > 200:
        try:
            with open(cache_file, encoding="utf-8") as fh:
                return json.load(fh), cache_file, "cache"
        except Exception:  # noqa: BLE001 — 缓存被截断/损坏（大仓常见）→ 丢弃重取
            os.remove(cache_file)
    last_err = None
    for br in branches:
        url = f"https://api.github.com/repos/{slug}/git/trees/{br}?recursive=1"
        try:
            raw = curl_get(url)
            if not raw:
                req = urllib.request.Request(url, headers={"User-Agent": "dsh-skill-update-check"})
                with urllib.request.urlopen(req, timeout=240) as resp:
                    raw = resp.read()
            data = json.loads(raw.decode("utf-8", "replace"))
            if "tree" not in data:
                last_err = f"{br}: {data.get('message')}"
                continue
            data["_branch"] = br
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False)
            return data, cache_file, br
        except Exception as exc:  # noqa: BLE001
            last_err = f"{br}: {exc}"
    raise RuntimeError(f"{slug} 取树失败 -> {last_err}")


def walk_files(root):
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            out.append(os.path.join(dirpath, fn))
    return out


def upstream_files_for(blobs, sub):
    if sub:
        prefix = sub + "/"
        return {p[len(prefix):]: sha for p, sha in blobs.items() if p.startswith(prefix) and p != prefix}
    return {p: sha for p, sha in blobs.items() if "/" not in p}


def check_repo(slug, branches, refresh=False, verbose=True):
    tree, cache_file, branch = fetch_tree(slug, branches, refresh=refresh)
    blobs, skill_dirs = {}, {}
    for e in (tree.get("tree") or []):
        if e.get("type") != "blob":
            continue
        p = e["path"]
        blobs[p] = e.get("sha")
        if p == "SKILL.md":
            skill_dirs["(root)"] = ""
        elif p.endswith("/SKILL.md"):
            d = p[: -len("/SKILL.md")]
            skill_dirs[os.path.basename(d)] = d
    result = {
        "repo": slug, "branch": branch, "tree_sha": tree.get("sha"),
        "truncated": bool(tree.get("truncated")), "cache": cache_file, "skills": {},
        "summary": {"up_to_date": 0, "crlf_only": 0, "outdated": 0, "not_installed": 0},
    }
    for name, sub in sorted(skill_dirs.items()):
        if (slug, name) in SKIP_DIRS:
            continue
        local_name = ALIASES.get((slug, name), name)
        local_root = os.path.join(SKILLS_ROOT, slug.split("/")[-1] if name == "(root)" else local_name)
        if not os.path.isdir(local_root):
            result["summary"]["not_installed"] += 1
            result["skills"][name] = {"status": "上游有 / 本机未装", "upstream_dir": sub}
            continue
        local_raw, local_norm = {}, {}
        for ap in walk_files(local_root):
            rel = os.path.relpath(ap, local_root).replace("\\", "/")
            local_raw[rel], local_norm[rel] = file_shas(ap)
        up = upstream_files_for(blobs, sub)
        changed, crlf, missing, extra = [], [], [], []
        for rel, sha in sorted(up.items()):
            if rel not in local_raw:
                missing.append(rel)
            elif local_raw[rel] == sha:
                continue
            elif local_norm[rel] == sha:
                crlf.append(rel)
            else:
                changed.append(rel)
        extra = sorted(r for r in local_raw if r not in up)
        if changed or missing or extra:
            result["summary"]["outdated"] += 1
            status = f"真实差异 {len(changed)+len(missing)+len(extra)} (改{len(changed)}/上游增{len(missing)}/本机多{len(extra)})"
            if crlf:
                status += f" + 换行{len(crlf)}"
        elif crlf:
            result["summary"]["crlf_only"] += 1
            status = f"仅换行差异 {len(crlf)} 文件（CRLF）"
        else:
            result["summary"]["up_to_date"] += 1
            status = "最新"
        result["skills"][name] = {
            "status": status, "local_dir": local_root, "upstream_dir": sub,
            "files_local": len(local_raw), "files_upstream": len(up),
            "changed": changed[:40], "missing_locally": missing[:40],
            "extra_locally": extra[:40], "crlf_only": crlf[:40],
        }
    if verbose:
        mark = "TRUNCATED" if result["truncated"] else "ok"
        print(f"\n=== {slug} [{branch}] tree={(result['tree_sha'] or '?')[:10]} {mark}")
        for name, info in result["skills"].items():
            if str(info.get("status", "")).startswith("上游有"):
                print(f"    - {name:34s} 上游有 / 本机未装")
                continue
            print(f"    - {name:34s} {info['status']}")
            for tag, key in (("改", "changed"), ("上游增", "missing_locally"), ("本机多", "extra_locally")):
                for rel in info.get(key, [])[:6]:
                    print(f"        {tag}: {rel}")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--json", default=r"D:\Resources\DSH\_probe\skill-update-report.json")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    report = {"repos": [], "errors": []}
    for slug, branches in [r for r in REPOS if not args.repo or r[0] in args.repo]:
        try:
            report["repos"].append(check_repo(slug, branches, refresh=args.refresh))
        except Exception as exc:  # noqa: BLE001
            print(f"\n=== {slug} 失败: {exc}")
            report["errors"].append({"repo": slug, "error": str(exc)})

    print("\n========== 汇总 ==========")
    tot = {"最新": 0, "仅换行": 0, "真实差异": 0, "未装": 0}
    for r in report["repos"]:
        s = r["summary"]
        tot["最新"] += s["up_to_date"]
        tot["仅换行"] += s["crlf_only"]
        tot["真实差异"] += s["outdated"]
        tot["未装"] += s["not_installed"]
        print(f"  {r['repo']:42s} 最新 {s['up_to_date']:3d} | 仅换行 {s['crlf_only']:3d} | 真实差异 {s['outdated']:3d} | 未装 {s['not_installed']:3d}")
    print(f"  合计：最新 {tot['最新']} / 仅换行差异 {tot['仅换行']} / 真实差异 {tot['真实差异']} / 上游有本机无 {tot['未装']}")
    if report["errors"]:
        print(f"  失败 {len(report['errors'])}：{', '.join(e['repo'] for e in report['errors'])}")
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(f"  报告 -> {args.json}")


if __name__ == "__main__":
    main()
