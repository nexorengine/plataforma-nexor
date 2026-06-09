"""
patch_lote_gerador.py
Adiciona suporte a --lote no gerar_mini_apps_cfe.py
Uso: python patch_lote_gerador.py
"""

from pathlib import Path

TARGET = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")

# Backup
bak = TARGET.with_suffix(".py.bak_prelote")
if not bak.exists():
    bak.write_bytes(TARGET.read_bytes())
    print(f"Backup salvo: {bak}")

content = TARGET.read_text(encoding="utf-8")

# Verifica se ja foi patchado
if "--lote" in content:
    print("Ja patchado. Nada a fazer.")
    exit(0)

# Localiza o bloco "if __name__ == '__main__':" e substitui
old_main = 'if __name__ == "__main__":\n    main()'
new_main = '''if __name__ == "__main__":
    import sys
    lote_num = None
    if "--lote" in sys.argv:
        idx = sys.argv.index("--lote")
        lote_num = int(sys.argv[idx + 1])

    LOTE_SIZE = 10
    if lote_num is not None:
        inicio = (lote_num - 1) * LOTE_SIZE
        fim    = inicio + LOTE_SIZE
        dominios_rodar = DOMAINS[inicio:fim]
        print(f"LOTE {lote_num}: dominios {inicio+1}-{min(fim, len(DOMAINS))} de {len(DOMAINS)}")
    else:
        dominios_rodar = DOMAINS

    # Sobrescreve DOMAINS temporariamente para main() usar o subset
    _orig = DOMAINS[:]
    DOMAINS.clear()
    DOMAINS.extend(dominios_rodar)
    main()
    DOMAINS.clear()
    DOMAINS.extend(_orig)'''

if old_main in content:
    content = content.replace(old_main, new_main)
    TARGET.write_text(content, encoding="utf-8")
    print("Patch aplicado com sucesso.")
else:
    # Tenta variacao com aspas simples
    old_main2 = "if __name__ == '__main__':\n    main()"
    if old_main2 in content:
        content = content.replace(old_main2, new_main)
        TARGET.write_text(content, encoding="utf-8")
        print("Patch aplicado com sucesso (aspas simples).")
    else:
        print("AVISO: padrao nao encontrado. Adicionando ao final do arquivo.")
        content += "\n\n" + new_main
        TARGET.write_text(content, encoding="utf-8")
        print("Adicionado ao final.")

print("Pronto. Use: python gerar_mini_apps_cfe.py --lote 1")
