#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unicodedata
from pathlib import Path

def create_book_html():
    """Könyv HTML generálása formázott szövegből - JAVÍTOTT VERZIÓ"""
    
    # AUTOMATIKUSAN MEGTALÁLJA A FÁJLOKAT
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"📁 Munkamappa: {os.getcwd()}")
    
    # Ellenőrizzük hogy megvannak-e a fájlok
    if not os.path.exists('text.txt'):
        print("❌ HIBA: text.txt nem található!")
        print(f"   Kerestem itt: {os.path.abspath('text.txt')}")
        return
    
    print("✅ text.txt megtalálva")
    
    # HTML fejléc (frissítve a flow-hoz)
    html = '''<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Értékőrzők — Vásárosbéci antológia</title>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        /* RESET */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* OLDAL BEÁLLÍTÁSOK NYOMTATÁSHOZ */
        @page {
            size: 230mm 230mm;
            margin: 22mm 22mm 25mm 22mm;
        }

        @page :left {
            margin-left: 22mm;
            margin-right: 28mm;
        }

        @page :right {
            margin-left: 28mm;
            margin-right: 22mm;
        }
        
        @page cover {
            margin: 0;
        }
        
        @page front {
            @bottom-center { content: none; }
        }
        
        @page toc {
            @bottom-center { content: counter(page, lower-roman); }
        }
        
        /* ALAP STÍLUSOK */
        body {
            font-family: 'EB Garamond', serif;
            font-size: 13.5pt;
            line-height: 1.65;
            color: #1a1a1a;
            background: #e0e0e0;
            margin: 0;
            padding: 40px 0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }

        /* OLDAL KONTÉNER */
        .page-container {
            width: 230mm;
            margin: 0 auto;
            background: white;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.25);
        }
        
        /* ÁLTALÁNOS TARTALOM */
        .content {
            text-align: justify;
            hyphens: auto;
            -webkit-hyphens: auto;
            -moz-hyphens: auto;
            orphans: 3;
            widows: 3;
        }

        .main-content {
            counter-reset: page 1;
        }
        
        /* BORÍTÓ OLDALAK */
        .cover-page {
            page-break-after: always;
        }
        
        .cover-page img {
            width: 230mm;
            height: 230mm;
            object-fit: cover;
            display: block;
        }
        
        /* BELSŐ BORÍTÓ ÉS KÉPEK */
        .inner-cover {
            page-break-before: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 22mm 28mm 25mm 28mm;
        }

        .inner-cover img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
        }

        .image-page {
            page-break-before: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 22mm 22mm 25mm 22mm;
            gap: 10mm;
        }

        .image-wrapper {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .image-wrapper img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
        }

        .image-placeholder {
            color: #999;
            font-style: italic;
            font-size: 14pt;
        }
        
        /* CÍMOLDAL */
        .title-page {
            page-break-before: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        
        .title-page h1 {
            font-size: 49pt;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1em;
            font-weight: normal;
        }
        
        .title-page .subtitle {
            font-size: 18pt;
            font-style: italic;
        }
        
        /* IMPRESSZUM */
        .impressum-page {
            page-break-before: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        
        /* TARTALOMJEGYZÉK */
        .toc-page {
            page-break-before: always;
            counter-reset: page 1;
        }
        
        .toc-page h2 {
            font-size: 18pt;
            margin-bottom: 1.2em;
            text-align: center;
            text-transform: uppercase;
        }
        
        .toc-entry {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.4em;
            font-size: 9pt;
        }

        .toc-entry a {
            flex: 1 1 auto;
            text-decoration: none;
            color: inherit;
        }
        
        .toc-dots {
            flex: 1;
            border-bottom: 1px dotted #666;
            margin: 0 0.5em;
            position: relative;
            top: -0.3em;
        }
        
        .toc-entry .page-num {
            min-width: 2.5em;
            text-align: right;
        }

        .toc-entry .page-num::before {
            content: target-counter(attr(data-target), page);
        }
        
        /* NOVELLA CÍMEK */
        h2 {
            font-size: 19pt;
            margin-bottom: 1.5em;
            text-align: center;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            page-break-before: avoid;
            margin-top: 3em;
        }

        h2:first-of-type {
            margin-top: 0;
        }
        
        /* BEKEZDÉSEK */
        p {
            margin-bottom: 0.5em;
            text-indent: 0.5cm;
            text-align: justify;
        }
        
        /* Első bekezdés és cím utáni */
        h2 + p,
        .first-p {
            text-indent: 0;
        }
        
        /* INICIÁLÉ - DROP CAP */
        .drop-cap::first-letter {
            float: left;
            font-size: 4.5em;
            line-height: 0.8;
            margin-right: 0.05em;
            margin-top: 0.05em;
            font-weight: 700;
            color: #1a1a1a;
        }
        
        /* ELŐSZÓ */
        .preface-content {
            font-style: italic;
        }
        
        .preface-content h2 {
            font-style: normal;
        }
        
        /* SZERZŐ ALÁÍRÁSA */
        .author-sig {
            text-align: right;
            font-style: italic;
            margin-top: 2em;
            text-indent: 0;
            page-break-after: always;
        }
        
        /* OLDALSZÁMOK */
        @page {
            @bottom-center {
                content: counter(page);
                font-size: 10pt;
                font-family: 'EB Garamond', serif;
            }
        }
        
        /* NYOMTATÁSI BEÁLLÍTÁSOK */
        @media print {
            body {
                background: white;
                padding: 0;
                display: block;
            }

            .page-container {
                margin: 0;
                box-shadow: none;
            }
        }
    </style>
    
    <!-- PAGED.JS -->
    <script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
</head>
<body>
    <div class="page-container">
        <div class="content">
'''
    
    # BORÍTÓ (KÜLSŐ)
    html += '''
            <!-- ELSŐ BORÍTÓ -->
            <section class="cover-page" page="cover">
'''
    if os.path.exists('images/000_elso_borito.jpg'):
        html += '                <img src="images/000_elso_borito.jpg" alt="Borító">\n'
    else:
        html += '                <div class="image-placeholder">[Első borító]</div>\n'
    html += '            </section>\n'
    
    # BORÍTÓ BELSŐ
    html += '''
            <!-- ELSŐ BORÍTÓ BELSŐ -->
            <section class="inner-cover" page="front">
'''
    if os.path.exists('images/001_elso_borito_belso.jpg'):
        html += '                <img src="images/001_elso_borito_belso.jpg" alt="Belső borító">\n'
    else:
        html += '                <div class="image-placeholder">[Első borító belső oldala]</div>\n'
    html += '            </section>\n'
    
    # CÍMOLDAL
    html += '''
            <!-- CÍMOLDAL -->
            <section class="title-page" page="front">
                <h1>ÉRTÉKŐRZŐK</h1>
                <p class="subtitle">Vásárosbéci történetek</p>
            </section>
'''
    
    # IMPRESSZUM
    html += '''
            <!-- IMPRESSZUM -->
            <section class="impressum-page" page="front">
                <p>Szerkesztő: Bánki Eszter</p>
                <p style="margin-top: 1em;">2025</p>
                <p style="margin-top: 2em; font-size: 10pt;">© Minden jog fenntartva</p>
            </section>
'''
    
    # TARTALOMJEGYZÉK (később töltjük ki)
    toc_html = '''
            <!-- TARTALOMJEGYZÉK -->
            <section class="toc-page" page="toc">
                <h2>TARTALOMJEGYZÉK</h2>
'''
    
    # SZÖVEG FELDOLGOZÁSA - FLOW LOGIKA
    print("\nSzöveg feldolgozása...")
    
    with open('text.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    content_html = ''
    toc_entries = []
    
    current_section = None
    current_title = None
    first_paragraph = False
    pending_author = None
    lines = content.split('\n')
    i = 0
    
    def slugify(value: str) -> str:
        normalized = unicodedata.normalize('NFKD', value)
        without_accents = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
        cleaned = without_accents.lower().replace(' ', '_').replace('.', '').replace('-', '_')
        return cleaned

    def add_author_page(author):
        nonlocal content_html

        print(f"    Szerző: {author}")

        author_lower = slugify(author)
        image_found = False
        images_dir = Path('images')

        if images_dir.exists():
            skip_stems = {
                '000_elso_borito',
                '001_elso_borito_belso',
                '998_hatso_borito_belso',
                '999_hatso_borito',
            }

            for img_path in sorted(images_dir.iterdir()):
                if not img_path.is_file():
                    continue

                stem = img_path.stem
                if stem in skip_stems:
                    continue

                img_slug = slugify(stem)
                if author_lower in img_slug:
                    content_html += f'''
                    <!-- KÉP: {author} -->
                    <section class="image-page" data-author="{author_lower}">
                        <div class="image-wrapper">
                            <img src="images/{img_path.name}" alt="{author}">
                        </div>
                    </section>
'''
                    image_found = True
                    print(f"    - Kép találva: {img_path.name}")
                    break

        if not image_found:
            content_html += f'''
                    <!-- KÉP PLACEHOLDER: {author} -->
                    <section class="image-page" data-author="{author_lower}">
                        <div class="image-wrapper">
                            <div class="image-placeholder">[{author} képe]</div>
                        </div>
                    </section>
'''
            print(f"    ! Kép nem található: {author_lower}")
    
    while i < len(lines):
        line = lines[i].strip()
        
        # ELŐSZÓ kezdete
        if line == '[ELŐSZÓ]':
            print("  - Előszó kezdete")
            current_section = 'preface'
            title_slug = slugify('Előszó')
            content_html += f'<div class="preface-content">\n'
            content_html += f'    <h2 id="{title_slug}">ELŐSZÓ</h2>\n'
            toc_entries.append({'title': 'Előszó', 'slug': title_slug})
            first_paragraph = True
            i += 1
            continue
        
        # NOVELLA címe
        if line.startswith('[CÍM:'):
            new_title = line[5:-1].strip()
            title_slug = slugify(new_title)
            
            # Ha volt előző szekció, zárjuk le
            if current_section:
                if pending_author:
                    content_html += f'    <p class="author-sig">Írta: {pending_author}</p>\n'
                    if current_section == 'story':
                        add_author_page(pending_author)
                    pending_author = None
                if current_section == 'preface':
                    content_html += '</div>\n'
                current_section = None
            
            current_title = new_title
            print(f"  - Novella: {current_title}")
            current_section = 'story'
            content_html += f'    <h2 id="{title_slug}">{current_title}</h2>\n'
            first_paragraph = True
            toc_entries.append({'title': current_title, 'slug': title_slug})
            i += 1
            continue
        
        # SZERZŐ
        if line.startswith('[SZERZŐ:') and not line.startswith('[SZERZŐ_TEMP:'):
            pending_author = line[8:-1].strip()
            i += 1
            continue
        
        # TEMP SZERZŐ (átugorjuk)
        if line.startswith('[SZERZŐ_TEMP:'):
            i += 1
            continue
        
        # Üres sor - bekezdés vége
        if not line:
            i += 1
            continue
        
        # BEKEZDÉS
        if current_section:
            paragraph_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith('['):
                    break
                paragraph_lines.append(next_line)
                j += 1
            
            paragraph = ' '.join(paragraph_lines)
            
            if first_paragraph:
                content_html += f'    <p class="first-p drop-cap">{paragraph}</p>\n'
                first_paragraph = False
            else:
                content_html += f'    <p>{paragraph}</p>\n'
            
            i = j
        else:
            i += 1
    
    # Utolsó szekció lezárása
    if current_section:
        if pending_author:
            content_html += f'    <p class="author-sig">Írta: {pending_author}</p>\n'
            if current_section == 'story':
                add_author_page(pending_author)
            pending_author = None
        if current_section == 'preface':
            content_html += '</div>\n'
        current_section = None
    
    # TARTALOMJEGYZÉK befejezése
    for entry in toc_entries:
        toc_html += f'''                <div class="toc-entry">
                    <a href="#{entry['slug']}" class="toc-link">{entry['title']}</a>
                    <span class="toc-dots"></span>
                    <span class="page-num" data-target="#{entry['slug']}"></span>
                </div>
'''
    
    toc_html += '            </section>\n'
    
    # ÖSSZERAKJUK (TOC majd content)
    html += toc_html
    html += '            <main class="main-content">\n'
    html += content_html
    html += '            </main>\n'
    
    # HÁTSÓ BORÍTÓK
    html += '''
            <!-- HÁTSÓ BORÍTÓ BELSŐ -->
            <section class="inner-cover" page="front">
'''
    if os.path.exists('images/998_hatso_borito_belso.jpg'):
        html += '                <img src="images/998_hatso_borito_belso.jpg" alt="Hátsó borító belső">\n'
    else:
        html += '                <div class="image-placeholder">[Hátsó borító belső oldala]</div>\n'
    html += '            </section>\n'
    
    html += '''
            <!-- HÁTSÓ BORÍTÓ -->
            <section class="cover-page" page="cover">
'''
    if os.path.exists('images/999_hatso_borito.jpg'):
        html += '                <img src="images/999_hatso_borito.jpg" alt="Hátsó borító">\n'
    else:
        html += '                <div class="image-placeholder">[Hátsó borító]</div>\n'
    html += '            </section>\n'
    
    # HTML vége
    html += '''        </div>
    </div>
</body>
</html>'''
    
    # MENTÉS
    with open('book.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n" + "="*50)
    print("✅ KÉSZ! book.html létrehozva")
    print("="*50)
    print(f"\nFeldolgozott elemek:")
    print(f"  - Novellák száma: {len(toc_entries)}")
    print("\nKövetkező lépések:")
    print("1. Nyisd meg a book.html fájlt böngészőben (Paged.js betöltődik, oldalakra bontja)")
    print("2. Nézd meg hogy minden rendben van-e")
    print("3. Ctrl+P -> Print to PDF")
    print("4. Beállítások:")
    print("   - Margók: None/Nincs")
    print("   - Méretezés: 100%")
    print("   - Háttérgrafika: bekapcsolva")
    print(f"\nA HTML fájl itt található:")
    print(f"   {os.path.abspath('book.html')}")

if __name__ == "__main__":
    try:
        create_book_html()
    except Exception as e:
        print(f"\n❌ HIBA történt: {e}")
        import traceback
        traceback.print_exc()
