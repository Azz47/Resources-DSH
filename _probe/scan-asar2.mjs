const fs = require("fs");
const f = "D:\\tools\\dsh\\resources\\app.asar";
const buf = fs.readFileSync(f);
for (const needle of ["--throw-deprecation", "throw-deprecation", "DEP0180", "deprecation"]) {
  const nb = Buffer.from(needle);
  let i = 0, n = 0;
  while (n < 3) { i = buf.indexOf(nb, i); if (i === -1) break;
    console.log(`\n=== [${needle}] @${i} ===`);
    console.log(buf.slice(Math.max(0,i-200), i+260).toString("utf8").replace(/[^\x20-\x7e\n\r\t]/g,"."));
    i += nb.length; n++; }
  console.log(`--- [${needle}] hits: ${n}`);
}
