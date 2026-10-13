// Full-page capture of the public /welcome screen (profile-type choice), mobile viewport.
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, locale: "fr-FR" });
  const p = await ctx.newPage();
  await p.goto("https://manoo.fr/welcome", { waitUntil: "networkidle", timeout: 45000 });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: path.resolve(__dirname, "..", "capture", "app", "welcome-full.png"), fullPage: true });
  console.log(await p.evaluate(() => [document.documentElement.scrollHeight, getComputedStyle(document.body).fontFamily, getComputedStyle(document.body).backgroundColor]));
  await b.close();
})();
