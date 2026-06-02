#!/usr/bin/env python3
from pathlib import Path
import re

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# Remove o bloco dh-version do HTML (patch_barra_flex)
# e restaura o HTML simples do cert-header
old_html = '''    <div style="display:flex;align-items:stretch;gap:0;">
      <div style="flex:1;">
        <div class="cert-header-name" id="dh-name"></div>
        <div class="cert-header-meta" id="dh-meta"></div>
      </div>
      <div id="dh-version" style="display:none;align-items:flex-end;gap:10px;padding-left:20px;">
        <div style="width:1px;background:#ffffff;opacity:0.3;align-self:stretch;margin-right:2px;"></div>
        <span id="dh-version-text" style="color:#ffffff;font-size:10px;font-weight:300;opacity:0.6;letter-spacing:0.5px;white-space:nowrap;padding-bottom:1px;"></span>
      </div>
    </div>'''

new_html = '''    <div>
      <div class="cert-header-name" id="dh-name"></div>
      <div class="cert-header-meta" id="dh-meta"></div>
    </div>'''

if old_html in c:
    c = c.replace(old_html, new_html)
    f.write_text(c, encoding="utf-8")
    print("OK - dh-version removido, HTML restaurado")
else:
    # tenta encontrar padrão aproximado
    idx = c.find('dh-version')
    if idx > 0:
        print(f"dh-version encontrado na posição {idx}")
        print(repr(c[max(0,idx-200):idx+300]))
    else:
        print("dh-version não encontrado no HTML")
