import sys
sys.path.insert(0, r"C:\ARAGORN\aragorn_quiz")

# Patch para mostrar traceback completo
import gerar_mini_apps_cfe as g
import json, traceback
from pathlib import Path

for dom in g.DOMAINS:
    if dom['key'] not in ['data_theft_ip', 'identity_theft_cyberfraud']:
        continue
    
    dom_key = dom['key']
    print(f"\n--- {dom_key} ---")
    
    try:
        fc_en = json.load(open(f"static/flashcards/cfe/{dom_key}/flashcards_en.json", encoding="utf-8"))
        fc_pt = json.load(open(f"static/flashcards/cfe/{dom_key}/flashcards_pt.json", encoding="utf-8"))
        fc_es = json.load(open(f"static/flashcards/cfe/{dom_key}/flashcards_es.json", encoding="utf-8"))
        result = g.merge_fc(fc_en, fc_pt, fc_es)
        print(f"merge_fc OK: {len(result)} cards")
    except Exception as e:
        print("ERRO em merge_fc:")
        traceback.print_exc()
