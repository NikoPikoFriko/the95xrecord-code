#!/usr/bin/env python3
"""Generate preview/brand-preview.html: the wordmark on paper and on ink.

The wordmark is inlined so that fill="currentColor" is exercised exactly as it
would be on the site (host sets `color`). Also shows the favicon at 180, 32 and
16 px, and the 16 px icon upscaled x8 (nearest) for pixel inspection.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
OUT = os.path.join(BRAND, "preview", "brand-preview.html")

wm = open(os.path.join(BRAND, "wordmark.svg"), encoding="utf-8").read()
fav = open(os.path.join(BRAND, "favicon.svg"), encoding="utf-8").read()


def strip_header(svg):
    return svg.split("?>", 1)[-1]


wm_inline = strip_header(wm).replace('width="474.22" height="94.47"', 'width="474" height="94"')
fav_inline = strip_header(fav).replace('width="32" height="32"', 'width="180" height="180"')
fav32 = strip_header(fav)
fav16 = strip_header(fav).replace('width="32" height="32"', 'width="16" height="16"')
fav48 = strip_header(fav).replace('width="32" height="32"', 'width="48" height="48"')

html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Brand preview — The 95x Record</title>
<style>
  html,body{margin:0;background:#e8e4d8}
  .row{display:flex}
  .panel{flex:1;padding:56px 64px;min-height:300px;box-sizing:border-box}
  .panel-paper{background:#f5f1e6;color:#111111}
  .panel-ink{background:#111111;color:#f5f1e6}
  .panel-site{background:#faf9f7;color:#111111}
  .cap{font:11px/1.4 Consolas,Menlo,ui-monospace,monospace;letter-spacing:.18em;
       text-transform:uppercase;opacity:.55;margin-bottom:26px}
  .foot{background:#e8e4d8;padding:34px 64px;font:12px/1.6 Consolas,Menlo,monospace;color:#444}
  .icons{display:flex;gap:36px;align-items:flex-end;background:#f5f1e6;padding:34px 64px}
  .icons div{text-align:center;font:10px/1.4 Consolas,Menlo,monospace;color:#555}
  .zoom{image-rendering:pixelated}
  h2{font:12px/1 Consolas,Menlo,monospace;letter-spacing:.2em;margin:0 0 18px;opacity:.6;text-transform:uppercase}
</style></head><body>
<div class="row">
  <div class="panel panel-paper"><h2>On paper #f5f1e6 · color #111</h2>__WM__</div>
  <div class="panel panel-ink"><h2>On ink #111 · color #f5f1e6</h2>__WM__</div>
</div>
<div class="panel panel-site" style="padding-top:34px;padding-bottom:34px">
  <h2 style="margin-bottom:14px">On the live site background #faf9f7</h2>__WM__
</div>
<div class="icons">
  <div>__FAV180__<br>180 px</div>
  <div>__FAV48__<br>48 px</div>
  <div>__FAV32__<br>32 px</div>
  <div>__FAV16__<br>16 px</div>
  <div>__FAV16Z__<br>16 px, x8</div>
</div>
<div class="foot">wordmark.svg 474 x 94.5 · favicon.svg 32 x 32 (paper field, ink 95, red bar) ·
outlines from Georgia / Consolas, no font dependency</div>
</body></html>"""

html = (html.replace("__WM__", wm_inline)
            .replace("__FAV180__", fav_inline)
            .replace("__FAV48__", fav48)
            .replace("__FAV32__", fav32)
            .replace("__FAV16__", fav16)
            .replace("__FAV16Z__", fav16.replace('<svg ', '<svg class="zoom" ', 1).replace('width="16" height="16"', 'width="128" height="128"', 1)))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(html)
print("wrote", OUT, len(html), "bytes")
