"""
fix_template_strings.py — Corrige strings corrompidas no template do gerador
"""
from pathlib import Path

src = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")
c = src.read_text(encoding="utf-8")

replacements = [
    # Ponto médio
    ("Â·", "·"),
    # Português
    ("questÃµes", "questões"),
    ("SeÃ§Ã£o", "Seção"),
    ("SecciÃ³n", "Sección"),
    ("ConcluÃ­do em", "Concluído em"),
    ("NÃ£o sei", "Não sei"),
    ("PrÃ³xima", "Próxima"),
    ("Â¡Correcto!", "¡Correcto!"),
    ("Â¡Incorreto", "¡Incorrecto"),
    ("Â¡Insignia", "¡Insignia"),
    ("Â¡Obtenida!", "¡Obtenida!"),
    ("obteniÃ³n", "obtención"),
    ("FormaciÃ³n", "Formación"),
    ("HistÃ"RICO", "HISTORIAL"),
    ("HISTÃ"RICO", "HISTORIAL"),
    ("NingÃºn", "Ningún"),
    ("todavÃ­a", "todavía"),
    ("Ã©", "é"),
    ("Ã£", "ã"),
    ("Ã§", "ç"),
    ("Ã³", "ó"),
    ("Ãº", "ú"),
    ("Ã¡", "á"),
    ("Ã­", "í"),
    ("ÃÃ", "Ã"),
    ("â˜…", "★"),
    ("â˜†", "☆"),
    ("âœ"", "✓"),
    ("âœ—", "✗"),
    ("â€"", "—"),
    ("â€™", "'"),
    ("â‰¥", "≥"),
    ("NÃVEL", "NÍVEL"),
    ("NÍVEL", "NÍVEL"),
    ("DESEMPENHO POR DIFICULDADE", "DESEMPENHO POR DIFICULDADE"),
    ("HISTÃ"RICO", "HISTÓRICO"),
    ("HISTÃ"RICO DE TENTATIVAS", "HISTÓRICO DE TENTATIVAS"),
    ("BADGE DO DOMÃNIO", "BADGE DO DOMÍNIO"),
    ("DOMÃNIO", "DOMÍNIO"),
    ("DISTRÃTORES", "DISTRATORES"),
    ("JUSTIFICATIVA", "JUSTIFICATIVA"),
    ("Candidato em FormaciÃ³n", "Candidato en Formación"),
    ("Candidato en Progreso", "Candidato en Progreso"),
    ("JUSTIFICAÃšÃO", "JUSTIFICAÇÃO"),
    ("JUSTIFICACIÃ"N", "JUSTIFICACIÓN"),
    ("nohist:'Nenhuma tentativa ainda'", "nohist:'Nenhuma tentativa ainda'"),
    ("Â·", "·"),  # segunda passagem
]

count = 0
for old, new in replacements:
    if old in c and old != new:
        c = c.replace(old, new)
        count += 1
        print(f"  ✓ '{old}' → '{new}'")

src.write_text(c, encoding="utf-8")
print(f"\nTotal substituições: {count}")
print("Verificando resultado...")

# Verifica se ainda tem corrompidos
for old, new in replacements:
    if old in c and old != new:
        print(f"  AINDA TEM: '{old}'")
