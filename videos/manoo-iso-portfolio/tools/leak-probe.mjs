// Dev tool: steps the world through the film frame by frame and logs time + memory, to find leaks/stalls.
// usage: node tools/leak-probe.mjs <playwright-core dir> [fromFrame] [toFrame] [step]
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
const require = createRequire(process.argv[2] + "/");
const { chromium } = require("playwright-core");
const from = Number(process.argv[3] ?? 0), to = Number(process.argv[4] ?? 1080), step = Number(process.argv[5] ?? 1);
const server = spawn("python3", ["-m", "http.server", "8766", "--bind", "127.0.0.1"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 900));
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--enable-precise-memory-info"] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on("pageerror", (e) => console.log("pageerror", e.message));
await page.goto("http://127.0.0.1:8766/tools/photo-export.html");
await page.waitForFunction(() => window.__manooWorld && window.__manooWorld.ready, null, { timeout: 60000 });
await page.evaluate(async () => { await window.__manooWorld.ready; });
const cdp = await page.context().newCDPSession(page);
for (let f = from; f <= to; f += step) {
  const t0 = Date.now();
  const info = await page.evaluate((t) => {
    window.__manooWorld.renderAt(t);
    const m = performance.memory;
    return { heap: Math.round(m.usedJSHeapSize / 1048576) };
  }, f / 30);
  const dt = Date.now() - t0;
  if (f % 30 === 0 || dt > 4000) {
    const { metrics } = await cdp.send("Performance.getMetrics").catch(() => ({ metrics: [] }));
    const nodes = (metrics.find((m) => m.name === "Nodes") || {}).value;
    console.log(`frame ${f} t=${(f / 30).toFixed(2)} ${dt}ms heap=${info.heap}MB nodes=${nodes}`);
  }
}
console.log("done");
await browser.close();
server.kill();
