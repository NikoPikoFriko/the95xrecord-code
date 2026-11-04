# BRAND — The 95× Record

Identity, card system and production rules for everything in `site/assets/brand/`.
Nothing in this folder is wired into a live page: the site HTML is untouched and
nothing was deployed. The look is derived from the live pages
(`site/index.html` and siblings), not invented beside them.

---

## 0. What is in this folder

| file | what it is |
|---|---|
| `wordmark.svg` | lockup: *The 95× Record* + `CIVIL NO. 1RC19-1-003776`; outlined letterforms, `fill="currentColor"` |
| `favicon.svg` | 32 × 32 tile: paper field, ink `95`, red base bar |
| `favicon-32.png` · `favicon-180.png` | rasters of `favicon.svg` (32 px, 180 px) |
| `og/*.png` | six 1200 × 630 title cards: index, hook, numbers, findings, coverage, pl |
| `og/src/*.html` | the HTML each OG card was rendered from |
| `og/MANIFEST.json` | page, og:title, og:description, og:url, og:image per card |
| `posts/01.png … 08.png` | eight 1600 × 900 images, one per final post |
| `posts/src/01.html … 08.html` | the HTML each post image was rendered from |
| `posts/MANIFEST.json` | headline, word count, cite, target URL per post |
| `PRESS-FACT-SHEET.md` · `press.pdf` | one-page press sheet (PDF is one Letter page) |
| `preview/brand-preview.html` + `brand-preview.png` | the wordmark on paper, ink and the site background (1280 × 900) |
| `CHECKSUMS.txt` | size, pixel dimensions and sha256 of every file here |
| `src/*.py` | the generators; the assets are outputs, not drawings |

---

## 1. The idea

A cold record: paper, ink, one red, one green, and nothing decorative that is not
information. The red is a spine and a citation colour — it never signals danger or a
verdict. The green appears only where something has been verified. Type does the work;
there are no icons, no shadows, no gradients, no stock photography.

The mark is deliberately **monochrome**: it takes the colour of whatever page holds it,
so it survives light and dark without a second file.

---

## 2. Palette

| token | value | used for | never used for |
|---|---|---|---|
| **Paper** | `#f5f1e6` | card fields, favicon field, brand surfaces | body text |
| **Site paper** | `#faf9f7` | the live pages only — unchanged by this folder | the cards (cards use Paper) |
| **Ink** | `#111111` | headlines, rules, body | — |
| **Ink muted** | `rgba(17,17,17,.55–.78)` | sub-lines, labels, secondary metadata | the headline |
| **Red** | `#7a1f1f` | spine, eyebrow, cite chip, URL, accent rules | verdicts, warnings, "bad" figures |
| **Green** | `#1f5f3a` | verification status only (dot + `SOURCE VERIFIED`) | decoration of any other kind |
| **Red, dark scheme** | `#c8705f` | the wordmark spine under `prefers-color-scheme: dark` only | anywhere else |

Two rules:

1. **Green means verified.** If a card does not carry a verification status, it gets no green.
2. **Red is citation, not alarm.** The same red marks a docket cite, the spine and the URL.

No other hue is introduced. If a new surface needs a tint, use ink at an opacity.

---

## 3. Type

| role | family | notes |
|---|---|---|
| Display | **Georgia** (serif) | the site's serif; oldstyle figures are kept on purpose — they match the live pages |
| Labels, cites, URLs, figures | **Consolas**, falling back to `ui-monospace, Menlo` | uppercase, letter-spaced |
| Wordmark | Georgia 64 → outlined | plus Consolas 11 at 1.75 px tracking → outlined |

Letter-spacing for caps labels: `.13em` (status), `.16em` (stats labels), `.2em` (eyebrow).
Display tracking: `-.012em`.

### Scale

