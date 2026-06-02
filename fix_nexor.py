#!/usr/bin/env python3
from pathlib import Path

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# Substitui badge NEXOR -> NEXOR
old1 = '<span class="hdr-badge">NEXOR</span>'
new1 = '<span class="hdr-badge">NEXOR</span>'

# Substitui titulo
old2 = '<span class="hdr-title">QUIZ ENGINE — Sistema de Preparação para Certificações GRC</span>'
new2 = '<span class="hdr-title">Certification Readiness Engine | Powered by FractalLearning™</span>'

if old1 in c:
    c = c.replace(old1, new1)
    print("OK - badge: NEXOR → NEXOR")
else:
    print("AVISO - badge nao encontrado")

if old2 in c:
    c = c.replace(old2, new2)
    print("OK - titulo atualizado")
else:
    print("AVISO - titulo nao encontrado")

f.write_text(c, encoding="utf-8")
print("Salvo. Ctrl+Shift+R no navegador.")
