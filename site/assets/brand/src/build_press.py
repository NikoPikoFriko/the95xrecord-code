#!/usr/bin/env python3
"""Build PRESS-FACT-SHEET.md and press.pdf from one source.

The Markdown is the canonical text. The PDF is the same text set for one
Letter page and printed with headless Chrome, because LibreOffice (soffice)
is not installed on this station:

  chrome --headless=new --disable-gpu --no-sandbox
         --print-to-pdf=press.pdf --no-pdf-header-footer file:///.../src/press-print.html

Every figure below is one that is published on the site with a docket and a
page; nothing here is added for the press release.
"""
import os
import subprocess
import sys

from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = "C:/Temp/chrome-brand"

URL = "https://the95xrecord.vercel.app"

FIGURES = [
    ("$2,260.15", "the repair figure",
     "\u201cThe underlying trial was for the recovery of $2,260.15 to repair the elevator\u201d",
     "[Dkt 453 p.2]"),
    ("$211,747.77", "total judgment amount",
     "\u201cTotal Judgment Amount $211,747.77\u201d", "[Dkt 453 p.15]"),
    ("$2,842.46", "interest per HRS 478-3",
     "\u201cInterest per HRS 478-3 $2,842.46\u201d", "[Dkt 453 p.15]"),
    ("$300.00", "legal fees and costs",
     "\u201cLegal Fees & Costs $300.00\u201d", "[Dkt 453 p.15]"),
    ("$214,890.23", "total amount",
     "\u201cTotal Amount $214,890.23\u201d", "[Dkt 453 p.15]"),
]

MD = """# PRESS FACT SHEET — The 95× Record

**Case:** AOAO Marine Surf Waikiki v. Nikodem Pikor · Civil No. 1RC19-1-003776 ·
Circuit Court of the First Circuit, Hawaii · appeal CAAP-26-0000625
**Version:** v1.0 · 2026-10-31 (HST) · prepared from the published record
**Site:** {url}

## What this record is

An open publication of the court record in a Hawaii condominium-association case. 1,121
documents are published, each hashed with SHA-256 and matched against the register before
quotation (1,121/1,121, zero mismatches). Every quotation carries a docket number and a page.
The site also publishes what it does not have: 491 of 495 circuit entries are present, and the
four entries it cannot show are named. It states no conclusion about the merits.

## Five verified figures

Each quotation was downloaded from the record and SHA-256 matched before it was quoted.

| Figure | What it is | Quotation | Cite |
|---|---|---|---|
{figures}

## What the record contains (measured, not estimated)

- 1,121 published documents · 1,121/1,121 SHA-256 matches · 0 mismatches.
- 491 of 495 circuit entries present · four named gaps: Dkt 484, 486, 487, 493.
- The shared Drive behind the material: 2,114 files, 42 folders, 6.29 GB, counted recursively.

## Three URLs to verify

1. {url}/ — the record and its verification totals
2. {url}/numbers — the five figures above, each with its page
3. {url}/coverage — the four declared gaps

## No conclusion about the merits

This sheet reports what the documents say and what the site measured. It states no conclusion
about the merits of the case, about the appeal, or about the conduct of any party. Every figure
is quoted with a docket and a page so that it can be checked against the record; nothing here
is an opinion.

## Contact

**[PRESS CONTACT — name · e-mail · telephone]** — placeholder, to be completed before
distribution.

---

*Quotations carry docket and page. Arithmetic performed by the site is labelled as the site's.*
"""


def build_md():
    rows = "\n".join(
        "| **%s** | %s | %s | `%s` |" % f for f in FIGURES
    )
    text = MD.format(url=URL, figures=rows)
    path = os.path.join(BRAND, "PRESS-FACT-SHEET.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote PRESS-FACT-SHEET.md (%d bytes, %d lines)"
          % (len(text), text.count("\n")))
    return text


