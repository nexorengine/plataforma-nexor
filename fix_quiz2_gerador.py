"""
fix_quiz2_gerador.py — Adiciona quiz_002 ao gerador de mini-apps
"""
from pathlib import Path
import json, base64

src = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")
c = src.read_text(encoding="utf-8")
original = c

# PATCH 1 — adiciona carregamento quiz_002
old1 = '            continue\n\n        # Carrega flashcards'
new1 = '''            continue\n\n        # Carrega quiz_002 (opcional)\n        q2_en_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_en.json"\n        q2_pt_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_pt.json"\n        q2_es_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_es.json"\n        try:\n            if q2_en_path.exists() and q2_pt_path.exists() and q2_es_path.exists():\n                q2en = json.load(open(str(q2_en_path), encoding="utf-8"))["questions"]\n                q2pt = json.load(open(str(q2_pt_path), encoding="utf-8"))["questions"]\n                q2es = json.load(open(str(q2_es_path), encoding="utf-8"))["questions"]\n            else:\n                q2en, q2pt, q2es = [], [], []\n        except Exception as e:\n            print(f"  AVISO quiz_002: {e}")\n            q2en, q2pt, q2es = [], [], []\n\n        # Carrega flashcards'''

if old1 in c:
    c = c.replace(old1, new1)
    print("OK Patch 1")
else:
    print("ERRO Patch 1 — padrão não encontrado")
    exit(1)

# PATCH 2 — assinatura da função
old2 = "def generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64):"
new2 = "def generate_mini_app(domain, q1en, q1pt, q1es, q2en, q2pt, q2es, fc_merged, badge_b64):"
if old2 in c:
    c = c.replace(old2, new2)
    print("OK Patch 2")
else:
    print("ERRO Patch 2")
    exit(1)

# PATCH 3 — chamada da função
old3 = "html = generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64)"
new3 = "html = generate_mini_app(domain, q1en, q1pt, q1es, q2en, q2pt, q2es, fc_merged, badge_b64)"
if old3 in c:
    c = c.replace(old3, new3)
    print("OK Patch 3")
else:
    print("ERRO Patch 3")
    exit(1)

# PATCH 4 — serialização base64
old4 = '    fc_b64 = base64.b64encode(json.dumps(fc_merged, ensure_ascii=False).encode()).decode()'
new4 = '''    q2_b64 = {
        "en": base64.b64encode(json.dumps(q2en, ensure_ascii=False).encode()).decode(),
        "pt": base64.b64encode(json.dumps(q2pt, ensure_ascii=False).encode()).decode(),
        "es": base64.b64encode(json.dumps(q2es, ensure_ascii=False).encode()).decode(),
    }
    fc_b64 = base64.b64encode(json.dumps(fc_merged, ensure_ascii=False).encode()).decode()'''
if old4 in c:
    c = c.replace(old4, new4)
    print("OK Patch 4")
else:
    print("ERRO Patch 4")
    exit(1)

# PATCH 5 — template QS2
old5 = "var QS2 = {{en:[],pt:[],es:[]}};"
new5 = """var QS2 = {{
  en: JSON.parse(utfDecode('{q2_b64["en"]}')),
  pt: JSON.parse(utfDecode('{q2_b64["pt"]}')),
  es: JSON.parse(utfDecode('{q2_b64["es"]}'))
}};"""
if old5 in c:
    c = c.replace(old5, new5)
    print("OK Patch 5")
else:
    print("ERRO Patch 5")
    idx = c.find("QS2")
    print(repr(c[max(0,idx-20):idx+100]))
    exit(1)

src.write_text(c, encoding="utf-8")
print("\nTodos os patches aplicados!")
print("Agora execute: python gerar_mini_apps_cfe_s1d06.py")
