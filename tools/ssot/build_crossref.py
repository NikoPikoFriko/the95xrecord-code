"""Build a single cross-reference: docket <-> RA page <-> held file/text <-> hash <-> published URL."""
import csv, json, os, hashlib
COV = r"D:\PROJECT_CENTER\temp\aoao-dashboard\DOCKET_COVERAGE.csv"
TEXTS = r"D:\PROJECT_CENTER\temp\texts-export\texts.json"
OUT = r"C:\Users\NIKO\TEMPLE\site\data\crossref.json"
SITE = "https://the95xrecord.vercel.app"
rows = list(csv.DictReader(open(COV, encoding="utf-8")))
texts = {e["docket"]: e for e in json.load(open(TEXTS, encoding="utf-8"))["entries"]}
out = []
for r in rows:
    d = int(r["dkt"])
    entry = {
        "case": "1RC191003776",
        "docket": d,
        "code": r["code"],
        "filed": r["filed"],
        "ra_pdf_page": r["ra_pdf_page"],
        "register_url": f"{SITE}/register#dkt-{d}",
        "pdf": None,
        "text": None,
    }
    if r["has_pdf"] == "Y" and r["pdf_file"]:
        entry["pdf"] = {"file": r["pdf_file"].replace("\\", "/"), "availability": "station"}
    if d in texts:
        t = texts[d]
        entry["text"] = {"file": t["text_file"], "grade": t["grade"], "method": t["method"],
                         "sha256": t["text_sha256"], "source_sha256": t["source_sha256"],
                         "published_url": f"{SITE}/{t['text_file']}" if t.get("text_file") else None}
    out.append(entry)
json.dump({"schema": "ssot/crossref@1", "generated": "2026-11-03", "case": "1RC191003776",
           "count": len(out), "note": "one row per RA register docket: where it sits in the record, what is held, and where it is published",
           "entries": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("crossref rows:", len(out), "| with text:", sum(1 for e in out if e["text"]), "| with pdf:", sum(1 for e in out if e["pdf"]))
