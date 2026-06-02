#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# PATCH CSS: agrupa barra+versão alinhado pela linha de baixo
old = re.search(r'\.cert-version-bar\{[^}]+\}\.cert-version\{[^}]+\}', c)
if old:
    new = (
        '.cert-version-wrap{'
        'display:inline-flex;'
        'align-items:flex-end;'
        'vertical-align:bottom;'
        'margin-left:12px;'
        'gap:0;'
        '}'
        '.cert-version-bar{'
        'display:inline-block;'
        'width:1px;'
        'height:38px;'
        'background:#ffffff;'
        'opacity:0.35;'
        'margin-right:12px;'
        'flex-shrink:0;'
        '}'
        '.cert-version{'
        'color:#ffffff;'
        'font-size:10px;'
        'font-weight:300;'
        'opacity:0.65;'
        'letter-spacing:0.5px;'
        'line-height:1;'
        'padding-bottom:1px;'
        '}'
    )
    c = c.replace(old.group(), new)
    print("PATCH CSS OK")
else:
    print("AVISO CSS não encontrado")

# PATCH JS: envolve barra+versão num wrapper
old_js = '`<span class="cert-version-bar"></span><span class="cert-version">${sel.cert.version}</span>`'
new_js = '`<span class="cert-version-wrap"><span class="cert-version-bar"></span><span class="cert-version">${sel.cert.version}</span></span>`'

if old_js in c:
    c = c.replace(old_js, new_js)
    print("PATCH JS OK: wrapper adicionado")
else:
    print("AVISO JS não encontrado")

f.write_text(c, encoding="utf-8")
print("\nPATCH CONCLUÍDO - Ctrl+Shift+R")
