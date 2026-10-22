const H = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  "Referer": "https://basic.smartedu.cn/",
  "Origin": "https://basic.smartedu.cn",
  "Accept": "application/json, text/plain, */*",
  "Accept-Language": "zh-CN,zh;q=0.9",
};
const urls = [
  "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/version/data_version.json",
  "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/national_lesson/resources/tch_material/version/data_version.json",
  "https://s-file-2.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/version/data_version.json",
  "https://basic.smartedu.cn/api/tchMaterial",
];
for (const u of urls) {
  try {
    const r = await fetch(u, { headers: H, signal: AbortSignal.timeout(15000) });
    const t = await r.text();
    console.log(`\n=== ${r.status}  ${u}`);
    console.log(t.slice(0, 420).replace(/\s+/g, " "));
  } catch (e) { console.log(`\n=== ERR ${e.cause?.code || e.name}  ${u}`); }
}
