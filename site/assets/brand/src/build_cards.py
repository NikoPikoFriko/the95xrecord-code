#!/usr/bin/env python3
"""Build the six 1200x630 OG cards and the eight 1600x900 post images.

Each card is a local HTML file (og/src/NN.html, posts/src/NN.html) rendered by
headless Chrome at the exact pixel size, so every PNG is reproducible from the
source in this folder:

  chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --user-data-dir=C:/Temp/chrome-brand --window-size=1200,630 \
    --screenshot=.../og/index.png file:///.../og/src/index.html

Copy rule: a card may state only figures that are printed on the site with a
docket and a page, or the site's own measured counts. Every claim card carries
exactly one [Dkt] cite.
"""
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.dirname(HERE)
OG_DIR = os.path.join(BRAND, "og")
OG_SRC = os.path.join(OG_DIR, "src")
POST_DIR = os.path.join(BRAND, "posts")
POST_SRC = os.path.join(POST_DIR, "src")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = "C:/Temp/chrome-brand"

INK = "#111111"
PAPER = "#f5f1e6"
RED = "#7a1f1f"
GREEN = "#1f5f3a"

URL = "the95xrecord.vercel.app"
CIVIL = "CIVIL NO. 1RC19-1-003776"

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:%(paper)s;color:%(ink)s;overflow:hidden}
body{width:%(w)dpx;height:%(h)dpx;font-family:Georgia,'Times New Roman',serif;
     -webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.frame{position:absolute;inset:0;padding:%(pad)dpx %(padx)dpx %(padb)dpx %(padx)dpx;
       display:flex;flex-direction:column}
.spine{position:absolute;left:0;top:0;width:10px;height:100%%;background:%(red)s}
.ghost{position:absolute;right:%(padx)dpx;top:-38px;font-family:Georgia,serif;
       font-size:%(ghost)dpx;line-height:1;color:%(ink)s;opacity:.05;letter-spacing:-.02em}
.mono{font-family:Consolas,'SF Mono',ui-monospace,Menlo,monospace}
.eyebrow{font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(eyebrow)dpx;
         letter-spacing:.2em;color:%(red)s;text-transform:uppercase}
.head{border-bottom:1px solid rgba(17,17,17,.22);padding-bottom:%(headpb)dpx}
.mid{flex:1 1 auto;display:flex;flex-direction:column;justify-content:center;
     padding:%(midskip)dpx 0 0 0}
h1{font-weight:400;letter-spacing:-.012em;line-height:1.03;max-width:%(h1max)dpx}
h1 .dim{color:rgba(17,17,17,.55)}
.h-xl{font-size:%(h1xl)dpx}
.h-l{font-size:%(h1l)dpx}
.h-m{font-size:%(h1m)dpx}
.sub{font-size:%(sub)dpx;line-height:1.32;color:rgba(17,17,17,.78);max-width:%(submax)dpx;
     margin-top:%(submt)dpx}
.quote{font-size:%(quote)dpx;line-height:1.22;font-style:italic;
       color:rgba(17,17,17,.86);max-width:%(quotemax)dpx}
.cite{display:inline-block;align-self:flex-start;margin-top:%(citepmt)dpx;
      font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(cite)dpx;
      color:%(red)s;border:1.5px solid %(red)s;padding:%(citepady)dpx %(citepadx)dpx;
      letter-spacing:.02em}
.status{display:flex;align-items:center;gap:10px;margin-top:%(statusmt)dpx;
        font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(status)dpx;
        letter-spacing:.13em;text-transform:uppercase}
.dot{width:%(dot)dpx;height:%(dot)dpx;background:%(green)s;display:inline-block;flex:0 0 auto}
.status b{font-weight:400;color:%(green)s;letter-spacing:.13em}
.status span.tail{color:rgba(17,17,17,.58);letter-spacing:.1em}
.stats{display:flex;gap:%(statsgap)dpx;padding:0 0 %(statspb)dpx 0}
.stats .s{display:flex;flex-direction:column;gap:6px}
.stats b{font-weight:400;font-size:%(statsnum)dpx;line-height:1}
.stats span{font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(statslbl)dpx;
            letter-spacing:.16em;text-transform:uppercase;color:rgba(17,17,17,.55)}
.foot{border-top:1px solid rgba(17,17,17,.22);padding-top:%(footpt)dpx;
      display:flex;align-items:baseline;justify-content:space-between;
      font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(url)dpx;
      letter-spacing:.04em}
.foot .u{color:%(red)s}
.foot .r{color:rgba(17,17,17,.55);letter-spacing:.14em;text-transform:uppercase;font-size:%(urlr)dpx}
.wm{font-family:Consolas,ui-monospace,Menlo,monospace;font-size:%(wmlabel)dpx;
    letter-spacing:.2em;color:rgba(17,17,17,.62);text-transform:uppercase}
"""

SIZES = {
    "og": dict(w=1200, h=630, pad=56, padx=68, padb=48, ghost=190, eyebrow=12,
               headpb=13, midskip=0, h1max=940, h1xl=96, h1l=64, h1m=52,
               sub=21, submax=820, submt=20, quote=30, quotemax=1050,
               citepmt=22, cite=15, citepady=7, citepadx=13, statusmt=22,
               status=12, dot=9, footpt=14, url=17, urlr=11, wmlabel=12,
               statsgap=54, statspb=22, statsnum=30, statslbl=10),
    "post": dict(w=1600, h=900, pad=74, padx=92, padb=64, ghost=250, eyebrow=14,
                 headpb=15, midskip=0, h1max=1300, h1xl=128, h1l=88, h1m=72,
                 sub=25, submax=1080, submt=26, quote=38, quotemax=1180,
                 citepmt=30, cite=18, citepady=9, citepadx=17, statusmt=30,
                 status=13, dot=10, footpt=16, url=20, urlr=12, wmlabel=13,
                 statsgap=54, statspb=22, statsnum=30, statslbl=10),
}


def css(kind):
    d = dict(SIZES[kind], paper=PAPER, ink=INK, red=RED, green=GREEN)
    return CSS % d


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def page(kind, title, body):
    d = SIZES[kind]
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        "<title>%s — The 95x Record</title>\n<style>%s</style></head>\n"
        "<body>%s</body></html>\n" % (esc(title), css(kind), body)
    )


def words(s):
    return len([w for w in re.split(r"\s+", s.strip()) if w])


# ------------------------------------------------------------------ OG cards

OG = [
    dict(
        slug="index", title="index",
        eyebrow="THE 95× RECORD · " + CIVIL,
        h1="The 95× Record", h1cls="h-xl",
        sub="An open record of AOAO Marine Surf Waikiki v. Nikodem Pikor, "
            "Circuit Court of the First Circuit, Hawaii.",
        status=("Source verified", "1,121/1,121 SHA-256 · 0 mismatches"),
        cite=None, right="index · 01",
        stats=[("1,121", "documents"), ("491/495", "entries held"),
               ("491", "docket numbers"), ("0.94 GB", "published bytes")],
    ),
    dict(
        slug="hook", title="the 95x record",
        eyebrow="THE 95× RECORD · THE RATIO",
        h1="One elevator repair.<br>One judgment.", h1cls="h-l",
        sub="$2,260.15 repair → $214,890.23 total. A ratio of 95.08, built "
            "from the record’s own figures.",
        status=("Source verified", "every figure quoted with a docket and a page"),
        cite="[Dkt 453 pp. 2, 15]", right="hook · 02",
    ),
    dict(
        slug="numbers", title="the numbers",
        eyebrow="THE 95× RECORD · THE NUMBERS",
        h1="$214,890.23", h1cls="h-xl",
        sub="211,747.77 + 2,842.46 + 300.00. Quoted from the letter; "
            "the addition is the site\u2019s.",
        status=("Source verified", "Dkt 453 downloaded and SHA-256 matched"),
        cite="[Dkt 453 p.15]", right="numbers · 03",
    ),
    dict(
        slug="findings", title="findings 001",
        eyebrow="THE 95× RECORD · FINDINGS 001",
        h1="“the AOAO demands literally 100 times the value of their claim "
           "in fees”",
        h1cls="h-m", quote=True,
        sub="Filed by the defendant, 2024-08-01. 214,890.23 / 2,260.15 = 95.08.",
        status=("Source verified", "assertion quoted, labelled, not adopted"),
        cite="[Dkt 405 p.5]", right="findings · 04",
    ),
    dict(
        slug="coverage", title="coverage",
        eyebrow="THE 95× RECORD · COVERAGE",
        h1="491 of 495 entries held.", h1cls="h-l",
        sub="Four entries the site cannot show: Dkt 484, 486, 487 and 493.",
        status=("Source verified", "gaps published on purpose"),
        cite="[Dkt 486]", right="coverage · 05",
    ),
    dict(
        slug="pl", title="streszczenie po polsku",
        eyebrow="THE 95× RECORD · PO POLSKU",
        h1="1 121 dokumentów.<br>Każdy z SHA-256.", h1cls="h-l",
        sub="214 890,23 / 2 260,15 = 95,08×. Każdy cytat z numerem Dkt i stroną.",
        status=("Źródło zweryfikowane", "1 121 / 1 121 haszy · 0 niezgodności"),
        cite="[Dkt 453 p.15]", right="pl · 06",
    ),
]

# -------------------------------------------------------------------- posts

POSTS = [
    dict(
        n=1, slug="index",
        h1='$214,890.23 for a $2,260.15<br>elevator repair.', h1cls="h-l",
        support="1,121 documents online. Every SHA-256 matched before publication.",
        cite="[Dkt 453 pp. 2, 15]",
    ),
    dict(
        n=2, slug="coverage",
        h1='The record publishes<br>its own gaps: 491 of 495.', h1cls="h-l",
        support="Dkt 484, 486, 487 and 493 are declared, with what is held and what is not.",
        cite="[Dkt 486]",
    ),
    dict(
        n=3, slug="numbers",
        h1='$214,890.23<br>= 211,747.77 + 2,842.46 + 300.00', h1cls="h-m",
        support="Quoted from Dkt 453. The addition is the site\u2019s, not the document\u2019s.",
        cite="[Dkt 453 p.15]",
    ),
    dict(
        n=4, slug="hinge",
        h1='The court: he did not<br>intend the doors to decouple.', h1cls="h-l",
        support="COL 16, quoted with its page. No conclusion about the merits.",
        cite="[Dkt 396 p.16]",
    ),
    dict(
        n=5, slug="gate",
        h1='Two minute entries, one day:<br>the gate before the merits.', h1cls="h-l",
        support="A clerk\u2019s sheet of 20 Aug 2026, then two minute entries of 5 Oct 2026.",
        cite="[Dkt 486]",
    ),
    dict(
        n=6, slug="sources",
        h1='2,114 files measured.<br>1,121 documents hash-matched.<br>0 mismatches.', h1cls="h-m",
        support="42 folders, 6.29 GB, counted through the Drive API. Dkt 453 sha256 ebfa7e1e\u2026 matched.",
        cite="[Dkt 453]",
    ),
    dict(
        n=7, slug="maintenance",
        h1='Two statements about service<br>records. Both are printed.', h1cls="h-l",
        support="The filing says records were produced. A case-room note says none were released.",
        cite="[Dkt 291 p.27]",
    ),
    dict(
        n=8, slug="process",
        h1='The error is published.<br>So is the correction.', h1cls="h-l",
        support="A gap claim was wrong. The file that forced the correction is on the record.",
        cite="[Dkt 484]",
    ),
]


def card_html(kind, c, ghost=None, right=None):
    parts = []
    parts.append('<div class="spine"></div>')
    if ghost:
        parts.append('<div class="ghost">%s</div>' % ghost)
    parts.append('<div class="frame">')
    parts.append('<div class="head"><div class="eyebrow">%s</div></div>'
                 % esc(c["eyebrow"]))
    parts.append('<div class="mid">')
    h1cls = "quote" if c.get("quote") else c["h1cls"]
    parts.append('<h1 class="%s">%s</h1>' % (h1cls, c["h1"]))
    if c.get("sub"):
        parts.append('<p class="sub">%s</p>' % c["sub"])
    if kind == "post" and c.get("support"):
        parts.append('<p class="sub">%s</p>' % c["support"])
    if c.get("cite"):
        parts.append('<div class="cite">%s</div>' % esc(c["cite"]))
    if c.get("status"):
        head, tail = c["status"]
        parts.append(
            '<div class="status"><span class="dot"></span><b>%s</b>'
            '<span class="tail">\u00b7 %s</span></div>' % (esc(head), esc(tail))
        )
    parts.append("</div>")
    if c.get("stats"):
        parts.append('<div class="stats">')
        for num_, lbl in c["stats"]:
            parts.append('<div class="s"><b>%s</b><span>%s</span></div>'
                         % (esc(num_), esc(lbl)))
        parts.append("</div>")
    parts.append(
        '<div class="foot"><div class="u">%s</div><div class="r">%s</div></div>'
        % (URL, esc(right))
    )
    parts.append("</div>")
    return page(kind, c.get("title") or c.get("slug") or "card", "".join(parts))


def render(kind, html_path, png_path, w, h):
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--force-device-scale-factor=1",
        "--user-data-dir=" + PROFILE,
        "--window-size=%d,%d" % (w, h),
        "--screenshot=" + png_path,
        "file:///" + html_path.replace("\\", "/"),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-800:], r.stderr[-800:], file=sys.stderr)
        raise SystemExit("chrome failed for " + png_path)
    im = Image.open(png_path)
    if im.size != (w, h):
        raise SystemExit("%s is %s, expected %dx%d" % (png_path, im.size, w, h))
    return os.path.getsize(png_path)


def main():
    os.makedirs(OG_SRC, exist_ok=True)
    os.makedirs(POST_SRC, exist_ok=True)

    og_sizes = []
    for i, c in enumerate(OG, 1):
        c["eyebrow"] = c["eyebrow"]
        html = card_html("og", c, ghost=None, right=c["right"])
        hp = os.path.join(OG_SRC, "%s.html" % c["slug"])
        with open(hp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        pp = os.path.join(OG_DIR, "%s.png" % c["slug"])
        size = render("og", hp, pp, 1200, 630)
        og_sizes.append((c["slug"], size))
        print("og  %-9s 1200x630 %6d bytes" % (c["slug"], size))

    post_sizes = []
    for c in POSTS:
        nw = words(re.sub(r"<br>", " ", c["h1"]))
        if nw > 12:
            raise SystemExit("post %d headline has %d words (>12)" % (c["n"], nw))
        c = dict(c)
        c["eyebrow"] = "THE 95\u00d7 RECORD \u00b7 POST %d OF 8 \u00b7 %s" % (
            c["n"], c["slug"].upper())
        html = card_html("post", c, ghost="%02d" % c["n"],
                         right="%02d / 08 \u00b7 %s" % (c["n"], c["slug"]))
        hp = os.path.join(POST_SRC, "%02d.html" % c["n"])
        with open(hp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        pp = os.path.join(POST_DIR, "%02d.png" % c["n"])
        size = render("post", hp, pp, 1600, 900)
        post_sizes.append((c["n"], size, nw))
        print("post %02d 1600x900 %6d bytes  headline=%d words" % (c["n"], size, nw))

    print("\nog: %d files, %d bytes total" % (len(og_sizes), sum(s for _, s in og_sizes)))
    print("posts: %d files, %d bytes total" % (
        len(post_sizes), sum(s for _, s, _ in post_sizes)))


if __name__ == "__main__":
    main()
