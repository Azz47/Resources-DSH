#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比 profile 里已装插件包与 npm registry 的 latest 版本，报告可更新项。

用法：python check_plugin_updates.py [--json 输出路径]
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROFILE = r"C:\Users\Administrator\.dsh\profiles\desktop"
PKG_JSON = os.path.join(PROFILE, "package.json")
NODE_MODULES = os.path.join(PROFILE, "node_modules")


def npm_latest(name):
    url = "https://registry.npmjs.org/" + urllib.parse.quote(name, safe="") + "/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "dsh-plugin-update-check"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp).get("version")


def installed_version(name):
    p = os.path.join(NODE_MODULES, *name.split("/"), "package.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh).get("version")
        except Exception:  # noqa: BLE001
            return None
    return None


def parse_ver(v):
    if not v:
        return ()
    core = v.split("+")[0].split("-")[0]
    out = []
    for part in core.split("."):
        num = "".join(ch for ch in part if ch.isdigit())
        out.append(int(num) if num else 0)
    return tuple(out)


def parse_tarball(spec):
    """codeload.github.com/<owner>/<repo>/tar.gz/<ref> → (owner, repo, ref)；不是则 None。"""
    m = re.match(r"https?://codeload\.github\.com/([^/]+)/([^/]+)/tar\.gz/(.+)$", spec or "")
    if not m:
        return None
    return m.group(1), m.group(2), re.sub(r"^refs/heads/", "", m.group(3))


def gh_commit(owner, repo, ref):
    """GitHub API 查 commit（无 token，60 次/时限）；失败返回 None。"""
    url = "https://api.github.com/repos/%s/%s/commits/%s" % (
        owner, repo, urllib.parse.quote(ref, safe=""))
    req = urllib.request.Request(url, headers={
        "User-Agent": "dsh-plugin-update-check",
        "Accept": "application/vnd.github+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.load(resp)
    except Exception:  # noqa: BLE001
        return None
    return {
        "sha": data.get("sha") or "",
        "date": ((data.get("commit") or {}).get("committer") or {}).get("date", "")[:10],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=r"D:\Resources\DSH\_probe\plugin-update-report.json")
    args = ap.parse_args()

    with open(PKG_JSON, encoding="utf-8-sig") as fh:
        pkg = json.load(fh)
    deps = pkg.get("dependencies", {})
    bundles = ((pkg.get("dsh") or {}).get("profile") or {}).get("bundles") or []
    rows, errors = [], []
    for name, spec in sorted(deps.items()):
        inst = installed_version(name)
        latest = None
        tb = parse_tarball(spec)
        local = spec.startswith(("file:", "link:", "workspace:"))
        if tb:
            owner, repo, ref = tb
            info = gh_commit(owner, repo, ref)
            if re.fullmatch(r"[0-9a-f]{40}", ref or ""):
                latest = ref[:7]
                if info:
                    status = f"codeload 钉死 commit {ref[:7]}｜GitHub 可解析=是"
                else:
                    status = f"codeload 钉死 commit {ref[:7]}｜GitHub 查不到（可能已 force-push）"
                    errors.append({"pkg": name, "error": f"commit {ref[:7]} 未解析"})
            elif info:
                latest = info["sha"][:7]
                status = f"跟随分支 {ref}｜上游 HEAD {info['sha'][:7]} ({info['date']})"
            else:
                status = f"跟随分支 {ref}｜GitHub 查询失败"
                errors.append({"pkg": name, "error": "GitHub API 查询失败"})
        elif local:
            status = "本地路径依赖，无 npm 版本"
        else:
            try:
                latest = npm_latest(name)
            except Exception as exc:  # noqa: BLE001
                errors.append({"pkg": name, "error": str(exc)})
                status = "查询失败"
        if latest and inst and not tb and not local:
            if parse_ver(latest) > parse_ver(inst):
                status = f"可更新 -> {latest}"
            elif parse_ver(latest) == parse_ver(inst):
                status = "已是最新"
            else:
                status = f"本机更新 (npm {latest})"
        elif latest and not inst:
            status = "未安装到 node_modules"
        rows.append({
            "pkg": name,
            "declared": spec,
            "installed": inst,
            "latest": latest,
            "in_bundles": name in bundles,
            "status": status,
        })

    print(f"{'插件包':46s} {'已装':12s} {'npm latest':12s} {'bundles':7s} 状态")
    print("-" * 110)
    outdated = []
    for r in rows:
        print(f"{r['pkg']:46s} {str(r['installed']):12s} {str(r['latest']):12s} {'是' if r['in_bundles'] else '否':7s} {r['status']}")
        if r["status"].startswith("可更新"):
            outdated.append(r)
    print("-" * 110)
    print(f"总计 {len(rows)} 个依赖；可更新 {len(outdated)} 个：{', '.join(r['pkg'] for r in outdated) or '无'}")
    print(f"deps={len(deps)}  bundles={len(bundles)}  deps⊆bundles={set(deps) <= set(bundles)}")
    if errors:
        print(f"查询失败 {len(errors)}：{', '.join(e['pkg'] for e in errors)}")
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "outdated": outdated, "errors": errors}, fh, ensure_ascii=False, indent=1)
    print(f"报告 -> {args.json}")


if __name__ == "__main__":
    main()
