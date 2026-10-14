// Export the portfolio photos from the 3D atelier (shots/atelier) as graded JPEGs in assets/photos/.
// Usage (from the project root): node tools/export-stills.cjs
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const http = require("http"), fs = require("fs"), path = require("path");
const root = path.resolve(__dirname, "../shots/atelier");
const out = path.resolve(__dirname, "../assets/photos");
const NAMES = ["jules-portail", "portail-detail", "garde-corps", "escalier"];
const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg" };
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split("?")[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { "Content-Type": types[path.extname(p)] || "application/octet-stream" }); res.end(d); });
}).listen(0, async () => {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
  await page.waitForFunction(() => window.__atelierStill, null, { timeout: 30000 });
  for (const name of NAMES) {
    const jpg = await page.evaluate(async (name) => {
      const src = window.__atelierStill(name, 1200, 900);
      const img = new Image();
      img.src = src;
      await img.decode();
      const c = document.createElement("canvas");
      c.width = 1200;
      c.height = 900;
      const g = c.getContext("2d");
      g.filter = "saturate(1.06) contrast(1.04)";
      g.drawImage(img, 0, 0);
      g.filter = "none";
      // phone-photo grade: warm lift + soft vignette
      g.fillStyle = "rgba(255,214,170,0.06)";
      g.fillRect(0, 0, 1200, 900);
      const v = g.createRadialGradient(600, 450, 260, 600, 450, 820);
      v.addColorStop(0, "rgba(0,0,0,0)");
      v.addColorStop(1, "rgba(20,14,10,0.28)");
      g.fillStyle = v;
      g.fillRect(0, 0, 1200, 900);
      return c.toDataURL("image/jpeg", 0.9);
    }, name);
    fs.writeFileSync(path.join(out, name + ".jpg"), Buffer.from(jpg.split(",")[1], "base64"));
    console.log("wrote", name);
  }
  await browser.close();
  srv.close();
});
