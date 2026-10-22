# -*- coding: utf-8 -*-
"""把 vision-router 的 httpProviders 换成一批候选 VL 模型 id，一次调用即可试出可用的那个。"""
import re, shutil
P = r"C:\Users\Administrator\.dsh\profiles\desktop\cordis.patch.yml"
t = open(P, "rb").read().decode("utf-8")

CAND = [
    "Qwen/Qwen3-VL-32B-Instruct",
    "Qwen/Qwen3-VL-8B-Instruct",
    "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen3-VL-235B-A22B-Instruct",
]
block = "    httpProviders:\n" + "".join(
    "      - name: siliconflow\n"
    "        baseURL: https://api.siliconflow.cn/v1\n"
    "        model: %s\n"
    "        apiKeyEnv: IMAGE_GEN_SILICONFLOW_API_KEY\n"
    "        maxTokens: 4096\n" % m for m in CAND)

i = t.index("- id: vision-router")
j = t.index("    httpProviders:", i)
k = t.index("\n\n", j) if "\n\n" in t[j:] else len(t)
# 找到该块结束（下一个顶层 "- id:"）
nxt = t.index("\n- id:", j)
new = t[:j] + block.rstrip("\n") + t[nxt:]
open(P, "wb").write(new.encode("utf-8"))
print("候选数:", len(CAND))
print("新文件:", len(new.encode("utf-8")), "B")
