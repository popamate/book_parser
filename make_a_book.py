#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ÉRTÉKŐRZŐK könyv HTML generátor Paged.js-hez

Fő tudás:
- Paged.js-es automatikus tördelés tükörmargókkal (@page :left / :right)
- Front matter (címoldal, impresszum, tartalomjegyzék, előszó) római számozással
- Főszöveg arab számozással, 1-től indul, jobb oldalon
- Cím + opcionális alcím (a cím utáni első nem tag sor)
- Bekezdések üres sorral, első bekezdés iniciáléval
- Szerző: csak a szerző UTOLSÓ novellájánál „Írta: …” és portrékép
- Szerzőkép-keresés ékezetlenítve, .jpg/.jpeg/.png/.webp/.gif/.tif/.tiff
- Chrome fallback: ha a Paged nem renderel (pl. file:// alatt), az eredeti tartalom látszik
"""

import os, re, sys, unicodedata
from pathlib import Path
from html import escape

# ------------ META ------------
BOOK_TITLE = "ÉRTÉKŐRZŐK"
BOOK_SUBTITLE = "Vásárosbéci történetek"
EDITOR = "Bánki Eszter"
BOOK_YEAR = "2025"

# ------------ FÁJLNEVEK ------------
TEXT_FILE = "text.txt"
OUT_FILE  = "book.html"

# Borítók (ha hiányoznak, placeholder jelenik meg)
COVER_OUTER        = "images/000_elso_borito.jpg"
COVER_INNER_FRONT  = "images/001_elso_borito_belso.jpg"
COVER_INNER_BACK   = "images/998_hatso_borito_belso.jpg"
COVER_BACK         = "images/999_hatso_borito.jpg"

IMG_DIR = "images"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"}  # <- .jpeg is!

# ------------ SEGÉDEK ------------
def norm(s: str) -> str:
    """Ékezet- és írásjel-független normalizálás névegyezéshez / slughoz."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def slugify(s: str) -> str:
    return norm(s).replace(" ", "-")

def find_author_image(author: str) -> str | None:
    """Fuzzy egyezés szerző→fájlnév: név tokenek ⊂ fájlnév tokenek → magas pont."""
    if not author or not os.path.isdir(IMG_DIR):
        return None
    target = set(norm(author).split())
    best, best_score = None, 0.0
    for fn in os.listdir(IMG_DIR):
        p = Path(IMG_DIR) / fn
        if not p.is_file() or p.suffix.lower() not in IMG_EXT:
            continue
        # fedlapokat hagyjuk
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
    return best if best_score >= 0.5 else None

# ------------ PARSER ------------
TAG_TITLE   = re.compile(r"^\[CÍM:\s*(.+?)\]$")
TAG_AUTHOR  = re.compile(r"^\[(SZERZŐ|SZERZŐ_TEMP):\s*(.+?)\]$")  # SZERZŐ_TEMP is szerző
TAG_PREFACE = re.compile(r"^\[ELŐSZÓ\]$")

class Section:
    def __init__(self, kind, title=None):
        self.kind = kind                 # 'preface' | 'story'
        self.title = title or ""
        self.subtitle = None
        self.author = None
        self.parts = []                  # list[('p', txt) | ('h3', txt)]
        self.anchor = None               # href id
        self.author_image = None
        self.show_author = False         # csak az UTOLSÓ novellánál True

    def add_paragraph(self, t): self.parts.append(("p", t))
    def add_subhead(self, t):   self.parts.append(("h3", t))

def parse_text(raw_text: str):
    """TXT feldolgozás. Kezeli a literális '\n' szekvenciákat is."""
    # Ha a fájlban escape-elt sortörések vannak, konvertáljuk
    if "\\n" in raw_text or "\\t" in raw_text:
        raw_text = raw_text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")

    lines = raw_text.splitlines()

    sections = []
    cur = None
    buf = []
    expecting_subtitle = False

    def flush_buf():
        nonlocal buf, cur
        if buf and cur:
            text = " ".join(x.strip() for x in buf).strip()
            if text:
                cur.add_paragraph(text)
        buf = []

    for line in lines:
        s = line.strip()

        if not s:
            flush_buf()
            continue

        if TAG_PREFACE.match(s):
            if cur:
                flush_buf()
                sections.append(cur)
            cur = Section("preface", "ELŐSZÓ")
            cur.anchor = "sec-eloszo"
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
            cur.anchor = "sec-" + slugify(title)
            expecting_subtitle = True
            buf = []
            continue

        m = TAG_AUTHOR.match(s)
        if m and cur:
            flush_buf()
            cur.author = m.group(2).strip()
            cur.author_image = find_author_image(cur.author)
            sections.append(cur)
            cur = None
            expecting_subtitle = False
            buf = []
            continue

        if cur is None:
            # magányos sor: átugorjuk
            continue

        # A cím utáni első nem tag sor: alcím
        if expecting_subtitle and cur.subtitle is None:
            cur.subtitle = s
            expecting_subtitle = False
            continue

        # (opcionális) belső alcím heur.: rövid, önálló sor, központozás nélkül
        if (len(s) <= 80 and "\t" not in s and s.count(".")==0 and s.count("?")==0 and s.count("!")==0):
            if not buf:  # új blokk elején
                cur.add_subhead(s)
                continue

        buf.append(s)

    if cur:
        flush_buf()
        sections.append(cur)

    return sections

def mark_last_by_author(sections):
    """Bejelöli, hogy melyik történet a szerző utolsó előfordulása."""
    last_idx = {}
    for i, sec in enumerate(sections):
        if sec.kind == "story" and sec.author:
            last_idx[sec.author] = i
    for i, sec in enumerate(sections):
        sec.show_author = (sec.kind == "story" and sec.author and last_idx.get(sec.author) == i)

# ------------ HTML ------------
def build_html(sections):
    css = r"""
/* Oldalbeállítások */
@page { size: 230mm 230mm; margin: 0; }
@page :left  { margin: 20mm 25mm 25mm 20mm; }  /* tükörmargó bal */
@page :right { margin: 20mm 20mm 25mm 25mm; }  /* tükörmargó jobb */

/* Lapstílusok (oldalszámok) */
@page cover { margin: 0; @bottom-center { content: none; } }
@page nonum { @bottom-center { content: none; } }
@page front { @bottom-center { content: counter(page, lower-roman); font: 10pt 'EB Garamond', serif; } }
@page main  { @bottom-center { content: counter(page);             font: 10pt 'EB Garamond', serif; } }

/* Alap */
html, body { background:#e7e7e7; margin:0; padding:0; color:#1a1a1a;
             font-family:'EB Garamond',serif; font-size:13.5pt; line-height:1.65; }

/* Képernyős lapnézet */
@media screen {
  .sheet { width:230mm; margin:10mm auto; background:#fff; box-shadow:0 5px 20px rgba(0,0,0,.15); border:1px solid #ddd; }
}

/* Borítók */
.cover { page: cover; break-before: page; }
.cover img { width:100%; height:230mm; object-fit:cover; display:block; }

/* Szám nélküli oldalak */
.nonum { page: nonum; break-before: page; }

/* Front matter (római) */
.front-matter { page: front; break-before: page; }

/* Főszöveg (arab, 1-től) */
.main-start { page: main; break-before: right; counter-reset: page 1; }
.story      { page: main; break-before: right; }

/* Címoldal / impresszum */
.title-page, .impressum { height:230mm; display:flex; align-items:center; justify-content:center; text-align:center; }
.title-page h1 { font-size:49pt; letter-spacing:.1em; text-transform:uppercase; font-weight:400; margin:0 0 .6em; }
.title-page .subtitle { font-size:18pt; font-style:italic; }

/* Tartalomjegyzék */
.toc h2, h2 { font-size:19pt; text-transform:uppercase; letter-spacing:.05em; font-weight:400; text-align:center; margin:0 0 1.2em; }
.toc .entry { display:flex; align-items:baseline; gap:.5em; margin:.35em 0; font-size:11.5pt; }
.toc .title { flex:1 1 auto; }
.toc .dots  { flex:0 0 auto; border-bottom:1px dotted #666; transform:translateY(-.2em); width:100%; }
.toc .page::after { content: target-counter(attr(data-href), page); }
.toc a { text-decoration:none; color:inherit; }

/* Szövegblokk */
.text p { text-align:justify; hyphens:auto; margin:0 0 .5em; text-indent:.5cm; orphans:3; widows:3; }
.text p.noindent { text-indent:0; }

/* Előszó: TÖRZS dőlt (cím és aláírás normál) */
.preface .text { font-style: italic; }
.preface h2, .preface .author { font-style: normal; }

/* Iniciálé az első bekezdésen (alcím után is működjön) */
.text p.par:first-of-type::first-letter,
.text p.subtitle-inline + p.par::first-letter {
  float:left; font-size:4.5em; line-height:.8; margin-right:.05em; margin-top:.05em; font-weight:700; color:#1a1a1a;
}

/* Alcímek */
.text h3 { text-align:center; font-style:italic; font-weight:400; margin:1.2em 0 .5em; }
.subtitle-inline { text-align:center; font-style:italic; margin:-.2em 0 1.2em; }

/* Szerző sor (csak utolsó történetnél) */
.author { text-align:right; font-style:italic; margin:1.5em 0 0; }

/* Szerző portré (csak utolsó történet után) */
figure.author-image { break-before: page; page: main; height:230mm;
  display:flex; align-items:center; justify-content:center; margin:0; }
figure.author-image img { max-width:100%; max-height:100%; object-fit:contain; display:block; }
figure.author-image figcaption { position:absolute; bottom:12mm; right:20mm; font-size:9pt; font-style:italic; opacity:.7; }

/* Fallback nézet a Paged.js-hez (file:// alatt se legyen üres) */
@media screen {
  .pagedjs_pages {
    display:flex; flex-direction:column; align-items:center; gap:10mm;
    background:#e7e7e7; padding:10mm 0;
  }
  .pagedjs_page { background:#fff; box-shadow:0 5px 20px rgba(0,0,0,.15); }
}
body.show-original .sheet { display:block; }
body.hide-original .sheet { display:none; }
"""

    head = f"""<!DOCTYPE html>
<html lang="hu"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{escape(BOOK_TITLE)} — {escape(BOOK_SUBTITLE)}</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>{css}</style>
<!-- Paged.js -->
<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
<!-- Fallback logika: ha a Paged nem rakja ki a lapokat, marad az eredeti nézet -->
<script>
document.addEventListener("DOMContentLoaded", function () {{
  document.body.classList.add("show-original");
  function swapIfReady(){{
    var pages = document.querySelector(".pagedjs_pages");
    if (pages) {{
      document.body.classList.remove("show-original");
      document.body.classList.add("hide-original");
    }}
  }}
  document.addEventListener("pagedjs:rendered", swapIfReady);
  setTimeout(swapIfReady, 4000);
}});
</script>
</head><body><div class="sheet">
"""

    html = [head]

    def cover(path, alt):
        if os.path.exists(path):
            return f'<section class="cover"><img src="{escape(path)}" alt="{escape(alt)}"></section>\n'
        return f'<section class="cover"><div style="height:230mm;display:flex;align-items:center;justify-content:center;color:#888;font-style:italic;">[{escape(alt)}]</div></section>\n'

    # Borítók
    html.append(cover(COVER_OUTER, "Első borító"))
    html.append(cover(COVER_INNER_FRONT, "Első borító belső"))

    # Címoldal + impresszum (szám nélkül)
    html.append(f"""
<section class="nonum title-page">
  <div>
    <h1>{escape(BOOK_TITLE)}</h1>
    <p class="subtitle">{escape(BOOK_SUBTITLE)}</p>
  </div>
</section>
<section class="nonum impressum">
  <div>
    <p>Szerkesztő: {escape(EDITOR)}</p>
    <p style="margin-top:1em;">{escape(BOOK_YEAR)}</p>
    <p style="margin-top:2em;font-size:10pt;">© Minden jog fenntartva</p>
  </div>
</section>
""")

    # Tartalomjegyzék (front matter, római)
    html.append('<section class="front-matter toc"><h2>TARTALOM</h2>\n')
    for sec in sections:
        if sec.kind != "story":
            continue
        href = f"#{sec.anchor}"
        title = escape(sec.title)
        html.append(f'''  <div class="entry">
    <span class="title"><a href="{href}">{title}</a></span>
    <span class="dots"></span>
    <span class="page" data-href="{href}"></span>
  </div>\n''')
    html.append("</section>\n")

    # Előszó (front matter, dőlt törzs)
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
        break  # csak egy előszót várunk

    # Főszöveg (arab számozás 1-től, jobb oldalon indul)
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
        # Szerzőt csak az utolsó történetnél írjuk ki
        if sec.show_author:
            html.append(f'<p class="author">Írta: {escape(sec.author)}</p>\n')
        html.append("</div>\n</section>\n")

        # Portrékép is csak az utolsó történet után
        if sec.show_author and sec.author_image:
            html.append(f'''
<figure class="author-image">
  <img src="{escape(sec.author_image)}" alt="{escape(sec.author)}">
  <figcaption>Szerző: {escape(sec.author)}</figcaption>
</figure>
''')

    # Hátsó borítók
    html.append(cover(COVER_INNER_BACK, "Hátsó borító belső"))
    html.append(cover(COVER_BACK, "Hátsó borító"))

    html.append("</div></body></html>")
    return "".join(html)

# ------------ FŐ ------------
def main():
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Munkamappa: {os.getcwd()}")

    if not os.path.exists(TEXT_FILE):
        print(f"❌ HIBA: {TEXT_FILE} nem található!")
        print(f"   Kerestem itt: {os.path.abspath(TEXT_FILE)}")
        sys.exit(1)

    raw = Path(TEXT_FILE).read_text(encoding="utf-8", errors="replace")
    sections = parse_text(raw)
    if not sections:
        print("❌ HIBA: Nem sikerült szekciókat találni. Ellenőrizd a TXT jelöléseit.")
        sys.exit(2)

    mark_last_by_author(sections)
    html = build_html(sections)
    Path(OUT_FILE).write_text(html, encoding="utf-8")

    print("\n" + "="*56)
    print(f"KÉSZ! {OUT_FILE} létrehozva")
    print("="*56)
    print("\nMegnyitás tipp:")
    print(" - Legstabilabb: python -m http.server 8000  ➜  http://localhost:8000/book.html")
    print(" - VAGY file:// megnyitás is ok, mert van fallback; nyomtatáshoz Chrome/Edge:")
    print("   Margó: None/Nincs • Méretezés: 100% • Háttérgrafika: BE")
    print(f"\nElérési út: {Path(OUT_FILE).resolve()}")

if __name__ == "__main__":
    main()
