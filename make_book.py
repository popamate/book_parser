#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, unicodedata
from pathlib import Path

def _slugify_image_name(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value)
    without_accents = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = re.sub(r'_+', '_', (
        without_accents.lower()
        .replace(' ', '_').replace('.', '').replace('-', '_')
    )).strip('_')
    return cleaned

def _strip_numeric_prefix(slug: str) -> str:
    return re.sub(r'^\d+_+', '', slug)

def _find_author_image(author: str) -> str | None:
    img_dir = Path('images')
    if not img_dir.exists():
        return None
    skip = {'000_elso_borito','001_elso_borito_belso','998_hatso_borito_belso','999_hatso_borito'}
    exts = {'.jpg','.jpeg','.png','.webp','.gif'}
    a = _slugify_image_name(author)
    cands = []
    for p in sorted(img_dir.iterdir()):
        if p.is_file() and p.suffix.lower() in exts and p.stem not in skip:
            s = _slugify_image_name(p.stem)
            cands.append((p.name, s, _strip_numeric_prefix(s)))
    for n,_,np in cands:
        if np == a: return n
    for n,s,np in cands:
        if a in s or a in np: return n
    at = [t for t in a.split('_') if t]
    for n,_,np in cands:
        if all(t in set(np.split('_')) for t in at if len(t)>1): return n
    return None

