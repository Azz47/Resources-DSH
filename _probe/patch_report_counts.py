"""修正报告里两个被少算的行数，并补一条「量行数的坑」记录。定点替换，命中次数必须精确。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"D:\Resources\DSH\环境盘点与整合方案.md"
text = io.open(P, encoding="utf-8").read()

CAVEAT = (
    "- **量行数的坑（本次踩到）**：本机 `pwsh` 的 `Get-Content` 会用系统 GBK 码页解码 UTF-8 文件（中文变乱码），"
    "并把部分换行字节当作双字节字符的尾字节吃掉 → **行数会被少算**（同一文件：`Get-Content` 报 288 行，"
    "python 实数 **347 行**）。行数一律用 python 数 `\\n`（`open(f,'rb').read().decode('utf-8').count('\\n')`）；"
    "`Get-Item.Length` 的**字节数可信**，`(Get-Content).Count` 的行数**不可信**。"
)

for old, new, expect in [
    ("17,318 B / 229 行", "17,318 B / 309 行", 2),
    ("3,916 B / 107 行", "3,916 B / 111 行", 2),
]:
    n = text.count(old)
    assert n == expect, "命中 %d 次（应为 %d）: %r" % (n, expect, old)
    text = text.replace(old, new)
    print("替换 %r → %r  ×%d" % (old, new, n))

assert "Get-Content" not in text, "已存在同类记录，勿重复追加"
text = text.rstrip("\n") + "\n" + CAVEAT + "\n"

io.open(P, "w", encoding="utf-8", newline="\n").write(text)
b = text.encode("utf-8")
print("报告现 %d B / %d 行" % (len(b), text.count("\n")))
