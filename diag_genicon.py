#!/usr/bin/env python3
from pathlib import Path

c = Path("static/index.html").read_text(encoding="utf-8")

# Busca o bloco S4
idx = c.find("S4: GENERATING")
if idx > 0:
    print("S4 encontrado:")
    print(repr(c[idx:idx+400]))
else:
    print("S4 nao encontrado, buscando gen-title...")
    idx = c.find("gen-title")
    idx2 = c.rfind("gen-title")
    print(repr(c[max(0,idx2-200):idx2+200]))
