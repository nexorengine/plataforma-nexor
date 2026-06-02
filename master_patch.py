#!/usr/bin/env python3
"""
NEXOR — MASTER PATCH
Aplica todos os patches na ordem correta em uma única execução.
Execute em: C:\NEXOR\nexor_quiz\
"""

import shutil
import re
from pathlib import Path

HTML = Path("static/index.html")
BACKUP = Path("static/index.html.backup")

# ─── RESTAURA BACKUP LIMPO ───────────────────────────────────────────────────
if BACKUP.exists():
    shutil.copy(BACKUP, HTML)
    print("✅ Backup restaurado")
else:
    print("⚠️  Backup não encontrado — usando index.html atual")

c = HTML.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 1 — ES: has_es + botão ES + label + TTS + breadcrumb
# ═══════════════════════════════════════════════════════════════════════════════

# 1a. has_es
old = "    const hasEn = typeof q === 'object' ? q.has_en : false;"
new = "    const hasEn = typeof q === 'object' ? q.has_en : false;\n    const hasEs = typeof q === 'object' ? q.has_es : false;"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1a: has_es adicionado")

# 1b. botão ES
old = "          ${hasEn ? `<button class=\"lang-btn en\" onclick=\"startQuiz(${n},'en')\">🇺🇸 EN</button>` : ''}"
new = "          ${hasEn ? `<button class=\"lang-btn en\" onclick=\"startQuiz(${n},'en')\">🇺🇸 EN</button>` : ''}\n          ${hasEs ? `<button class=\"lang-btn es\" onclick=\"startQuiz(${n},'es')\">🇪🇸 ES</button>` : ''}"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1b: botão ES adicionado")

# 1c. label gerar
old = "  const genLabel = bilingual ? 'GERAR PT + EN' : 'GERAR NOVO';"
new = "  const genLabel = bilingual ? 'GERAR PT + EN + ES' : 'GERAR NOVO';"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1c: label gerar atualizado")

# 1d. TTS espanhol
old = "  const lang = (sel.lang === 'en') ? 'en-US' : 'pt-BR';"
new = "  const lang = sel.lang === 'en' ? 'en-US' : sel.lang === 'es' ? 'es-ES' : 'pt-BR';"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1d: TTS espanhol adicionado")

# 1e. breadcrumb ES
old = "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : ' 🇧🇷 PT';"
new = "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : sel.lang === 'es' ? ' 🇪🇸 ES' : ' 🇧🇷 PT';"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1e: breadcrumb ES adicionado")

# 1f. CSS botão ES
old = ".lang-btn.en{border-color:#4a8fd4;color:#4a8fd4;}"
new = ".lang-btn.en{border-color:#4a8fd4;color:#4a8fd4;}.lang-btn.es{border-color:#ffffff;color:#ffffff;}"
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 1f: CSS botão ES adicionado")

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 2 — Texto geração trilíngue
# ═══════════════════════════════════════════════════════════════════════════════
old = "Gerando vers\u251c\u00c1\u00b5es PT + EN. Aguarde ~6 minutos."
new_txt = "Gerando versões PT + EN + ES. Aguarde ~8 minutos."

variacoes_warn = [
    ("Gerando vers\u00f5es PT + EN. Aguarde ~6 minutos.", "Gerando versões PT + EN + ES. Aguarde ~8 minutos."),
    ("Gerando vers├Áes PT + EN. Aguarde ~6 minutos.", "Gerando versões PT + EN + ES. Aguarde ~8 minutos."),
]
for old_v, new_v in variacoes_warn:
    if old_v in c:
        c = c.replace(old_v, new_v)
        print("✅ PATCH 2: texto geração trilíngue")
        break

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 3 — Badge da certificadora na tela de geração
# ═══════════════════════════════════════════════════════════════════════════════

# 3a. id no gen-icon
old = '<div class="gen-icon">⚙️</div>'
new = '<div class="gen-icon" id="gen-icon">⚙️</div>'
if old in c:
    c = c.replace(old, new)
    print("✅ PATCH 3a: gen-icon com id")

# 3b. JS badge dinâmico
old_gen_sub = "  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;"
new_gen_sub = (
    "  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;\n"
    "  const certBadge = CERT_BADGES[sel.cert.id];\n"
    "  if (certBadge) {\n"
    "    document.getElementById('gen-icon').innerHTML = certBadge;\n"
    "    document.getElementById('gen-icon').style.fontSize = '0';\n"
    "  } else {\n"
    "    document.getElementById('gen-icon').innerHTML = '\u2699\ufe0f';\n"
    "    document.getElementById('gen-icon').style.fontSize = '';\n"
    "  }"
)

variacoes_sub = [
    ("  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;", new_gen_sub),
    ("  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;".replace('\u00b7', '·'), new_gen_sub),
]
for old_v, new_v in variacoes_sub:
    if old_v in c and 'certBadge' not in c:
        c = c.replace(old_v, new_v)
        print("✅ PATCH 3b: badge dinâmico na geração")
        break

# 3c. CSS SVG no gen-icon
css_addition = ".gen-icon svg{width:80px;height:80px;display:block;margin:0 auto;}"
if css_addition not in c:
    c = c.replace("</style>", css_addition + "</style>", 1)
    print("✅ PATCH 3c: CSS SVG gen-icon")

# ═══════════════════════════════════════════════════════════════════════════════
# PATCH 4 — Versão da certificação na linha das métricas (simples e elegante)
# ═══════════════════════════════════════════════════════════════════════════════

# 4a. JS — adiciona versão no dh-meta com separador simples
old_meta_js = "  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios`;"

new_meta_js = (
    "  const versionSuffix = sel.cert.version ? '  |  ' + sel.cert.version : '';\n"
    "  document.getElementById('dh-meta').textContent = "
    "`${sel.cert.exam_minutes} min \u00b7 ${sel.cert.exam_questions} quest\u00f5es \u00b7 ${sel.cert.domains.length} dom\u00ednios${versionSuffix}`;"
)

variacoes_meta = [
    (old_meta_js, new_meta_js),
    (old_meta_js.replace('·', '\u00b7'), new_meta_js),
]

for old_v, new_v in variacoes_meta:
    if old_v in c and 'versionSuffix' not in c:
        c = c.replace(old_v, new_v)
        print("✅ PATCH 4: versão adicionada às métricas")
        break

# 4b. CSS versão nas métricas
css_version = ".cert-header-meta-version{opacity:0.6;}"
if css_version not in c:
    c = c.replace("</style>", css_version + "</style>", 1)

# ═══════════════════════════════════════════════════════════════════════════════
# SALVA
# ═══════════════════════════════════════════════════════════════════════════════
HTML.write_text(c, encoding="utf-8")
print("\n" + "="*50)
print("✅ MASTER PATCH CONCLUÍDO!")
print("Faça Ctrl+Shift+R no navegador.")
print("="*50)