def html(text):
    fig_rows = "\n".join(
        "<tr><td class='fig'>%s</td><td>%s</td><td>%s</td><td class='cite'>%s</td></tr>"
        % (fig, what, quote, cite)
        for fig, what, quote, cite in FIGURES
    )
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Press fact sheet — The 95x Record</title>
<style>
  @page { size: letter; margin: 15mm 15mm 12mm 15mm; }
  html,body{margin:0;background:#ffffff;color:#111111}
  body{font-family:Georgia,'Times New Roman',serif;font-size:9.8pt;line-height:1.4}
  .kicker{font-family:Consolas,'SF Mono',monospace;font-size:7.4pt;letter-spacing:.2em;
          color:#7a1f1f;text-transform:uppercase;border-bottom:1px solid #111;
          padding-bottom:5pt;margin-bottom:9pt}
  h1{font-size:19pt;font-weight:400;margin:0 0 5pt;letter-spacing:-.01em}
  .meta{font-family:Consolas,'SF Mono',monospace;font-size:7.6pt;line-height:1.5;
        color:#333;margin:0 0 9pt}
  .meta b{font-weight:400;color:#7a1f1f;letter-spacing:.08em}
  h2{font-family:Consolas,'SF Mono',monospace;font-size:8pt;letter-spacing:.16em;
     text-transform:uppercase;color:#7a1f1f;margin:11pt 0 3pt;font-weight:400}
  p{margin:0 0 5pt}
  table{border-collapse:collapse;width:100%;margin:3pt 0 4pt;font-size:8.9pt}
  th{font-family:Consolas,'SF Mono',monospace;font-size:7pt;letter-spacing:.1em;
     text-transform:uppercase;color:#555;text-align:left;font-weight:400;
     border-bottom:1px solid #bbb;padding:2pt 4pt 2pt 0}
  td{border-bottom:1px solid #e2ded2;padding:2.6pt 4pt 2.6pt 0;vertical-align:top}
  td.fig{white-space:nowrap;font-weight:700;font-family:Consolas,'SF Mono',monospace;
         font-size:8.7pt;letter-spacing:0}
  td.cite{font-family:Consolas,'SF Mono',monospace;font-size:7.8pt;color:#7a1f1f;
          white-space:nowrap}
  ul,ol{margin:0 0 5pt;padding-left:13pt}
  li{margin-bottom:2pt}
  .urls{font-family:Consolas,'SF Mono',monospace;font-size:8.2pt}
  .box{border-left:3px solid #1f5f3a;padding:4pt 0 4pt 8pt;margin:4pt 0 6pt}
  .contact{border:1px solid #ccc;padding:6pt 8pt;font-family:Consolas,monospace;
           font-size:8.4pt}
  .foot{font-family:Consolas,'SF Mono',monospace;font-size:7pt;color:#666;
        border-top:1px solid #ccc;padding-top:4pt;margin-top:9pt}
  .page{max-width:190mm}
</style></head><body><div class="page">
<div class="kicker">The 95× Record · Civil No. 1RC19-1-003776</div>
<h1>Press fact sheet</h1>
<p class="meta"><b>CASE</b> AOAO Marine Surf Waikiki v. Nikodem Pikor \u00b7 Civil No.
1RC19-1-003776 \u00b7 Circuit Court of the First Circuit, Hawaii \u00b7 appeal
CAAP-26-0000625<br>
<b>VERSION</b> v1.0 \u00b7 2026-10-31 (HST) \u00b7 prepared from the published record<br>
<b>SITE</b> __URL__</p>

<h2>What this record is</h2>
<p>An open publication of the court record in a Hawaii condominium-association case.
1,121 documents are published, each hashed with SHA-256 and matched against the register
before quotation (1,121/1,121, zero mismatches). Every quotation carries a docket number and
a page. The site also publishes what it does not have: 491 of 495 circuit entries are present,
and the four entries it cannot show are named. It states no conclusion about the merits.</p>

<h2>Five verified figures</h2>
<p>Each quotation was downloaded from the record and SHA-256 matched before it was quoted.</p>
<table><thead><tr><th>Figure</th><th>What it is</th><th>Quotation</th><th>Cite</th></tr></thead>
<tbody>
__FIGROWS__
</tbody></table>

<h2>What the record contains (measured, not estimated)</h2>
<ul>
<li>1,121 published documents \u00b7 1,121/1,121 SHA-256 matches \u00b7 0 mismatches.</li>
<li>491 of 495 circuit entries present \u00b7 four named gaps: Dkt 484, 486, 487, 493.</li>
<li>The shared Drive behind the material: 2,114 files, 42 folders, 6.29 GB, counted recursively.</li>
</ul>

<h2>Three URLs to verify</h2>
<ol class="urls">
<li>__URL__/ \u2014 the record and its verification totals</li>
<li>__URL__/numbers \u2014 the five figures above, each with its page</li>
<li>__URL__/coverage \u2014 the four declared gaps</li>
</ol>

<h2>No conclusion about the merits</h2>
<div class="box"><p>This sheet reports what the documents say and what the site measured.
It states no conclusion about the merits of the case, about the appeal, or about the conduct
of any party. Every figure is quoted with a docket and a page so that it can be checked
against the record; nothing here is an opinion.</p></div>

<h2>Contact</h2>
<div class="contact">[PRESS CONTACT \u2014 name \u00b7 e-mail \u00b7 telephone]<br>
placeholder, to be completed before distribution</div>

<p class="foot">Quotations carry docket and page. Arithmetic performed by the site is
labelled as the site\u2019s. the95xrecord.vercel.app</p>
</div></body></html>""".replace("__FIGROWS__", fig_rows).replace("__URL__", URL)


def main():
    build_md()
    hp = os.path.join(HERE, "press-print.html")
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html(MD))
    pdf = os.path.join(BRAND, "press.pdf")
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--user-data-dir=" + PROFILE, "--no-pdf-header-footer",
        "--print-to-pdf=" + pdf,
        "file:///" + hp.replace("\\", "/"),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1000:], file=sys.stderr)
        raise SystemExit("chrome print-to-pdf failed")
    reader = PdfReader(pdf)
    box = reader.pages[0].mediabox
    print("press.pdf  %d page(s)  %.0f x %.0f pt  %d bytes"
          % (len(reader.pages), box.width, box.height, os.path.getsize(pdf)))
    if len(reader.pages) != 1:
        raise SystemExit("press.pdf is not one page")


if __name__ == "__main__":
    main()
