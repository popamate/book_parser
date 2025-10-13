#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
ÉRTÉKŐRZŐK könyv HTML generátor Paged.js-hez
JAVÍTOTT v2 - target-counter hiba megoldva
"""

import argparse
import logging
import os, re, sys, unicodedata
from pathlib import Path
from html import escape

# ------------ LOGGING ------------
logger = logging.getLogger("book_builder")


def setup_logging(verbosity: int) -> None:
    """Általános naplózás beállítása."""

    if verbosity is None:
        level = logging.INFO
    elif verbosity < 0:
        level = logging.WARNING
    elif verbosity == 0:
        level = logging.INFO
    else:
        level = logging.DEBUG

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)

# ------------ META ------------
BOOK_TITLE = "ÉRTÉKŐRZŐK"
BOOK_SUBTITLE = "Vásárosbéci történetek"
EDITOR = "Bánki Eszter"
BOOK_YEAR = "2025"

# ------------ FÁJLNEVEK ------------
TEXT_FILE = "text.txt"
OUT_FILE  = "book.html"

# Borítók
COVER_OUTER        = "images/000_elso_borito.jpg"
COVER_INNER_FRONT  = "images/001_elso_borito_belso.jpg"
COVER_INNER_BACK   = "images/998_hatso_borito_belso.jpg"
COVER_BACK         = "images/999_hatso_borito.jpg"

IMG_DIR = "images"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}

# ------------ SEGÉDEK ------------
def norm(s: str) -> str:
    """Ékezet- és írásjel-független normalizálás."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def slugify(s: str) -> str:
    return norm(s).replace(" ", "-")

def find_author_image(author: str) -> str | None:
    """Fuzzy egyezés szerző→fájlnév."""
    if not author or not os.path.isdir(IMG_DIR):
        return None
    target = set(norm(author).split())
    logger.debug("Portré keresés: %s → %s", author, ", ".join(sorted(target)))
    best, best_score = None, 0.0
    for fn in os.listdir(IMG_DIR):
        p = Path(IMG_DIR) / fn
        if not p.is_file() or p.suffix.lower() not in IMG_EXT:
            continue
        if p.name.startswith(("000_", "001_", "998_", "999_")):
            continue
        tokens = set(norm(p.stem).split())
        if not tokens:
            continue
        inter = len(target & tokens)
        union = len(target | tokens) or 1
        score = inter / union
        if target.issubset(tokens):
            score = max(score, 0.95)
        if score > best_score:
            best_score, best = score, str(p).replace("\\", "/")
            logger.debug("  ↳ jelölt: %s (%.2f)", best, best_score)
    if best and best_score >= 0.5:
        logger.info("  ✓ Portré társítva: %s", best)
        return best
    if best:
        logger.warning("  ⚠ Gyenge portré-találat: %s (%.2f)", best, best_score)
    return None

# ------------ PARSER ------------
TAG_TITLE   = re.compile(r"^\[CÍM:\s*(.+?)\]$")
TAG_AUTHOR  = re.compile(r"^\[(SZERZŐ|SZERZŐ_TEMP):\s*(.+?)\]$")
TAG_PREFACE = re.compile(r"^\[ELŐSZÓ\]$")

class Section:
    def __init__(self, kind, title=None):
        self.kind = kind
        self.title = title or ""
        self.subtitle = None
        self.author = None
        self.parts = []
        self.anchor = None
        self.author_image = None
        self.show_author = False

    def add_paragraph(self, t): self.parts.append(("p", t))
    def add_subhead(self, t):   self.parts.append(("h3", t))