| role | post `1600×900` | OG `1200×630` |
|---|---:|---:|
| eyebrow (mono caps) | 14 px | 12 px |
| display XL | 128 px | 96 px |
| display L | 88 px | 64 px |
| display M | 72 px | 52 px |
| quote (italic) | — | 30 px |
| sub / support | 25 px | 21 px |
| cite chip | 18 px | 15 px |
| status line | 13 px | 12 px |
| footer URL | 20 px | 17 px |
| ghost number | 250 px at 5 % ink | — |

Sentence case for headlines; the eyebrow is the only all-caps display element.
No exclamation marks anywhere. No emoji.

---

## 4. Spacing

- Base unit **8 px**; horizontal gaps 24 / 54 px.
- **Card frame:** posts pad `74` top / `92` sides / `64` bottom; OG pad `56` / `68` / `48`.
- **Head:** eyebrow, then a full-width 1 px rule at 22 % ink.
- **Content block:** centred between the head rule and the footer rule.
- **Footer:** 1 px rule at 22 % ink, URL left, section label right.
- The URL line is never crowded: 64 px clear below the last content element.
- Spine: 10 px solid red at the left edge of every card; 5 px on the wordmark.

---

## 5. Card rules

1. **One claim per card.** A card that argues two things is two cards.
2. **Every post image carries exactly one `[Dkt]` cite.** Cited to docket *and* page.
3. **The bottom line of every post is the string** `the95xrecord.vercel.app` — exact,
   lowercase, no `https://`, no trailing slash.
4. **Headlines on post images are 12 words or fewer.** `src/build_cards.py` counts them
   and refuses to render past 12.
5. **A verification status is a sentence, not a badge.** Format:
   `■ SOURCE VERIFIED · <what exactly was checked>`.
6. **A quoted assertion must be labelled as one.** The findings card prints a filing's
   words and says `assertion quoted, labelled, not adopted`. Never present a party's
   assertion as the site's finding.
7. **Gaps are allowed on a card.** "491 of 495" is stronger than a rounded "495".
8. **No card may out-run the page it links to.** If the figure is not on the page, it does
   not go on the card.
9. **Ghost numbers are for sequence only** (`01`–`08`), at 5 % ink, and never carry meaning.

---

## 6. SVG usage

**`wordmark.svg`** — 474.2 × 94.5 units.

- Every letterform is inside `<g fill="currentColor">`. Inline the SVG and set `color`
  on a parent (`color:#111` on paper, `color:#f5f1e6` on ink).
- Loaded through `<img>`, `currentColor` resolves to black — correct on light
  backgrounds, wrong on dark. Inline it when the background is dark.
- The red spine (`rect.wm-spine`) is decorative. Its colour is fixed at `#7a1f1f`, with a
  `prefers-color-scheme: dark` override to `#c8705f`. It can be deleted without losing
  the mark.
- The `CIVIL NO.` line is the same `currentColor` at 78 % opacity, so it dims instead of
  disappearing.
- Do not set a fixed `fill` on the letters; do not place the mark on a mid-tone
  background where neither ink nor paper reads.

**`favicon.svg`** — 32 × 32 viewBox, fixed colours by design.

- Paper field, ink `95`, red base bar; no border, so it survives a 16 px browser tab on
  both light and dark chrome.
- The multiplication sign is deliberately absent below 64 px: at 16 px it is a smudge,
  and a smudge is not a mark. The `×` returns at wordmark and card sizes.
- `favicon-32.png` / `favicon-180.png` are LANCZOS reductions of a 720 px Chromium
  render of the SVG, so the PNGs cannot drift from the vector.

---

## 7. Rebuilding

Requires Python 3.12 with `fontTools`, `Pillow`; Chrome at
`C:\Program Files\Google\Chrome\Application\chrome.exe`; the Windows fonts
`georgia.ttf`, `georgiab.ttf`, `consola.ttf` (outline sources only — the SVGs carry no
font dependency).

