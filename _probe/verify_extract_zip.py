#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 GitHub tree API 的 blob SHA 校验 ZIP 内容并抽取指定前缀（可信校验 + 精确解包）。

用法：
  python verify_extract_zip.py --zip O.zip --tree tree.json --dest out --prefix skills/ --prefix SKILL.md

行为：
  * 从 ZIP 里读 <root>/<path>，按 git blob 定义算 sha1(b"blob <len>\\0" + data)，
    与 tree API 给的 sha 逐个比对（镜像/代理下载后的完整性证明）。
  * 只解出 tree 里登记且校验通过的文件；报告 匹配 / 不符 / ZIP 缺 / 额外文件。
  * 不做任何网络请求。
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--prefix", action="append", default=[])
    ap.add_argument("--strip", default="", help="ZIP 内该路径前缀（相对仓库根）也一并剥掉，"
                                                "使 tree 的相对路径与 ZIP 条目对齐")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    with open(args.tree, encoding="utf-8") as fh:
        tree = json.load(fh)
    blobs = {e["path"]: e["sha"] for e in tree.get("tree", []) if e.get("type") == "blob"}
    if args.prefix:
        wanted = {p: s for p, s in blobs.items()
                  if any(p.startswith(x) if x.endswith("/") else p == x for x in args.prefix)}
    else:
        wanted = dict(blobs)

    zf = zipfile.ZipFile(args.zip)
    names = zf.namelist()
    root = names[0].split("/")[0] + "/" if names else ""
    strip = root + args.strip
    by_rel = {}
    for n in names:
        if n.endswith("/"):
            continue
        if n.startswith(strip):
            by_rel[n[len(strip):]] = n
        elif n.startswith(root):
            by_rel[n[len(root):]] = n

    ok = bad = missing = 0
    bad_list, miss_list = [], []
    for path, sha in sorted(wanted.items()):
        entry = by_rel.get(path)
        if entry is None:
            missing += 1
            miss_list.append(path)
            continue
        data = zf.read(entry)
        if blob_sha(data) == sha:
            ok += 1
            out = os.path.join(args.dest, path.replace("/", os.sep))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as fh:
                fh.write(data)
        else:
            bad += 1
            bad_list.append(path)

    extra = sorted(p for p in by_rel if p not in blobs)
    print(f"ZIP root={root!r}  登记 {len(wanted)}  校验通过并解出 {ok}  哈希不符 {bad}  ZIP 缺 {missing}")
    for p in bad_list[:10]:
        print(f"   ! 哈希不符 {p}")
    for p in miss_list[:10]:
        print(f"   ! ZIP 缺 {p}")
    if extra:
        print(f"   额外（tree 未登记、已跳过）{len(extra)}：{extra[:8]}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"zip": args.zip, "tree": args.tree, "verified": ok, "mismatch": bad,
                       "missing": missing, "bad": bad_list, "missing_list": miss_list,
                       "extra_count": len(extra)}, fh, ensure_ascii=False, indent=1)
    return 0 if (bad == 0 and missing == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
