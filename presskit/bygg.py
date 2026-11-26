"""Bygger presskittets PDF från presskit/presskit.html.

Kör från repots rot:  python3 presskit/bygg.py
1. Gör om de bilder som används till jpg (presskit/jpg/, checkas inte in), så att PDF:en blir liten.
2. Skriver ut sidan med Chromium till assets/press/Hallfjallet-Press-Kit-2026.pdf
"""
import pathlib, re, subprocess, json
from PIL import Image

ROT = pathlib.Path(__file__).resolve().parent.parent
KALLA = ROT / "presskit" / "presskit.html"
JPG = ROT / "presskit" / "jpg"
UT = ROT / "assets" / "press" / "Hallfjallet-Press-Kit-2026.pdf"
JPG.mkdir(exist_ok=True)
UT.parent.mkdir(exist_ok=True)

for namn in sorted(set(re.findall(r'jpg/([\w-]+)\.jpg', KALLA.read_text()))):
    storlekar = sorted(ROT.glob(f"assets/img/{namn}-*.webp"), key=lambda p: Image.open(p).width)
    im = Image.open(storlekar[-1]).convert("RGB")
    im.thumbnail((2000, 2000), Image.LANCZOS)
    im.save(JPG / f"{namn}.jpg", quality=80, optimize=True, progressive=True)

# Utskriften görs med Playwright för Node (finns i molnmiljön)
js = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const s = await b.newPage();
  await s.goto(%s, { waitUntil: 'networkidle' });
  await s.evaluate(() => document.fonts.ready);
  await s.pdf({ path: %s, width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
""" % (json.dumps(KALLA.as_uri()), json.dumps(str(UT)))
subprocess.run(["node", "-e", js], check=True)
print(UT, round(UT.stat().st_size / 1e6, 1), "MB")
