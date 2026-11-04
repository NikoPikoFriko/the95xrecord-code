#!/usr/bin/env python3
"""Verify the live SSOT against its own published datasets (read-only, no network writes)."""
import json, hashlib, urllib.request, sys
BASE = "https://the95xrecord.vercel.app"
def get(u):
    with urllib.request.urlopen(u, timeout=30) as r: return r.read()
def main():
    fails = []
    ssot = json.loads(get(f"{BASE}/ssot.json"))
    if get(f"{BASE}/ssot.json") != get(f"{BASE}/data/ssot.json"): fails.append("ssot.json != data/ssot.json")
    texts = json.loads(get(f"{BASE}/data/texts.json"))
    if texts.get("count") != len(texts["entries"]): fails.append("texts count mismatch")
    for e in texts["entries"][:20]:
        b = get(f"{BASE}/{e['text_file']}")
        if hashlib.sha256(b).hexdigest() != e["text_sha256"]: fails.append(f"hash {e['text_file']}")
    cross = json.loads(get(f"{BASE}/data/crossref.json"))
    if cross.get("count") != 495: fails.append("crossref count != 495")
    routes = ["/", "/appeal", "/register", "/access", "/texts", "/coverage", "/sitemap.xml"]
    for r in routes:
        try: get(BASE + r)
        except Exception: fails.append(f"route {r}")
    print("FAILS:", fails if fails else "none")
    return 1 if fails else 0
if __name__ == "__main__":
    sys.exit(main())
