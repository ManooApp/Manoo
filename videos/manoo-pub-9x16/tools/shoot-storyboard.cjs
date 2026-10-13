// Screenshots every storyboard cell's 9:16 frame at 1080x1920 (3x a 360px cell).
// NODE_PATH must reach a Playwright install (the global one works).
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

(async () => {
  const root = path.resolve(__dirname, "..");
  const out = path.join(root, "review", process.argv[2] || "storyboard-v1");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1640, height: 1200 }, deviceScaleFactor: 3 });
  await page.goto("file://" + path.join(root, "storyboard.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  for (const cell of await page.$$("section.cell")) {
    const id = await cell.getAttribute("id");
    const frame = await cell.$(".frame");
    await frame.screenshot({ path: path.join(out, id + ".png") });
    console.log("shot", id);
  }
  await browser.close();
})();
