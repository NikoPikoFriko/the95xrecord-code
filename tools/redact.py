#!/usr/bin/env python3
"""redact.py — PII redaction for court-record email exhibits (operator decision L-02).

Redacts: personal cell/home phone numbers, private home addresses, personal email handles.
Keeps: full names, timestamps, body text — the evidentiary substance.

Usage:
  python redact.py FILE [--out OUT]   redact one text file
  python redact.py --selftest         prove the patterns fire and that text survives
"""
import argparse
import re
import sys

PHONE = re.compile(r"(?<![\w-])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?![\w-])")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ADDR = re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|"
                  r"Boulevard|Blvd|Way|Place|Pl|Court|Ct)\b\.?")
PII_EMAILS = {-1}  # set of personal handles to keep? empty: redact all


def redact(text, keep_emails=()):
    n = {"phone": 0, "email": 0, "address": 0}
    def ph(m):
        n["phone"] += 1
        return "[PHONE REDACTED]"
    def em(m):
        if m.group(0).lower() in keep_emails:
            return m.group(0)
        n["email"] += 1
        return "[EMAIL REDACTED]"
    def ad(m):
        n["address"] += 1
        return "[ADDRESS REDACTED]"
    out = PHONE.sub(ph, text)
    out = EMAIL.sub(em, out)
    out = ADDR.sub(ad, out)
    return out, n


def selftest():
    cases = []
    sample = ("Call 808-555-1234 or (808) 555-9876. Email terry@revereandassociates.com. "
              "Address 1234 Kalaheo Avenue. Judge Kupau-Odo. Mar 8, 2021 at 5:00 PM.")
    out, n = redact(sample)
    cases.append(("phone redacted", "[PHONE REDACTED]" in out, "two numbers masked"))
    cases.append(("email redacted", "[EMAIL REDACTED]" in out, "handle absent" if "terry@" not in out else "LEAK"))
    cases.append(("address redacted", "[ADDRESS REDACTED]" in out, out[-60:]))
    cases.append(("name kept", "Kupau-Odo" in out, "name survives"))
    cases.append(("date kept", "Mar 8, 2021" in out, "date survives"))
    cases.append(("counts reported", n["phone"] == 2, str(n)))
    for name, ok, detail in cases:
        print(("PASS " if ok else "FAIL ") + name + " — " + detail)
    return 0 if all(c[1] for c in cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.file:
        ap.print_help()
        return 2
    text = open(a.file, encoding="utf-8").read()
    out, n = redact(text)
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="").write(out)
    else:
        sys.stdout.write(out)
    print("\nredacted: %d phones, %d emails, %d addresses" % (n["phone"], n["email"], n["address"]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
