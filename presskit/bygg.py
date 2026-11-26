"""Bygger presskittets två PDF:er (engelska och svenska).

Kör från repots rot:  python3 presskit/bygg.py

Texterna står i presskit/text-en.md och presskit/text-sv.md, ord för ord som Linda skrivit dem.
Avsnitten skiljs åt med en rad med bara ---. Ordningen bestämmer vilken sida och vilken layout
avsnittet får (se SIDOR nedan), så lägg inte till eller ta bort avsnitt utan att ändra här.
Utseendet står i presskit/presskit.css. Bilderna görs om till jpg i presskit/jpg/ (checkas inte in).
"""
import html, json, pathlib, re, subprocess
from PIL import Image

ROT = pathlib.Path(__file__).resolve().parent.parent
MAPP = ROT / "presskit"
JPG = MAPP / "jpg"
UT = ROT / "assets" / "press"

SPRAK = {
    "en": dict(fil="Hallfjallet-Press-Kit-2026-2027.pdf", folio="Hållfjället · Press kit 2026/2027", bildtexter=[
        ("The trail", "Skiing up to Hållfjället through snow-covered mountain birch, pulling a sled."),
        ("The house", "Hållfjället in autumn light, above Ottsjö in the southern Åre mountains."),
        ("Winter", "A frozen lake and snow-laden forest below the fell."),
        ("The way up", "Winter on the fell above Ottsjö, seen from a snowmobile."),
        ("The garden", "Beetroot pulled from the kitchen garden in Ottsjö."),
        ("The table", "A dish from the kitchen, with wine poured at the table."),
        ("The kitchen", "The wood-fired oven at the heart of the kitchen."),
        ("The cellar", "The wine cellar in the old boiler room."),
        ("The dining room", "Tables set for the evening, daylight through the window."),
        ("The rooms", "An original bunk bed with hand-painted woodwork."),
        ("The loft", "Armchairs, a chess set and a book by the window."),
        ("The people", "The Hållfjället team around the kitchen counter."),
    ]),
    "sv": dict(fil="Hallfjallet-Pressmaterial-2026-2027.pdf", folio="Hållfjället · Pressmaterial 2026/2027", bildtexter=[
        ("Leden", "På skidor upp till Hållfjället genom snöig fjällbjörkskog, med pulka."),
        ("Huset", "Hållfjället i höstljus, ovanför Ottsjö i södra Årefjällen."),
        ("Vinter", "En frusen sjö och snötyngd skog nedanför fjället."),
        ("Vägen upp", "Vinter på fjället ovanför Ottsjö, sett från snöskotern."),
        ("Odlingen", "Rödbetor från köksträdgården i Ottsjö."),
        ("Bordet", "En rätt från köket, och vin som hälls upp vid bordet."),
        ("Köket", "Vedugnen i hjärtat av köket."),
        ("Källaren", "Vinkällaren i det gamla pannrummet."),
        ("Matsalen", "Dukade bord inför kvällen, dagsljus genom fönstret."),
        ("Rummen", "En ursprunglig våningssäng med handmålade snickerier."),
        ("Loftet", "Fåtöljer, ett schackspel och en bok vid fönstret."),
        ("Människorna", "Laget på Hållfjället samlat kring köksbänken."),
    ]),
}
BILDOVERSIKT = ["hero-skidakare", "lodge-autumn", "hero-frusen-sjo", "dagar-skoter", "beetroot-hands", "hero-majrova",
                "hero-vedugn", "hero-vinkallare", "hero-matsal", "vaningssang", "hero-sallskapsrum", "laget"]

