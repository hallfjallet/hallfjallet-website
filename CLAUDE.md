# Hållfjället website

Static website for Hållfjället, a small off-grid mountain hotel and restaurant above Ottsjö, Åre. Plain HTML, CSS and a little JavaScript. No build step, no framework.

**The person you are helping is not technical.** Reply in plain language, avoid jargon, and explain what you changed and where she can see it. Never ask her to run commands. Do the work yourself. She may write in Swedish or English; answer in the language she uses.

## How changes go live (always follow this)

1. Make every change on a **new branch**, never directly on `main`.
2. Open a pull request and tell her it is ready.
3. Give her the **preview link** so she can check it on her phone and computer. Cloudflare builds branches with `wrangler preview`. Look for the URL in the build output or in a comment on the pull request, and paste it in the chat. If you cannot find it, say so honestly and do not guess a link.
4. Only when she says it looks good, tell her to press **Merge** on the pull request in GitHub. Do not merge it yourself and do not push to `main` unless she explicitly tells you to.
5. After merging, the live site updates within a couple of minutes at https://website.hallfjallet.workers.dev (the real domain will be connected later).

If she wants to undo something, revert the change on a new branch and open a pull request. Do not rewrite history.

## Site structure

- `en/<page>/index.html` and `sv/<page>/index.html` — 7 pages per language, always in pairs:

| Page | English folder | Swedish folder |
| --- | --- | --- |
| Home | `en/` | `sv/` |
| Stay & Dine | `en/stay-and-dine/` | `sv/bo-och-ata/` |
| Our story | `en/our-story/` | `sv/var-historia/` |
| Getting here | `en/getting-here/` | `sv/hitta-hit/` |
| What's on | `en/whats-on/` | `sv/nu-pa-hallfjallet/` |
| Work with us | `en/work-with-us/` | `sv/jobba-hos-oss/` |
| Contact | `en/contact/` | `sv/kontakt/` |

- `assets/style.css`, `assets/site.js` — styling and script for the inner pages (old look, to be redesigned).
- `assets/hf.css`, `assets/hf.js`, `assets/fonts/` — the designer's look from hallfjallet.se, used by the **home pages** (`sv/index.html`, `en/index.html`). Fonts are Oregon LDO (headings, menu, BOKA) and Suisse Neue (body); she owns the licences.
- `assets/img/` — photos as `name-640.webp`, `name-1280.webp`, `name-1920.webp`, plus `og.jpg` (the share image).

### The home pages (new look)

The home pages copy the structure of the WordPress site: one long page with a slideshow at the top, then full-screen text sections, each followed by a full-screen photo. The menu (hamburger, top right) opens a full-screen overlay and jumps to the sections by id.

- **Section ids** — Swedish: `hitta-hem-i-det-vilda`, `mat-dryck`, `bo-hos-oss`, `var-historia`, `hitta-hit`, `boka`, `newsletter`. English: `home-in-the-wild`, `food-beverage`, `stay-with-us`, `our-story`, `getting-here`, `reservation`, `newsletter`.
- **Slideshow** — the `<img>` tags inside `.bildspel`, in order. The same 13 images, in the same order, in both languages and on phone and computer. Only the first has `src`; the rest have `data-src`/`data-srcset` and load just before they are shown. `--pos-d` / `--pos-m` set the crop on computer / phone. `data-ljus-d` / `data-ljus-m` = `1` when the logo and BOKA should be light on that image (dark image behind them), `0` when they should be dark. Timing is in `assets/hf.js` (first change after 2 s, then 3.5 s; 1.6 s fade in `hf.css`). Order agreed with her: the frozen lake first, then the martini, then the winter mountain with the lodge, so the winter pictures are spread out.
- **Title on the slideshow** — `.hero-text` shows "Hitta hem i det vilda" / "Home in the wild" and a small arrow to the first section when the page opens, then stays for the first three slides (fading as the fourth arrives) or until the visitor scrolls (`assets/hf.js`). Agreed with her: no extra line under the title. Light grey (`--gra` in `hf.css`) is the one tone for logo, BOKA, language switch, menu and title on dark images; the logo is drawn through a CSS mask so it matches exactly. BOKA hover/tap switches to the opposite tone (never red).
- **Menu background** — a double exposure she loved: `hero-martini` (`data-bild` on `.meny`) with `hero-fjallet-vinter` (`data-skog`) at 27 % opacity on top (`.meny::before` in `hf.css`), loaded by `hf.js` when the menu first opens. Same attributes on all six new-look pages. She may want this combination again for Berättelser från fjället.
- **Language switch** — chosen by her: `.sprakval` ("English" / "Svenska", same size as BOKA) next to BOKA on every new-look page, linking to the counterpart page, plus `.sprak-under` ("Svenska · English", current language underlined) under the title on the two home pages. No language item in the menu any more.
- **Photos between sections** — `<div class="bild">` with the same `--pos-*` and `data-ljus-*` attributes.
- **LÄS MER** — text blocks with the classes `las-mer bara-mobil` get a LÄS MER / VISA MINDRE button on phones only (800px and narrower). The text breaks at the paragraph closest to half. Add `data-las-mer-efter="2"` to force the break after paragraph 2.
- The texts are copied word for word from hallfjallet.se. Do not edit them unless she asks.
- `sitemap.xml`, `robots.txt`, `favicon.ico`, `apple-touch-icon.png`, `ikon-hf-16/32/192.png` (the curly Hf monogram; links carry `?v=2` so browsers drop the old cached H — bump it if the icon changes again), `fall.webp` (background of the language picker).
- `_redirects` — old WordPress addresses (English pages at the root, Swedish under /sv/, the activity detail pages, the WP sitemaps) sent with 301 to the matching place on the new site. Add a line here when an address changes.
- `404.html` — the "Här tog stigen slut" page, shown for unknown addresses (`not_found_handling: "404-page"` in `wrangler.jsonc`).
- `index.html` — the language picker, in the new look. It sends visitors to /sv/ or /en/ by browser language; an old English link with a #section goes to /en/ with the same section.
- `wrangler.jsonc` and `.assetsignore` — Cloudflare deploy settings. **Do not edit these** unless she asks for a deploy change. `.assetsignore` keeps repo files like this one out of the public site.

