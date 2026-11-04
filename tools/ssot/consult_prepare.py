#!/usr/bin/env python3
"""Prepare an Argon consult brief from the LIVE state — no frozen header values (T78).

The previous version printed `deployment: unknown`, a stale ssot sha and "texts 266" because it took
the deployment id from the FIRST entry of versions.json and the counts from typed template text. Every
value in this brief is now fetched or derived in the same run, and the run refuses to write a brief when
its own header does not match the bytes it just downloaded.

What is fetched live:
  * /ssot.json            -> sha256, bytes, build_timestamp, deployment{id,derivable,previous,as_of,note},
                            cases[].counts.rows, library.text_only
  * /data/texts.json      -> count (the corpus size)
  * /data/crossref.json   -> count
  * /data/ssot.sqlite     -> sha256
  * /api/v1/index.json    -> availability probe for the machine API
  * evidence (publication/mirror) -> canonical manifests, each value named with its source
  * JIMS probe            -> literal `curl` (http_code + <title>), not a claim

Assertions before writing (any failure -> exit 2, **no brief written**):
  A1 the `ssot_sha256` line in the produced brief == sha256 of the /ssot.json downloaded in this run
  A2 deployment.id is present and not "unknown"
  A3 no banned frozen literal appears in the brief ("deployment: unknown", "texts 266", "266 text",
     the old sha prefix 2ae91ad8)

Usage:
  python tools/ssot/consult_prepare.py
  python tools/ssot/consult_prepare.py --generated-at 2026-11-04T12:00:00-10:00   # determinism tests
  python tools/ssot/consult_prepare.py --base file:///.../fixture --out <dir>     # offline test
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = "https://the95xrecord.vercel.app"
OUT = r"D:\PROJECT_CENTER\temp\argon-consult"
HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "consult_brief_template_header.md")
TEMPLE = r"C:\Users\NIKO\TEMPLE"
EVID = r"D:\PROJECT_CENTER\temp\ssot-arch"
MIRROR = os.path.join(TEMPLE, "verify", "mirror-2026-11-03")
HST = timezone(timedelta(hours=-10))
BANNED = ["deployment: unknown", "texts 266", "266 text", "2ae91ad8"]


def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "ssot-consult/2"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def jload(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def evidence():
    """Every evidence figure carries its source, or an explicit `unavailable: <reason>`."""
    ev = {}
    # objects + mirror: the canonical mirror verification (documents + 4 remote destinations)
    try:
        mv = jload(os.path.join(EVID, "MIRROR_VERIFY.json"))
        rows = mv.get("rows") or []
        dests = [c for c in ("local", "github", "github_served", "drive", "box") if rows and c in rows[0]]

        def _row_ok(r):
            """github_served records the sha it actually served, not the word MATCH."""
            for c in dests:
                v = str(r.get(c, "")).upper()
                if c == "github_served":
                    if v != str(r.get("sha256", "")).upper():
                        return False
                elif v != "MATCH":
                    return False
            return True

        ok = sum(1 for r in rows if _row_ok(r))
        ev["objects"] = {"value": mv.get("documents"), "source": "temp/ssot-arch/MIRROR_VERIFY.json"}
        ev["mirror"] = {"value": f"{ok}/{len(rows)}", "source": "temp/ssot-arch/MIRROR_VERIFY.json",
                        "destinations": dests, "pass": mv.get("pass_"), "fail": mv.get("fail")}
    except Exception as exc:
        ev["objects"] = f"unavailable: MIRROR_VERIFY.json ({type(exc).__name__})"
        ev["mirror"] = f"unavailable: MIRROR_VERIFY.json ({type(exc).__name__})"
    # catalogue: the exported object catalogue
    try:
        cat = jload(os.path.join(EVID, "R2_CATALOGUE_80.json"))
        ev["catalogue"] = {"value": cat.get("rows"), "verified": cat.get("pass_verify"),
                           "source": "temp/ssot-arch/R2_CATALOGUE_80.json"}
    except Exception as exc:
        ev["catalogue"] = f"unavailable: R2_CATALOGUE_80.json ({type(exc).__name__})"
    # receipts: the remote receipt verification table (header row excluded)
    rp = os.path.join(MIRROR, "RECEIPTS_REMOTE_VERIFY.tsv")
    try:
        n = sum(1 for i, line in enumerate(open(rp, encoding="utf-8", errors="replace")) if i and line.strip())
        ev["receipts"] = {"value": n, "source": "verify/mirror-2026-11-03/RECEIPTS_REMOTE_VERIFY.tsv"}
    except Exception as exc:
        ev["receipts"] = f"unavailable: RECEIPTS_REMOTE_VERIFY.tsv ({type(exc).__name__})"
    # published + ledger: the publication view manifest and the ledger it names
    try:
        pv = jload(os.path.join(TEMPLE, "captures", "PUBLICATION_VIEW_MANIFEST.json"))
        ev["published"] = {"value": pv.get("published"), "rows": pv.get("rows"),
                           "source": "captures/PUBLICATION_VIEW_MANIFEST.json"}
    except Exception as exc:
        ev["published"] = f"unavailable: PUBLICATION_VIEW_MANIFEST.json ({type(exc).__name__})"
    lp = os.path.join(EVID, "repo-build", "captures", "ledger.jsonl")
    try:
        n = sum(1 for line in open(lp, encoding="utf-8", errors="replace") if line.strip())
        ev["ledger"] = {"value": n, "source": "temp/ssot-arch/repo-build/captures/ledger.jsonl"}
    except Exception as exc:
        ev["ledger"] = f"unavailable: repo-build ledger ({type(exc).__name__})"
    return ev


def jims_probe(timeout=40):
    """Literal HTTP evidence from the court: status code + page title, via `curl`."""
    url = "https://jimspss1.courts.state.hi.us/JIMSExternal/manage-cases.iface"
    out = {"url": url, "at": datetime.now(HST).replace(microsecond=0).isoformat(),
           "argv": "curl -s -o NUL -m 40 -w '%{http_code}' <url> ; curl -s -m 40 <url> -> <title>"}
    try:
        code = subprocess.run(["curl", "-s", "-o", os.devnull, "-m", str(timeout),
                               "-w", "%{http_code}", url],
                              capture_output=True, text=True, timeout=timeout + 20)
        out["http_code"] = (code.stdout or "").strip() or "(no output)"
        page = subprocess.run(["curl", "-s", "-m", str(timeout), url],
                              capture_output=True, text=True, timeout=timeout + 20)
        m = re.search(r"<title>(.*?)</title>", page.stdout or "", re.S | re.I)
        out["title"] = (m.group(1).strip() if m else "(no <title>)")
    except Exception as exc:
        out["http_code"] = f"unavailable: {type(exc).__name__}"
        out["title"] = "unavailable"
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE, help="served base URL (tests may point at a fixture)")
    ap.add_argument("--out", default=OUT, help="output directory")
    ap.add_argument("--generated-at", default=None,
                    help="fix generated_at (determinism tests); default: now in HST")
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    now = (datetime.fromisoformat(args.generated_at) if args.generated_at
           else datetime.now(HST).replace(microsecond=0))
    date = now.strftime("%Y-%m-%d")
    unavailable = []

    ssot_raw = get(f"{args.base}/ssot.json")
    ssot = json.loads(ssot_raw)
    try:
        texts_raw = get(f"{args.base}/data/texts.json")
        texts = json.loads(texts_raw)
    except Exception as exc:
        texts, texts_raw = {}, b""
        unavailable.append(f"texts.json: {type(exc).__name__}")
    try:
        cross_raw = get(f"{args.base}/data/crossref.json")
        cross = json.loads(cross_raw)
    except Exception as exc:
        cross, cross_raw = {}, b""
        unavailable.append(f"crossref.json: {type(exc).__name__}")
    try:
        sqlite_raw = get(f"{args.base}/data/ssot.sqlite")
    except Exception as exc:
        sqlite_raw = b""
        unavailable.append(f"ssot.sqlite: {type(exc).__name__}")
    try:
        api_index = json.loads(get(f"{args.base}/api/v1/index.json"))
    except Exception as exc:
        api_index = None
        unavailable.append(f"api/v1/index.json: {type(exc).__name__}")

    dep = ssot.get("deployment") or {}
    cases = {c.get("case"): (c.get("counts") or {}).get("rows") for c in ssot.get("cases") or []}
    state = {
        "generated_at": now.isoformat(),
        "base": args.base,
        "ssot": {"sha256": sha(ssot_raw), "bytes": len(ssot_raw),
                 "build_timestamp": ssot.get("build_timestamp")},
        "deployment": {"id": dep.get("id") or "", "derivable": dep.get("derivable"),
                       "previous": dep.get("previous"), "as_of": dep.get("as_of"),
                       "live_at_build": dep.get("live_at_build"),
                       "note": dep.get("describes") or dep.get("note")},
        "counts": {"trial_rows": cases.get("1RC191003776"),
                   "appeal_rows": cases.get("CAAP-26-0000625"),
                   "texts": (texts or {}).get("count"),
                   "crossref": (cross or {}).get("count"),
                   "library_text_only": (ssot.get("library") or {}).get("text_only")},
        "datasets": {"ssot.json": sha(ssot_raw),
                     "texts.json": sha(texts_raw) if texts_raw else "unavailable",
                     "crossref.json": sha(cross_raw) if cross_raw else "unavailable",
                     "ssot.sqlite": sha(sqlite_raw) if sqlite_raw else "unavailable"},
        "api": {"index_available": api_index is not None},
        "evidence": evidence(),
        "jims_probe": jims_probe(),
        "unavailable": unavailable,
    }
    if api_index:
        try:
            state["api"]["hash_count"] = api_index["endpoints"]["hash"]["count"]
        except (KeyError, TypeError):
            state["api"]["hash_count"] = "unavailable: no endpoints.hash.count"

    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, "verify_published.py")],
                           capture_output=True, text=True, timeout=180)
        lines = (p.stdout or "").strip().splitlines()
        state["verifier"] = lines[-1] if lines else f"verifier rc={p.returncode} with no output"
    except Exception as exc:
        state["verifier"] = f"verifier unavailable: {type(exc).__name__}: {exc}"

    try:
        state["commits"] = subprocess.run(["git", "-C", TEMPLE, "log", "--oneline", "-5"],
                                          capture_output=True, text=True, timeout=30
                                          ).stdout.strip().splitlines() or ["(no commits)"]
    except Exception as exc:
        state["commits"] = [f"(git unavailable: {type(exc).__name__})"]

    ssot_sha16 = state["datasets"]["ssot.json"][:16]
    dep_id = state["deployment"]["id"] or "unavailable: no deployment.id in /ssot.json"
    dep_flags = (f"derivable={state['deployment']['derivable']} "
                 f"previous={state['deployment']['previous']} "
                 f"as_of={state['deployment']['as_of']}")
    c = state["counts"]
    counts_line = ("trial %s rows · appeal %s rows · texts %s · crossref %s · text-only dockets %s"
                   % (c.get("trial_rows"), c.get("appeal_rows"), c.get("texts"),
                      c.get("crossref"), c.get("library_text_only")))
    datasets_line = ("ssot.json %s · texts %s · crossref %s · sqlite %s"
                     % (ssot_sha16, str(state["datasets"]["texts.json"])[:16],
                        str(state["datasets"]["crossref.json"])[:16],
                        str(state["datasets"]["ssot.sqlite"])[:16]))

    def ev_line(key, label):
        v = state["evidence"].get(key)
        if isinstance(v, dict):
            extra = ""
            if key == "mirror" and v.get("destinations"):
                extra = " (" + ", ".join(v["destinations"]) + ")"
            return f"{label}: {v.get('value')}{extra} [{v.get('source')}]"
        return f"{label}: {v}"

    probe = state["jims_probe"]
    probe_line = (f"HTTP {probe.get('http_code')} · <title>{probe.get('title')}</title> · "
                  f"{probe.get('url')}")

    tpl = open(TEMPLATE, encoding="utf-8").read()
    brief = (tpl
             .replace("{{DATE}}", date)
             .replace("{{GENERATED_AT}}", state["generated_at"])
             .replace("{{BUILD_TS}}", str(state["ssot"]["build_timestamp"]))
             .replace("{{DEPLOYMENT_ID}}", dep_id)
             .replace("{{DEPLOYMENT_FLAGS}}", dep_flags)
             .replace("{{TEXTS_COUNT}}", str(c.get("texts") if c.get("texts") is not None
                                                else "unavailable: texts.json"))
             .replace("{{SSOT_SHA}}", ssot_sha16)
             .replace("{{COMMITS}}", " | ".join(state["commits"]))
             .replace("{{DATASETS_LINE}}", datasets_line)
             .replace("{{COUNTS_LINE}}", counts_line)
             .replace("{{EVIDENCE_LINE}}", " · ".join([
                 ev_line("objects", "objects"), ev_line("catalogue", "catalogue"),
                 ev_line("published", "published"), ev_line("receipts", "receipts"),
                 ev_line("ledger", "publication ledger"), ev_line("mirror", "mirror")]))
             .replace("{{JIMS_PROBE_LINE}}", probe_line)
             .replace("{{VERIFIER_RESULT}}", state["verifier"]))

    # ---- assertions: the brief must agree with the bytes fetched in THIS run
    problems = []
    m = None
    for line in brief.splitlines():
        if line.strip().startswith("ssot_sha256"):
            m = line.split(":", 1)[1].strip().split()[0]
            break
    if not m or m != ssot_sha16:
        problems.append(f"A1 ssot_sha256 in brief ({m!r}) != sha256 of the /ssot.json fetched now "
                        f"({ssot_sha16})")
    if not state["deployment"]["id"] or state["deployment"]["id"].lower() == "unknown":
        problems.append("A2 deployment.id missing or 'unknown' in /ssot.json")
    # scan the header's state lines only: the commits line is repo history and may legitimately quote an
    # old change name ("T17: 266 texts + crossref"), which is not a current-state label.
    header_only = chr(10).join(l for l in brief.splitlines()
                               if not l.strip().startswith("commits (last 5)"))
    low = header_only.lower()
    for literal in BANNED:
        if literal in low:
            problems.append(f"A3 banned frozen literal in the header: {literal!r}")

    if problems:
        for p in problems:
            print(f"FAIL  {p}")
        print("BRIEF NOT PUBLISHED — assertion failed; no BRIEF file written to " + args.out)
        state["assertions"] = {"verdict": "FAIL", "problems": problems}
        json.dump(state, open(os.path.join(args.out, "STATE-FAILED.json"), "w", encoding="utf-8",
                              newline="\n"), ensure_ascii=False, indent=1)
        return 2

    state["assertions"] = {"verdict": "PASS", "a1_ssot_sha256": ssot_sha16,
                           "a2_deployment_id": state["deployment"]["id"],
                           "a3_no_banned_literals": True}
    path = os.path.join(args.out, f"BRIEF-{date}.md")
    open(path, "w", encoding="utf-8", newline="\n").write(brief)
    json.dump(state, open(os.path.join(args.out, f"STATE-{date}.json"), "w", encoding="utf-8",
                          newline="\n"), ensure_ascii=False, indent=1)
    print(f"BRIEF={path}")
    print(f"STATE={os.path.join(args.out, f'STATE-{date}.json')}")
    print(f"ASSERTIONS: PASS — ssot_sha256 {ssot_sha16} == fetched /ssot.json; deployment "
          f"{state['deployment']['id']}; no banned literals")
    print(f"counts: {json.dumps(state['counts'], ensure_ascii=False)}")
    print(f"jims_probe: {probe_line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
