#!/usr/bin/env python3
"""Build wordmark.svg and favicon.svg for The 95x Record.

Letterforms are converted to outlines with fontTools, so the SVG files carry no
font dependency: they render identically on any machine, with any font set.

Outline sources (not shipped):
  C:/Windows/Fonts/georgia.ttf    Georgia Regular   -> wordmark
  C:/Windows/Fonts/georgiab.ttf   Georgia Bold      -> favicon
  C:/Windows/Fonts/consola.ttf    Consolas          -> CIVIL NO. line

Outputs (parent folder):
  wordmark.svg   monochrome; every letterform carries fill="currentColor"
  favicon.svg    paper tile, ink 95, red base bar (fixed colours by design)
"""
import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

GEORGIA = "C:/Windows/Fonts/georgia.ttf"
GEORGIA_BOLD = "C:/Windows/Fonts/georgiab.ttf"
CONSOLAS = "C:/Windows/Fonts/consola.ttf"

INK = "#111111"
PAPER = "#f5f1e6"
RED = "#7a1f1f"


def num(v):
    s = "%.2f" % v
    if s in ("-0.00", "0.00"):
        return "0"
    s = s.rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


# ---------------------------------------------------------------- GPOS kerning

def _coverage_glyphs(cov, order):
    if cov is None:
        return []
    glyphs = getattr(cov, "glyphs", None)
    if glyphs is not None:
        return list(glyphs)
    out = []
    for r in getattr(cov, "RangeRecord", []):
        out.extend(order[r.Start:r.End + 1])
    return out


def _class_map(classdef, order):
    m = {}
    cd = getattr(classdef, "ClassDef", classdef)
    ranges = getattr(cd, "RangeRecord", None)
    if ranges is not None:
        for r in ranges:
            for gid in range(r.Start, r.End + 1):
                if gid < len(order):
                    m[order[gid]] = r.Class
        return m
    classes = getattr(cd, "ClassDef", None)
    if classes is not None:
        for gid, cls in classes.items():
            if gid < len(order):
                m[order[gid]] = cls
    return m


def load_kern(font):
    """{(leftGlyphName, rightGlyphName): xadvanceDelta} from the GPOS 'kern' feature."""
    if "GPOS" not in font:
        return {}
    gpos = font["GPOS"].table
    if not gpos.FeatureList:
        return {}
    lookup_idx = set()
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            lookup_idx.update(fr.Feature.LookupListIndex)
    order = font.getGlyphOrder()
    pairs = {}
    for li in sorted(lookup_idx):
        lookup = gpos.LookupList.Lookup[li]
        if lookup.LookupType != 2:
            continue
        for sub in lookup.SubTable:
            fmt = getattr(sub, "Format", None)
            cov_names = _coverage_glyphs(sub.Coverage, order)
            if fmt == 1:
                for gi, ps in enumerate(sub.PairSet):
                    if gi >= len(cov_names):
                        break
                    left = cov_names[gi]
                    for pvr in ps.PairValueRecord:
                        v = pvr.Value1
                        dx = int(getattr(v, "XAdvance", 0) or 0) if v else 0
                        if dx:
                            pairs[(left, pvr.SecondGlyph)] = dx
            elif fmt == 2:
                c1 = _class_map(sub.ClassDef1, order)
                c2 = _class_map(sub.ClassDef2, order)
                by_class = {}
                for gname, cls in c2.items():
                    by_class.setdefault(cls, []).append(gname)
                for left in cov_names:
                    rec = sub.Class1Record[c1.get(left, 0)]
                    for cj, r2 in enumerate(rec.Class2Record):
                        v = r2.Value1
                        dx = int(getattr(v, "XAdvance", 0) or 0) if v else 0
                        if not dx:
                            continue
                        for right in by_class.get(cj, []):
                            pairs[(left, right)] = dx
    return pairs


# ---------------------------------------------------------------- path builder

def build_line(fontpath, text, size, tracking=0.0, kerning=True):
    font = TTFont(fontpath)
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    scale = size / upm
    kern = load_kern(font) if kerning else {}

    cmds, x, prev = [], 0.0, None
    minx = miny = 1e9
    maxx = maxy = -1e9
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            raise SystemExit("glyph missing for %r in %s" % (ch, fontpath))
        if prev and (prev, gname) in kern:
            x += kern[(prev, gname)] * scale
        adv = font["hmtx"].metrics[gname][0] * scale
        pen = SVGPathPen(gs, ntos=num)
        bpen = BoundsPen(gs)
        gs[gname].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        gs[gname].draw(TransformPen(bpen, (scale, 0, 0, -scale, x, 0)))
        d = pen.getCommands()
        if d:
            cmds.append(d)
            if bpen.bounds:
                x0, y0, x1, y1 = bpen.bounds
                minx, miny = min(minx, x0), min(miny, y0)
                maxx, maxy = max(maxx, x1), max(maxy, y1)
        x += adv + tracking
        prev = gname
    return {
        "d": " ".join(cmds),
        "advance": x - tracking,
        "bbox": (minx, miny, maxx, maxy),
        "font": os.path.basename(fontpath),
    }


