// Dev tool: exports the in-world réalisation photos to assets/photos/*.jpg
// usage: node tools/export-photos.mjs <playwright-core dir> (serves the project on :8765)
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
const require = createRequire(process.argv[2] + "/");
const { chromium } = require("playwright-core");
const server = spawn("python3", ["-m", "http.server", "8765", "--bind", "127.0.0.1"], { stdio: "ignore" });
await new Promise((r) => setTimeout(r, 900));
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on("pageerror", (e) => console.error("pageerror", e.message));
await page.goto("http://127.0.0.1:8765/tools/photo-export.html");
await page.waitForFunction(() => window.__manooWorld && window.__manooWorld.ready, null, { timeout: 60000 });
const out = await page.evaluate(async () => {
  await window.__manooWorld.ready;
  const ph = window.__manooWorld.photos;
  const o = {};
  for (const k of Object.keys(ph)) o[k] = ph[k].map((c) => c.toDataURL("image/jpeg", 0.9));
  return o;
});
mkdirSync("assets/photos", { recursive: true });
for (const [k, arr] of Object.entries(out)) arr.forEach((d, i) => writeFileSync(`assets/photos/${k}${i}.jpg`, Buffer.from(d.split(",")[1], "base64")));
console.log("exported", Object.values(out).flat().length);
await browser.close();
server.kill();
