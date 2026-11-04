#!/usr/bin/env python3
"""Write og/MANIFEST.json, posts/MANIFEST.json and CHECKSUMS.txt from the card table.

The metadata is derived from the same text the cards render, so a manifest line
cannot describe an image that does not exist. Run after build_cards.py.
"""
import hashlib
import importlib.util
import json
import os
import re
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location(
    "build_cards", os.path.join(HERE, "build_cards.py"))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

URL = "https://" + bc.URL   # og:url and og:image must be absolute


def plain(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


def page_url(slug):
    return URL + "/" if slug == "index" else URL + "/" + slug


og_cards = []
for c in bc.OG:
    og_cards.append({
        "page": c["slug"],
        "og:title": plain(c["h1"]),
        "og:description": plain(c["sub"]),
        "og:url": page_url(c["slug"]),
        "og:image": "%s/assets/brand/og/%s.png" % (URL, c["slug"]),
        "file": "og/%s.png" % c["slug"],
        "cite": c.get("cite"),
        "status": plain(c["status"][1]) if c.get("status") else None,
    })

og_manifest = {
    "generated": time.strftime("%Y-%m-%d %H:%M %Z"),
    "generator": "src/build_cards.py",
    "size": "1200x630",
    "note": ("Designed title cards, not screenshots of the live pages: they keep the site's "
             "palette, eyebrow, serif headline and docket cites, and they do not update when "
             "page copy changes. og:image paths assume the site root is site/; nothing here "
             "was deployed or tested against a live social scraper."),
    "cards": og_cards,
}

post_cards = []
for c in bc.POSTS:
    post_cards.append({
        "n": c["n"],
        "file": "posts/%02d.png" % c["n"],
        "page": c["slug"],
        "url": page_url(c["slug"]),
        "headline": plain(c["h1"]),
        "words": bc.words(plain(c["h1"])),
        "cite": c["cite"],
        "support": plain(c["support"]),
        "in_feed": "posts/FINAL/%d-post.md" % c["n"],
    })

post_manifest = {
    "generated": time.strftime("%Y-%m-%d %H:%M %Z"),
    "generator": "src/build_cards.py",
    "size": "1600x900",
    "note": ("One image per final post. Headline is 12 words or fewer (asserted at build "
             "time); every card carries exactly one [Dkt] cite and the bottom line "
             "the95xrecord.vercel.app."),
    "cards": post_cards,
}

for path, data in ((os.path.join(BRAND, "og", "MANIFEST.json"), og_manifest),
                   (os.path.join(BRAND, "posts", "MANIFEST.json"), post_manifest)):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote", os.path.relpath(path, BRAND))

# ---------------------------------------------------------------- checksums

rows = []
for root, dirs, files in os.walk(BRAND):
    dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
    for name in sorted(files):
        if name == "CHECKSUMS.txt":
            continue
        p = os.path.join(root, name)
        rel = os.path.relpath(p, BRAND).replace("\\", "/")
        with open(p, "rb") as fh:
            data = fh.read()
        dims = ""
        if name.lower().endswith(".png"):
            im = Image.open(p)
            dims = "%dx%d" % im.size
        rows.append((rel, len(data), dims, hashlib.sha256(data).hexdigest()))

rows.sort()
out = ["The 95x Record - brand assets - sha256 of every shipped file",
       "generated %s by src/make_manifests.py" % time.strftime("%Y-%m-%d %H:%M %Z"),
       "",
       "%-38s %9s %10s  sha256" % ("file", "bytes", "pixels"),
       "-" * 100]
for rel, size, dims, sha in rows:
    out.append("%-38s %9d %10s  %s" % (rel, size, dims, sha))
out.append("")
out.append("%d files" % len(rows))

path = os.path.join(BRAND, "CHECKSUMS.txt")
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(out) + "\n")
print("wrote CHECKSUMS.txt (%d files)" % len(rows))
