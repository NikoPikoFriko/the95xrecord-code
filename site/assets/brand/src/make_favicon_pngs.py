#!/usr/bin/env python3
"""Rasterise favicon.svg to favicon-32.png and favicon-180.png.

Chromium renders the SVG at 720 px (antialiased from the vector), then Pillow
downsamples with LANCZOS to the two target sizes. Nothing is drawn by hand, so
the PNGs and the SVG cannot drift apart.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
PREVIEW = os.path.join(BRAND, "preview")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = "C:/Temp/chrome-brand"
TMP = os.path.join(PREVIEW, "_icon.html")
BIG = os.path.join(PREVIEW, "_icon-720.png")

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:#f5f1e6}
img{display:block;width:720px;height:720px;margin:0}
</style></head><body><img src="%s" width="720" height="720"></body></html>""" % (
    "file:///" + os.path.join(BRAND, "favicon.svg").replace("\\", "/")
)

os.makedirs(PREVIEW, exist_ok=True)
with open(TMP, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(HTML)

cmd = [
    CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
    "--force-device-scale-factor=1", "--user-data-dir=" + PROFILE,
    "--window-size=720,720", "--screenshot=" + BIG,
    "file:///" + TMP.replace("\\", "/"),
]
subprocess.run(cmd, check=True, capture_output=True)

src = Image.open(BIG).convert("RGB")
if src.size != (720, 720):
    print("unexpected render size", src.size, file=sys.stderr)

for size, name in ((32, "favicon-32.png"), (180, "favicon-180.png")):
    out = src.resize((size, size), Image.LANCZOS)
    path = os.path.join(BRAND, name)
    out.save(path, "PNG", optimize=True)
    print("%-16s %dx%d %d bytes" % (name, size, size, os.path.getsize(path)))
