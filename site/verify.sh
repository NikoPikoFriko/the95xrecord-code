#!/bin/sh
# verify.sh — check the published record without trusting its JavaScript.
# usage:  curl -s https://the95xrecord.vercel.app/verify.sh | sh
# Requires: curl (or wget), gpg, and python3 OR python/py (Windows). Prints VERDICT: PASS|FAIL.
set -u
BASE="${BASE:-https://the95xrecord.vercel.app}"
FPR="26E607360BC8A529C289866DC4F8D52EC76EE1C5"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAIL=0
# python3 on POSIX, python/py on Windows (the Microsoft Store alias for python3 is not an interpreter)
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "FAIL  no python interpreter found (python3/python/py)"; echo "VERDICT: FAIL"; exit 1; }
say() { printf '%s\n' "$*"; }
bad() { say "FAIL  $*"; FAIL=1; }

get() { # url, outfile
  if command -v curl >/dev/null 2>&1; then curl -fsS "$1" -o "$2" || return 1
  else wget -qO "$2" "$1" || return 1; fi
}

say "== fetching published artefacts from $BASE"
for f in data/transparency_log.jsonl data/transparency_log.jsonl.asc ssot-signing-key.asc MANIFEST.csv MANIFEST.csv.asc; do
  get "$BASE/$f" "$TMP/$(echo "$f" | tr '/' '_')" || bad "cannot fetch $f"
done
[ "$FAIL" = 0 ] || { say "VERDICT: FAIL"; exit 1; }

say "== importing the published key"
export GNUPGHOME="$TMP/gnupg"; mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME" 2>/dev/null
gpg --batch --quiet --import "$TMP/ssot-signing-key.asc" || bad "cannot import ssot-signing-key.asc"
GOT_FPR=$(gpg --batch --with-colons --fingerprint 2>/dev/null | awk -F: '/^fpr:/{print $10; exit}')
[ "$GOT_FPR" = "$FPR" ] || bad "published key fingerprint $GOT_FPR != documented $FPR"

say "== verifying the detached signatures"
for pair in "data_transparency_log.jsonl data_transparency_log.jsonl.asc" "MANIFEST.csv MANIFEST.csv.asc"; do
  set -- $pair
  gpg --batch --verify "$TMP/$2" "$TMP/$1" 2>/dev/null || bad "signature does not verify for $1"
done

say "== recomputing the chain"
BASE="$BASE" "$PY" - "$TMP/data_transparency_log.jsonl" "$TMP" <<'PY' || FAIL=1
import hashlib, json, sys, os
log, tmp = sys.argv[1], sys.argv[2]
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
prev, n, newest = "GENESIS", 0, None
for line in open(log, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    e = json.loads(line); n += 1
    h = hashlib.sha256(canon({k: v for k, v in e.items() if k != "entry_hash"})).hexdigest()
    if h != e.get("entry_hash"): print(f"FAIL  seq {n}: entry_hash mismatch"); sys.exit(1)
    if e.get("prev_hash") != prev: print(f"FAIL  seq {n}: prev_hash link broken"); sys.exit(1)
    if e.get("seq") != n: print(f"FAIL  seq {n}: numbering broken"); sys.exit(1)
    prev, newest = h, e
print(f"PASS  chain: {n} entries, every entry_hash recomputes, every prev_hash links")
print(f"PASS  newest entry {newest['build_timestamp']} (deployment {newest.get('deployment_id_at_build')})")
datasets = newest.get("datasets") or {}
base = os.environ.get("BASE", "https://the95xrecord.vercel.app").rstrip("/")
bad = 0
for rel, want in sorted(datasets.items()):
    url = base + "/" + rel
    try:
        import urllib.request
        body = urllib.request.urlopen(url, timeout=120).read()
    except Exception as exc:
        print(f"FAIL  dataset {rel}: cannot fetch ({exc})"); bad += 1; continue
    got = hashlib.sha256(body).hexdigest()
    if got != want:
        print(f"FAIL  dataset {rel}: served {got[:16]} != logged {want[:16]}"); bad += 1
if bad: sys.exit(1)
print(f"PASS  newest entry's {len(datasets)} dataset hashes match the bytes served")
PY

say "== checking /verify.sh is served and self-consistent"
get "$BASE/verify.sh" "$TMP/verify.sh" || bad "cannot fetch /verify.sh"
grep -q "VERDICT:" "$TMP/verify.sh" || bad "/verify.sh does not print a verdict"
grep -q "$FPR" "$TMP/verify.sh" || bad "/verify.sh does not carry the documented fingerprint"

if [ "$FAIL" = 0 ]; then say "VERDICT: PASS"; exit 0; else say "VERDICT: FAIL"; exit 1; fi
