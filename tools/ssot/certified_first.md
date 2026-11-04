# Certified-first capture policy + Windows download telemetry

**Why:** JIMS shows three buttons in the document modal — `Download Regular Copy`, `Download Certified Copy`,
`Cancel`. The certified button is enabled **only while a certified copy is still available** (it is a one-time
download per document, at no charge). The screenshot of CAAP-26-0000625 Dkt 19/20 shows it enabled, which means
**no certified copy of that document has ever been downloaded**. A regular copy can be downloaded any number of
times; the certified one cannot be re-obtained once taken. So the rule is mechanical:

| certified button | action | grade |
|---|---|---|
| **enabled** | click **Download Certified Copy** first, then verify the Clerk sentence on page 1 | `CERT` (OBS when hash+stamp verified) |
| disabled / absent | fall back to `Download Regular Copy` | `SRC`, and record `certified_available: false` (already taken, or not offered) |

Never take a regular copy while the certified one is enabled — that is a one-way loss of the strongest available
form of the document.

## Trace every capture through Windows telemetry (proves *when* and *from where*)

`tools/ssot/download_telemetry.ps1` writes a provenance record for a downloaded file from evidence the OS keeps
independently of our notes:

1. **File bytes** — sha256, size, and `LastWriteTime`/`CreationTime`.
2. **Zone.Identifier** (NTFS alternate data stream) — Chrome writes the source URL and referrer for downloads; it
   is the closest thing to a signed receipt that the file came from `jimspss1.courts.state.hi.us`.
3. **Chrome download history** — a copy of the live `History` SQLite database, queried for the file name (the
   `downloads` table: target path, start time, URL, referrer, received bytes, state).
4. **USN journal (optional)** — `fsutil usn readjournal C:` filtered for the file, which survives even if the
   browser history is cleared.

The record binds: **file → docket → JIMS URL → download timestamp → browser row → hash**, and is appended to
`D:\PROJECT_CENTER\temp\download-telemetry\TELEMETRY.jsonl`. A capture without telemetry is still valid evidence of
the file, but it cannot prove *when* it was taken — and "already downloaded" is exactly the state the certified
button encodes.

## Vault consequence

Because the certified button's state tells us whether a certified copy still exists for a docket, the vault can
carry, per docket: `certified_taken` (bool), `certified_available` (bool), `telemetry_ref` (JSONL line id).
That is what turns "we have a PDF" into "we have the strongest copy that was obtainable, and here is the proof of
when we obtained it".

## Gmail cross-reference (already working)

JEFS sends "JEFS Notice in case:<case id>" e-mails from `efiling@courts.hawaii.gov`. The index built from
`niko@mojehawaje.pl` (67 NEF-related messages, 39 of them for `1RC191003776`, 2026-08-19 → 2026-10-29) matched
**15** docket NEF dates and left exactly **two unmatched: 28-OCT-2026 and 29-OCT-2026** — the dates of the
post-495 tail. That is independent corroboration, from a different system, that Dockets 496–503 exist even though
the Record on Appeal register stops at 495.

Open gap: **no appellate NEF e-mails for `CAAP-26-0000625` appear in that mailbox** — the appellate notices must
have gone to another address (`1rc191003776@gmail.com` is the likely one). Granting Gmail access to that mailbox
would complete the appeal-side cross-reference.


---

## 2026-11-03 — amendment: **best available** when certified is gone

Operator instruction: *"IF NO CERTIFIED AVAILABLE — GRAB CURRENT UNCERTIFIED COPY AND USE AS 'BEST AVAILABLE'."*

The hierarchy is now three tiers, and every captured file must be labelled with the tier it came from:

| tier | when | label | grade |
|---|---|---|---|
| 1. **CERTIFIED** | certified button ENABLED (never downloaded before) | `certified copy` | OBS once the Clerk sentence on page 1 and the hash are verified |
| 2. **BEST AVAILABLE** | certified button DISABLED and a regular copy is downloadable **now** | `best available (current regular copy, certified channel consumed)` | OBS for the bytes; the absence of certification is stated, never implied |
| 3. **TEXT / GAP** | no document downloadable at all | `text rendition` or explicit `GAP` | PARTIAL / GAP |

Rules that keep tier 2 honest:

- "Best available" is **a statement about what was obtainable at capture time**, not a claim of quality. It must never be rendered as "certified", and it must never inherit a certified badge.
- Capture the **current** copy — i.e. download it now, do not reuse an older file on the assumption it is the same. Then compare the new sha256 with any file we already hold:
  - same hash → the held copy is current; record `already current, hash identical` and keep one file;
  - different hash → **both are kept**: the older as `superseded rendition`, the new one as `best available`, each with its own telemetry record and capture time. A changed hash on the same docket is a fact about the record and must not be overwritten.
- Every best-available capture carries: sha256, bytes, pages, `captured_at`, the JIMS servlet URL from `Zone.Identifier`, and the reason the certified tier was unavailable (`confirmCertifiedSingleDocumentButtonDisable` observed at that timestamp).
- Telemetry (`download_telemetry.ps1`) runs for tier 2 exactly as for tier 1. A "best available" without a telemetry record is a file, not a capture.

Why this matters: on 1RC191003776 the certified channel is consumed, so the strongest thing still obtainable is a **fresh, hash-recorded regular copy**. Refusing it would leave the record with text where a document exists — and JIMS renders 468 document rows against our 454 text-only rows, so there is real material to gain.