# (layout, bild, beskärning) per avsnitt, i samma ordning som i textfilerna
SIDOR = [
    ("omslag", "hero-fjallet-vinter-drom", "50% 40%"),
    ("lang", "hiker-ridge", "50% 50%"),
    ("raden topp", "lodge-autumn", "50% 70%"),
    ("uppslag", "vaningssang", "50% 50%"),
    ("uppslag vand", "cabbage-dark", "50% 50%"),
    ("uppslag", "hero-majrova", "50% 60%"),
    ("uppslag vand", "hero-vinkallare", "46% 50%"),
    ("folk", "laget", "50% 30%"),
    ("arstider", ["hero-frusen-sjo", "wildflowers", "beetroot-hands"], ["35% 50%", "50% 50%", "45% 50%"]),
    ("aktiviteter", ["hero-skidakare", "dagar-pimpelfiske", "dagar-hundspann-fjall", "dagar-jakt"], ["62% 55%", "50% 50%", "50% 50%", "50% 40%"]),
    ("pris", "champagne-window", "50% 50%"),
    ("fakta", "karta", "50% 50%"),
    ("kontakt", "hero-sallskapsrum-mork", "50% 50%"),
]
LOGGA = "../assets/img/hallfjallet-logo.png"


def e(t):
    return html.escape(t, quote=False).replace("'", "’")


def avsnitt(text):
    """Delar ett avsnitt i rubrik (##), underrubriker (###), fetstil-etiketter och stycken."""
    rader = [r.strip() for r in text.strip().split("\n\n")]
    ut = {"h1": None, "h2": None, "delar": []}
    for r in rader:
        if r.startswith("# "):
            ut["h1"] = r.split("\n")
        elif r.startswith("### "):
            ut["delar"].append(("h3", r[4:]))
        elif r.startswith("## "):
            ut["h2"] = r[3:]
        elif r.startswith("**") and r.endswith("**"):
            ut["delar"].append(("dt", r[2:-2]))
        elif r.startswith("> "):
            ut["delar"].append(("p", "\x00" + r[2:]))
        elif r.startswith("*") and r.endswith("*"):
            ut["delar"].append(("kursiv", r[1:-1]))
        else:
            ut["delar"].append(("p", r))
    return ut


def lank(t):
    """Gör e-post, webbadress och Instagram klickbara i PDF:en."""
    t = re.sub(r"\b([\w.+-]+@[\w-]+\.[\w.]+)", r'<a href="mailto:\1">\1</a>', t)
    t = re.sub(r"(?<![/@\w])(www\.[\w.-]+\.[a-z]{2,}(?:/[\w/-]*)?)", r'<a href="https://\1">\1</a>', t)
    t = re.sub(r"(?<![\w])@(hallfjallet_1943)", r'<a href="https://instagram.com/\1">@\1</a>', t)
    return t


def stycken(delar, slutrad=True):
    """Stycken som html. Stycken som börjar med "> " i textfilen blir en avslutande rad i versaler."""
    out = []
    for k, t in delar:
        if k != "p":
            continue
        if t.startswith("\x00"):
            out.append(f'<p class="slut">{e(t[1:])}</p>' if slutrad else f"<p>{e(t[1:])}</p>")
        else:
            out.append(f"<p>{e(t)}</p>")
    return "\n".join(out)


def bild(namn, pos):
    return f'<img class="fyll" src="jpg/{namn}.jpg" alt="" style="object-position:{pos}">'


def folio(n, sida, etikett):
    if sida == "v":
        return f'<div class="folio v"><b>{n}</b>{e(etikett)}</div>'
    return f'<div class="folio h">{e(etikett)}<b>{n}</b></div>'


