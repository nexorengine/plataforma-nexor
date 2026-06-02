#!/usr/bin/env python3
# PATCH NEXOR FRONTEND - Adiciona botao ES e capsule layout
# Coloque em C:\NEXOR\nexor_quiz\ e execute:
# python patch_frontend.py

import shutil
from pathlib import Path

HTML = Path("static/index.html")
BACKUP = Path("static/index.html.backup")

shutil.copy(HTML, BACKUP)
print(f"Backup criado: {BACKUP}")

content = HTML.read_text(encoding="utf-8")

# PATCH 1: adicionar has_es na leitura dos dados
old_has = "    const hasEn = typeof q === 'object' ? q.has_en : false;"
new_has = """    const hasEn = typeof q === 'object' ? q.has_en : false;
    const hasEs = typeof q === 'object' ? q.has_es : false;"""

if old_has in content:
    content = content.replace(old_has, new_has)
    print("PATCH 1 OK: has_es adicionado")
else:
    print("PATCH 1 ERRO: linha has_en nao encontrada")

# PATCH 2: adicionar botao ES na capsule
old_btns = """          ${hasPt ? `<button class="lang-btn pt" onclick="startQuiz(${n},'pt')">🇧🇷 PT</button>` : ''}
          ${hasEn ? `<button class="lang-btn en" onclick="startQuiz(${n},'en')">🇺🇸 EN</button>` : ''}"""

new_btns = """          ${hasPt ? `<button class="lang-btn pt" onclick="startQuiz(${n},'pt')">🇧🇷 PT</button>` : ''}
          ${hasEn ? `<button class="lang-btn en" onclick="startQuiz(${n},'en')">🇺🇸 EN</button>` : ''}
          ${hasEs ? `<button class="lang-btn es" onclick="startQuiz(${n},'es')">🇪🇸 ES</button>` : ''}"""

if old_btns in content:
    content = content.replace(old_btns, new_btns)
    print("PATCH 2 OK: botao ES adicionado")
else:
    print("PATCH 2 ERRO: bloco de botoes nao encontrado")

# PATCH 3: label do botao gerar
old_label = "  const genLabel = bilingual ? 'GERAR PT + EN' : 'GERAR NOVO';"
new_label = "  const genLabel = bilingual ? 'GERAR PT + EN + ES' : 'GERAR NOVO';"

if old_label in content:
    content = content.replace(old_label, new_label)
    print("PATCH 3 OK: label gerar atualizado")
else:
    print("PATCH 3 AVISO: label gerar nao encontrado")

# PATCH 4: TTS para espanhol
old_tts = "  const lang = (sel.lang === 'en') ? 'en-US' : 'pt-BR';"
new_tts = "  const lang = sel.lang === 'en' ? 'en-US' : sel.lang === 'es' ? 'es-ES' : 'pt-BR';"

if old_tts in content:
    content = content.replace(old_tts, new_tts)
    print("PATCH 4 OK: TTS espanhol adicionado")
else:
    print("PATCH 4 AVISO: TTS lang nao encontrado")

# PATCH 5: breadcrumb com ES
old_bread = "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : ' 🇧🇷 PT';"
new_bread = "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : sel.lang === 'es' ? ' 🇪🇸 ES' : ' 🇧🇷 PT';"

if old_bread in content:
    content = content.replace(old_bread, new_bread)
    print("PATCH 5 OK: breadcrumb ES adicionado")
else:
    print("PATCH 5 AVISO: breadcrumb nao encontrado")

# PATCH 6: CSS para botao ES
old_css_en = ".lang-btn.en { background: #1a3a6e; }"
new_css_en = """.lang-btn.en { background: #1a3a6e; }
      .lang-btn.es { background: #c0392b; }"""

if old_css_en in content:
    content = content.replace(old_css_en, new_css_en)
    print("PATCH 6 OK: CSS ES adicionado")
else:
    # tenta alternativa sem espaco
    old_css_en2 = ".lang-btn.en{background:#1a3a6e}"
    if old_css_en2 in content:
        content = content.replace(old_css_en2, old_css_en2 + ".lang-btn.es{background:#c0392b}")
        print("PATCH 6 OK: CSS ES adicionado (minificado)")
    else:
        print("PATCH 6 AVISO: CSS en nao encontrado - adicione manualmente se necessario")

HTML.write_text(content, encoding="utf-8")
print("\nPATCH FRONTEND CONCLUIDO!")
print("Faca um hard refresh no navegador: Ctrl+Shift+R")
