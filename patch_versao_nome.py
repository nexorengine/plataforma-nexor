#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# PATCH 1: Remover versão do dh-meta (linha das métricas)
old_meta = """  const versionInfo = sel.cert.version ? ` | ${sel.cert.version}` : '';
  document.getElementById('dh-meta').innerHTML = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios<span class="cert-version">${versionInfo}</span>`;"""

new_meta = """  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios`;
  const versionInfo = sel.cert.version ? `<span class="cert-version-bar"></span><span class="cert-version">${sel.cert.version}</span>` : '';
  document.getElementById('dh-name').innerHTML = sel.cert.name + (versionInfo ? ' ' + versionInfo : '');"""

if old_meta in c:
    c = c.replace(old_meta, new_meta)
    print("PATCH 1 OK: versão movida para ao lado do nome")
else:
    # tenta com encoding diferente
    match = re.search(r'const versionInfo.*?innerHTML.*?cert-version.*?`;\s*renderDomains', c, re.DOTALL)
    if match:
        old_found = match.group().replace('\n  renderDomains', '')
        c = c.replace(old_found, new_meta)
        print("PATCH 1 OK: versão movida (alternativa)")
    else:
        print("PATCH 1 AVISO: padrão não encontrado")

# PATCH 2: CSS — barra fina vertical alinhada pelo topo + texto fino
old_css = re.search(r'\.cert-version\{[^}]+\}', c)
if old_css:
    new_css = (
        '.cert-version-bar{'
        'display:inline-block;'
        'width:1px;'
        'height:14px;'
        'background:#ffffff;'
        'opacity:0.5;'
        'margin:0 8px;'
        'vertical-align:top;'
        'margin-top:3px;'
        '}'
        '.cert-version{'
        'color:#ffffff;'
        'font-size:11px;'
        'font-weight:300;'
        'opacity:0.7;'
        'vertical-align:top;'
        'margin-top:2px;'
        'display:inline-block;'
        '}'
    )
    c = c.replace(old_css.group(), new_css)
    print("PATCH 2 OK: CSS barra fina vertical alinhada pelo topo")
else:
    print("PATCH 2 AVISO: CSS cert-version não encontrado")

# PATCH 3: Garantir que dh-name aceita innerHTML (já aceita por padrão)
f.write_text(c, encoding="utf-8")
print("\nPATCH CONCLUÍDO!")
print("Faça Ctrl+Shift+R no navegador.")
