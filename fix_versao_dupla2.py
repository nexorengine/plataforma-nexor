#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# O padrão exato encontrado no diagnóstico
# dh-meta.textContent seguido de versionInfo que vai para dh-name
# precisamos remover o bloco do dh-meta que foi adicionado pelo patch_versao_ui
# e manter apenas o do patch_versao_nome

old = (
    "document.getElementById('dh-meta').textContent = "
    "`${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios`;\n"
    "  const versionInfo = sel.cert.version ? "
    "`<span class=\"cert-version-bar\"></span><span class=\"cert-version\">${sel.cert.version}</span>` : '';\n"
    "  document.getElementById('dh-name').innerHTML = sel.cert.name + (versionInfo ? ' ' + versionInfo : '');"
)

new = (
    "document.getElementById('dh-meta').textContent = "
    "`${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios`;\n"
    "  const versionInfo = sel.cert.version ? "
    "`<span class=\"cert-version-wrap\"><span class=\"cert-version-bar\"></span><span class=\"cert-version\">${sel.cert.version}</span></span>` : '';\n"
    "  document.getElementById('dh-name').innerHTML = sel.cert.name + (versionInfo ? ' ' + versionInfo : '');"
)

# primeiro vamos ver quantas ocorrencias de versionInfo existem
count_vi = c.count("const versionInfo")
print(f"Ocorrências de versionInfo: {count_vi}")

if count_vi > 1:
    # remove a primeira ocorrência (a do patch_versao_ui que é a errada)
    # a primeira fica no bloco do dh-meta com " | "
    old_ui = (
        "  const versionInfo = sel.cert.version ? ` | ${sel.cert.version}` : '';\n"
        "  document.getElementById('dh-meta').innerHTML = "
        "`${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios"
        "<span class=\"cert-version\">${versionInfo}</span>`;"
    )
    if old_ui in c:
        c = c.replace(old_ui, "")
        f.write_text(c, encoding="utf-8")
        print("OK - versão duplicada removida")
    else:
        # mostra contexto das duas ocorrências
        idx1 = c.find("const versionInfo")
        idx2 = c.find("const versionInfo", idx1+10)
        print("Primeira ocorrência:")
        print(repr(c[max(0,idx1-50):idx1+200]))
        print("\nSegunda ocorrência:")
        print(repr(c[max(0,idx2-50):idx2+200]))
else:
    print("Apenas uma ocorrência — sem duplicação no JS")
    # verifica se a duplicação está no HTML
    count_dh = c.count("cert-version")
    print(f"Ocorrências de cert-version no HTML: {count_dh}")
