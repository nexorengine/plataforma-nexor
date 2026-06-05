"""
fix_strings_gerador.py
Corrige double-encoding (mojibake) no gerar_mini_apps_cfe.py.
Lê o arquivo como bytes, aplica substituições binárias precisas, salva UTF-8 limpo.
"""

import shutil
from pathlib import Path

SRC = Path("gerar_mini_apps_cfe.py")
BAK = Path("gerar_mini_apps_cfe.py.bak")

# Mapeamento binário: bytes corrompidos → bytes UTF-8 corretos
# Derivado da análise do arquivo real (double-encoding Latin-1 sobre UTF-8)
REPLACEMENTS = [
    # ─── sequências 4-byte (mais específicas primeiro) ───────────────────────
    (b'\xc3\x83\xc2\xb5',  'õ'.encode()),   # õ  (questões)
    (b'\xc3\x83\xc2\xa7',  'ç'.encode()),   # ç  (Seção)
    (b'\xc3\x83\xc2\xa3',  'ã'.encode()),   # ã  (Não, Seção)
    (b'\xc3\x83\xc2\xad',  'í'.encode()),   # í  (trilíngue, concluído)
    (b'\xc3\x83\xc2\xb3',  'ó'.encode()),   # ó  (Sección, próxima)
    (b'\xc3\x83\xc2\xa9',  'é'.encode()),   # é  (sé)
    (b'\xc3\x83\xc2\xba',  'ú'.encode()),   # ú  (ningún)
    (b'\xc3\x83\xc2\x81',  'Á'.encode()),   # Á  (DISTRÁTORES)
    (b'\xc3\x83\xe2\x80\x9c', 'Ó'.encode()), # Ó  (HISTÓRICO, JUSTIFICACIÓN)
    (b'\xc3\x83\xc2\x8d',  'Í'.encode()),   # Í  (NÍVEL, DOMÍNIO)

    # ─── sequências 3-byte ───────────────────────────────────────────────────
    (b'\xc3\x82\xc2\xb7',  '·'.encode()),   # ·  (bullet middle dot)
    (b'\xc3\x82\xc2\xa1',  '¡'.encode()),   # ¡  (¡Correcto!)
    (b'\xc3\x82\xc2\xa5',  '¥'.encode()),   # ¥  (≥ parte — ver abaixo)

    # ─── sequências de símbolos especiais ────────────────────────────────────
    # — (em dash U+2014): \xc3\xa2\xe2\x82\xac\xe2\x80\x9d
    (b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', '—'.encode()),
    # ✓ (check mark U+2713): \xc3\xa2\xc5\x93\xe2\x80\x9c
    (b'\xc3\xa2\xc5\x93\xe2\x80\x9c', '✓'.encode()),
    # ✗ (ballot X U+2717): \xc3\xa2\xc5\x93\xe2\x80\x94
    (b'\xc3\xa2\xc5\x93\xe2\x80\x94', '✗'.encode()),
    # ≥ (U+2265): \xc3\xa2\xe2\x80\xb0\xc2\xa5
    (b'\xc3\xa2\xe2\x80\xb0\xc2\xa5', '≥'.encode()),
    # ★ (U+2605): \xc3\xa2\xcb\x9c\xe2\x80\xa6
    (b'\xc3\xa2\xcb\x9c\xe2\x80\xa6', '★'.encode()),
    # ☆ (U+2606): \xc3\xa2\xcb\x9c\xe2\x80\xa0
    (b'\xc3\xa2\xcb\x9c\xe2\x80\xa0', '☆'.encode()),
    # → (U+2192): \xc3\xa2\xe2\x80\xa0\xe2\x80\x99
    (b'\xc3\xa2\xe2\x80\xa0\xe2\x80\x99', '→'.encode()),
    # ═ ou ─ (box drawing): \xc3\xa2\xe2\x80\xa2\xc2\x90
    (b'\xc3\xa2\xe2\x80\xa2\xc2\x90', '═'.encode()),
]

def fix():
    if not SRC.exists():
        print(f"ERRO: {SRC} não encontrado. Execute no diretório C:\\ARAGORN\\aragorn_quiz")
        return

    # Backup
    shutil.copy2(SRC, BAK)
    print(f"Backup criado: {BAK}")

    raw = SRC.read_bytes()
    original_size = len(raw)

    total_fixes = 0
    for bad, good in REPLACEMENTS:
        count = raw.count(bad)
        if count:
            raw = raw.replace(bad, good)
            print(f"  {count:3d}x  {bad.hex()} → {good.decode('utf-8')!r}")
            total_fixes += count

    SRC.write_bytes(raw)
    print(f"\nTotal substituições: {total_fixes}")
    print(f"Tamanho: {original_size} → {len(raw)} bytes")
    print("\nVerificando resultado...")

    # Verificação
    text = SRC.read_text(encoding='utf-8')
    checks = [
        ('questões', '·', 'NÍVEL', 'Seção', '≥', '✓', '✗', '★', '☆', '→', '—')
    ]
    for term in checks[0]:
        status = '✓' if term in text else '✗ AUSENTE'
        print(f"  {status}  {term!r}")

    # Checa se ainda há bytes suspeitos
    remaining = raw.count(b'\xc3\x82') + raw.count(b'\xc3\x83\xc2')
    if remaining:
        print(f"\nATENÇÃO: ainda há {remaining} ocorrências suspeitas — revise manualmente")
    else:
        print("\nArquivo limpo. Nenhum byte suspeito restante.")

if __name__ == "__main__":
    fix()
