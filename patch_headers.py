"""
patch_headers.py — Atualiza headers das camadas 1 e 3

Camada 1 (index.html): nexor_ → nexor_cert
Camada 3 (mini_apps): adiciona etiqueta CFE 2026 ao lado do nexor_
"""
from pathlib import Path

# ── CAMADA 1 — Portal ────────────────────────────────────────────────────────
portal = Path(r"C:\ARAGORN\aragorn_quiz\index.html")
c = portal.read_text(encoding="utf-8")

old_portal = 'nexor<span>_</span>'
new_portal = 'nexor<span>_</span>cert'

if old_portal in c:
    c = c.replace(old_portal, new_portal)
    portal.write_text(c, encoding="utf-8")
    print("OK Camada 1 — nexor_cert")
else:
    print("ERRO Camada 1 — padrão não encontrado")

# ── CAMADA 3 — Mini-apps ─────────────────────────────────────────────────────
mini_dir = Path(r"C:\ARAGORN\aragorn_quiz\mini_apps\cfe")
ok = skip = 0

for domain_dir in sorted(mini_dir.iterdir()):
    html = domain_dir / "index.html"
    if not html.exists():
        continue
    c = html.read_text(encoding="utf-8")

    # Verifica se já tem cert-badge
    if 'cert-badge' in c:
        skip += 1
        continue

    # Adiciona CFE 2026 badge após o logo
    old_logo = '<div class="logo">NEXOR<span class="logo-dot">_</span></div>'
    new_logo = '<div class="logo">NEXOR<span class="logo-dot">_</span></div>\n    <div class="cert-badge">CFE 2026</div>'

    if old_logo in c:
        # Adiciona CSS do cert-badge se não existir
        if 'cert-badge{' not in c and '.cert-badge{' not in c:
            css_inject = '.cert-badge{font-size:11px;font-weight:600;padding:3px 8px;border-radius:5px;background:rgba(255,255,255,0.2);color:#FFF;letter-spacing:0.06em}'
            c = c.replace('</style>', css_inject + '\n</style>', 1)

        c = c.replace(old_logo, new_logo)
        html.write_text(c, encoding="utf-8")
        ok += 1
    else:
        skip += 1

print(f"OK Camada 3 — {ok} mini-apps atualizados · {skip} pulados")