The HTML files are the source of truth. There is no generator. The header, footer and booking button are repeated in every page, so a change to them must be made in **all 14 pages** (the two home pages have their own header, menu and footer markup in the new look). Search before you edit and check nothing was missed.

## Rules for every change

- **Keep Swedish and English in sync.** If you change or add something in one language, make the equivalent change in the other. Write natural Swedish, not a literal translation. If you are unsure about the Swedish wording, tell her.
- **Do not invent facts.** Prices, dates, awards, opening hours and names come from her. If something is missing, ask or leave a visible `TODO` and tell her.
- **Booking** goes to the Bookvisit page: `https://online.bookvisit.com/package?channelid=b6e866a4-7126-457c-83b1-7e566d886ac0` with `langid=2` (English) and `langid=1` (Swedish). Search for `bookvisit` to find every use.
- **Contact details** (`info@hallfjallet.se`, `+46 647 690 466`, the map link and coordinates, Instagram) appear in the footer of every page, on the contact pages and in the structured data (JSON-LD) on the home pages. Update all of them together.
- **Opening times** (open Thursday–Sunday, check-in Thursday–Saturday, check-out Sunday, open August–October and from January) appear on the home pages, the contact pages and in the footer.
- **Activities** ("Dagar på fjället" / "Activities in the Mountains") are on `sv/nu-pa-hallfjallet/` and `en/whats-on/`, in the new look. They are grouped under a season heading (`<div class="sasong">` Vinter / Sommar). Each activity is an `<article class="uppslag">`: a large photo beside the text, with every other one mirrored (`vand`). Copy a block to add one, in both languages. The texts are word for word from hallfjallet.se; each activity shows its first paragraph with LÄS MER (`data-las-mer-efter="1"`, on all screens) and one plain link, "Boka – lägg till i er vistelse" / "Book – add it to your stay", styled like BOKA, to Bookvisit. The experiences are set up in Bookvisit as add-ons (Tillvalsprodukter, e.g. "Önskemål om hundspann", priced 0 kr), so the request arrives with the booking. An enquiry form (Web3Forms) was built and then removed at her request; she has a Web3Forms account if it is needed later. Prices are always on request because every experience is tailored; that is said once at the bottom (`.notis`). Hunting sits under Sommar because it falls in the summer season (August–October); confirm with her if that changes.
- **Jobs** are on the Work with us pages. Each opening is an `<article class="job">` block with the email address to apply to. Remove an opening in both languages when it is filled.
- **Photos:** resize to widths 640, 1280 and 1920 pixels (never larger than the original), save each as WebP at about quality 76, and name them `name-640.webp` and so on. Use Python with Pillow for this. Add descriptive alt text in both languages. Do not commit large originals.
- **New page:** create the page in both languages, add it to the nav and footer on every page, add it to `sitemap.xml`, and add the `hreflang` links in the head to point at its counterpart.
- Keep the design as it is (colours and fonts are set at the top of `assets/style.css`) unless she asks for a design change.

## Checks before you open a pull request

- Serve the site locally with `python3 -m http.server` from the repo root and look at the changed pages at phone width (375px) and desktop width (1440px). Chromium and Playwright are available in cloud sessions.
- Make sure every link and image path you touched resolves, every image has alt text, and each page has exactly one `h1`.
- If you changed text in one language, confirm the other language has the matching change.

## Open items (waiting for her answers)

- Awards and press: no awards are named yet. The home pages have an HTML comment marking where an awards strip goes.
- The Instagram link was reused from the old page. Confirm it.
- The newsletter sign-up from the old WordPress site has not been rebuilt (needs a mail service). For now the "Följ våra berättelser" / "Follow our stories" button on the home pages opens an email to info@hallfjallet.se. Ask which newsletter service they use.
- Jobba hos oss / Work with us is rebuilt in the new look (`<article class="jobb">` per opening, built like the activities page). Summer chef opening is 2028 in both languages, and applications go to anders@hallfjallet.se (both confirmed by her).
- The old inner pages (bo-och-ata, var-historia, hitta-hit, kontakt and their English pairs) are now small redirect pages to the matching home-page section, and are out of the sitemap. The site is effectively: home, activities, work with us. hallfjallet.se also has a detail page per activity; on the new site the full text is on the activities page instead (LÄS MER on phones). Old detail-page addresses redirect via `_redirects`.
- The skier photo is used twice on the home page (in the slideshow and after Vår historia). Avoid the same person in two pictures in a row. She wants the flower bouquet as the last photo before the footer.
- The winter mountain photo (`hero-fjallet-vinter`) only exists at 900px wide. Replace it when she sends a larger version.
- The domain `www.hallfjallet.se` still points at the old WordPress site. Connecting it is a separate step done in Cloudflare by the owner, not something to do here.
