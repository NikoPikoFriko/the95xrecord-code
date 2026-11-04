# the95xrecord — public source of the 95× Record

Readable, audit-ready source behind **https://the95xrecord.vercel.app** — a public record room for
AOAO Marine Surf Waikiki v. Nikodem Pikor, Hawaii First Circuit No. **1RC191003776** and appeal
**CAAP-26-0000625**.

This repository exists so an external analyst can verify **how** the site is built, not only **what** it says.

## What is here

| path | content |
|---|---|
| `site/` | the deployed static site (HTML pages, `/data/*.json` endpoints, sitemap, robots) |
| `site/texts/` | 266 published text files — byte copies of the held sources, one per text-only docket |
| `site/data/texts.json` | the text corpus with full provenance (docket, code, filed, RA page, grade, method, source file, source sha256, text sha256) |
| `site/data/crossref.json` | docket → record page → held file/text → hash → published URL |
| `site/ssot.json` | the machine index for both cases (counts, dataset hashes, immutable facts, access block) |
| `tools/ssot/` | generators: `build_texts.py`, `build_crossref.py`, `verify_published.py`, `update.sh` |
| `tools/deploy-live.sh` | the deploy path actually used (outside-the-work-tree copy, `vercel deploy --prod`) |

Not here: the case-room library, the private register exports and any third-party salvage material.
The documents themselves are reachable through the site's `/access` page (three public stores + SHA-256 manifests).

## The rules the build is held to

1. **Four fields per published row** — case, docket, evidence (file, hash or explicit GAP), grade.
2. **No PDF bytes on the site** — rows carry file name + SHA-256 + page count; `/access` is where the
   documents live.
3. **Byte-exact texts** — `site/texts/*.txt` are binary copies of the held sources, so `text_sha256`
   equals `source_sha256` by construction (a text-mode write once broke this; the generator now writes binary).
4. **No invented numbers** — every count on the site is computed by a script from a dataset that is
   published next to it.
5. **"for counsel"** marks every place where a legal conclusion would be required. The site reports; it does not advise.

## Verify it yourself

```bash
python tools/ssot/verify_published.py     # checks the live site against its own datasets
```

It asserts: `/ssot.json` == `/data/ssot.json`; `/data/texts.json` count == entries and 20 sampled
text hashes recompute; `/data/crossref.json` count == 495; the core routes return 200.

## Deploy (maintainers)

```bash
bash tools/deploy-live.sh    # sync site/ → deploy bundle → copy outside the git work tree → vercel deploy --prod
```

The outside-tree copy is required: Vercel refuses a deploy whose local git author is not a project member.

## Links

- Live: <https://the95xrecord.vercel.app>
- Evidence access: <https://the95xrecord.vercel.app/access>
- Machine index: <https://the95xrecord.vercel.app/ssot.json>
- Provenance: <https://the95xrecord.vercel.app/provenance>
