f = open('static/index.html', encoding='utf-8')
html = f.read()
f.close()

# ─────────────────────────────────────────────────────────────
# CORRECAO 1: tela s-quizzes — adiciona badge ao lado do nome
# ANTES:
#   <div class="cert-header">
#     <div>
#       <div class="cert-header-name" id="qh-domain"></div>
#       <div class="cert-header-meta" id="qh-cert"></div>
#     </div>
#   </div>
# DEPOIS: adiciona div para badge com id="qh-badge"
# ─────────────────────────────────────────────────────────────

old1 = (
    '<div class="screen" id="s-quizzes">\n'
    '  <button class="back-btn" onclick="goTo(\'s-domains\')">← DOMÍNIOS</button>\n'
    '  <div class="cert-header">\n'
    '    <div>\n'
    '      <div class="cert-header-name" id="qh-domain"></div>\n'
    '      <div class="cert-header-meta" id="qh-cert"></div>\n'
    '    </div>\n'
    '  </div>'
)

new1 = (
    '<div class="screen" id="s-quizzes">\n'
    '  <button class="back-btn" onclick="goTo(\'s-domains\')">← DOMÍNIOS</button>\n'
    '  <div class="cert-header">\n'
    '    <div id="qh-badge" style="font-size:38px;margin-right:14px;flex-shrink:0;"></div>\n'
    '    <div>\n'
    '      <div class="cert-header-name" id="qh-domain"></div>\n'
    '      <div class="cert-header-meta" id="qh-cert"></div>\n'
    '    </div>\n'
    '  </div>'
)

# ─────────────────────────────────────────────────────────────
# CORRECAO 2: tela s-quiz — adiciona badge e cert no topbar
# ANTES:
#   <div class="quiz-topbar">
#     <div style="display:flex;align-items:center;gap:12px;">
#       <button class="interrupt-btn" onclick="interruptQuiz()">✕ Interromper</button>
#       <div class="quiz-breadcrumb" id="q-breadcrumb"></div>
#     </div>
# DEPOIS: adiciona badge pequeno antes do breadcrumb
# ─────────────────────────────────────────────────────────────

old2 = (
    '  <div class="quiz-topbar">\n'
    '    <div style="display:flex;align-items:center;gap:12px;">\n'
    '      <button class="interrupt-btn" onclick="interruptQuiz()">✕ Interromper</button>\n'
    '      <div class="quiz-breadcrumb" id="q-breadcrumb"></div>\n'
    '    </div>'
)

new2 = (
    '  <div class="quiz-topbar">\n'
    '    <div style="display:flex;align-items:center;gap:12px;">\n'
    '      <button class="interrupt-btn" onclick="interruptQuiz()">✕ Interromper</button>\n'
    '      <div id="q-badge" style="font-size:22px;flex-shrink:0;opacity:0.85;"></div>\n'
    '      <div class="quiz-breadcrumb" id="q-breadcrumb"></div>\n'
    '    </div>'
)

# ─────────────────────────────────────────────────────────────
# Aplica correcoes
# ─────────────────────────────────────────────────────────────

errors = []

if old1 in html:
    html = html.replace(old1, new1)
    print('OK — badge adicionado na tela s-quizzes')
else:
    errors.append('ERRO — trecho s-quizzes nao encontrado')

if old2 in html:
    html = html.replace(old2, new2)
    print('OK — badge adicionado na tela s-quiz')
else:
    errors.append('ERRO — trecho s-quiz nao encontrado')

if errors:
    for e in errors:
        print(e)
    print('Nenhuma alteracao salva.')
else:
    open('static/index.html', 'w', encoding='utf-8').write(html)
    print()
    print('Arquivo salvo.')
    print()
    print('PROXIMO PASSO:')
    print('Atualizar o JavaScript para popular qh-badge e q-badge')
    print('quando as telas forem carregadas.')
