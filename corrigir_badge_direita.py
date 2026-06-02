f = open('static/index.html', encoding='utf-8')
html = f.read()
f.close()

# ─────────────────────────────────────────────────────────────
# CORRECAO: move qh-badge para o lado direito
# ANTES: badge antes do texto (esquerda)
# DEPOIS: badge depois do texto (direita) com margin-left:auto
# ─────────────────────────────────────────────────────────────

old = (
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

new = (
    '<div class="screen" id="s-quizzes">\n'
    '  <button class="back-btn" onclick="goTo(\'s-domains\')">← DOMÍNIOS</button>\n'
    '  <div class="cert-header">\n'
    '    <div>\n'
    '      <div class="cert-header-name" id="qh-domain"></div>\n'
    '      <div class="cert-header-meta" id="qh-cert"></div>\n'
    '    </div>\n'
    '    <div id="qh-badge" style="font-size:42px;margin-left:auto;flex-shrink:0;opacity:0.9;"></div>\n'
    '  </div>'
)

if old in html:
    html = html.replace(old, new)
    open('static/index.html', 'w', encoding='utf-8').write(html)
    print('OK — badge movido para o lado direito')
else:
    print('ERRO — trecho nao encontrado')
