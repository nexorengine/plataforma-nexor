import json, traceback
from pathlib import Path

FLASHCARD_DIR = r"static\flashcards\cfe"

def merge_fc(fc_en, fc_pt, fc_es):
    merged = []
    cards_en = fc_en.get("cards", [])
    cards_pt = fc_pt.get("cards", [])
    cards_es = fc_es.get("cards", [])
    for i, card in enumerate(cards_en):
        topic = card["topic"]
        c_pt = cards_pt[i] if i < len(cards_pt) else {}
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
        })
    return merged

for dom in ['data_theft_ip', 'identity_theft_cyberfraud']:
    print(f"\n--- {dom} ---")
    try:
        fc_en = json.load(open(f'{FLASHCARD_DIR}\\{dom}\\flashcards_en.json', encoding='utf-8'))
        fc_pt = json.load(open(f'{FLASHCARD_DIR}\\{dom}\\flashcards_pt.json', encoding='utf-8'))
        fc_es = json.load(open(f'{FLASHCARD_DIR}\\{dom}\\flashcards_es.json', encoding='utf-8'))
        result = merge_fc(fc_en, fc_pt, fc_es)
        print(f"OK — {len(result)} cards merged")
        print(f"Card 1: {result[0]['front']}")
    except Exception as e:
        traceback.print_exc()
