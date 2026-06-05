"""
fix_merge_fc.py — Corrige merge_fc no gerador para tratar cards vazios
"""
from pathlib import Path

src = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")
c = src.read_text(encoding="utf-8")

OLD = '''        c_pt = cards_pt[i] if i < len(cards_pt) else {}
        c_es = cards_es[i] if i < len(cards_es) else {}
        merged.append({
            "id": card["id"],
            "topic": topic,
            "front": {
                "en": card["front"].get("en", ""),
                "pt": c_pt["front"].get("pt", ""),
                "es": c_es["front"].get("es", "")
            },
            "back": {
                "en": card["back"].get("en", ""),
                "pt": c_pt["back"].get("pt", ""),
                "es": c_es["back"].get("es", "")
            }
        })'''

NEW = '''        c_pt = cards_pt[i] if i < len(cards_pt) else {}
        c_es = cards_es[i] if i < len(cards_es) else {}
        merged.append({
            "id": card["id"],
            "topic": topic,
            "front": {
                "en": card.get("front", {}).get("en", ""),
                "pt": c_pt.get("front", {}).get("pt", ""),
                "es": c_es.get("front", {}).get("es", "")
            },
            "back": {
                "en": card.get("back", {}).get("en", ""),
                "pt": c_pt.get("back", {}).get("pt", ""),
                "es": c_es.get("back", {}).get("es", "")
            }
        })'''

if OLD in c:
    c = c.replace(OLD, NEW)
    src.write_text(c, encoding="utf-8")
    print("OK — merge_fc corrigido")
else:
    print("ERRO — padrão não encontrado")
