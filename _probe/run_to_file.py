#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把另一个脚本的 stdout 以 UTF-8 落到文件，避开 pwsh 重定向的编码坑。
用法: python run_to_file.py <target.py> <out.txt>
"""
import sys, runpy, io

class _Buf(io.StringIO):
    """StringIO + 空转的 reconfigure，兼容被调用脚本里的 sys.stdout.reconfigure(...)。"""
    def reconfigure(self, *a, **kw):
        return None


target, out = sys.argv[1], sys.argv[2]
buf = _Buf()
old = sys.stdout
sys.stdout = buf
try:
    runpy.run_path(target, run_name="__main__")
finally:
    sys.stdout = old
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(buf.getvalue())
old.write(f"[written] {out} ({len(buf.getvalue())} chars)\n")
