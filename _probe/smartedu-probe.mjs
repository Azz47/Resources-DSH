const urls = [
  "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/version/data_version.json",
  "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/national_lesson/resources/tch_material/version/data_version.json",
  "https://basic.smartedu.cn/tchMaterial",
  "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/version/2024-11-27_15-33-52/list.json"
];
for (const u of urls) {
  const t = Date.now();
  try {
    const r = await fetch(u, { signal: AbortSignal.timeout(15000) });
    const txt = await r.text();
    console.log(`\n=== ${r.status} ${((Date.now()-t)/1000).toFixed(1)}s  ${u}`);
    console.log(txt.slice(0, 500).replace(/\s+/g, " "));
  } catch (e) { console.log(`\n=== ERR ${((Date.now()-t)/1000).toFixed(1)}s ${e.cause?.code || e.name}  ${u}`); }
}
