# -*- coding: utf-8 -*-
"""收敛：只保留实测可用的那个 VL 模型（OVH 匿名层由 freeFallback 自动兜底）。"""
P = r"C:\Users\Administrator\.dsh\profiles\desktop\cordis.patch.yml"
t = open(P, "rb").read().decode("utf-8")
i = t.index("- id: vision-router"); j = t.index("    httpProviders:", i); nxt = t.index("\n- id:", j)
block = ("    httpProviders:\n"
         "      - name: siliconflow\n"
         "        baseURL: https://api.siliconflow.cn/v1\n"
         "        model: Qwen/Qwen3-VL-32B-Instruct\n"
         "        apiKeyEnv: IMAGE_GEN_SILICONFLOW_API_KEY\n"
         "        maxTokens: 4096\n")
new = t[:j] + block.rstrip("\n") + t[nxt:]
open(P, "wb").write(new.encode("utf-8"))
print("vision-router 已收敛为 1 条可用后端；文件 %d B" % len(new.encode("utf-8")))
