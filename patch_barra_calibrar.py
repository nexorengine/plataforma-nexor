#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

old = re.search(r'\.cert-version-bar\{[^}]+\}\.cert-version\{[^}]+\}', c)
if old:
    new = (
        '.cert-version-bar{'
        'display:inline-block;'
        'width:1px;'
        'height:38px;'
        'background:#ffffff;'
        'opacity:0.35;'
        'margin:0 12px;'
        'vertical-align:top;'
        'margin-top:-20px;'
        '}'
        '.cert-version{'
        'color:#ffffff;'
        'font-size:10px;'
        'font-weight:300;'
        'opacity:0.65;'
        'vertical-align:middle;'
        'display:inline-block;'
        'letter-spacing:0.5px;'
        '}'
    )
    c = c.replace(old.group(), new)
    f.write_text(c, encoding="utf-8")
    print("OK - barra calibrada")
else:
    print("AVISO - padrão não encontrado")
    match = re.search(r'\.cert-version-bar\{[^}]+\}', c)
    if match:
        print(f"Encontrado separado: {match.group()}")
