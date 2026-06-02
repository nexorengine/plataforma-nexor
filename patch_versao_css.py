#!/usr/bin/env python3
from pathlib import Path

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# Remove border-left (barra dupla) e corrige para letra fina branca
old = '.cert-version{color:#ffffff;font-size:11px;margin-left:6px;letter-spacing:0.5px;vertical-align:middle;border-left:1.5px solid #ffffff;padding-left:8px;}'
new = '.cert-version{color:#ffffff;font-size:11px;margin-left:4px;letter-spacing:0.5px;font-weight:300;opacity:0.85;}'

if old in c:
    c = c.replace(old, new)
    print("OK - CSS corrigido: letra fina branca, sem barra dupla")
else:
    print("AVISO - padrao nao encontrado, tentando alternativa...")
    # busca qualquer versao do cert-version CSS
    import re
    match = re.search(r'\.cert-version\{[^}]+\}', c)
    if match:
        print(f"Encontrado: {match.group()}")
        c = c.replace(match.group(), new)
        print("OK - substituido")
    else:
        print("ERRO - cert-version CSS nao encontrado")

f.write_text(c, encoding="utf-8")
