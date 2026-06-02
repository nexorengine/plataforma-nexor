#!/usr/bin/env python3
from pathlib import Path

f = Path("static/index.html")
linhas = f.read_text(encoding="utf-8").split('\n')

novas = []
skip = False
div_depth = 0

for linha in linhas:
    if 'id="dh-version"' in linha:
        skip = True
        div_depth = 1
        continue
    if skip:
        div_depth += linha.count('<div')
        div_depth -= linha.count('</div>')
        if div_depth <= 0:
            skip = False
        continue
    novas.append(linha)

resultado = '\n'.join(novas)

if 'id="dh-version"' not in resultado:
    f.write_text(resultado, encoding="utf-8")
    print(f"OK - {len(linhas)-len(novas)} linhas removidas")
else:
    print("ERRO - nao salvou")

print("Ctrl+Shift+R no navegador.")
