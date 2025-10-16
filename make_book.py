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

/* Könyvoldal méret */
@page{size:230mm 230mm;margin:0}
@page :left {margin:20mm 25mm 25mm 20mm}
@page :right{margin:20mm 20mm 25mm 25mm}

body{
  font-family:'EB Garamond',serif;font-size:13.5pt;line-height:1.65;color:#1a1a1a;
  background:#e0e0e0;margin:0;padding:20px;
}

.page-container{width:230mm;margin:0 auto;background:#fff}

.page{
  width:230mm;height:230mm;background:#fff;position:relative;
  margin:0 auto 10mm;box-shadow:0 5px 20px rgba(0,0,0,.3);
  page-break-after:always;display:flex;flex-direction:column;
}

.page-content{
  position:relative;flex:1;padding:20mm 20mm 25mm 20mm;text-align:left;
  hyphens:auto;-webkit-hyphens:auto;-moz-hyphens:auto;
}

/* bal/jobb margók */
.page:nth-child(even) .page-content{padding-right:25mm}
.page:nth-child(odd)  .page-content{padding-left:25mm}

/* borítók */
.cover-page{padding:0!important}
.cover-page img{width:230mm;height:230mm;object-fit:cover;display:block}

/* címoldal */
.title-page .page-content{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.title-page h1{font-size:49pt;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1em;font-weight:400}
.title-page .subtitle{font-size:18pt;font-style:italic}

/* impresszum */
.impressum-page .page-content{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}

/* címek */
h2{font-size:19pt;margin-bottom:1.5em;text-align:center;font-weight:400;text-transform:uppercase;letter-spacing:.05em}
.page-content h2:not(:first-child){margin-top:2em}

/* bekezdések */
p{margin-bottom:.5em;text-indent:.5cm;text-align:left;orphans:3;widows:3}
h2 + p,.first-p{text-indent:0}

/* iniciálé */
.drop-cap::first-letter{float:left;font-size:4.5em;line-height:.8;margin-right:.05em;margin-top:.05em;font-weight:700;color:#1a1a1a}

/* előszó */
.preface-content{font-style:italic}
.preface-content h2{font-style:normal}

/* aláírás */
.author-sig{text-align:right;font-style:italic;margin-top:2em;text-indent:0}

/* Képoldal: szimmetrikus margó, középre kényszerítve */
.image-page .page-content{display:flex;justify-content:center;align-items:center;padding:20mm!important}
.image-page img{max-width:100%;max-height:100%;object-fit:contain;display:block;margin:auto}
.image-placeholder{color:#999;font-style:italic;text-align:center;font-size:14pt}

/* TOC */
.toc-page h2{margin-bottom:1.2em;font-size:18pt}
.toc-entry{display:flex;justify-content:space-between;margin-bottom:.4em;font-size:9pt}
.toc-entry .toc-title{flex:0 1 auto}
.toc-entry .toc-page{min-width:18pt;text-align:right}
.toc-dots{flex:1;border-bottom:1px dotted #666;margin:0 .5em;position:relative;top:-.3em}

/* OLDALSZÁM: rugalmas lábléc */
.page-number{
  display:block;margin-top:auto;padding:0 0 8mm;text-align:center;
  font-size:10pt;font-family:'EB Garamond',serif;pointer-events:none;
}

.cover-page .page-number{display:none}

/* PRINT: teljes méretkényszer, nincs külső margó/árnyék, 1 könyvoldal = 1 PDF oldal */
@media print{
  @page{size:230mm 230mm;margin:0}
  html,body{width:230mm;margin:0;padding:0;background:#fff}
  .page-container{width:230mm!important;margin:0 auto!important}
  .page{
    width:230mm!important;height:230mm!important;
    margin:0!important;box-shadow:none!important;break-after:page;
  }
}

/* képernyős segédkeret csak képernyőn */
@media screen{
  .page{border:1px solid #ddd}
  .page::before{content:"";position:absolute;border:1px dashed #ccc;pointer-events:none}
  .page:nth-child(even)::before{top:20mm;left:20mm;right:25mm;bottom:25mm}
  .page:nth-child(odd)::before {top:20mm;left:25mm;right:20mm;bottom:25mm}
}
/* PAGEDJS FELÜLÍRÁS STÍLUSOK */
.pagedjs_pages {
  margin: 0 !important;
  padding: 0 !important;
  transform: none !important;
}

.pagedjs_page {
  margin: 0 !important;
  transform: none !important;
  position: static !important;
}

.pagedjs_pagebox {
  margin: 0 !important;
  padding: 0 !important;
  transform: none !important;
}

.pagedjs_page_content {
  transform: none !important;
  position: relative !important;
}
</style>
<style>
/* === JAVÍTOTT MARGÓK ÉS OLDALSZÁMOZÁS === */
:root{
  --outer: 20mm;
  --inner: 25mm;
  --top:   20mm;
  --bottom: 30mm;  /* Nagyobb alsó margó PDF-hez */
  --imgpad: 6mm;
}

/* Egyszerű, konzisztens margó kezelés */
.page-content{
  padding: var(--top) var(--outer) var(--bottom) var(--outer) !important;
}

/* Kötés felőli oldalak */
.page:nth-child(even) .page-content{ 
  padding-right: var(--inner) !important; 
}
.page:nth-child(odd) .page-content{  
  padding-left: var(--inner) !important; 
}

/* Képoldalak */
.image-page .page-content{
  padding: var(--imgpad) !important;
}
.image-page img{
  max-width: 100% !important;
  max-height: 100% !important;
  object-fit: contain !important;
  display: block;
  margin: 0 auto;
}

/* Oldalszám - belső margón belül, rugalmasan */
.page-number{
  position: static !important;
  margin: 0 !important;
  padding: 0 0 8mm !important;
  text-align: center !important;
  font-size: 10pt !important;
  font-family: 'EB Garamond', serif !important;
  pointer-events: none !important;
}

/* @page margók kikapcsolása */
@page { 
  margin: 0 !important; 
  size: 230mm 230mm !important;
}
@page :left  { margin: 0 !important; }
@page :right { margin: 0 !important; }

/* Paged.js transzformok kikapcsolása */
.pagedjs_pages,
.pagedjs_page,
.pagedjs_pagebox,
.pagedjs_page_content{
  margin: 0 !important;
  padding: 0 !important;
  transform: none !important;
}
</style>
<style id="fix-dropcap-20250115">
/* JAVÍTOTT INICIÁLÉ KEZELÉS - minden novella első bekezdésénél */
.page-content h2 + p::first-letter,
.page-content .drop-cap::first-letter{
  float: left !important;
  font-size: 4.5em !important;
  line-height: 0.8 !important;
  margin-right: 0.05em !important;
  margin-top: 0.05em !important;
  font-weight: 700 !important;
  color: #1a1a1a !important;
}

/* A cím utáni első bekezdés NEM húzódjon be */
.page-content h2 + p{ 
  text-indent: 0 !important; 
}

/* Biztosítjuk, hogy az iniciálé mindig működjön */
.page-content .first-p::first-letter{
  float: left !important;
  font-size: 4.5em !important;
  line-height: 0.8 !important;
  margin-right: 0.05em !important;
  margin-top: 0.05em !important;
  font-weight: 700 !important;
  color: #1a1a1a !important;
}
</style>

<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>

<script>
class PositionFixHandler extends Paged.Handler {
  constructor(chunker, polisher, caller) {
    super(chunker, polisher, caller);
    console.log('PositionFixHandler betöltve - javítja az elcsúszást');
  }

  beforeParsed(content) {
    console.log('beforeParsed - tartalom tisztítása');
    const allElements = content.querySelectorAll('*');
    allElements.forEach(el => {
  el.style.transform = 'none';
  // Ne írjuk felül a pozíciót! Hagyjuk a saját CSS-t érvényesülni.
});
  }

  afterPageLayout(pageElement, page, breakToken) {
    console.log('afterPageLayout - oldal pozíció javítása', page);
    pageElement.style.transform = 'none';
    pageElement.style.margin = '0';
    pageElement.style.padding = '0';
    
    const pageBox = pageElement.querySelector('.pagedjs_pagebox');
    if (pageBox) {
      pageBox.style.transform = 'none';
      pageBox.style.margin = '0';
      pageBox.style.padding = '0';
    }
    
    const pageContent = pageElement.querySelector('.pagedjs_page_content');
    if (pageContent) {
      pageContent.style.transform = 'none';
      pageContent.style.position = 'relative';
    }
  }

  afterRendered(pages) {
    console.log('afterRendered - végső pozíció ellenőrzés', pages.length, 'oldal');

    const pagesContainer = document.querySelector('.pagedjs_pages');
    if (pagesContainer) {
      pagesContainer.style.margin = '0';
      pagesContainer.style.padding = '0';
      pagesContainer.style.transform = 'none';
    }
    
    pages.forEach((page, index) => {
      page.style.margin = '0';
      page.style.transform = 'none';
    });

    const customCSS = `
      .pagedjs_pages { margin: 0 !important; padding: 0 !important; transform: none !important; }
      .pagedjs_page { margin: 0 !important; transform: none !important; position: static !important; }
      .pagedjs_pagebox { margin: 0 !important; padding: 0 !important; transform: none !important; }
      .pagedjs_page_content { transform: none !important; position: relative !important; }
    `;
    
    const style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = customCSS;
    document.head.appendChild(style);

    console.log('✅ Pozíció javítás befejezve - elcsúszás megszüntetve');

    const renderedPages = pages
      .map(page => page && (page.element || page))
      .filter(pageEl => pageEl && pageEl.classList);

    renderedPages.forEach((pageEl, index) => {
      const pageNumber = index + 1;
      pageEl.dataset.renderedNumber = pageNumber;
      const originalPage = pageEl.querySelector('.page');
      if (!originalPage) {
        return;
      }
      let holder = originalPage.querySelector('.page-number');
      if (!holder) {
        holder = document.createElement('span');
        holder.className = 'page-number';
        originalPage.appendChild(holder);
      }
      if (originalPage.classList.contains('cover-page')) {
        holder.textContent = '';
        return;
      }
      holder.textContent = pageNumber;
      originalPage.dataset.renderedNumber = pageNumber;
    });

    document.querySelectorAll('.toc-entry[data-target]').forEach(entry => {
      const targetId = entry.dataset.target;
      if (!targetId) {
        return;
      }
      const target = document.getElementById(targetId);
      if (!target) {
        return;
      }
      const hostPage = target.closest('.page');
      if (!hostPage) {
        return;
      }
      const pageNumber = hostPage.dataset.renderedNumber;
      if (!pageNumber) {
        return;
      }
      const pageSpan = entry.querySelector('.toc-page');
      if (pageSpan) {
        pageSpan.textContent = pageNumber;
      }
    });
  }
}

Paged.registerHandlers(PositionFixHandler);

document.addEventListener('DOMContentLoaded', function() {
  console.log('🔧 PagedJS pozíció javító handler aktív');
});
</script>

<style id="alsomargo-fix-from-v1">
  /* Alsó margó + lábléc védősáv különválasztva */
  :root{
    --bottom: 22mm;      /* tényleges alsó szöveg-margó */
    --footer-safe: 8mm;  /* védősáv a lapszámnak */
  }
  .page-content{
    /* szöveg alá: margó + védősáv */
    padding-bottom: calc(var(--bottom) + var(--footer-safe)) !important;
  }
  .page-content::after{
    content:""; display:block; height: var(--footer-safe);
  }
  .page-number{ padding-bottom: var(--footer-safe) !important; }
</style>

</head>
<body>
<div class="page-container">
'''

    # Borító (külső)
    html += '''
<!-- ELSŐ BORÍTÓ -->
<div class="page cover-page">
'''
    html += ('            <img src="images/000_elso_borito.jpg" alt="Borító">\n'
             if Path('images/000_elso_borito.jpg').exists()
             else '            <div class="page-content"><div class="image-placeholder">[Első borító]</div></div>\n')
    html += '        </div>\n'

    # Borító belső
    html += '''
<!-- ELSŐ BORÍTÓ BELSŐ -->
<div class="page cover-page">
'''
    html += ('            <img src="images/001_elso_borito_belso.jpg" alt="Belső borító">\n'
             if Path('images/001_elso_borito_belso.jpg').exists()
             else '            <div class="page-content"><div class="image-placeholder">[Első borító belső oldala]</div></div>\n')
    html += '        </div>\n'

    # Címoldal
    html += '''
<!-- CÍMOLDAL -->
<div class="page title-page">
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
<div class="page impressum-page">
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
<div class="page toc-page">
  <div class="page-content">
    <h2>TARTALOM</h2>
'''

    # --- Szöveg feldolgozás ---
    content = Path('text.txt').read_text('utf-8').replace('\r\n','\n').replace('\r','\n')

    content_html = ''
    toc_entries  = []
    current_section = None  # 'preface' | 'story'
    first_paragraph = False
    section_content = []

    lines = content.split('\n')
    i = 0

    def close_section(section_type):
        nonlocal content_html, section_content
        if section_content:
            for para in section_content:
                content_html += para
            section_content = []
        content_html += '            </div>\n            <span class="page-number"></span>\n        </div>\n'
        return section_type

    def add_author_page(author):
        nonlocal content_html
        img = _find_author_image(author)
        if img:
            content_html += f'''
<!-- KÉP: {author} -->
<div class="page image-page">
  <div class="page-content">
    <img src="images/{img}" alt="{author}">
  </div>
  <span class="page-number"></span>
</div>
'''
        else:
            content_html += f'''
<!-- KÉP PLACEHOLDER: {author} -->
<div class="page image-page">
  <div class="page-content"><div class="image-placeholder">[{author} képe]</div></div>
  <span class="page-number"></span>
</div>
'''

    while i < len(lines):
        line = lines[i].strip()

        if line == '[ELŐSZÓ]':
            current_section = 'preface'
            content_html += '''
<!-- ELŐSZÓ -->
<div class="page">
  <div class="page-content preface-content">
    <h2>ELŐSZÓ</h2>
'''
            first_paragraph = True
            section_content = []
            i += 1
            continue

        # CÍM — ugyanabban a blokkban folytatjuk, amíg nincs [SZERZŐ:]
        if line.startswith('[CÍM:'):
            title = line[5:-1].strip()
            entry_index = len(toc_entries) + 1
            base_slug = _slugify_image_name(title)
            heading_slug = re.sub(r'[^a-z0-9_]+', '', base_slug) or f'resz-{entry_index:03d}'
            heading_id = f'section-{entry_index:03d}-{heading_slug}'
            if current_section == 'story':
                section_content.append(f'                <h2 id="{heading_id}">{title}</h2>\n')
                toc_entries.append({'title': title, 'target': heading_id})
                first_paragraph = True
                i += 1
                continue
            if current_section:
                close_section(current_section)
            current_section = 'story'
            content_html += f'''
<!-- NOVELLA BLOKK -->
<div class="page" id="{heading_id}">
  <div class="page-content">
    <h2 id="{heading_id}-title">{title}</h2>
'''
            first_paragraph = True
            section_content = []
            toc_entries.append({'title': title, 'target': f'{heading_id}-title'})
            i += 1
            continue

        # SZERZŐ — itt zár a blokk, majd képes oldal
        if line.startswith('[SZERZŐ:') and not line.startswith('[SZERZŐ_TEMP:'):
            author = line[8:-1].strip()
            if current_section:
                section_content.append(f'                <p class="author-sig">Írta: {author}</p>\n')
                closed = close_section(current_section)
                if closed == 'story':
                    add_author_page(author)
                current_section = None
            i += 1
            continue

        if line.startswith('[SZERZŐ_TEMP:'):
            i += 1; continue

        if not line:
            i += 1; continue

        if current_section:
            # bekezdés összefűzés
            paras = [line]; j = i + 1
            while j < len(lines):
                nx = lines[j].strip()
                if not nx or nx.startswith('['): break
                paras.append(nx); j += 1
            txt = ' '.join(paras)
            if first_paragraph:
                section_content.append(f'                <p class="first-p drop-cap">{txt}</p>\n')
                first_paragraph = False
            else:
                section_content.append(f'                <p>{txt}</p>\n')
            i = j
        else:
            i += 1

    # zárás, ha maradt nyitva
    if current_section:
        close_section(current_section)

    # TOC lezárás - számítsuk ki a TOC oldal számát
    for e in toc_entries:
        toc_html += f'''      <div class="toc-entry" data-target="{e['target']}"><span class="toc-title">{e['title']}</span><span class="toc-dots"></span><span class="toc-page">–</span></div>
'''
    toc_html += f'''  </div>
  <span class="page-number"></span>
</div>
'''

    html += toc_html
    html += content_html

    # Hátsó borító belső
    html += '''
<!-- HÁTSÓ BORÍTÓ BELSŐ -->
<div class="page cover-page">
'''
    html += ('  <img src="images/998_hatso_borito_belso.jpg" alt="Hátsó borító belső">\n'
             if Path('images/998_hatso_borito_belso.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Hátsó borító belső oldala]</div></div>\n')
    html += '</div>\n'

    # Hátsó borító
    html += '''
<!-- HÁTSÓ BORÍTÓ -->
<div class="page cover-page">
'''
    html += ('  <img src="images/999_hatso_borito.jpg" alt="Hátsó borító">\n'
             if Path('images/999_hatso_borito.jpg').exists()
             else '  <div class="page-content"><div class="image-placeholder">[Hátsó borító]</div></div>\n')
    html += '</div>\n'

    html += '</div>\n</body>\n</html>'

    Path('book.html').write_text(html, encoding='utf-8')
    print("KESZ: book.html - nyomtatásnál állítsd: Margók=Nincs, Méretezés=100%, Háttérgrafika=on.")

if __name__ == "__main__":
    try:
        create_book_html()
    except Exception as e:
        print("HIBA:", e)
        import traceback; traceback.print_exc()