def create_book_html():
    os.chdir(Path(__file__).parent)
    if not Path('text.txt').exists():
        print("HIBA: text.txt nem található!"); return

    html = '''<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Értékőrzők — Vásárosbéci antológia</title>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html{background:#e0e0e0}
body{
  font-family:'EB Garamond',serif;font-size:13.5pt;line-height:1.65;color:#1a1a1a;
  background:#e0e0e0;padding:20px;
}
main{max-width:230mm;margin:0 auto;background:#fff}

@page{size:230mm 230mm;margin:20mm 20mm 28mm 20mm}
@page:left{margin:20mm 28mm 28mm 20mm}
@page:right{margin:20mm 20mm 28mm 28mm}
@page{ @bottom-center{content:counter(page);font-size:10pt;font-family:'EB Garamond',serif} }
@page cover{margin:0}
@page cover,@page front-matter{ @bottom-center{content:none} }

.page{position:relative;background:#fff}
.page.front-matter{page:front-matter}
.cover-page{page:cover}
.cover-page img{width:100%;height:100%;object-fit:cover;display:block}

.page-content{padding:0;hyphens:auto;-webkit-hyphens:auto;-moz-hyphens:auto}

h2{font-size:19pt;margin-bottom:1.5em;text-align:center;font-weight:400;text-transform:uppercase;letter-spacing:.05em}
.page-content h2:not(:first-child){margin-top:2em}

p{margin-bottom:.5em;text-indent:.5cm;text-align:left;orphans:3;widows:3}
h2 + p,.first-p{text-indent:0}

.drop-cap::first-letter{float:left;font-size:4.5em;line-height:.8;margin-right:.05em;margin-top:.05em;font-weight:700;color:#1a1a1a}

.preface-content{font-style:italic}
.preface-content h2{font-style:normal}

.author-sig{text-align:right;font-style:italic;margin-top:2em;text-indent:0}

.image-page .page-content{display:flex;justify-content:center;align-items:center}
.image-page img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.image-placeholder{color:#999;font-style:italic;text-align:center;font-size:14pt}

.toc-page h2{margin-bottom:1.2em;font-size:18pt}
.toc-entry{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:.4em;font-size:9pt;gap:.5em}
.toc-entry .toc-title{flex:1 1 auto}
.toc-entry .toc-page{min-width:18pt;text-align:right}
.toc-dots{flex:1;border-bottom:1px dotted #666}

.page-marker{position:absolute;width:0;height:0;overflow:hidden;}
.page-marker[data-numbering-start]{counter-reset: page 0;}

.title-page .page-content,.impressum-page .page-content{
  display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center
}
.title-page h1{font-size:49pt;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1em;font-weight:400}
.title-page .subtitle{font-size:18pt;font-style:italic}

.cover-page,
.title-page,
.impressum-page,
.toc-page,
.preface-page,
.story-page,
.image-page{break-after:page}

.preface-page,
.story-page,
.image-page{break-before:page}

@media screen{
  main{padding:0 15mm}
  .page{margin:0 auto 10mm;box-shadow:0 5px 20px rgba(0,0,0,.3)}
  .page-content{padding:20mm 20mm 28mm 20mm}
  .image-page .page-content{padding:20mm}
}

@media print{
  body{padding:0;background:#fff}
  main{padding:0;margin:0;box-shadow:none}
  .page{margin:0;background:#fff}
  .page-content{padding:0}
}
</style>
<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
<script>
class BookPaginationHandler extends Paged.Handler {
  afterRendered(pages) {
    const anchorPages = new Map();
    let numberingStarted = false;
    let logicalCounter = 0;

    pages.forEach(page => {
      const pageElement = page && (page.element || page);
      if (!pageElement || !pageElement.querySelector) {
        return;
      }

      const hasStartMarker = pageElement.querySelector('[data-numbering-start]') !== null;
      const excludeNumbering = pageElement.querySelector('[data-exclude-numbering]') !== null;

      if (hasStartMarker) {
        numberingStarted = true;
        logicalCounter = 1;
      } else if (numberingStarted && !excludeNumbering) {
        logicalCounter += 1;
      }

      const logicalNumber = numberingStarted && !excludeNumbering ? logicalCounter : null;

      if (logicalNumber !== null) {
        pageElement.setAttribute('data-logical-page', String(logicalNumber));
      } else {
        pageElement.removeAttribute('data-logical-page');
      }

      pageElement.querySelectorAll('[data-toc-anchor]').forEach(anchor => {
        if (anchor.id) {
          anchorPages.set(anchor.id, logicalNumber);
        }
      });
    });

    document.querySelectorAll('.toc-entry[data-target]').forEach(entry => {
      const targetId = entry.dataset.target;
      if (!targetId) {
        return;
      }
      const pageSpan = entry.querySelector('.toc-page');
      if (!pageSpan) {
        return;
      }
      const logical = anchorPages.get(targetId);
      pageSpan.textContent = logical != null ? logical : '';
    });
  }
}

Paged.registerHandlers(BookPaginationHandler);
</script>
</head>
<body>
<main class="page-container">
'''

    # Borító (külső)
    html += '''
<!-- ELSŐ BORÍTÓ -->
<div class="page cover-page front-matter" data-page-role="cover">
  <span class="page-marker" data-exclude-numbering></span>
'''
    html += ('  <img src="images/000_elso_borito.jpg" alt="Borító">\n'
             if Path('images/000_elso_borito.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Első borító]</div></div>\n')
    html += '</div>\n'

    # Borító belső
    html += '''
<!-- ELSŐ BORÍTÓ BELSŐ -->
<div class="page cover-page front-matter" data-page-role="inner-cover">
  <span class="page-marker" data-exclude-numbering></span>
'''
    html += ('  <img src="images/001_elso_borito_belso.jpg" alt="Belső borító">\n'
             if Path('images/001_elso_borito_belso.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Első borító belső oldala]</div></div>\n')
    html += '</div>\n'

    # Címoldal
    html += '''
<!-- CÍMOLDAL -->
<div class="page title-page front-matter" data-page-role="title">
  <span class="page-marker" data-exclude-numbering></span>
  <div class="page-content">
    <h1>ÉRTÉKŐRZŐK</h1>
    <p class="subtitle">Vásárosbéci történetek</p>
  </div>
  <span class="page-number"></span>
</div>
'''

    # Impresszum
    html += '''
<!-- IMPRESSZUM -->
<div class="page impressum-page front-matter" data-page-role="impressum">
  <span class="page-marker" data-exclude-numbering></span>
  <div class="page-content">
    <p>Írta: Mindenkori vásárosbéci lakosok</p>
    <p>A könyvet tervezte, szerkesztette: Bánki Eszter, 2025</p>

    <p style="margin-top:1.5em;">A könyv szabadon másolható, sokszorosítható</p>

    <p style="margin-top:2em;">Nyomás, kötés: Kontraszt Nyomda, Pécs</p>
    <p>ISBN 978-615-02-5049-6</p>
  </div>
  <span class="page-number"></span>
</div>
'''

    # TOC (később töltjük)
    toc_html = '''
<!-- TARTALOMJEGYZÉK -->
<div class="page toc-page front-matter" data-page-role="toc">
  <span class="page-marker" data-exclude-numbering></span>
  <div class="page-content">
    <h2>TARTALOM</h2>
'''

    # --- Szöveg feldolgozás ---
    content = Path('text.txt').read_text('utf-8').replace('\r\n','\n').replace('\r','\n')

    content_html = ''
    toc_entries = []
    section_opening = ''
    section_content = []
    current_section = None
    first_paragraph = False

    lines = content.split('\n')
    i = 0

    def make_heading_id(title: str, entry_index: int) -> str:
        base_slug = _slugify_image_name(title)
        heading_slug = re.sub(r'[^a-z0-9_]+', '', base_slug) or f'resz-{entry_index:03d}'
        return f'section-{entry_index:03d}-{heading_slug}'

    def open_section(section_type: str, opening_html: str):
        nonlocal current_section, section_opening, section_content, first_paragraph
        if current_section:
            close_section(current_section)
        current_section = section_type
        section_opening = opening_html
        section_content = []
        first_paragraph = True

    def close_section(section_type: str):
        nonlocal content_html, section_opening, section_content, current_section
        if not section_opening:
            current_section = None
            section_content = []
            return section_type
        content_html += section_opening
        for para in section_content:
            content_html += para
        content_html += '  </div>\n</div>\n'
        section_opening = ''
        section_content = []
        current_section = None
        return section_type

    def add_author_page(author: str):
        nonlocal content_html
        img = _find_author_image(author)
        if img:
            content_html += f'''
<!-- KÉP: {author} -->
<div class="page image-page" data-page-role="image">
  <div class="page-content">
    <img src="images/{img}" alt="{author}">
  </div>
</div>
'''
        else:
            content_html += f'''
<!-- KÉP PLACEHOLDER: {author} -->
<div class="page image-page" data-page-role="image">
  <div class="page-content"><div class="image-placeholder">[{author} képe]</div></div>
</div>
'''

    while i < len(lines):
        line = lines[i].strip()

        if line == '[ELŐSZÓ]':
            entry_index = len(toc_entries) + 1
            heading_id = make_heading_id('eloszo', entry_index)
            open_section('preface', f'''<!-- ELŐSZÓ -->
<div class="page preface-page" data-page-role="preface">
  <div class="page-content preface-content">
    <span class="page-marker" data-numbering-start></span>
    <h2 id="{heading_id}" data-toc-anchor>ELŐSZÓ</h2>
''')
            toc_entries.append({'title': 'ELŐSZÓ', 'target': heading_id})
            i += 1
            continue

        # CÍM — ugyanabban a blokkban folytatjuk, amíg nincs [SZERZŐ:]
        if line.startswith('[CÍM:'):
            title = line[5:-1].strip()
            entry_index = len(toc_entries) + 1
            heading_id = make_heading_id(title, entry_index)
            if current_section == 'story':
                section_content.append(f'    <h2 id="{heading_id}" data-toc-anchor>{title}</h2>\n')
                toc_entries.append({'title': title, 'target': heading_id})
                first_paragraph = True
                i += 1
                continue
            open_section('story', f'''<!-- NOVELLA BLOKK -->
<div class="page story-page" data-page-role="story">
  <div class="page-content">
    <h2 id="{heading_id}" data-toc-anchor>{title}</h2>
''')
            toc_entries.append({'title': title, 'target': heading_id})
            i += 1
            continue

        # SZERZŐ — itt zár a blokk, majd képes oldal
        if line.startswith('[SZERZŐ:') and not line.startswith('[SZERZŐ_TEMP:'):
            author = line[8:-1].strip()
            if current_section:
                section_content.append(f'    <p class="author-sig">Írta: {author}</p>\n')
                closed = close_section(current_section)
                if closed == 'story':
                    add_author_page(author)
            current_section = None
            i += 1
            continue

        if line.startswith('[SZERZŐ_TEMP:'):
            i += 1
            continue

        if not line:
            i += 1
            continue

        if current_section:
            # bekezdés összefűzés
            paras = [line]; j = i + 1
            while j < len(lines):
                nx = lines[j].strip()
                if not nx or nx.startswith('['): break
                paras.append(nx); j += 1
            txt = ' '.join(paras)
            if first_paragraph:
                section_content.append(f'    <p class="first-p drop-cap">{txt}</p>\n')
                first_paragraph = False
            else:
                section_content.append(f'    <p>{txt}</p>\n')
            i = j
        else:
            i += 1

    # zárás, ha maradt nyitva
    if current_section:
        close_section(current_section)

    # TOC lezárás
    for e in toc_entries:
        toc_html += f'''      <div class="toc-entry" data-target="{e['target']}"><span class="toc-title">{e['title']}</span><span class="toc-dots"></span><span class="toc-page">–</span></div>
'''
    toc_html += '  </div>\n</div>\n'

    html += toc_html
    html += content_html

    # Hátsó borító belső
    html += '''
<!-- HÁTSÓ BORÍTÓ BELSŐ -->
<div class="page cover-page front-matter" data-page-role="back-inner">
  <span class="page-marker" data-exclude-numbering></span>
'''
    html += ('  <img src="images/998_hatso_borito_belso.jpg" alt="Hátsó borító belső">\n'
             if Path('images/998_hatso_borito_belso.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Hátsó borító belső oldala]</div></div>\n')
    html += '</div>\n'

    # Hátsó borító
    html += '''
<!-- HÁTSÓ BORÍTÓ -->
<div class="page cover-page front-matter" data-page-role="back-cover">
  <span class="page-marker" data-exclude-numbering></span>
'''
    html += ('  <img src="images/999_hatso_borito.jpg" alt="Hátsó borító">\n'
             if Path('images/999_hatso_borito.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Hátsó borító]</div></div>\n')
    html += '</div>\n'

    html += '</main>\n</body>\n</html>'

    Path('book.html').write_text(html, encoding='utf-8')
    print("KESZ: book.html - nyomtatásnál állítsd: Margók=Nincs, Méretezés=100%, Háttérgrafika=on.")

if __name__ == "__main__":
    try:
        create_book_html()
    except Exception as e:
        print("HIBA:", e)
        import traceback; traceback.print_exc()
