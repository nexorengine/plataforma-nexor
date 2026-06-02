#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# PATCH 1: Reestruturar o cert-header para usar flexbox no bloco de texto+versão
# Antes: [icon] [div > [name] [meta]]
# Depois: [icon] [div.name-block > [name]] [div.version-block > [bar] [version-text]]

# Localiza e modifica a função selectCert no JS
old_js = """  document.getElementById('dh-icon').innerHTML = badgeSvg || sel.cert.icon;
  document.getElementById('dh-name').textContent = sel.cert.name;
  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios`;"""

new_js = """  document.getElementById('dh-icon').innerHTML = badgeSvg || sel.cert.icon;
  document.getElementById('dh-name').textContent = sel.cert.name;
  document.getElementById('dh-meta').textContent = `${sel.cert.exam_minutes} min · ${sel.cert.exam_questions} questões · ${sel.cert.domains.length} domínios`;
  const dhVersion = document.getElementById('dh-version');
  if (dhVersion) {
    dhVersion.style.display = sel.cert.version ? 'flex' : 'none';
    const dhVersionText = document.getElementById('dh-version-text');
    if (dhVersionText) dhVersionText.textContent = sel.cert.version || '';
  }"""

variacoes_js = [
    (old_js, new_js),
    (old_js.replace('·', '\u00b7'), new_js),
    (old_js.replace('questões', 'quest\u00f5es').replace('domínios', 'dom\u00ednios'), new_js),
]

ok1 = False
for old_v, new_v in variacoes_js:
    if old_v in c:
        c = c.replace(old_v, new_v)
        print("PATCH 1 OK: JS atualizado")
        ok1 = True
        break

if not ok1:
    print("PATCH 1 AVISO: padrão JS não encontrado - verificar manualmente")

# PATCH 2: Atualizar HTML - adicionar div#dh-version ao lado do bloco de nome/meta
old_html = '''    <div>
      <div class="cert-header-name" id="dh-name"></div>
      <div class="cert-header-meta" id="dh-meta"></div>
    </div>'''

new_html = '''    <div style="display:flex;align-items:stretch;flex:1;gap:0;">
      <div style="flex:1;">
        <div class="cert-header-name" id="dh-name"></div>
        <div class="cert-header-meta" id="dh-meta"></div>
      </div>
      <div id="dh-version" style="display:none;align-items:flex-end;gap:10px;padding-left:4px;">
        <div style="width:1px;background:#ffffff;opacity:0.3;align-self:stretch;margin-right:2px;"></div>
        <span id="dh-version-text" style="color:#ffffff;font-size:10px;font-weight:300;opacity:0.6;letter-spacing:0.5px;white-space:nowrap;padding-bottom:1px;"></span>
      </div>
    </div>'''

if old_html in c:
    c = c.replace(old_html, new_html)
    print("PATCH 2 OK: HTML reestruturado com barra flex")
else:
    print("PATCH 2 AVISO: HTML não encontrado")

f.write_text(c, encoding="utf-8")
print("\nPATCH CONCLUÍDO - Ctrl+Shift+R")
