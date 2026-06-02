#!/usr/bin/env python3
from pathlib import Path

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

old = "Gerando vers\u251c\u00c1\u00b5es PT + EN. Aguarde ~6 minutos."
new = "Gerando vers\u00f5es PT + EN + ES. Aguarde ~8 minutos."

# tenta variações
variacoes = [
    ("Gerando vers├Áes PT + EN. Aguarde ~6 minutos.", "Gerando versões PT + EN + ES. Aguarde ~8 minutos."),
    ("Gerando versões PT + EN. Aguarde ~6 minutos.", "Gerando versões PT + EN + ES. Aguarde ~8 minutos."),
    ("Gerando vers\\u00f5es PT + EN. Aguarde ~6 minutos.", "Gerando versões PT + EN + ES. Aguarde ~8 minutos."),
]

ok = False
for old_v, new_v in variacoes:
    if old_v in c:
        c = c.replace(old_v, new_v)
        f.write_text(c, encoding="utf-8")
        print(f"OK - texto atualizado para trilíngue")
        ok = True
        break

if not ok:
    print("AVISO - padrao nao encontrado, buscando alternativa...")
    # busca qualquer menção a PT + EN no gen-warn
    import re
    match = re.search(r"gen-warn.*?'([^']*PT[^']*EN[^']*)'", c)
    if match:
        print(f"Encontrado: {match.group(1)}")
    else:
        print("Nao encontrado - verifique manualmente a linha 509")
