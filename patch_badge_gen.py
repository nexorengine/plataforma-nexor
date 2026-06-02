#!/usr/bin/env python3
# PATCH - Substitui engrenagem pelo badge da certificadora na tela de geração
# Execute em: C:\NEXOR\nexor_quiz\

from pathlib import Path

f = Path("static/index.html")
c = f.read_text(encoding="utf-8")

# PATCH 1: Tornar o gen-icon dinâmico
old_icon = '<div class="gen-icon">⚙️</div>'
new_icon = '<div class="gen-icon" id="gen-icon">⚙️</div>'

if old_icon in c:
    c = c.replace(old_icon, new_icon)
    print("PATCH 1 OK: gen-icon agora tem id")
else:
    print("PATCH 1 AVISO: gen-icon não encontrado")

# PATCH 2: Atualizar a função generateQuiz para injetar o badge correto
old_gen = """  document.getElementById('gen-num').textContent = '#' + num;
  document.getElementById('gen-sub').textContent = sel.domain.name + ' · ' + sel.cert.name;"""

new_gen = """  document.getElementById('gen-num').textContent = '#' + num;
  document.getElementById('gen-sub').textContent = sel.domain.name + ' · ' + sel.cert.name;
  const certBadge = CERT_BADGES[sel.cert.id];
  if (certBadge) {
    document.getElementById('gen-icon').innerHTML = certBadge;
    document.getElementById('gen-icon').style.fontSize = '0';
  } else {
    document.getElementById('gen-icon').innerHTML = '⚙️';
    document.getElementById('gen-icon').style.fontSize = '';
  }"""

# tenta variações de encoding
variacoes = [
    ("  document.getElementById('gen-num').textContent = '#' + num;\n  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;",
     "  document.getElementById('gen-num').textContent = '#' + num;\n  document.getElementById('gen-sub').textContent = sel.domain.name + ' \u00b7 ' + sel.cert.name;\n  const certBadge = CERT_BADGES[sel.cert.id];\n  if (certBadge) {\n    document.getElementById('gen-icon').innerHTML = certBadge;\n    document.getElementById('gen-icon').style.fontSize = '0';\n  } else {\n    document.getElementById('gen-icon').innerHTML = '\u2699\ufe0f';\n    document.getElementById('gen-icon').style.fontSize = '';\n  }"),
    (old_gen, new_gen),
]

ok = False
for old_v, new_v in variacoes:
    if old_v in c:
        c = c.replace(old_v, new_v)
        print("PATCH 2 OK: badge dinâmico adicionado à função generateQuiz")
        ok = True
        break

if not ok:
    print("PATCH 2 AVISO: bloco generateQuiz não encontrado - verificar manualmente")

# PATCH 3: CSS para o gen-icon exibir SVG corretamente
old_css_target = ".gen-icon{"
new_css_addition = ".gen-icon svg{width:80px;height:80px;display:block;margin:0 auto;}"

if old_css_target in c:
    # adiciona CSS após o bloco gen-icon existente
    idx = c.find(old_css_target)
    end_idx = c.find("}", idx) + 1
    c = c[:end_idx] + new_css_addition + c[end_idx:]
    print("PATCH 3 OK: CSS para SVG no gen-icon adicionado")
else:
    print("PATCH 3 AVISO: .gen-icon CSS não encontrado - badge pode precisar de ajuste de tamanho")

f.write_text(c, encoding="utf-8")
print("\nPATCH BADGE CONCLUÍDO!")
print("Faça Ctrl+Shift+R no navegador para testar.")
