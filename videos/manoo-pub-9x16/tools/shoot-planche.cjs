const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const root = path.resolve(__dirname, "..");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2280, height: 1400 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(root, "review", "planche.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  for (const id of ["p1", "p2"]) {
    await (await page.$("#" + id)).screenshot({ path: path.join(root, "review", `planche-v1-${id}.png`) });
    console.log("shot", id);
  }
  await browser.close();
})();
