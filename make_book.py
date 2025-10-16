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
html,body{background:#fff;color:#1a1a1a}
body{
  font-family:'EB Garamond',serif;font-size:13.5pt;line-height:1.65;
  margin:0;
}
main{
  max-width:230mm;margin:0 auto;background:#fff;
}
main{max-width:230mm;margin:0 auto;background:#fff}

@page{size:230mm 230mm;margin:20mm 20mm 28mm 20mm}
@page:left{margin:20mm 28mm 28mm 20mm}
@page:right{margin:20mm 20mm 28mm 28mm}
@page{ @bottom-center{content:counter(page);font-size:10pt;font-family:'EB Garamond',serif} }
@page cover{margin:0; @bottom-center{content:none}}
@page front-matter{ @bottom-center{content:none} }

section{hyphens:auto;-webkit-hyphens:auto;-moz-hyphens:auto;break-inside:auto}
section:not(.cover-section):not(.image-section){padding:0 20mm 28mm 20mm}
section.front-matter{page:front-matter;break-before:page}
section.body-section{break-before:page}
section.numbering-start{counter-reset:page 0}

.cover-section{
  page:cover;break-after:page;display:flex;align-items:center;justify-content:center;
  min-height:100%;block-size:100%;padding:0;background:#fff;
}
.cover-section img{width:100%;height:100%;object-fit:cover;display:block}

.title-page,.impressum-page{display:flex;flex-direction:column;justify-content:center;text-align:center}
.title-page{align-items:center}
.toc-section{display:block;text-align:left}
.title-page h1{font-size:49pt;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1em;font-weight:400}
.title-page .subtitle{font-size:18pt;font-style:italic}

.impressum-page p{margin-bottom:.5em}

.toc-section h2{font-size:18pt;margin-bottom:1.2em;text-align:center;letter-spacing:.05em}
.toc-list{list-style:none;margin:0;padding:0}
.toc-entry{display:flex;align-items:flex-end;gap:.5em;font-size:9pt;margin-bottom:.35em}
.toc-title{flex:1 1 auto}
.toc-title a{color:inherit;text-decoration:none}
.toc-title a:hover{text-decoration:underline}
.toc-dots{flex:1 1 50px;border-bottom:1px dotted #666}
.toc-page{min-width:18pt;text-align:right}
.toc-page::after{content:target-counter(attr(data-target url), page)}

h2{font-size:19pt;margin-bottom:1.5em;text-align:center;font-weight:400;text-transform:uppercase;letter-spacing:.05em}
section.body-section h2:not(:first-child){margin-top:2em}

p{margin-bottom:.5em;text-indent:.5cm;text-align:justify;orphans:3;widows:3}
h2 + p,.first-p{text-indent:0}

.drop-cap::first-letter{float:left;font-size:4.5em;line-height:.8;margin-right:.05em;margin-top:.05em;font-weight:700;color:#1a1a1a}

.preface-section{font-style:italic}
.preface-section h2{font-style:normal}

.author-sig{text-align:right;font-style:italic;margin-top:2em;text-indent:0}

.image-section{page:image;break-before:page;break-after:page;display:flex;align-items:center;justify-content:center;padding:0 20mm;background:#fff}
.image-section img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.image-placeholder{color:#999;font-style:italic;text-align:center;font-size:14pt}

@media screen{
  body{background:#fff}
  main{padding:0}
}

@media print{
  body{background:#fff}
  main{margin:0}
}
</style>
<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
</head>
<body>
<main class="book">
'''

    # Borító (külső)
    html += '''
<!-- ELSŐ BORÍTÓ -->
<section class="cover-section cover-front">
'''
    html += ('  <img src="images/000_elso_borito.jpg" alt="Borító">\n'
             if Path('images/000_elso_borito.jpg').exists()
             else '  <div class="image-placeholder">[Első borító]</div>\n')
    html += '</section>\n'

    # Borító belső
    html += '''
<!-- ELSŐ BORÍTÓ BELSŐ -->
<section class="cover-section cover-inner">
'''
    html += ('  <img src="images/001_elso_borito_belso.jpg" alt="Belső borító">\n'
             if Path('images/001_elso_borito_belso.jpg').exists()
             else '  <div class="image-placeholder">[Első borító belső oldala]</div>\n')
    html += '</section>\n'

    # Címoldal
    html += '''
<!-- CÍMOLDAL -->
<section class="title-page front-matter">
  <h1>ÉRTÉKŐRZŐK</h1>
  <p class="subtitle">Vásárosbéci történetek</p>
</section>
'''

    # Impresszum
    html += '''
<!-- IMPRESSZUM -->
<section class="impressum-page front-matter">
  <p>Írta: Mindenkori vásárosbéci lakosok</p>
  <p>A könyvet tervezte, szerkesztette: Bánki Eszter, 2025</p>

  <p style="margin-top:1.5em;">A könyv szabadon másolható, sokszorosítható</p>

  <p style="margin-top:2em;">Nyomás, kötés: Kontraszt Nyomda, Pécs</p>
  <p>ISBN 978-615-02-5049-6</p>
</section>
'''

    # TOC (később töltjük)
    toc_html = '''
<!-- TARTALOMJEGYZÉK -->
<section class="toc-section front-matter">
  <h2>TARTALOM</h2>
  <ol class="toc-list">
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
        content_html += '</section>\n'
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
<section class="image-section">
  <img src="images/{img}" alt="{author}">
</section>
'''
        else:
            content_html += f'''
<!-- KÉP PLACEHOLDER: {author} -->
<section class="image-section">
  <div class="image-placeholder">[{author} képe]</div>
</section>
'''

    while i < len(lines):
        line = lines[i].strip()

        if line == '[ELŐSZÓ]':
            entry_index = len(toc_entries) + 1
            heading_id = make_heading_id('eloszo', entry_index)
            open_section('preface', f'''<!-- ELŐSZÓ -->
<section class="preface-section body-section numbering-start">
  <h2 id="{heading_id}">ELŐSZÓ</h2>
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
                section_content.append(f'  <h2 id="{heading_id}">{title}</h2>\n')
                toc_entries.append({'title': title, 'target': heading_id})
                first_paragraph = True
                i += 1
                continue
            open_section('story', f'''<!-- NOVELLA BLOKK -->
<section class="story-section body-section">
  <h2 id="{heading_id}">{title}</h2>
''')
            toc_entries.append({'title': title, 'target': heading_id})
            i += 1
            continue

        # SZERZŐ — itt zár a blokk, majd képes oldal
        if line.startswith('[SZERZŐ:') and not line.startswith('[SZERZŐ_TEMP:'):
            author = line[8:-1].strip()
            if current_section:
                section_content.append(f'  <p class="author-sig">Írta: {author}</p>\n')
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
                section_content.append(f'  <p class="first-p drop-cap">{txt}</p>\n')
                first_paragraph = False
            else:
                section_content.append(f'  <p>{txt}</p>\n')
            i = j
        else:
            i += 1

    # zárás, ha maradt nyitva
    if current_section:
        close_section(current_section)

    # TOC lezárás
    for e in toc_entries:
        target = e['target']
        title = e['title']
        toc_html += f'''    <li class="toc-entry"><span class="toc-title"><a href="#{target}">{title}</a></span><span class="toc-dots"></span><span class="toc-page" data-target="#{target}"></span></li>
'''
    toc_html += '  </ol>\n</section>\n'

    html += toc_html
    html += content_html

    # Hátsó borító belső
    html += '''
<!-- HÁTSÓ BORÍTÓ BELSŐ -->
<section class="cover-section cover-back-inner">
'''
    html += ('  <img src="images/998_hatso_borito_belso.jpg" alt="Hátsó borító belső">\n'
             if Path('images/998_hatso_borito_belso.jpg').exists()
             else '  <div class="image-placeholder">[Hátsó borító belső oldala]</div>\n')
    html += '</section>\n'

    # Hátsó borító
    html += '''
<!-- HÁTSÓ BORÍTÓ -->
<section class="cover-section cover-back">
'''
    html += ('  <img src="images/999_hatso_borito.jpg" alt="Hátsó borító">\n'
             if Path('images/999_hatso_borito.jpg').exists()
             else '  <div class="image-placeholder">[Hátsó borító]</div>\n')
    html += '</section>\n'

    html += '</main>\n</body>\n</html>'

    Path('book.html').write_text(html, encoding='utf-8')
    print("KESZ: book.html - nyomtatásnál állítsd: Margók=Nincs, Méretezés=100%, Háttérgrafika=on.")

if __name__ == "__main__":
    try:
        create_book_html()
    except Exception as e:
        print("HIBA:", e)
        import traceback; traceback.print_exc()