def bygg_html(lang):
    cfg = SPRAK[lang]
    block = (MAPP / f"text-{lang}.md").read_text().split("\n---\n")
    assert len(block) == len(SIDOR), f"text-{lang}.md har {len(block)} avsnitt, väntade {len(SIDOR)}"
    sidor = []
    for n, (txt, (layout, b, pos)) in enumerate(zip(block, SIDOR), 1):
        a = avsnitt(txt)
        h2 = e(a["h2"] or "")
        if layout == "omslag":
            hornet = a["h1"][1] if len(a["h1"]) > 1 else ""
            sidor.append(f'''<section class="sida omslag">{bild(b, pos)}<div class="botten"></div>
  <img class="logga" src="jpg/logga-ljus.png" alt="Hållfjället"><div class="hornet">{hornet}</div>
  <div class="titel"><h1>{h2}</h1>{stycken(a["delar"], False)}</div></section>''')
        elif layout == "lang":
            sidor.append(f'''<section class="sida lang"><div class="text"><h2>{h2}</h2><div class="spalter">{stycken(a["delar"])}</div></div>
  <div class="bildyta">{bild(b, pos)}</div>{folio(n, "v", cfg["folio"])}</section>''')
        elif layout.startswith("raden"):
            rad = [t for k, t in a["delar"] if k == "kursiv"][0]
            spans = e(rad)
            sidor.append(f'''<section class="sida {layout}">{bild(b, pos)}<div class="slöja"></div><blockquote>{spans}</blockquote></section>''')
        elif layout.startswith("uppslag"):
            sida = "h" if "vand" in layout else "v"
            sidor.append(f'''<section class="sida {layout}"><div class="text"><h2>{h2}</h2>{stycken(a["delar"])}</div>
  <div class="bildyta">{bild(b, pos)}</div>{folio(n, sida, cfg["folio"])}</section>''')
        elif layout == "folk":
            sidor.append(f'''<section class="sida folk"><div class="bildyta">{bild(b, pos)}</div>
  <div class="text"><div><h2>{h2}</h2></div><div class="spalter">{stycken(a["delar"])}</div></div>{folio(n, "h", cfg["folio"])}</section>''')
        elif layout == "aktiviteter":
            # Text överst i två spalter, sedan aktiviteterna med var sin bild (som Genom årstiderna)
            intro, kol, aktuell, efter = [], [], None, ""
            for k, t in a["delar"]:
                if k == "kursiv":
                    efter = f'<p class="efter">{e(t)}</p>'
                elif k == "h3":
                    aktuell = [t, []]; kol.append(aktuell)
                elif aktuell:
                    aktuell[1].append(t)
                else:
                    intro.append((k, t))
            fyra = "".join(f'<div><div class="bildyta">{bild(b[i], pos[i])}</div><h3>{e(t)}</h3>' + "".join(f"<p>{e(p)}</p>" for p in ps) + "</div>"
                           for i, (t, ps) in enumerate(kol))
            sidor.append(f'''<section class="sida aktiviteter"><h2>{h2}</h2><div class="intro">{stycken(intro)}</div><div class="fyra">{fyra}</div>{efter}{folio(n, "v", cfg["folio"])}</section>''')
        elif layout == "arstider":
            kol, aktuell = [], None
            for k, t in a["delar"]:
                if k == "h3":
                    aktuell = [t, []]; kol.append(aktuell)
                elif aktuell:
                    aktuell[1].append(t)
            tre = "".join(f'<div><div class="bildyta">{bild(b[i], pos[i])}</div><h3>{e(t)}</h3>' + "".join(f"<p>{e(p)}</p>" for p in ps) + "</div>"
                          for i, (t, ps) in enumerate(kol))
            sidor.append(f'''<section class="sida arstider"><h2>{h2}</h2><div class="tre">{tre}</div>{folio(n, "v", cfg["folio"])}</section>''')
        elif layout == "pris":
            ar, rader, aktuell = "", [], None
            for k, t in a["delar"]:
                if k == "h3":
                    aktuell = [t, []]; rader.append(aktuell)
                elif aktuell:
                    aktuell[1].append(t)
                else:
                    ar = t
            lis = "".join(f'<li><span class="vem">{e(t)}</span><span class="vad">' + "".join(f"<span>{e(p)}</span>" for p in ps) + "</span></li>" for t, ps in rader)
            sidor.append(f'''<section class="sida pris"><div class="bildyta">{bild(b, pos)}</div>
  <div class="text"><h2>{h2}</h2><p class="ar">{e(ar)}</p><ul>{lis}</ul></div>{folio(n, "h", cfg["folio"])}</section>''')
        elif layout == "fakta":
            dl, aktuell = [], None
            for k, t in a["delar"]:
                if k == "dt":
                    aktuell = [t, []]; dl.append(aktuell)
                elif aktuell:
                    aktuell[1].append(t)
            rader = "".join(f"<dt>{e(t)}</dt><dd>" + "".join(f"<p>{lank(e(p))}</p>" for p in ps) + "</dd>" for t, ps in dl)
            sidor.append(f'''<section class="sida fakta"><div class="text"><h2>{h2}</h2><dl>{rader}</dl></div>
  <div class="bildyta">{bild(b, pos)}</div>{folio(n, "v", cfg["folio"])}</section>''')
        elif layout == "oversikt":
            info = "".join(f"<p>{e(t)}</p>" for k, t in a["delar"] if k == "p")
            figs = "".join(f'<figure><img src="jpg/{nm}.jpg" alt=""><figcaption><b>{i:02d} · {e(t)}</b>{e(c)}</figcaption></figure>'
                           for i, (nm, (t, c)) in enumerate(zip(BILDOVERSIKT, cfg["bildtexter"]), 1))
            sidor.append(f'''<section class="sida oversikt"><div class="huvudrad"><h2>{h2}</h2><div class="info">{info}</div></div>
  <div class="rutnat">{figs}</div>{folio(n, "v", cfg["folio"])}</section>''')
        elif layout == "kontakt":
            ps = [t for k, t in a["delar"] if k == "p"]
            sista = [t for k, t in a["delar"] if k == "kursiv"]
            # Grupper: namn+e-post, webb+instagram, adress
            intro = ""
            if ps and ps[0].endswith(":"):
                intro = f'<p class="intro">{e(ps[0])}</p>'; ps = ps[1:]
            grupper = [ps[0:2], ps[2:4], ps[4:]]
            g = "".join('<div class="grupp">' + "".join(f"<p>{lank(e(p))}</p>" for p in gr) + "</div>" for gr in grupper if gr)
            s = f'<p class="sista">{e(sista[0])}</p>' if sista else ""
            sidor.append(f'''<section class="sida kontakt">{bild(b, pos)}<div class="slöja"></div>
  <div class="ruta"><img class="logga" src="jpg/logga-ljus.png" alt="Hållfjället"><h2>{h2}</h2>{intro}{g}{s}</div></section>''')
    titel = "Hållfjället – " + ("Press kit" if lang == "en" else "Pressmaterial")
    return f'''<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="UTF-8"><meta name="robots" content="noindex"><title>{titel}</title>
<link rel="stylesheet" href="presskit.css"></head><body>
{chr(10).join(sidor)}
</body></html>'''