def parse_text(raw_text: str):
    if "\\n" in raw_text or "\\t" in raw_text:
        raw_text = raw_text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")

    lines = raw_text.splitlines()
    sections = []
    cur = None
    buf = []
    expecting_subtitle = False
    used_anchors: set[str] = set()

    def unique_anchor(base: str) -> str:
        anchor = base or "sec"
        if anchor in used_anchors:
            i = 2
            while f"{anchor}-{i}" in used_anchors:
                i += 1
            anchor = f"{anchor}-{i}"
        used_anchors.add(anchor)
        return anchor

    def flush_buf():
        nonlocal buf, cur
        if buf and cur:
            text = " ".join(x.strip() for x in buf).strip()
            if text:
                cur.add_paragraph(text)
        buf = []

    for idx, line in enumerate(lines, 1):
        s = line.strip()

        if not s:
            flush_buf()
            continue

        if TAG_PREFACE.match(s):
            if cur:
                flush_buf()
                sections.append(cur)
            cur = Section("preface", "ELŐSZÓ")
            cur.anchor = unique_anchor("sec-eloszo")
            logger.info("[%03d] Előszó blokk indítása (anchor=%s)", idx, cur.anchor)
            expecting_subtitle = False
            buf = []
            continue

        m = TAG_TITLE.match(s)
        if m:
            if cur:
                flush_buf()
                sections.append(cur)
                cur = None
            title = m.group(1).strip()
            cur = Section("story", title)
            slug = slugify(title) or "resz"
            cur.anchor = unique_anchor("sec-" + slug)
            logger.info("[%03d] Új történet: %s (anchor=%s)", idx, title, cur.anchor)
            expecting_subtitle = True
            buf = []
            continue

        m = TAG_AUTHOR.match(s)
        if m and cur:
            flush_buf()
            cur.author = m.group(2).strip()
            cur.author_image = find_author_image(cur.author)
            sections.append(cur)
            logger.info("[%03d] Szerző lezárás: %s", idx, cur.author)
            cur = None
            expecting_subtitle = False
            buf = []
            continue

        if cur is None:
            logger.debug("[%03d] Árválkodó sor kihagyva: %s", idx, s)
            continue

        if expecting_subtitle and cur.subtitle is None:
            cur.subtitle = s
            logger.info("[%03d]  ↳ alcím: %s", idx, s)
            expecting_subtitle = False
            continue

        if (len(s) <= 80 and "\t" not in s and s.count(".")==0 and s.count("?")==0 and s.count("!")==0):
            if not buf:
                cur.add_subhead(s)
                logger.debug("[%03d]  ↳ köztes alcím: %s", idx, s)
                continue

        buf.append(s)

    if cur:
        flush_buf()
        sections.append(cur)
        logger.warning("Utolsó szakasz automatikusan lezárva: %s", cur.title or "(névtelen)")

    return sections

def mark_last_by_author(sections):
    last_idx = {}
    for i, sec in enumerate(sections):
        if sec.kind == "story" and sec.author:
            last_idx[sec.author] = i
    for i, sec in enumerate(sections):
        sec.show_author = (sec.kind == "story" and sec.author and last_idx.get(sec.author) == i)
        if sec.kind == "story" and not sec.author:
            logger.warning("Hiányzó szerző: %s", sec.title)


def summarize_sections(sections):
    logger.info("Összesen %d szakasz feldolgozva.", len(sections))
    for sec in sections:
        parts = sum(1 for kind, _ in sec.parts if kind == "p")
        heads = sum(1 for kind, _ in sec.parts if kind == "h3")
        logger.info(
            "  • %-8s | cím=%s | anchor=%s | bekezdés=%d | alcím=%d",
            sec.kind,
            sec.title or "(n/a)",
            sec.anchor or "(n/a)",
            parts,
            heads,
        )
        if sec.subtitle:
            logger.debug("     ↳ alcím: %s", sec.subtitle)
        if sec.author:
            logger.debug("     ↳ szerző: %s", sec.author)
        if sec.author_image:
            logger.debug("     ↳ portré: %s", sec.author_image)

