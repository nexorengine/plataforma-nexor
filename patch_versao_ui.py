#!/usr/bin/env python3
# PATCH - Adiciona versão com separador elegante na página de domínios
# Execute em: C:\NEXOR\nexor_quiz\

from pathlib import Path

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# PATCH 1: Atualizar selectCert para incluir version na meta
old_meta = "  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios`;"

new_meta = """  const versionInfo = sel.cert.version ? ` | ${sel.cert.version}` : '';
  document.getElementById('dh-meta').innerHTML = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios<span class="cert-version">${versionInfo}</span>`;"""

# tenta variações de encoding
variacoes = [
    ("  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios`;",
     "  const versionInfo = sel.cert.version ? ` | ${sel.cert.version}` : '';\n  document.getElementById('dh-meta').innerHTML = `${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios<span class=\"cert-version\">${versionInfo}</span>`;"),
    (old_meta, new_meta),
    ("  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min ┬À ${sel.cert.exam_questions} quest├Áes ┬À ${sel.cert.domains.length} dom├¡nios`;",
     "  const versionInfo = sel.cert.version ? ` | ${sel.cert.version}` : '';\n  document.getElementById('dh-meta').innerHTML = `${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios<span class=\"cert-version\">${versionInfo}</span>`;"),
]

ok = False
for old_v, new_v in variacoes:
    if old_v in c:
        c = c.replace(old_v, new_v)
        print("PATCH 1 OK: versão adicionada ao dh-meta")
        ok = True
        break

if not ok:
    print("PATCH 1 AVISO: linha dh-meta não encontrada")

# PATCH 2: Adicionar CSS para o separador e versão
old_css = ".cert-header-meta{"
new_css_addition = ".cert-version{opacity:0.5;font-size:11px;margin-left:4px;letter-spacing:0.5px;}"

if old_css in c:
    idx = c.find(old_css)
    end_idx = c.find("}", idx) + 1
    c = c[:end_idx] + new_css_addition + c[end_idx:]
    print("PATCH 2 OK: CSS cert-version adicionado")
else:
    # injeta antes do fechamento do style
    old_style_end = "</style>"
    if old_style_end in c:
        c = c.replace(old_style_end, new_css_addition + old_style_end, 1)
        print("PATCH 2 OK: CSS cert-version injetado no style")
    else:
        print("PATCH 2 AVISO: CSS não encontrado")

f.write_text(c, encoding="utf-8")
print("\nPATCH VERSÃO INTERFACE CONCLUÍDO!")
print("Faça Ctrl+Shift+R no navegador para ver a versão na página de domínios.")
