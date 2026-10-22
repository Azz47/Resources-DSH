# -*- coding: utf-8 -*-
"""给 vision-router 配一条真 Key 的视觉后端（硅基流动，复用 image-gen 已存的凭据名）。
   只插入 YAML 行，其余字节不动；幂等。"""
import io, os, shutil, sys

P = r"C:\Users\Administrator\.dsh\profiles\desktop\cordis.patch.yml"
raw = open(P, "rb").read()
text = raw.decode("utf-8")
if "httpProviders" in text:
    print("SKIP  已存在 httpProviders，未改动"); sys.exit(0)

anchor = "- id: vision-router"
i = text.index(anchor)
j = text.index("onboardingSeen: true", i) + len("onboardingSeen: true")
insert = (
    "\n"
    "    # ── 视觉后端（2026-10-14 修）─────────────────────────────────\n"
    "    # 内置默认只挂了 OVHcloud 匿名链：DSH 的会话亲和层对非 openrouter 端点\n"
    "    # 一律按 'openai' 格式下发 prompt_cache_key，而 OVH 该字段直接 400\n"
    "    # (\"feature 'prompt_cache_key' is not currently supported\")，5 个模型全灭。\n"
    "    # 这里把硅基流动提到链首（复用 image-gen 已保存的同名凭据，无需新 Key），\n"
    "    # OVH 匿名层保留为兜底。\n"
    "    httpProviders:\n"
    "      - name: siliconflow\n"
    "        baseURL: https://api.siliconflow.cn/v1\n"
    "        model: Qwen/Qwen2.5-VL-32B-Instruct\n"
    "        apiKeyEnv: IMAGE_GEN_SILICONFLOW_API_KEY\n"
    "        maxTokens: 4096\n"
    "      - name: siliconflow\n"
    "        baseURL: https://api.siliconflow.cn/v1\n"
    "        model: Qwen/Qwen2.5-VL-7B-Instruct\n"
    "        apiKeyEnv: IMAGE_GEN_SILICONFLOW_API_KEY\n"
    "        maxTokens: 4096\n"
)
shutil.copy2(P, P + ".bak-20261014")
new = text[:j] + insert + text[j:]
open(P, "wb").write(new.encode("utf-8"))
print("OK    已写入；备份 -> cordis.patch.yml.bak-20261014")
print("原 %d B -> 新 %d B" % (len(raw), len(new.encode('utf-8'))))