```bash
cd site/assets/brand
python src/build_marks.py        # wordmark.svg, favicon.svg
python src/make_favicon_pngs.py  # favicon-32.png, favicon-180.png
python src/make_preview.py       # preview/brand-preview.html
python src/build_cards.py        # og/*.png (6) and posts/*.png (8)
python src/build_press.py        # PRESS-FACT-SHEET.md and press.pdf
python src/make_manifests.py     # og/MANIFEST.json, posts/MANIFEST.json, CHECKSUMS.txt
```

Each card is rendered exactly as its source file, e.g.:

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu
  --no-sandbox --hide-scrollbars --user-data-dir="C:/Temp/chrome-brand"
  --window-size=1600,900
  --screenshot="C:/Users/NIKO/TEMPLE/site/assets/brand/posts/01.png"
  "file:///C:/Users/NIKO/TEMPLE/site/assets/brand/posts/src/01.html"
```

`press.pdf` is printed by Chrome (`--print-to-pdf`, `--no-pdf-header-footer`), not by
LibreOffice: `soffice` is not installed on this machine. It is one Letter page
(612 × 792 pt) and the generator refuses to ship more than one page.

---

## 8. The rule that outranks the rest

> **No design element may state an unverified claim.**

A colour, a figure, a quote, a label, a URL — each one is a statement. Before anything
enters a card it must be one of:

- a figure quoted from a document that is published with a `[Dkt N p.X]` cite and was
  SHA-256 matched before quotation, or
- a count the site measured and publishes (`1,121 documents`, `491/495`,
  `2,114 files · 6.29 GB`), or
- a quotation reproduced verbatim and labelled (assertion, court's words, party's filing).

If it is none of those, it does not go on a card. "Approximately", "reportedly" and
"critics say" are not mitigations; they are unverified claims with a hedge attached.

Where to check: `register/documents.json` (the register), `verify/hash-sweep-full.jsonl`
(the hash sweep), `verify/GROUNDING-REPORT.md` (the quotation checker),
`site/*.html` (what the card is allowed to echo).

---

## 9. MAGIC cards — not cleared for design use

The seven "MAGIC" exhibit cards (`pii-redacted-exhibit-cards.md`) are **not a design
source**. Their verdict is **0 of 7 camera-ready** (`verify/reports/MAGIC-CARDS-VERDICT.md`,
`verify/reports/DAY3-CARD-VERIFICATION.md`).

- **Card 1 is spliced.** The Whitmore sentences are not a Day 3 quotation: they are read
  from two reports on Day 4 pp. 20–21, joined, and reworded ("required by the 1996 code"
  → "ASME A17.1").
- **Card 5's time claims are contradicted.** "1:35 PM" against 1:44:38 p.m. in the
  transcript; "fourteen minutes later" against 11 min 25 s by the card's own cite
  (03:26:17 → 03:37:42).
- Other cards carry wrong page cites (n.8 is p.15, not p.16), a wrong invoice number
  (the record's Ex. D-CC invoice is #5000967997) and an unverifiable claim number.

**Rule:** no MAGIC-card sentence, figure or quote may be used in a card, the press sheet
or the wordmark until it is re-verified against the record on its own page. If one is ever
cleared, it enters through the same gate as everything else: docket, page, hash, label.

---

## 10. Known limits

- **Not deployed.** `og:image` paths in `og/MANIFEST.json` assume the site root is `site/`
  (`/assets/brand/og/<page>.png`). Nothing was tested against a live social scraper.
- **OG cards are designed, not screenshots.** They reuse the site's palette, eyebrow,
  serif headline and cites, but they do not update when page copy changes: rebuild them.
- **Georgia's figures are oldstyle** (2, 3, 4, 5, 7, 9 descend). This is deliberate and
  matches the live pages; it is not a rendering fault. In the press sheet, figures are set
  in Consolas so a table of money lines up.
- **No LibreOffice** on this station, so `press.pdf` came from Chrome. Same text, same
  one-page constraint, different engine.
- **The favicon omits the `×`.** That is a legibility decision at 16 px, not a typo.