def svg_open(w, h, x0, y0):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" '
        'width="%s" height="%s" role="img" aria-labelledby="t d" '
        'preserveAspectRatio="xMidYMid meet">'
        % (num(x0), num(y0), num(w), num(h), num(w), num(h))
    )


# ------------------------------------------------------------------- wordmark

def make_wordmark():
    title = build_line(GEORGIA, "The 95\u00d7 Record", 64.0, tracking=0.0)
    civil = build_line(CONSOLAS, "CIVIL NO. 1RC19-1-003776", 11.0, tracking=1.75,
                       kerning=False)

    wm_w = title["advance"]
    rule_y = 20.0
    civil_base = 42.0

    ink_top = title["bbox"][1]
    ink_bottom = civil_base + civil["bbox"][3]
    spine_w = 5.0
    spine_gap = 20.0
    spine_x = -spine_gap
    pad = 2.0
    width = wm_w - spine_x + pad
    height = ink_bottom - ink_top + pad * 2
    y0 = ink_top - pad
    spine_top = ink_top - 1.0
    spine_bottom = ink_bottom + 1.0

    parts = [
        svg_open(width, height, spine_x, y0),
        '<title id="t">The 95\u00d7 Record \u2014 Civil No. 1RC19-1-003776</title>',
        '<desc id="d">Wordmark for The 95\u00d7 Record. Letterforms are outlined; '
        'every letterform is fill="currentColor", so the mark takes the colour of '
        'the host page. The red spine is decorative and may be removed without loss.</desc>',
        '<style>.wm-spine{fill:%s}'
        '@media (prefers-color-scheme:dark){.wm-spine{fill:#c8705f}}</style>' % RED,
        '<rect class="wm-spine" x="%s" y="%s" width="%s" height="%s"/>'
        % (num(spine_x), num(spine_top), num(spine_w), num(spine_bottom - spine_top)),
        '<g fill="currentColor">',
        '<path d="%s"/>' % title["d"],
        '<rect x="0" y="%s" width="%s" height="0.9" opacity=".28"/>'
        % (num(rule_y), num(wm_w)),
        '<g transform="translate(0,%s)" opacity=".78"><path d="%s"/></g>'
        % (num(civil_base), civil["d"]),
        "</g>",
        "</svg>",
    ]
    svg = "\n".join(parts)
    path = os.path.join(OUT, "wordmark.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg + "\n")
    print("wordmark.svg  %.1f x %.1f  wm_w=%.1f  bytes=%d"
          % (width, height, wm_w, len(svg)))
    return path


# -------------------------------------------------------------------- favicon

def make_favicon():
    """Paper tile, ink 95, red base bar: legible on light and dark browser chrome.

    At 16 device pixels a multiplication sign is below the perceptual threshold,
    so the icon carries the numerals only; the x returns at wordmark and card
    sizes.
    """
    size = 32.0
    bar_h = 4.6
    ink_area_h = size - bar_h
    probe = build_line(GEORGIA_BOLD, "95", 16.0)
    fs = 16.0 * 22.5 / probe["advance"]
    line = build_line(GEORGIA_BOLD, "95", fs)
    x0, y0, x1, y1 = line["bbox"]
    tx = (size - (x1 - x0)) / 2.0 - x0
    ty = (ink_area_h + (y1 - y0)) / 2.0 - y1

    parts = [
        svg_open(size, size, 0, 0),
        '<title id="t">The 95\u00d7 Record</title>',
        '<desc id="d">Favicon: paper field, ink 95, red base bar.</desc>',
        '<rect width="32" height="32" fill="%s"/>' % PAPER,
        '<rect x="0" y="%s" width="32" height="%s" fill="%s"/>'
        % (num(size - bar_h), num(bar_h), RED),
        '<path d="%s" fill="%s" transform="translate(%s,%s)"/>'
        % (line["d"], INK, num(tx), num(ty)),
        "</svg>",
    ]
    svg = "\n".join(parts)
    path = os.path.join(OUT, "favicon.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg + "\n")
    print("favicon.svg   font-size=%.2f ink=%.1f x %.1f bytes=%d"
          % (fs, x1 - x0, y1 - y0, len(svg)))
    return path


if __name__ == "__main__":
    make_wordmark()
    make_favicon()
