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

- `index.html` — language picker at the root. It redirects to `/sv/` or `/en/` by browser language.
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

- `assets/style.css`, `assets/site.js` — shared styling and script.
- `assets/img/` — photos as `name-640.webp`, `name-1280.webp`, `name-1920.webp`, plus `og.jpg` (the share image).
- `sitemap.xml`, `robots.txt`, `favicon.ico`, `apple-touch-icon.png`, `fall.webp` (background of the language picker).
- `wrangler.jsonc` and `.assetsignore` — Cloudflare deploy settings. **Do not edit these** unless she asks for a deploy change. `.assetsignore` keeps repo files like this one out of the public site.

The HTML files are the source of truth. There is no generator. The header, footer and booking button are repeated in every page, so a change to them must be made in **all 14 pages**. Search before you edit and check nothing was missed.

## Rules for every change

- **Keep Swedish and English in sync.** If you change or add something in one language, make the equivalent change in the other. Write natural Swedish, not a literal translation. If you are unsure about the Swedish wording, tell her.
- **Do not invent facts.** Prices, dates, awards, opening hours and names come from her. If something is missing, ask or leave a visible `TODO` and tell her.
- **Booking** goes to the Bookvisit page: `https://online.bookvisit.com/package?channelid=b6e866a4-7126-457c-83b1-7e566d886ac0` with `langid=2` (English) and `langid=1` (Swedish). Search for `bookvisit` to find every use.
- **Contact details** (`info@hallfjallet.se`, `+46 647 690 466`, the map link and coordinates, Instagram) appear in the footer of every page, on the contact pages and in the structured data (JSON-LD) on the home pages. Update all of them together.
- **Opening times** (open Thursday–Sunday, check-in Thursday–Saturday, check-out Sunday, open August–October and from January) appear on the home pages, the contact pages and in the footer.
- **Events** are on the What's on pages. Each event is an `<article class="event">` block. Copy an existing block to add one. Finished events get the extra class `past`, and the label changes to "Past event" / "Tidigare evenemang". Do the same in both languages.
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
- The summer chef opening has unclear dates. Confirm them.
- The newsletter sign-up from the old WordPress site has not been rebuilt (needs a mail service).
- The domain `www.hallfjallet.se` still points at the old WordPress site. Connecting it is a separate step done in Cloudflare by the owner, not something to do here.
