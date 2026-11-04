# EVIDENCE ACCESS — full document set for external analysts

**Why this folder exists.** The site `https://the95xrecord.vercel.app` deliberately publishes **no PDF bytes** —
every row there gives the file name, its SHA-256 and its page count (SSOT contract §4). This folder is the
counterpart: the actual documents, with a hash manifest, so an external analyst can read the primary material
instead of trusting a claim about it.

## What is here

| item | content |
|---|---|
| `documents/` | **70 files, 49,495,079 bytes** — the canonical case library as held on the station |
| `MANIFEST.csv` | one row per document: case, docket, grade, file, bytes, pages, sha256 |
| `MANIFEST.sha256` | `sha256sum -c` compatible manifest over `documents/` |

Composition by case and grade:

| case | documents | breakdown |
|---|---|---|
| **1RC191003776** (trial) | 54 | **10 `CERTIFIED`** (Clerk-certified) · **42 `SRC`** (regular copies, incl. the 33 promoted from agent worktrees / email pack / trial bundle) · 2 `TEXT` (minute entries Dkt 486/487, portal text with provenance header) |
| **CAAP-26-0000625** (appeal) | 16 | 13 `SRC` appellate documents (ICA Dkts 1,2,3,4,5,6,8,10,11,13,15,17,19) · 3 `PACK` (deadline pack: memo, timeline, citations) |

## How to verify what you read

1. Download `MANIFEST.csv` and `documents/`.
2. Recompute each file's SHA-256 and compare with `MANIFEST.csv` (or run `sha256sum -c MANIFEST.sha256`).
3. Every document filename is canonical: `YYYY-MM-DD__<CASE>__DKT__DKT<NNNN>-<CODE>__<slug>__<FORM>__h<sha12>.pdf` —
   the trailing `h<sha12>` is the first 12 hex characters of the file's SHA-256, so a name that does not match its
   own hash is a red flag.
4. Cross-check any row against the live SSOT: `https://the95xrecord.vercel.app/register` (495 trial rows) and
   `/appeal` (20 appeal rows), and against `https://the95xrecord.vercel.app/ssot.json`.

## What is NOT here (and why)

- **No PDF for 454 of the 495 trial dockets** — the station holds those as OCR/text only (491 of 495 have text). All **41** rows that do hold a PDF of their own document are now in the canonical library (**0 outside**).
- **Dkt 423 is a bundle**: the canonical file is the court's combined DOC423-424 print — the 12-page certified order WITH the 2-page certified NEF 424 appended (no standalone 423 exists on the station). Dkt 424 itself stays graded text-only.
- **24 of the 33 promoted sources are image-only scans** filed `SRC`: certification cannot be read from text, so none was upgraded on a guess.
  Derivation: 495 register rows − **41** rows that hold a PDF of their own document = 454. (The 70 files in this
  export are not 70 trial PDFs: 54 trial documents — 2 of them text minutes — plus 16 appeal documents.)
  Their rows are still published in the SSOT with a grade; they are simply not in this export.
- **No certified copies of Dkt 480 or the 486/487 minutes** — those exist only at the courthouse; the text is here
  for the minutes, the certified scan is not.
- **No appeal dockets 12, 14, 16, 18, 20** — never captured (published as explicit GAP, not guessed).
- **Nothing is redacted or altered.** Files are byte copies; the hashes prove it.

## Ground rules for the analyst

- Cite file + SHA-256 (or docket + page) for every finding; do not accept an unsourced claim, including one from this folder.
- "for counsel" in the SSOT marks every place where a legal conclusion would be required; this folder adds no opinion.
- If a hash mismatches, stop and report it — a mismatch would mean the export, not the record, is wrong.
