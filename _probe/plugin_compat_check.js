// Check every installed desktop-profile plugin against the running DSH build.
//   node _probe/plugin_compat_check.js [--json]
// Answers: does this plugin's client half resolve for the host, does it parse,
// are its peer ranges satisfied, and was it written after the app booted (which
// invalidates the client-module revision -> the entry cannot activate until restart).
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const PROFILE = "C:/Users/Administrator/.dsh/profiles/desktop";
const semver = require("C:/Program Files/nodejs/node_modules/npm/node_modules/semver");

// Versions the 0.2.1-rc.2 app.asar actually provides (read out of the archive).
const HOST = {
  "@deepseek-ai/cordis": "4.0.5",
  "@deepseek-ai/schemastery": "3.18.5"
};
const HOST_CORE = "0.2.1-rc.2";

const pkg = JSON.parse(fs.readFileSync(path.join(PROFILE, "package.json"), "utf8"));
const deps = Object.keys(pkg.dependencies || {});
const readJson = (p) => { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return null; } };
const installed = (name) => readJson(path.join(PROFILE, "node_modules", name, "package.json"));

function hostVersion(peer) {
  if (HOST[peer]) return HOST[peer];
  if (peer.startsWith("@deepseek-ai/")) return HOST_CORE;
  const local = installed(peer);
  return local && local.version;
}

const rows = [];
for (const name of deps) {
  const meta = installed(name);
  const row = { name, version: meta && meta.version, notes: [], errors: [], mtime: 0 };
  if (!meta) { row.errors.push("未安装"); rows.push(row); continue; }

  const decl = meta.dsh && meta.dsh.client;
  const exp = meta.exports && meta.exports["./client"];
  const rel = typeof exp === "string" ? exp : exp && typeof exp.default === "string" ? exp.default : undefined;

  if (!decl) {
    row.notes.push("服务端插件（无客户端）");
  } else {
    if (decl.platform !== "web") row.errors.push(`dsh.client.platform=${decl.platform}，不参与 web 装载`);
    if (!rel) row.errors.push('声明了 dsh.client 但缺 exports["./client"]');
    else {
      const file = path.join(PROFILE, "node_modules", name, rel);
      if (!fs.existsSync(file)) row.errors.push("client 文件不存在: " + rel);
      else {
        const st = fs.statSync(file);
        row.clientRel = rel;
        row.bytes = st.size;
        row.mtime = st.mtimeMs;
        try { new vm.Script(fs.readFileSync(file, "utf8"), { filename: file }); }
        catch (error) { row.errors.push("语法错误: " + String(error.message).slice(0, 140)); }
      }
    }
  }

  for (const [peer, range] of Object.entries(meta.peerDependencies || {})) {
    const have = hostVersion(peer);
    if (!have) {
      const optional = meta.peerDependenciesMeta && meta.peerDependenciesMeta[peer] && meta.peerDependenciesMeta[peer].optional;
      row.notes.push(`peer ${peer} 未安装${optional ? "（optional）" : ""}`);
      continue;
    }
    try {
      if (!semver.satisfies(have, range, { includePrerelease: true }))
        row.errors.push(`peer 不满足 ${peer}: 需要 ${range}，实际 ${have}`);
    } catch { row.errors.push(`peer 区间无法解析 ${peer}@${range}`); }
  }

  const engines = meta.engines && meta.engines.node;
  if (engines) {
    try {
      if (!semver.satisfies(process.version.replace(/^v/, ""), engines, { includePrerelease: true }))
        row.errors.push(`engines.node 不满足 需要 ${engines}，实际 ${process.version}`);
    } catch { /* ignore */ }
  }
  if (!row.errors.length) row.notes.unshift("OK");
  rows.push(row);
}

// Any client file newer than the app process means the running server built its
// bundle revision from older file metadata: the entry 404s until a restart.
let startedAt = 0;
try {
  const { execSync } = require("child_process");
  const out = execSync(
    'powershell -NoProfile -Command "(Get-Process -Name \'DeepSeek Harness\' -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -First 1).StartTime.ToString(\'o\')"',
    { encoding: "utf8" }
  ).trim();
  if (out) startedAt = new Date(out).getTime();
} catch { /* best effort */ }
if (startedAt) for (const row of rows) if (row.mtime && row.mtime > startedAt) row.staleAfterBoot = true;

// Runtime evidence: the host writes crash-*-web-boot.log only when a boot has
// entries that failed to activate, so freshness of that file outranks any
// declaration-level finding above.
let lastBootCrash = 0;
try {
  const dir = "C:/Users/Administrator/AppData/Roaming/@deepseek-ai/dsh-desktop/logs";
  for (const name of fs.readdirSync(dir)) {
    if (!/^crash-.*-web-boot\.log$/.test(name)) continue;
    const t = fs.statSync(path.join(dir, name)).mtimeMs;
    if (t > lastBootCrash) lastBootCrash = t;
  }
} catch { /* logs dir may not exist */ }
const bootClean = startedAt > 0 && lastBootCrash < startedAt;

if (process.argv.includes("--json")) {
  console.log(JSON.stringify({ hostCore: HOST_CORE, startedAt, lastBootCrash, bootClean, rows }, null, 2));
} else {
  const bad = rows.filter((r) => r.errors.length);
  const warn = rows.filter((r) => !r.errors.length && r.notes.some((n) => n.includes("未安装")));
  console.log(`host core ${HOST_CORE} · cordis ${HOST["@deepseek-ai/cordis"]} · schemastery ${HOST["@deepseek-ai/schemastery"]}`);
  console.log(`app started ${startedAt ? new Date(startedAt).toISOString() : "?"} · plugins ${rows.length}`);
  console.log(`声明不匹配 ${bad.length}（不阻断加载）/ 仅提示 ${warn.length} / 正常 ${rows.length - bad.length - warn.length}`);
  console.log(bootClean
    ? "runtime        : 本次启动后没有 web-boot 崩溃日志 -> 客户端条目全部激活"
    : `runtime        : 启动后仍有 web-boot 崩溃日志（${new Date(lastBootCrash).toISOString()}）`);
  console.log();
  for (const row of bad) {
    console.log(`${row.name}@${row.version || "?"}`);
    for (const e of row.errors) console.log("  x " + e);
    if (row.staleAfterBoot) console.log("  ~ 客户端文件在本次启动后被改写：重启应用即可恢复");
  }
  const stale = rows.filter((r) => r.staleAfterBoot).map((r) => `${r.name}@${r.version}`);
  if (stale.length) console.log(`\n启动后被改写（重启即修）: ${stale.join(", ")}`);
}