# ------------ HTML ------------
def build_html(sections):
    # CSS - JAVÍTVA: target-counter működik
    css = r"""
/* Oldalbeállítások */
@page {
  size: 230mm 230mm;
  margin: 0;
}

@page :left {
  margin: 20mm 25mm 25mm 20mm;
}

@page :right {
  margin: 20mm 20mm 25mm 25mm;
}

@page cover {
  margin: 0;
  @bottom-center { content: none; }
}

@page nonum {
  @bottom-center { content: none; }
}

@page front {
  @bottom-center {
    content: counter(page, lower-roman);
    font: 10pt 'EB Garamond', serif;
  }
}

@page main {
  @bottom-center {
    content: counter(page);
    font: 10pt 'EB Garamond', serif;
  }
}

/* Alap */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  color: #1a1a1a;
  font-family: 'EB Garamond', serif;
  font-size: 13.5pt;
  line-height: 1.65;
}

/* Borítók */
.cover {
  page: cover;
  break-before: page;
  text-align: center;
}

.cover img {
  width: 100%;
  height: 230mm;
  object-fit: cover;
  display: block;
}

.cover-placeholder {
  height: 230mm;
  text-align: center;
  padding-top: 110mm;
  color: #888;
  font-style: italic;
  font-size: 14pt;
}

/* Szám nélküli oldalak */
.nonum {
  page: nonum;
  break-before: page;
}

/* Front matter */
.front-matter {
  page: front;
  break-before: page;
}

/* Főszöveg */
.main-start {
  page: main;
  break-before: right;
  counter-reset: page 1;
}

.story {
  page: main;
  break-before: right;
}

/* Címoldal */
.title-page {
  height: 230mm;
  text-align: center;
}

.title-page-inner {
  display: table;
  width: 100%;
  height: 100%;
}

.title-page-cell {
  display: table-cell;
  vertical-align: middle;
  padding: 20mm;
}

.title-page h1 {
  font-size: 49pt;
  letter-spacing: .1em;
  text-transform: uppercase;
  font-weight: 400;
  margin: 0 0 .6em;
  line-height: 1.2;
}

.title-page .subtitle {
  font-size: 18pt;
  font-style: italic;
}

/* Impresszum */
.impressum {
  height: 230mm;
  text-align: center;
}

.impressum-inner {
  display: table;
  width: 100%;
  height: 100%;
}

.impressum-cell {
  display: table-cell;
  vertical-align: middle;
  padding: 20mm;
}

.impressum p {
  margin: .5em 0;
}

/* Tartalomjegyzék */
.toc {
  padding: 0;
}

.toc h2, h2 {
  font-size: 19pt;
  text-transform: uppercase;
  letter-spacing: .05em;
  font-weight: 400;
  text-align: center;
  margin: 0 0 1.5em;
  padding-top: 10mm;
}

/* TOC bejegyzések - JAVÍTVA */
.toc-entries {
  padding: 0 20mm;
}

.toc .entry {
  display: table;
  width: 100%;
  margin: .35em 0;
  font-size: 11.5pt;
  border-collapse: collapse;
}

.toc .title {
  display: table-cell;
  padding-right: .5em;
}

.toc .dots {
  display: table-cell;
  width: 100%;
  border-bottom: 1px dotted #666;
  height: 1em;
}

.toc .page-num {
  display: table-cell;
  padding-left: .5em;
  text-align: right;
  white-space: nowrap;
}

/* JAVÍTÁS: target-counter megfelelő használata */
.toc .page-ref::after {
  content: target-counter(attr(href), page);
}

.toc a {
  text-decoration: none;
  color: inherit;
}

/* Szövegblokk */
.text {
  padding: 0;
}

.text p {
  text-align: justify;
  hyphens: auto;
  margin: 0 0 .5em;
  text-indent: .5cm;
  orphans: 3;
  widows: 3;
}

.text p.noindent {
  text-indent: 0;
}

/* Előszó */
.preface .text {
  font-style: italic;
}

.preface h2,
.preface .author {
  font-style: normal;
}

/* Iniciálé */
.text p.par:first-of-type::first-letter,
.text p.subtitle-inline + p.par::first-letter {
  float: left;
  font-size: 4.5em;
  line-height: .8;
  margin-right: .05em;
  margin-top: .05em;
  font-weight: 700;
  color: #1a1a1a;
}

/* Alcímek */
.text h3 {
  text-align: center;
  font-style: italic;
  font-weight: 400;
  margin: 1.2em 0 .5em;
}

.subtitle-inline {
  text-align: center;
  font-style: italic;
  margin: -.2em 0 1.2em;
}

/* Szerző sor */
.author {
  text-align: right;
  font-style: italic;
  margin: 1.5em 0 0;
}

/* Szerző portré */
.author-image {
  page: main;
  break-before: page;
  height: 230mm;
  text-align: center;
  padding: 20mm;
}

.author-image-wrapper {
  display: table;
  width: 100%;
  height: 100%;
}

.author-image-cell {
  display: table-cell;
  vertical-align: middle;
}

.author-image img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  display: inline-block;
}

.author-image figcaption {
  margin-top: 1em;
  font-size: 9pt;
  font-style: italic;
  opacity: .7;
}
"""

    head = f"""<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{escape(BOOK_TITLE)} — {escape(BOOK_SUBTITLE)}</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
<style>{css}</style>
</head>
<body>
"""

    html = [head]

    def cover(path, alt):
        if os.path.exists(path):
            return f'<section class="cover"><img src="{escape(path)}" alt="{escape(alt)}"></section>\n'
        return f'<section class="cover"><div class="cover-placeholder">[{escape(alt)}]</div></section>\n'

    # Borítók
    html.append(cover(COVER_OUTER, "Első borító"))
    html.append(cover(COVER_INNER_FRONT, "Első borító belső"))

    # Címoldal
    html.append(f"""
<section class="nonum title-page">
  <div class="title-page-inner">
    <div class="title-page-cell">
      <h1>{escape(BOOK_TITLE)}</h1>
      <p class="subtitle">{escape(BOOK_SUBTITLE)}</p>
    </div>
  </div>
</section>
""")

    # Impresszum
    html.append(f"""
<section class="nonum impressum">
  <div class="impressum-inner">
    <div class="impressum-cell">
      <p>Szerkesztő: {escape(EDITOR)}</p>
      <p style="margin-top:1em;">{escape(BOOK_YEAR)}</p>
      <p style="margin-top:2em;font-size:10pt;">© Minden jog fenntartva</p>
    </div>
  </div>
</section>
""")

    # Tartalomjegyzék - JAVÍTVA
    html.append('<section class="front-matter toc">\n<h2>TARTALOM</h2>\n<div class="toc-entries">\n')
    for sec in sections:
        if sec.kind != "story":
            continue
        title = escape(sec.title)
        # JAVÍTÁS: a href direkt módon hivatkozik az id-ra
        html.append(f'''  <div class="entry">
    <span class="title">{title}</span>
    <span class="dots"></span>
    <span class="page-num"><a href="#{sec.anchor}" class="page-ref"></a></span>
  </div>\n''')
    html.append("</div>\n</section>\n")

    # Előszó
    for sec in sections:
        if sec.kind != "preface":
            continue
        html.append(f'<section class="front-matter preface" id="{sec.anchor}">\n<h2>ELŐSZÓ</h2>\n<div class="text">\n')
        first = True
        for kind, text in sec.parts:
            if kind == "h3":
                html.append(f"<h3>{escape(text)}</h3>\n")
            else:
                cls = "par noindent" if first else "par"
                html.append(f'<p class="{cls}">{escape(text)}</p>\n')
                first = False
        if sec.author:
            html.append(f'<p class="author">Írta: {escape(sec.author)}</p>\n')
        html.append("</div>\n</section>\n")
        break

    # Főszöveg
    main_started = False
    for sec in sections:
        if sec.kind != "story":
            continue
        cls = "story main-start" if not main_started else "story"
        main_started = True
        html.append(f'<section class="{cls}" id="{sec.anchor}">\n')
        html.append(f"<h2>{escape(sec.title)}</h2>\n")
        if sec.subtitle:
            html.append(f'<div class="text"><p class="subtitle-inline">{escape(sec.subtitle)}</p>\n')
        else:
            html.append('<div class="text">\n')
        first = True
        for kind, text in sec.parts:
            if kind == "h3":
                html.append(f"<h3>{escape(text)}</h3>\n")
            else:
                cls_p = "par noindent" if first and not sec.subtitle else "par"
                html.append(f'<p class="{cls_p}">{escape(text)}</p>\n')
                first = False
        if sec.show_author:
            html.append(f'<p class="author">Írta: {escape(sec.author)}</p>\n')
        html.append("</div>\n</section>\n")

        # Portrékép
        if sec.show_author and sec.author_image:
            html.append(f'''
<figure class="author-image">
  <div class="author-image-wrapper">
    <div class="author-image-cell">
      <img src="{escape(sec.author_image)}" alt="{escape(sec.author)}">
      <figcaption>Szerző: {escape(sec.author)}</figcaption>
    </div>
  </div>
</figure>
''')

    # Hátsó borítók
    html.append(cover(COVER_INNER_BACK, "Hátsó borító belső"))
    html.append(cover(COVER_BACK, "Hátsó borító"))

    # JavaScript - hibakezelés hozzáadva
    html.append("""
<script>
console.log('[Könyv] Paged.js betöltve, renderelés indul...');

// Hibakezelő
window.addEventListener('error', function(e) {
  console.error('[Hiba]', e.message, e);
  if (e.message && e.message.includes("doesn't belong to list")) {
    console.warn('[Figyelmeztetés] TOC hivatkozási hiba - a célelem nem található.');
  }
});

class BookHandlers extends Paged.Handler {
  constructor(chunker, polisher, caller) {
    super(chunker, polisher, caller);
  }
  
  beforeParsed(content) {
    console.log('[Paged.js] Tartalom elemzése...');
    
    // Ellenőrizzük a TOC hivatkozásokat
    const tocLinks = content.querySelectorAll('.toc a[href^="#"]');
    tocLinks.forEach(link => {
      const targetId = link.getAttribute('href').substring(1);
      const target = content.getElementById(targetId);
      if (!target) {
        console.warn(`[Figyelmeztetés] Nem található elem: #${targetId}`);
      }
    });
  }
  
  afterParsed(parsed) {
    console.log('[Paged.js] Oldalak generálása...');
  }
  
  afterRendered(pages) {
    console.log('[Paged.js] ✓ Sikeres! Oldalak száma:', pages.length);
    
    // Manuális oldalszám frissítés, ha szükséges
    document.querySelectorAll('.toc .page-ref').forEach(link => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        const target = document.querySelector(href);
        if (target) {
          // A Paged.js automatikusan kezeli ezt, de itt ellenőrizhetjük
          console.log(`[TOC] ${href} → oldal renderelve`);
        }
      }
    });
  }
}

Paged.registerHandlers(BookHandlers);
</script>

</body>
</html>""")

    return "".join(html)

