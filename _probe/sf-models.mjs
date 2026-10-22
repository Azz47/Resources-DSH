const k = process.env.SF_KEY;
try {
  const r = await fetch("https://api.siliconflow.cn/v1/models?sub_type=text-to-image", {
    headers: { Authorization: `Bearer ${k}` }, signal: AbortSignal.timeout(20000) });
  const j = await r.json();
  console.log("HTTP", r.status);
  const imgs = (j.data || []).filter(m => /kolors|flux|stable|qwen-image|image/i.test(m.id));
  console.log(`生图类模型 ${imgs.length} 个（前 25）:`);
  imgs.slice(0, 25).forEach(m => console.log("   " + m.id));
} catch (e) { console.log("ERR", e.cause?.code || e.name, e.message); }