def gor_jpg(namn):
    mal = JPG / f"{namn}.jpg"
    if mal.exists():
        return
    storlekar = sorted(ROT.glob(f"assets/img/{namn}-*.webp"), key=lambda p: Image.open(p).width)
    im = Image.open(storlekar[-1]).convert("RGB")
    im.thumbnail((2400, 2400), Image.LANCZOS)
    im.save(mal, quality=84, optimize=True, progressive=True)


JPG.mkdir(exist_ok=True)
UT.mkdir(exist_ok=True)
# Ljus logga som färdig bild (i stället för CSS-filter, som vissa PDF-läsare visar fel)
_l = Image.open(ROT / "assets/img/hallfjallet-logo.png").convert("RGBA")
_ljus = Image.new("RGBA", _l.size, (207, 204, 196, 0)); _ljus.putalpha(_l.getchannel("A"))
_ljus.save(JPG / "logga-ljus.png")
# Avslutningssidan: bilden jämnt mörkare (som en mörkare exponering, ingen skugga eller vinjett), så att texten syns mot fönstret
from PIL import ImageEnhance
_k = Image.open(ROT / "assets/img/hero-sallskapsrum-1920.webp").convert("RGB")
ImageEnhance.Brightness(_k).enhance(0.5).save(JPG / "hero-sallskapsrum-mork.jpg", quality=84, optimize=True, progressive=True)
jobb = []
for lang, cfg in SPRAK.items():
    sida = MAPP / f"presskit-{lang}.html"
    sida.write_text(bygg_html(lang))
    for nm in set(re.findall(r'jpg/([\w-]+)\.jpg', sida.read_text())):
        gor_jpg(nm)
    jobb.append((sida.as_uri(), str(UT / cfg["fil"])))

js = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [url, ut] of %s) {
    const s = await b.newPage();
    await s.goto(url, { waitUntil: 'networkidle' });
    await s.evaluate(() => document.fonts.ready);
    await s.pdf({ path: ut, width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
    await s.close();
  }
  await b.close();
})();
""" % json.dumps(jobb)
subprocess.run(["node", "-e", js], check=True)
for _, ut in jobb:
    p = pathlib.Path(ut)
    print(p.name, round(p.stat().st_size / 1e6, 1), "MB")