# ------------ FŐ ------------
def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="ÉRTÉKŐRZŐK könyv HTML generátor")
    parser.add_argument(
        "-d",
        "--debug",
        action="count",
        default=0,
        help="Részletesebb naplózás (többször adva még részletesebb)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Csak a figyelmeztetések jelenjenek meg",
    )

    args = parser.parse_args(argv)

    verbosity = args.debug
    if args.quiet:
        verbosity = -1

    setup_logging(verbosity)

    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    logger.info("📁 Munkamappa: %s", os.getcwd())

    if not os.path.exists(TEXT_FILE):
        logger.error("❌ HIBA: %s nem található!", TEXT_FILE)
        sys.exit(1)

    raw = Path(TEXT_FILE).read_text(encoding="utf-8", errors="replace")
    logger.info("Bemeneti sorok száma: %d", raw.count("\n") + 1)

    sections = parse_text(raw)
    if not sections:
        logger.error("❌ HIBA: Nem sikerült szekciókat találni.")
        sys.exit(2)

    mark_last_by_author(sections)
    summarize_sections(sections)
    anchors = [sec.anchor for sec in sections if sec.anchor]
    if len(set(anchors)) != len(anchors):
        logger.warning("⚠ Ismétlődő anchor azonosítók találhatók!")

    html = build_html(sections)
    Path(OUT_FILE).write_text(html, encoding="utf-8")

    logger.info("\n" + "=" * 60)
    logger.info("✓ JAVÍTOTT v2 kész! %s", OUT_FILE)
    logger.info("=" * 60)
    logger.info("\n🔧 JAVÍTÁSOK v2:")
    logger.info("  • target-counter hiba javítva")
    logger.info("  • TOC hivatkozások átstrukturálva")
    logger.info("  • Hibakezelés hozzáadva a JavaScript-hez")
    logger.info("  • Ellenőrzés, hogy minden cél elem létezik")
    logger.info("\n🚀 INDÍTÁS:")
    logger.info("  python -m http.server 8000")
    logger.info("  http://localhost:8000/book.html")
    logger.info("\n🐛 DEBUG:")
    logger.info("  Nyisd meg az F12 konzolt a részletes hibaüzenetekért!")
    logger.info("\n📝 Ha továbbra is hiba van:")
    logger.info("  1. Ellenőrizd, hogy a text.txt megfelelő formátumú")
    logger.info("  2. Nézd meg a konzolban, mely elemek hiányoznak")
    logger.info("  3. Győződj meg róla, hogy minden [CÍM:...] után van [SZERZŐ:...]")

if __name__ == "__main__":
    main()
