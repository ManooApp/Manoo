// Read-only look at the public screens of the Manoo app (no form is ever submitted).
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const out = path.resolve(__dirname, "..", "capture", "app");
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, locale: "fr-FR" });
  const page = await ctx.newPage();
  const urls = process.argv.slice(2);
  for (const [i, u] of urls.entries()) {
    try {
      await page.goto(u, { waitUntil: "networkidle", timeout: 45000 });
    } catch (e) { console.log("goto", u, e.message.split("\n")[0]); }
    await page.waitForTimeout(1500);
    const name = "app-" + String(i).padStart(2, "0") + ".png";
    await page.screenshot({ path: path.join(out, name) });
    const info = await page.evaluate(() => ({
      url: location.href,
      title: document.title,
      text: document.body.innerText.slice(0, 1200),
      links: [...document.querySelectorAll("a[href]")].map(a => (a.innerText.trim() || a.getAttribute("aria-label") || "") + " -> " + a.getAttribute("href")).slice(0, 40),
      buttons: [...document.querySelectorAll("button, [role=button], ion-button")].map(b => b.innerText.trim()).filter(Boolean).slice(0, 40),
    }));
    console.log("=====", name, JSON.stringify(info, null, 1));
  }
  await browser.close();
})();
