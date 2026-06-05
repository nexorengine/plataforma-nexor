"""
patch_gerador_quiz2.py — Adiciona carregamento do quiz_002 no gerador
"""
from pathlib import Path

src = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")
content = src.read_text(encoding="utf-8")

# ── PATCH 1: adiciona carregamento dos arquivos quiz_002 ──────────────────────
OLD_LOAD = '''        except Exception as e:
            print(f"  ERRO quiz: {e}")
            falhou.append(dom_id)
            continue
        # Carrega flashcards'''

NEW_LOAD = '''        except Exception as e:
            print(f"  ERRO quiz: {e}")
            falhou.append(dom_id)
            continue
        # Carrega quiz_002 (opcional — se existir)
        q2_en_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_en.json"
        q2_pt_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_pt.json"
        q2_es_path = Path(QUIZZES_DIR) / dom_key / "quiz_002_es.json"
        try:
            if q2_en_path.exists() and q2_pt_path.exists() and q2_es_path.exists():
                q2en = json.load(open(str(q2_en_path), encoding="utf-8"))["questions"]
                q2pt = json.load(open(str(q2_pt_path), encoding="utf-8"))["questions"]
                q2es = json.load(open(str(q2_es_path), encoding="utf-8"))["questions"]
            else:
                q2en, q2pt, q2es = [], [], []
        except Exception as e:
            print(f"  AVISO quiz_002: {e}")
            q2en, q2pt, q2es = [], [], []
        # Carrega flashcards'''

if OLD_LOAD in content:
    content = content.replace(OLD_LOAD, NEW_LOAD)
    print("✓ Patch 1 aplicado — carregamento quiz_002")
else:
    print("ERRO — Patch 1: padrão não encontrado")
    exit(1)

# ── PATCH 2: passa q2en/q2pt/q2es para generate_mini_app ─────────────────────
OLD_CALL = "html = generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64)"
NEW_CALL = "html = generate_mini_app(domain, q1en, q1pt, q1es, q2en, q2pt, q2es, fc_merged, badge_b64)"

if OLD_CALL in content:
    content = content.replace(OLD_CALL, NEW_CALL)
    print("✓ Patch 2 aplicado — chamada generate_mini_app")
else:
    print("ERRO — Patch 2: padrão não encontrado")
    exit(1)

# ── PATCH 3: adiciona q2en/q2pt/q2es na assinatura de generate_mini_app ──────
OLD_DEF = "def generate_mini_app(domain, q1en, q1pt, q1es, fc_merged, badge_b64):"
NEW_DEF = "def generate_mini_app(domain, q1en, q1pt, q1es, q2en, q2pt, q2es, fc_merged, badge_b64):"

if OLD_DEF in content:
    content = content.replace(OLD_DEF, NEW_DEF)
    print("✓ Patch 3 aplicado — assinatura da função")
else:
    print("ERRO — Patch 3: padrão não encontrado")
    exit(1)

# ── PATCH 4: serializa q2 como base64 ────────────────────────────────────────
OLD_B64 = '    fc_b64 = base64.b64encode(json.dumps(fc_merged, ensure_ascii=False).encode()).decode()'
NEW_B64 = '''    q2_b64 = {
        "en": base64.b64encode(json.dumps(q2en, ensure_ascii=False).encode()).decode(),
        "pt": base64.b64encode(json.dumps(q2pt, ensure_ascii=False).encode()).decode(),
        "es": base64.b64encode(json.dumps(q2es, ensure_ascii=False).encode()).decode(),
    }
    fc_b64 = base64.b64encode(json.dumps(fc_merged, ensure_ascii=False).encode()).decode()'''

if OLD_B64 in content:
    content = content.replace(OLD_B64, NEW_B64)
    print("✓ Patch 4 aplicado — serialização base64 quiz_002")
else:
    print("ERRO — Patch 4: padrão não encontrado")
    exit(1)

# ── PATCH 5: substitui QS2 vazio pelo QS2 com dados ─────────────────────────
OLD_QS2 = "var QS2 = {{en:[],pt:[],es:[]}};"
NEW_QS2 = """var QS2 = {{
  en: JSON.parse(utfDecode('{q2_b64["en"]}')),
  pt: JSON.parse(utfDecode('{q2_b64["pt"]}')),
  es: JSON.parse(utfDecode('{q2_b64["es"]}'))
}};"""

if OLD_QS2 in content:
    content = content.replace(OLD_QS2, NEW_QS2)
    print("✓ Patch 5 aplicado — QS2 no template HTML")
else:
    print("ERRO — Patch 5: padrão não encontrado")
    idx = content.find("QS2")
    print(content[max(0,idx-50):idx+150])
    exit(1)

src.write_text(content, encoding="utf-8")
print("\n✅ Todos os patches aplicados — gerador atualizado")
print("Execute: python gerar_mini_apps_cfe_s1d06.py")
