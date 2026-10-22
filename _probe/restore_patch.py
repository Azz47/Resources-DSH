"""恢复 desktop profile 的 cordis.patch.yml：删掉 dsh-fix 批量禁用块。

背景：2026-10-07T16:57:38.523Z 时 dsh-fix 把 patch 里所有自定义配置项都加了
`- id: "xxx"  disabled: true`。其中 locale 被禁会让桌面端读不到 locale namespace，
readWelcomeState() 抛 "desktop welcome: invalid locale preference"，openInitialWindow()
直接失败 —— 表现就是"只有托盘图标、没有窗口、没有日志"。

本脚本只删「# dsh-fix: disabled entry ...」注释行与其后紧邻的
`- id: "..."` + `  disabled: true` 两行；其余内容一字不动。
"""
import io
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

P = r"C:\Users\Administrator\.dsh\profiles\desktop\cordis.patch.yml"
BAK = P + ".bak-before-dshfix-restore"

raw = io.open(P, encoding="utf-8").read()
shutil.copyfile(P, BAK)
print("备份: " + BAK)
print("原始: %d 字节 / %d 行" % (len(raw.encode("utf-8")), len(raw.split("\n"))))

lines = raw.split("\n")
out, dropped, i = [], [], 0
while i < len(lines):
    line = lines[i]
    # 匹配 "# dsh-fix: disabled entry "xxx" at ..."
    if re.match(r'^#\s*dsh-fix:\s*disabled entry', line):
        block = [line]
        j = i + 1
        # 吃紧随其后的 `- id: "xxx"` 与 `  disabled: true`
        if j < len(lines) and re.match(r'^-\s*id:\s*"', lines[j]):
            block.append(lines[j])
            j += 1
        if j < len(lines) and re.match(r'^\s+disabled:\s*true\s*$', lines[j]):
            block.append(lines[j])
            j += 1
        dropped.append(block[1].strip() if len(block) > 1 else line.strip())
        i = j
        continue
    out.append(line)
    i += 1

# 去掉尾部多余空行
while out and out[-1].strip() == "":
    out.pop()
text = "\n".join(out) + "\n"
io.open(P, "w", encoding="utf-8", newline="\n").write(text)

print("恢复后: %d 字节 / %d 行" % (len(text.encode("utf-8")), len(text.split("\n"))))
print("移除的禁用条目 (%d 个):" % len(dropped))
for d in dropped:
    print("   " + d)
print()
print("剩余 locale 配置是否还在:")
for key in ("- id: locale", "preference: zh", "- id: image-gen", "siliconflow",
            "- id: agency-agents", "- id: permission"):
    print("   %-24s %s" % (key, "有" if key in text else "缺失"))
