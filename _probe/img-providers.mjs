const hosts = [
 ["OpenAI 官方",      "https://api.openai.com/v1/models"],
 ["xAI 官方",         "https://api.x.ai/v1/models"],
 ["Gemini 官方",      "https://generativelanguage.googleapis.com/v1beta/models"],
 ["阿里 DashScope",   "https://dashscope.aliyuncs.com/compatible-mode/v1/models"],
 ["火山方舟(豆包)",   "https://ark.cn-beijing.volces.com/api/v3/models"],
 ["智谱 BigModel",    "https://open.bigmodel.cn/api/paas/v4/models"],
 ["硅基流动",         "https://api.siliconflow.cn/v1/models"],
 ["百度千帆",         "https://qianfan.baidubce.com/v2/models"],
];
for (const [name, u] of hosts) {
  const t = Date.now();
  try {
    const r = await fetch(u, { signal: AbortSignal.timeout(9000) });
    console.log(`${name.padEnd(18)} HTTP ${r.status}  ${(Date.now()-t)}ms`);
  } catch (e) {
    console.log(`${name.padEnd(18)} ✗ ${e.cause?.code || e.name}  ${(Date.now()-t)}ms`);
  }
}
