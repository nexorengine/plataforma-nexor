f = open('static/index.html', encoding='utf-8')
html = f.read()
f.close()

# ─────────────────────────────────────────────────────────────
# CORRECAO 1: selectDomain — popula qh-badge na tela s-quizzes
# ─────────────────────────────────────────────────────────────

old1 = (
    'function selectDomain(id) {\n'
    '  sel.domain = sel.cert.domains.find(d => d.id === id);\n'
    '  document.getElementById(\'qh-domain\').textContent = sel.domain.name;\n'
    '  document.getElementById(\'qh-cert\').textContent = sel.cert.name + \' · 50 questões por quiz\';\n'
    '  renderQuizList();\n'
    '  goTo(\'s-quizzes\');\n'
    '}'
)

new1 = (
    'function selectDomain(id) {\n'
    '  sel.domain = sel.cert.domains.find(d => d.id === id);\n'
    '  document.getElementById(\'qh-domain\').textContent = sel.domain.name;\n'
    '  document.getElementById(\'qh-cert\').textContent = sel.cert.name + \' · 50 questões por quiz\';\n'
    '  const qhBadge = document.getElementById(\'qh-badge\');\n'
    '  if (qhBadge) {\n'
    '    const b = CERT_BADGES[sel.cert.id];\n'
    '    qhBadge.innerHTML = b || \'\';\n'
    '    qhBadge.style.fontSize = b ? \'38px\' : \'0\';\n'
    '  }\n'
    '  renderQuizList();\n'
    '  goTo(\'s-quizzes\');\n'
    '}'
)

# ─────────────────────────────────────────────────────────────
# CORRECAO 2: startQuiz — popula q-badge na tela s-quiz
# Procura pelo trecho que seta o breadcrumb (linha 596-597)
# ─────────────────────────────────────────────────────────────

old2 = (
    "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : sel.lang === 'es' ? ' 🇪🇸 ES' : ' 🇧🇷 PT';\n"
    "  document.getElementById('q-breadcrumb').textContent = sel.cert.name + ' · ' + sel.domain.name + ' · Quiz #' + sel.quizNum + (sel.cert.bilingual ? langLabel : '');"
)

new2 = (
    "  const langLabel = sel.lang === 'en' ? ' 🇺🇸 EN' : sel.lang === 'es' ? ' 🇪🇸 ES' : ' 🇧🇷 PT';\n"
    "  document.getElementById('q-breadcrumb').textContent = sel.cert.name + ' · ' + sel.domain.name + ' · Quiz #' + sel.quizNum + (sel.cert.bilingual ? langLabel : '');\n"
    "  const qBadge = document.getElementById('q-badge');\n"
    "  if (qBadge) {\n"
    "    const b = CERT_BADGES[sel.cert.id];\n"
    "    qBadge.innerHTML = b || '';\n"
    "    qBadge.style.fontSize = b ? '22px' : '0';\n"
    "    qBadge.title = sel.cert.name;\n"
    "  }"
)

# ─────────────────────────────────────────────────────────────
# Aplica
# ─────────────────────────────────────────────────────────────

errors = []

if old1 in html:
    html = html.replace(old1, new1)
    print('OK — qh-badge populado em selectDomain')
else:
    errors.append('ERRO — trecho selectDomain nao encontrado')

if old2 in html:
    html = html.replace(old2, new2)
    print('OK — q-badge populado em startQuiz')
else:
    errors.append('ERRO — trecho startQuiz nao encontrado')

if errors:
    for e in errors:
        print(e)
    print('Nenhuma alteracao salva.')
else:
    open('static/index.html', 'w', encoding='utf-8').write(html)
    print()
    print('Arquivo salvo — teste no browser.')
