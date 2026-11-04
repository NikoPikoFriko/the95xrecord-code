#!/usr/bin/env python3
"""Rebuild the published text corpus from the held sources — byte-exact, provenance-carrying.

Rules learned the hard way (see BUILD_REPORT_TEXTS.md):
  * read the source in BINARY and publish those exact bytes — never open(...,'w') on Windows;
  * hash the bytes you publish, so text_sha256 == source_sha256 by construction;
  * never retype: the site's /texts/<file>.txt is a byte copy.
Inputs : register/coverage.json (or the station CSVs), the held text files
Outputs: site/texts/*.txt, site/data/texts.json, TEXTS_MANIFEST.sha256 (LF)
"""
import csv, json, os, hashlib, sys

ROOM = os.environ.get("CASE_ROOM", r"E:\REAL MAGIC\00_LEGAL\_1RC191003776 AOAO_Marine_Surf")
COV = os.environ.get("COVERAGE_CSV", r"D:\PROJECT_CENTER\temp\aoao-dashboard\DOCKET_COVERAGE.csv")
SITE = os.environ.get("SITE_DIR", r"C:\Users\NIKO\TEMPLE\site")
TXT_DIR = os.path.join(SITE, "texts")
DATA = os.path.join(SITE, "data")

def main():
    os.makedirs(TXT_DIR, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    rows = list(csv.DictReader(open(COV, encoding="utf-8")))
    target = [r for r in rows if r["has_pdf"] == "N" and r["has_text"] == "Y" and r["code"].upper() != "NEF"]
    items = []
    for r in target:
        src = os.path.join(ROOM, r["text_file"])
        if not os.path.isfile(src):
            print("MISSING", src, file=sys.stderr); continue
        raw = open(src, "rb").read()                      # BINARY — the whole point
        src_sha = hashlib.sha256(raw).hexdigest()
        name = f"{int(r['dkt']):03d}__{r['code'].replace('*','STAR').replace('/','-') or 'DOC'}__{r['filed']}.txt"
        open(os.path.join(TXT_DIR, name), "wb").write(raw)  # BINARY — byte copy
        method = "native" if "ocr" not in r["text_file"].lower() else "ocr"
        items.append({
            "case": "1RC191003776", "docket": int(r["dkt"]), "code": r["code"], "filed": r["filed"],
            "ra_pdf_page": r["ra_pdf_page"], "grade": "PARTIAL" if method == "ocr" else "OBS",
            "method": method, "source_file": r["text_file"].replace("\\", "/"),
            "source_sha256": src_sha, "text_file": f"texts/{name}", "text_sha256": src_sha,
            "bytes": len(raw), "lines": raw.count(b"\n") + 1,
        })
    items.sort(key=lambda x: x["docket"])
    json.dump({"schema": "site-ssot/text-corpus@1", "case": "1RC191003776", "count": len(items),
               "note": "Text-only dockets published with full provenance; files are byte copies of the held sources.",
               "entries": items}, open(os.path.join(DATA, "texts.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(SITE, "TEXTS_MANIFEST.sha256"), "w", encoding="utf-8", newline="\n") as f:
        for it in items:
            f.write(f"{it['text_sha256']}  {it['text_file']}\n")
    print(f"texts: {len(items)} files, {sum(i['bytes'] for i in items)} bytes")

if __name__ == "__main__":
    main()
