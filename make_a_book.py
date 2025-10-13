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
    
    # HTML fejléc (ugyanaz mint az eredeti)
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
            margin: 0;
        }
        
        @page :left {
            margin: 20mm 25mm 25mm 20mm;
        }
        
        @page :right {
            margin: 20mm 20mm 25mm 25mm;
        }
        
        /* ALAP STÍLUSOK */
        body {
            font-family: 'EB Garamond', serif;
            font-size: 13.5pt;
            line-height: 1.65;
            color: #1a1a1a;
            background: #e0e0e0;
            margin: 0;
            padding: 20px;
        }
        
        /* OLDAL KONTÉNER */
        .page-container {
            width: 230mm;
            margin: 0 auto;
            background: white;
        }
        
        /* MINDEN OLDAL */
        .page {
            width: 230mm;
            height: 230mm;
            background: white;
            position: relative;
            margin: 0 auto 10mm;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            page-break-after: always;
        }
        
        /* TARTALOM TERÜLETEK */
        .page-content {
            position: absolute;
            inset: 0;
            padding: 20mm 20mm 25mm 20mm;
            text-align: left;
            hyphens: auto;
            -webkit-hyphens: auto;
            -moz-hyphens: auto;
        }

        /* BAL OLDAL (páros) */
        .page:nth-child(even) .page-content {
            padding-right: 25mm;
        }

        /* JOBB OLDAL (páratlan) */
        .page:nth-child(odd) .page-content {
            padding-left: 25mm;
        }
        
        /* BORÍTÓ OLDALAK */
        .cover-page {
            padding: 0 !important;
        }
        
        .cover-page img {
            width: 230mm;
            height: 230mm;
            object-fit: cover;
            display: block;
        }
        
        /* CÍMOLDAL */
        .title-page .page-content {
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
        .impressum-page .page-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        
        /* NOVELLA CÍMEK - NAGYBETŰS */
        h2 {
            font-size: 19pt;
            margin-bottom: 1.5em;
            text-align: center;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .page-content h2:not(:first-child) {
            margin-top: 2em;
        }
        
        /* BEKEZDÉSEK */
        p {
            margin-bottom: 0.5em;
            text-indent: 0.5cm;
            text-align: left;
            orphans: 3;
            widows: 3;
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
        }
        
        /* KÉPOLDAL */
        .image-page .page-content {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20mm;
        }
        
        .image-page img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .image-placeholder {
            color: #999;
            font-style: italic;
            text-align: center;
            font-size: 14pt;
        }
        
        /* TARTALOMJEGYZÉK */
        .toc-page h2 {
            margin-bottom: 1.2em;
            font-size: 18pt;
        }
        
        .toc-entry {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.4em;
            font-size: 9pt;
        }
        
        .toc-dots {
            flex: 1;
            border-bottom: 1px dotted #666;
            margin: 0 0.5em;
            position: relative;
            top: -0.3em;
        }

        /* OLDALSZÁMOK */
        .page-number {
            position: absolute;
            bottom: 12mm;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10pt;
            font-family: 'EB Garamond', serif;
        }

        /* NYOMTATÁSI BEÁLLÍTÁSOK */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
            
            .page-container {
                margin: 0;
            }
        }
        
        /* KÉPERNYŐN VALÓ MEGJELENÍTÉS */
        @media screen {
            .page {
                border: 1px solid #ddd;
            }
            
            /* Margó jelzések */
            .page::before {
                content: "";
                position: absolute;
                border: 1px dashed #ccc;
                pointer-events: none;
            }
            
            .page:nth-child(even)::before {
                top: 20mm;
                left: 20mm;
                right: 25mm;
                bottom: 25mm;
            }
            
            .page:nth-child(odd)::before {
                top: 20mm;
                left: 25mm;
                right: 20mm;
                bottom: 25mm;
            }
        }
    </style>
    
    <!-- PAGED.JS -->
    <script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
</head>
<body>
    <div class="page-container">
'''
    
    # BORÍTÓ (KÜLSŐ)
    html += '''
        <!-- ELSŐ BORÍTÓ -->
        <div class="page cover-page">
'''
    if os.path.exists('images/000_elso_borito.jpg'):
        html += '            <img src="images/000_elso_borito.jpg" alt="Borító">\n'
    else:
        html += '''            <div class="page-content">
                <div class="image-placeholder">[Első borító]</div>
            </div>\n'''
    html += '        </div>\n'
    
    # BORÍTÓ BELSŐ
    html += '''
        <!-- ELSŐ BORÍTÓ BELSŐ -->
        <div class="page cover-page">
'''
    if os.path.exists('images/001_elso_borito_belso.jpg'):
        html += '            <img src="images/001_elso_borito_belso.jpg" alt="Belső borító">\n'
    else:
        html += '''            <div class="page-content">
                <div class="image-placeholder">[Első borító belső oldala]</div>
            </div>\n'''
    html += '        </div>\n'
    
    # CÍMOLDAL
    html += '''
        <!-- CÍMOLDAL -->
        <div class="page title-page">
            <div class="page-content">
                <h1>ÉRTÉKŐRZŐK</h1>
                <p class="subtitle">Vásárosbéci történetek</p>
            </div>
        </div>
'''
    
    # IMPRESSZUM
    html += '''
        <!-- IMPRESSZUM -->
        <div class="page impressum-page">
            <div class="page-content">
                <p>Szerkesztő: Bánki Eszter</p>
                <p style="margin-top: 1em;">2025</p>
                <p style="margin-top: 2em; font-size: 10pt;">© Minden jog fenntartva</p>
            </div>
        </div>
'''
    
    # TARTALOMJEGYZÉK (később töltjük ki)
    toc_html = '''
        <!-- TARTALOMJEGYZÉK -->
        <div class="page toc-page">
            <div class="page-content">
                <h2>TARTALOM</h2>
'''
    
    # SZÖVEG FELDOLGOZÁSA - JAVÍTOTT LOGIKA
    print("\nSzöveg feldolgozása...")
    
    with open('text.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Felosztjuk a szöveget blokkokra (elválasztó: dupla sortörés VAGY [TAG])
    # De először normalizáljuk a sortöréseket
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    content_html = ''
    toc_entries = []
    page_num = 1
    
    # Állapot változók
    current_section = None  # 'preface', 'story', None
    current_title = None
    first_paragraph = False
    section_content = []
    pending_author = None
    
    lines = content.split('\n')
    i = 0
    
    def close_section(section_type):
        """Bezár egy szekciót (előszó vagy novella)"""
        nonlocal content_html, page_num, section_content

        if section_content:
            # Kiírjuk az összegyűjtött bekezdéseket
            for para in section_content:
                content_html += para
            section_content = []

        content_html += f'            </div>\n            <span class="page-number">{page_num}</span>\n        </div>\n'
        page_num += 1
        return section_type
    
    def add_author_page(author):
        """Szerző oldal és kép hozzáadása"""
        nonlocal content_html, page_num
        
        print(f"    Szerző: {author}")
        
        # KÉP OLDAL
        def slugify(value: str) -> str:
            normalized = unicodedata.normalize('NFKD', value)
            without_accents = ''.join(
                ch for ch in normalized if not unicodedata.combining(ch)
            )
            cleaned = (
                without_accents.lower()
                .replace(' ', '_')
                .replace('.', '')
                .replace('-', '_')
            )
            return cleaned

        author_lower = slugify(author)
        image_found = False

        if os.path.exists('images'):
            skip_stems = {
                '000_elso_borito',
                '001_elso_borito_belso',
                '998_hatso_borito_belso',
                '999_hatso_borito',
            }

            for img in sorted(os.listdir('images')):
                stem = Path(img).stem
                if stem in skip_stems:
                    continue

                img_slug = slugify(stem)
                if author_lower in img_slug:
                    content_html += f'''
        <!-- KÉP: {author} -->
        <div class="page image-page">
            <div class="page-content">
                <img src="images/{img}" alt="{author}">
            </div>
            <span class="page-number">{page_num}</span>
        </div>
'''
                    image_found = True
                    page_num += 1
                    print(f"    - Kép találva: {img}")
                    break
        
        if not image_found:
            content_html += f'''
        <!-- KÉP PLACEHOLDER: {author} -->
        <div class="page image-page">
            <div class="page-content">
                <div class="image-placeholder">[{author} képe]</div>
            </div>
            <span class="page-number">{page_num}</span>
        </div>
'''
            page_num += 1
            print(f"    ! Kép nem található: {author_lower}")
    
    while i < len(lines):
        line = lines[i].strip()
        
        # ELŐSZÓ kezdete
        if line == '[ELŐSZÓ]':
            print("  - Előszó kezdete")
            current_section = 'preface'
            content_html += f'''
        <!-- ELŐSZÓ -->
        <div class="page">
            <div class="page-content preface-content">
                <h2>ELŐSZÓ</h2>
'''
            first_paragraph = True
            section_content = []
            i += 1
            continue
        
        # NOVELLA címe
        if line.startswith('[CÍM:'):
            new_title = line[5:-1].strip()

            # Ha ugyanaz a szerző (nincs új [SZERZŐ]) akkor folytathatjuk ugyanazon az oldalon
            if current_section == 'story' and pending_author is None:
                print(f"  - Novella (folytatás): {new_title}")
                section_content.append(f'                <h2>{new_title}</h2>\n')
                toc_entries.append({'title': new_title, 'page': page_num})
                first_paragraph = True
                current_title = new_title
                i += 1
                continue

            # Ha volt előző szekció, zárjuk le
            if current_section:
                # Ha volt pending author, adjuk hozzá most
                if pending_author:
                    # Szerző aláírás az előző szekcióhoz
                    section_content.append(f'                <p class="author-sig">Írta: {pending_author}</p>\n')
                    closed_type = close_section(current_section)
                    if closed_type == 'story':
                        add_author_page(pending_author)
                    pending_author = None
                else:
                    close_section(current_section)
                current_section = None

            current_title = new_title
            print(f"  - Novella: {current_title}")
            
            current_section = 'story'
            content_html += f'''
        <!-- NOVELLA: {current_title.upper()} -->
        <div class="page">
            <div class="page-content">
                <h2>{current_title}</h2>
'''
            first_paragraph = True
            section_content = []
            toc_entries.append({'title': current_title, 'page': page_num})
            i += 1
            continue
        
        # SZERZŐ
        if line.startswith('[SZERZŐ:') and not line.startswith('[SZERZŐ_TEMP:'):
            author = line[8:-1].strip()
            pending_author = author
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
            # Ellenőrizzük, hogy több sor tartozik-e ugyanahhoz a bekezdéshez
            # (azaz nincs dupla sortörés vagy új tag)
            paragraph_lines = [line]
            j = i + 1
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Ha üres sor vagy új tag, vége a bekezdésnek
                if not next_line or next_line.startswith('['):
                    break
                
                paragraph_lines.append(next_line)
                j += 1
            
            # Összerakjuk a bekezdést
            paragraph = ' '.join(paragraph_lines)
            
            if first_paragraph:
                section_content.append(f'                <p class="first-p drop-cap">{paragraph}</p>\n')
                first_paragraph = False
            else:
                section_content.append(f'                <p>{paragraph}</p>\n')
            
            i = j
        else:
            i += 1
    
    # Utolsó szekció lezárása
    if current_section:
        if pending_author:
            section_content.append(f'                <p class="author-sig">Írta: {pending_author}</p>\n')
            closed_type = close_section(current_section)
            if closed_type == 'story':
                add_author_page(pending_author)
        else:
            close_section(current_section)
        current_section = None
    
    # TARTALOMJEGYZÉK befejezése
    for entry in toc_entries:
        toc_html += f'''                <div class="toc-entry">
                    <span>{entry['title']}</span>
                    <span class="toc-dots"></span>
                    <span>{entry['page']}</span>
                </div>
'''
    
    toc_html += '''            </div>
            <span class="page-number">I</span>
        </div>
'''
    
    # ÖSSZERAKJUK
    html += toc_html
    html += content_html
    
    # HÁTSÓ BORÍTÓK
    html += '''
        <!-- HÁTSÓ BORÍTÓ BELSŐ -->
        <div class="page cover-page">
'''
    if os.path.exists('images/998_hatso_borito_belso.jpg'):
        html += '            <img src="images/998_hatso_borito_belso.jpg" alt="Hátsó borító belső">\n'
    else:
        html += '''            <div class="page-content">
                <div class="image-placeholder">[Hátsó borító belső oldala]</div>
            </div>\n'''
    html += '        </div>\n'
    
    html += '''
        <!-- HÁTSÓ BORÍTÓ -->
        <div class="page cover-page">
'''
    if os.path.exists('images/999_hatso_borito.jpg'):
        html += '            <img src="images/999_hatso_borito.jpg" alt="Hátsó borító">\n'
    else:
        html += '''            <div class="page-content">
                <div class="image-placeholder">[Hátsó borító]</div>
            </div>\n'''
    html += '        </div>\n'
    
    # HTML vége
    html += '''    </div>
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
    print(f"  - Oldalak száma: ~{page_num}")
    print("\nKövetkező lépések:")
    print("1. Nyisd meg a book.html fájlt böngészőben")
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
