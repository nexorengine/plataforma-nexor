import sys, json, base64, traceback
from pathlib import Path
sys.path.insert(0, r"C:\ARAGORN\aragorn_quiz")
import gerar_mini_apps_cfe as g

QUIZZES_DIR = r"static\quizzes\cfe"
FLASHCARD_DIR = r"static\flashcards\cfe"
BADGES_DIR = r"static\badges\cfe"

for dom in g.DOMAINS:
    if dom['key'] not in ['data_theft_ip', 'identity_theft_cyberfraud']:
        continue
    
    dom_key = dom['key']
    dom_id = dom['id']
    print(f"\n--- {dom_key} ---")
    
    try:
        q1en = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_001_en.json", encoding="utf-8"))["questions"]
        q1pt = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_001_pt.json", encoding="utf-8"))["questions"]
        q1es = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_001_es.json", encoding="utf-8"))["questions"]
        print(f"quiz_001 OK: en={len(q1en)} pt={len(q1pt)} es={len(q1es)}")
        
        q2en = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_002_en.json", encoding="utf-8"))["questions"]
        q2pt = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_002_pt.json", encoding="utf-8"))["questions"]
        q2es = json.load(open(f"{QUIZZES_DIR}\\{dom_key}\\quiz_002_es.json", encoding="utf-8"))["questions"]
        print(f"quiz_002 OK: en={len(q2en)} pt={len(q2pt)} es={len(q2es)}")
        
        fc_en = json.load(open(f"{FLASHCARD_DIR}\\{dom_key}\\flashcards_en.json", encoding="utf-8"))
        fc_pt = json.load(open(f"{FLASHCARD_DIR}\\{dom_key}\\flashcards_pt.json", encoding="utf-8"))
        fc_es = json.load(open(f"{FLASHCARD_DIR}\\{dom_key}\\flashcards_es.json", encoding="utf-8"))
        fc_merged = g.merge_fc(fc_en, fc_pt, fc_es)
        print(f"flashcards OK: {len(fc_merged)} cards")
        
        # Badge
        sec = dom["section"]
        badge_fname = f"CFE_SID{dom_id[-2:]}.png" if sec == 1 else f"CFE_{dom['code']}.png"
        badge_path = Path(BADGES_DIR) / badge_fname
        badge_b64 = base64.b64encode(badge_path.read_bytes()).decode() if badge_path.exists() else ""
        print(f"badge: {'OK' if badge_b64 else 'NAO ENCONTRADO'} ({badge_fname})")
        
        html = g.generate_mini_app(dom, q1en, q1pt, q1es, q2en, q2pt, q2es, fc_merged, badge_b64)
        print(f"HTML gerado: {len(html):,} chars")
        
    except Exception as e:
        print(f"ERRO:")
        traceback.print_exc()
