"""
patch_med_paths.py
Corrige paths dos mini-apps MED diretamente nos HTMLs gerados
"""
import os
import glob

MINI_BASE = r"C:\ARAGORN\aragorn_quiz\static\mini_apps\med\cirurgia_geral"

REPLACEMENTS = [
    # Badge path
    ('src="../../badges/med/cirurgia_geral/', 'src="../../../../badges/med/cirurgia_geral/'),
    # Botão voltar header
    ('href="../../index.html" class="hdr-back" id="hdr-back-btn"', 
     'href="../../../../med/cirurgia_geral/index.html" class="hdr-back" id="hdr-back-btn"'),
    # JS — botão voltar dinâmico menu
    ("hb.href='../../index.html'", "hb.href='../../../../med/cirurgia_geral/index.html'"),
    ('hb.href="../../index.html"', 'hb.href="../../../../med/cirurgia_geral/index.html"'),
    # Botão Domínios no scorecard
    ('href="../../index.html" class="btn"', 
     'href="../../../../med/cirurgia_geral/index.html" class="btn"'),
]

DOMINIOS = [
    "abdome_agudo","hepatobiliar","trauma","perioperatorio","hernias",
    "tgi_superior","tgi_inferior","vascular","queimaduras"
]

def main():
    print("="*50)
    print("PATCH — Corrigindo paths dos mini-apps MED")
    print("="*50)

    for dominio in DOMINIOS:
        path = os.path.join(MINI_BASE, dominio, "index.html")
        if not os.path.exists(path):
            print(f"  NAO ENCONTRADO: {path}")
            continue

        with open(path, encoding="utf-8") as f:
            content = f.read()

        original = content
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)

        if content != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  CORRIGIDO: {dominio}")
        else:
            print(f"  SEM MUDANCA: {dominio}")

    print("\nCONCLUIDO.")

if __name__ == "__main__":
    main()
