// 在 Node 里模拟宿主 ModuleLoader，执行插件 client 包，捕获 factory 内抛出的真实异常。
// 用法: node load_client_module.js <client.js>
const fs = require("fs");
const vm = require("vm");

const file = process.argv[2];
if (!file) { console.error("usage: node load_client_module.js <client.js>"); process.exit(2); }

const missing = new Set();
function proxy(name) {
  const fn = function () { return proxy(name + "()"); };
  return new Proxy(fn, {
    get(t, k) {
      if (k === Symbol.toPrimitive) return () => 0;
      if (k === "then") return undefined;
      if (k === "toString") return () => name;
      if (typeof k === "symbol") return undefined;
      return proxy(name + "." + String(k));
    },
    apply() { return proxy(name + "()"); },
    construct() { return proxy("new " + name); },
  });
}
const requireStub = (spec) => { missing.add(spec); return proxy(spec); };

global.window = global;
global.self = global;
const el = () => ({ style: {}, dataset: {}, setAttribute() {}, appendChild() {}, append() {}, addEventListener() {}, removeEventListener() {}, remove() {}, classList: { add() {}, remove() {}, toggle() {} }, querySelector: () => null, querySelectorAll: () => [], getBoundingClientRect: () => ({ width: 100, height: 100, top: 0, left: 0 }) });
global.document = { createElement: el, createElementNS: el, head: el(), body: el(), documentElement: el(), querySelector: () => null, querySelectorAll: () => [], addEventListener() {}, getElementById: () => null, createTextNode: () => ({}) };
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
global.navigator = { userAgent: "node", language: "zh-CN" };
global.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
global.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
global.IntersectionObserver = global.ResizeObserver;
global.requestAnimationFrame = (cb) => setTimeout(cb, 0);
global.cancelAnimationFrame = clearTimeout;

let loaded = 0;
global.window.__ModuleLoader__ = {
  load(mod) {
    try {
      const out = mod.factory(requireStub);
      loaded++;
      console.log("LOADED:", mod.id);
      if (out && typeof out === "object") console.log("  exports keys:", Object.keys(out).slice(0, 10).join(","));
    } catch (e) {
      console.log("THREW:", mod.id);
      console.log("  message:", e && e.message);
      const stack = (e && e.stack || "").split("\n").slice(0, 10).join("\n");
      console.log(stack);
    }
  },
  register() {},
  define() {},
};

const code = fs.readFileSync(file, "utf8");
try {
  vm.runInThisContext(code, { filename: file });
  console.log("top-level ok; loaded=", loaded, "| distinct require specifiers=", [...missing].slice(0, 8).join(", "));
} catch (e) {
  console.log("TOPLEVEL THREW:", e && e.message);
  console.log((e && e.stack || "").split("\n").slice(0, 10).join("\n"));
}
