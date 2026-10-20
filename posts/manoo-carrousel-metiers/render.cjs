// Shoots every <section class="slide"> of index.html at 2x (2160 × 2700) into exports/2x/, then
// tools in make.sh scale them to 1080 × 1350 and assemble the LinkedIn PDF.
// NODE_PATH must reach a Playwright install (here /opt/node-tools/node_modules).
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

(async () => {
  const root = __dirname;
  const out = path.join(root, "exports", "2x");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1180, height: 1450 }, deviceScaleFactor: 2 });
  await page.goto("file://" + path.join(root, "index.html"));
  await page.evaluate(async () => {
    const faces = ["400 20px Inter", "500 20px Inter", "600 20px Inter", "700 20px Inter", "800 20px Inter",
      '600 20px "Inter Display"', '700 20px "Inter Display"', '800 20px "Inter Display"'];
    await Promise.all(faces.map((f) => document.fonts.load(f)));
    await document.fonts.ready;
    await Promise.all(Array.from(document.images).map((img) => (img.complete ? null : new Promise((r) => { img.onload = img.onerror = r; }))));
  });
  await page.waitForTimeout(300);
  const only = process.argv.slice(2);
  for (const slide of await page.$$("section.slide")) {
    const id = await slide.getAttribute("id");
    if (only.length && !only.includes(id)) continue;
    await slide.screenshot({ path: path.join(out, id + ".png") });
    console.log("shot", id);
  }
  await browser.close();
})();
