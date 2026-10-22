"""从 dsh.profile.bundles 里移除指定插件（禁用），保留 dependencies 以便随时还原。"""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

P = Path(r"C:\Users\Administrator\.dsh\profiles\desktop\package.json")
BAK = P.with_suffix(".json.bak-before-plugin-consolidation")

DROP = [
    "dsh-echocat-skill-panel",
    "@michengai/dsh-skills-manager",
]

raw_bytes = P.read_bytes()
nl = "\r\n" if b"\r\n" in raw_bytes else "\n"
raw = raw_bytes.decode("utf-8")

shutil.copy2(P, BAK)
print(f"备份: {BAK}")

d = json.loads(raw)
b = d["dsh"]["profile"]["bundles"]
before = len(b)

missing = [x for x in DROP if x not in b]
if missing:
    print(f"!! 这些不在 bundles 里（跳过）: {missing}")

kept = [x for x in b if x not in DROP]
d["dsh"]["profile"]["bundles"] = kept

text = json.dumps(d, ensure_ascii=False, indent=2)
if nl == "\r\n":
    text = text.replace("\n", "\r\n")
P.write_bytes(text.encode("utf-8"))

print(f"bundles: {before} -> {len(kept)}")
for x in DROP:
    print(f"  已禁用: {x}")
print()
print("保留的技能管理插件:")
for x in kept:
    if any(k in x for k in ("skill", "run2skill", "echocat")):
        print(f"  - {x}")

# 回读校验
d2 = json.loads(P.read_text(encoding="utf-8"))
assert len(d2["dsh"]["profile"]["bundles"]) == len(kept), "回读长度不一致"
assert not any(x in d2["dsh"]["profile"]["bundles"] for x in DROP), "回读仍有被禁插件"
print()
print("回读校验: OK（JSON 合法，目标插件已移除）")
