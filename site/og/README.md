# Social preview cards — The 95× Record

Generated **2026-10-31 18:51 HST** from the live local site at
`http://127.0.0.1:8787/` (files in `site/`). Six pages, six 1200×630 PNGs,
one manifest and one paste-ready meta snippet file. No page HTML was edited;
everything here lives under `site/og/`.

## Files produced

| page | PNG | bytes | dimensions | what the crop shows |
|---|---|---:|---|---|
| index | `index.png` | 50,510 | 1200×630 | “The 95× Record”, the SHA-256 verification line, and the four stats: 1,121 documents · 491/495 entries · 491 docket numbers · 0.94 GB |
| hook | `hook.png` | 49,120 | 1200×630 | “One elevator repair. One judgment.”, the 95.08 ratio, the four-bar cost chart and the two addition lines |
| numbers | `numbers.png` | 53,182 | 1200×630 | the Dkt 453 figures table ($2,260.15 … $214,890.23) with quotations and cites |
| findings | `findings.png` | 57,615 | 1200×630 | Findings 001: Dkt 405 quotations tagged ASSERTION, with cites |
| coverage | `coverage.png` | 58,617 | 1200×630 | “491 of 495 circuit entries are present” and the four declared gaps (484, 486, 487, 493) |
| pl | `pl.png` | 54,945 | 1200×630 | “Streszczenie dla czytelników z Polski”, the Polish intro and the start of the verified-numbers table |

All images are RGB PNG, exactly 1200×630, and all are larger than 10 KB.
SHA-256 prefixes (for spot-checking that a file was not swapped):

```
index     c1686cf80bab3532…
hook      376f4afbf8cad567…
numbers   0c80663cea506529…
findings  1c27135e16ee9723…
coverage  921cb1a58c582ebf…
pl        d83fd990ab757beb…
```

`MANIFEST.json` is an array of `{page, url, image, title, description}` for the
six pages. The `url` and `image` values use the production placeholder
`https://the95xrecord.vercel.app`; the PNGs themselves are local files in this folder.
Every title/description uses only figures printed on the corresponding page
(see “Number provenance” below).

`og-snippet.html` holds one block per page: `og:title`, `og:description`,
`og:image`, `og:url` and `twitter:card`. Each block is wrapped in an HTML
comment naming the page whose `<head>` it belongs in.

## How to wire it

1. Open `og-snippet.html` and copy the block for a page (the comment says
   which page).
2. Paste it inside that page's `<head>`, directly after
   `<meta charset="utf-8">`. The `<meta>` tags must stay in `<head>`; the
   surrounding comments are harmless and can stay or go.
3. Upload `site/og/*.png` so they are served at `/og/<page>.png`.
4. Replace the placeholder origin `https://the95xrecord.vercel.app` in `og:image`
   and `og:url` if the site is deployed elsewhere. `og:image` must be an
   absolute URL for Facebook/LinkedIn/Slack/etc. to fetch it; `/og/<page>.png`
   alone is only a site-root path.
5. Re-scrape with a validator (e.g. Facebook Sharing Debugger, LinkedIn Post
   Inspector, or `opengraph.xyz`) after deploying. Nothing here was validated
   against a live social scraper because no public origin exists yet.

The snippet file is a fragment, not a standalone document: opening it in a
browser shows nothing, which is expected.

## Exact Chrome command used

Each page was rendered one at a time with this command (index shown; the other
five replace both occurrences of `index`):

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --no-sandbox --hide-scrollbars --user-data-dir="C:/Temp/chrome-prof" --window-size=1200,630 --screenshot="C:/Users/NIKO/TEMPLE/site/og/index.png" "http://127.0.0.1:8787/index.html"
```

The batch loop actually used, from Git Bash (line breaks added for readability):

```bash
for p in hook numbers findings coverage pl; do
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
    --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --user-data-dir="C:/Temp/chrome-prof" --window-size=1200,630 \
    --screenshot="C:/Users/NIKO/TEMPLE/site/og/$p.png" \
    "http://127.0.0.1:8787/$p.html"
done
```

The only difference from the `cmd`-style command above is the executable
path: Git Bash needs `/c/Program Files/...` instead of `C:\Program Files\...`.
The Chrome flags and output paths are identical.

The local server must be running at `http://127.0.0.1:8787/` with `site/` as
its root. Chrome writes the file and prints
`NNNNN bytes written to file …`; the renders above were 49–59 KB each.

## Freshness note

These images are **renders of the live pages**, not hand-drawn cards. They
show what each page looked like at 1200×630 at render time. When a page's
copy or figures change, the PNG does **not** update itself — re-run the Chrome
command for that page after the edit. Because the card is the page, the card
cannot drift from the page for long if the command is part of the page build
or release checklist.

Only the first 630 px of each page is captured. Material below the fold is
intentionally absent from the card.

## Number provenance (nothing invented)

- **index** — 1,121 published documents, “1,121 match, 0 mismatch”; 491/495
  entries; 491 docket numbers; 0.94 GB. All printed in the index stat block.
- **hook** — $2,260.15 repair; $12,743.54 costs; $196,744.08 fees;
  $211,747.77 judgment; $2,842.46 interest; $300.00 legal fees; $214,890.23
  total; “A ratio of 95.08”. All on the hook page.
- **numbers** — $2,260.15, $211,747.77, $2,842.46, $300.00, $214,890.23 and
  the additions, all quoted from Dkt 453 pp. 2 and 15.
- **findings** — Dkt 405 p.5: “literally 100 times” and the site's
  214,890.23 / 2,260.15 = 95.08.
- **coverage** — “491 of 495 circuit entries are present”, four entries the
  site cannot show: Dkt 484, 486, 487, 493.
- **pl** — 1 121 documents; 1 121 / 1 121 hashes; 214 890,23 / 2 260,15 =
  95,08×. All printed on the Polish page.

## What was not verified

- The production domain `the95xrecord.org` and the `/og/` hosting path: both
  are placeholders; no public deployment was tested.
- Social-platform rendering (crop behaviour, cache invalidation) was not
  tested against a live scraper.
- The snippets were not inserted into the six page files: this task's write
  scope is `site/og/` only.
- The `findings` crop is tight: the Cite column wraps and the bottom quote is
  clipped; this is the page's own layout at 1200×630, not an image edit.
