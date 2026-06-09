"""
sync_e_gerar_lote.py
1. Copia flashcards PT+EN retrofitados de flashcards/cfe/ para static/flashcards/cfe/
2. Roda gerar_mini_apps_cfe.py em lotes de 10 dominios

Uso:
    python sync_e_gerar_lote.py            -> roda todos os lotes
    python sync_e_gerar_lote.py --lote 1   -> roda so o lote 1 (dominios 1-10)
    python sync_e_gerar_lote.py --lote 2   -> roda so o lote 2 (dominios 11-20)
    python sync_e_gerar_lote.py --lote 3   -> roda so o lote 3 (dominios 21-30)
    python sync_e_gerar_lote.py --lote 4   -> roda so o lote 4 (dominios 31-40)
    python sync_e_gerar_lote.py --lote 5   -> roda so o lote 5 (dominios 41-45)
"""

import os, sys, shutil, json, base64
from pathlib import Path
from datetime import datetime

# â•â•â• DIRS â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
BASE          = Path(r"C:\ARAGORN\aragorn_quiz")
SRC_FC        = BASE / "flashcards" / "cfe"
DST_FC        = BASE / "static" / "flashcards" / "cfe"
QUIZZES_DIR   = BASE / "quizzes" / "cfe"
BADGES_DIR    = BASE / "static" / "badges" / "cfe"
OUTPUT_DIR    = BASE / "mini_apps" / "cfe"

# â•â•â• DOMINIOS (ordem original do gerador) â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
DOMAINS = [
    {"id":"s1d01","key":"accounting_concepts",        "code":"S1D01","section":1,"name":"Accounting Concepts & Financial Analysis"},
    {"id":"s1d02","key":"financial_statement_fraud",  "code":"S1D02","section":1,"name":"Financial Statement Fraud"},
    {"id":"s1d03","key":"cash_receipts_fraud",        "code":"S1D03","section":1,"name":"Asset Misappropriation â€“ Cash Receipts"},
    {"id":"s1d04","key":"fraudulent_disbursements",   "code":"S1D04","section":1,"name":"Asset Misappropriation â€“ Disbursements"},
    {"id":"s1d05","key":"inventory_fraud",            "code":"S1D05","section":1,"name":"Asset Misappropriation â€“ Inventory & Assets"},
    {"id":"s1d06","key":"corruption_bribery",         "code":"S1D06","section":1,"name":"Corruption & Bribery"},
    {"id":"s1d07","key":"data_theft_ip",              "code":"S1D07","section":1,"name":"Theft of Data & Intellectual Property"},
    {"id":"s1d08","key":"identity_theft_cyberfraud",  "code":"S1D08","section":1,"name":"Identity Theft & Cyberfraud"},
    {"id":"s1d09","key":"financial_institution_fraud","code":"S1D09","section":1,"name":"Financial Institution Fraud & Money Laundering"},
    {"id":"s1d10","key":"securities_fraud",           "code":"S1D10","section":1,"name":"Securities & Investment Fraud"},
    {"id":"s1d11","key":"payment_fraud",              "code":"S1D11","section":1,"name":"Payment Fraud"},
    {"id":"s1d12","key":"insurance_fraud",            "code":"S1D12","section":1,"name":"Insurance Fraud"},
    {"id":"s1d13","key":"consumer_fraud",             "code":"S1D13","section":1,"name":"Consumer Fraud & Scams"},
    {"id":"s1d14","key":"bankruptcy_fraud",           "code":"S1D14","section":1,"name":"Bankruptcy Fraud"},
    {"id":"s1d15","key":"tax_fraud",                  "code":"S1D15","section":1,"name":"Tax Fraud"},
    {"id":"s1d16","key":"healthcare_fraud",           "code":"S1D16","section":1,"name":"Health Care Fraud"},
    {"id":"s1d17","key":"government_fraud",           "code":"S1D17","section":1,"name":"Government & Public Sector Fraud"},
    {"id":"s1d18","key":"procurement_contract_fraud", "code":"S1D18","section":1,"name":"Procurement & Contract Fraud"},
    {"id":"s1d19","key":"international_fraud",        "code":"S1D19","section":1,"name":"International & Cross-Border Fraud"},
    {"id":"s1d20","key":"emerging_fraud",             "code":"S1D20","section":1,"name":"Emerging Fraud & Technology"},
    {"id":"s2d01","key":"investigation_planning",     "code":"S2D01","section":2,"name":"Planning & Conducting Fraud Examination"},
    {"id":"s2d02","key":"legal_issues_investigations","code":"S2D02","section":2,"name":"Legal Issues in Investigations"},
    {"id":"s2d03","key":"law_cfe",                    "code":"S2D03","section":2,"name":"Law Related to Fraud"},
    {"id":"s2d04","key":"legal_system_overview",      "code":"S2D04","section":2,"name":"Overview of the Legal System"},
    {"id":"s2d05","key":"criminal_prosecutions",      "code":"S2D05","section":2,"name":"Criminal Prosecutions"},
    {"id":"s2d06","key":"non_criminal_actions",       "code":"S2D06","section":2,"name":"Non-Criminal Actions"},
    {"id":"s2d07","key":"individual_rights",          "code":"S2D07","section":2,"name":"Individual Rights During Examinations"},
    {"id":"s2d08","key":"evidence_principles",        "code":"S2D08","section":2,"name":"Basic Principles of Evidence"},
    {"id":"s2d09","key":"collecting_evidence",        "code":"S2D09","section":2,"name":"Collecting Evidence"},
    {"id":"s2d10","key":"sources_information",        "code":"S2D10","section":2,"name":"Sources of Information"},
    {"id":"s2d11","key":"data_analysis_tools",        "code":"S2D11","section":2,"name":"Data Analysis Tools & Techniques"},
    {"id":"s2d12","key":"tracing_assets",             "code":"S2D12","section":2,"name":"Tracing Illicit Transactions"},
    {"id":"s2d13","key":"interview_techniques",       "code":"S2D13","section":2,"name":"Interview Techniques"},
    {"id":"s2d14","key":"covert_operations",          "code":"S2D14","section":2,"name":"Covert Operations"},
    {"id":"s2d15","key":"report_writing",             "code":"S2D15","section":2,"name":"Report Writing"},
    {"id":"s2d16","key":"expert_witness",             "code":"S2D16","section":2,"name":"Expert Witness"},
    {"id":"s3d01","key":"criminal_behavior",          "code":"S3D01","section":3,"name":"Criminal Behavior & Psychology"},
    {"id":"s3d02","key":"occupational_fraud",         "code":"S3D02","section":3,"name":"Occupational Fraud"},
    {"id":"s3d03","key":"corporate_governance",       "code":"S3D03","section":3,"name":"Corporate Governance & Ethics"},
    {"id":"s3d04","key":"auditor_responsibilities",   "code":"S3D04","section":3,"name":"Auditor Responsibilities"},
    {"id":"s3d05","key":"fraud_risk_assessment",      "code":"S3D05","section":3,"name":"Fraud Risk Assessment"},
    {"id":"s3d06","key":"prevention_deterrence",      "code":"S3D06","section":3,"name":"Fraud Prevention & Deterrence"},
    {"id":"s3d07","key":"fraud_prevention_programs",  "code":"S3D07","section":3,"name":"Fraud Prevention Programs"},
    {"id":"s3d08","key":"fraud_risk_management",      "code":"S3D08","section":3,"name":"Fraud Risk Management"},
    {"id":"s3d09","key":"ethics_fraud_examiners",     "code":"S3D09","section":3,"name":"Ethics for Fraud Examiners"},
]

LOTE_SIZE = 10
LOTES = [DOMAINS[i:i+LOTE_SIZE] for i in range(0, len(DOMAINS), LOTE_SIZE)]


# â•â•â• STEP 1: SYNC FLASHCARDS â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def sync_flashcards(domains):
    print("\nâ”€â”€ SYNC FLASHCARDS (flashcards/cfe â†’ static/flashcards/cfe) â”€â”€")
    for d in domains:
        key = d["key"]
        src = SRC_FC / key
        dst = DST_FC / key
        if not src.exists():
            print(f"  AVISO: {key} nao encontrado em src")
            continue
        dst.mkdir(parents=True, exist_ok=True)
        for lang in ["pt", "en"]:
            src_file = src / f"flashcards_{lang}.json"
            dst_file = dst / f"flashcards_{lang}.json"
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"  sync {key} [{lang}] OK")
            else:
                print(f"  AVISO: {src_file} nao encontrado")


# â•â•â• STEP 2: GERAR MINI-APPS â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def load_json_safe(path):
    with open(str(path), encoding="utf-8") as f:
        return json.load(f)

def merge_fc(fc_en, fc_pt):
    """Merge PT + EN nos cards (sem ES)"""
    cards_merged = []
    pt_map = {c["id"]: c for c in fc_pt.get("cards", [])}
    en_map = {c["id"]: c for c in fc_en.get("cards", [])}
    all_ids = sorted(set(list(pt_map.keys()) + list(en_map.keys())))
    for cid in all_ids:
        c_pt = pt_map.get(cid, {})
        c_en = en_map.get(cid, {})
        card = {
            "id": cid,
            "layer": c_pt.get("layer") or c_en.get("layer", "F1"),
            "topic": c_pt.get("topic") or c_en.get("topic", ""),
            "front": {
                "pt": (c_pt.get("front") or {}).get("pt", ""),
                "en": (c_en.get("front") or {}).get("en", ""),
            },
            "back": {
                "pt": (c_pt.get("back") or {}).get("pt", ""),
                "en": (c_en.get("back") or {}).get("en", ""),
            }
        }
        cards_merged.append(card)
    return cards_merged


def gerar_mini_app_lote(domains):
    print("\nâ”€â”€ GERANDO MINI-APPS â”€â”€")
    ok = 0
    falhou = []

    for domain in domains:
        key  = domain["key"]
        code = domain["code"]
        sec  = domain["section"]
        print(f"  {code} {key}...", end=" ", flush=True)

        # quiz_001
        q1pt_path = QUIZZES_DIR / key / "quiz_001_pt.json"
        q1en_path = QUIZZES_DIR / key / "quiz_001_en.json"
        if not q1pt_path.exists():
            print(f"ERRO: quiz_001_pt nao encontrado")
            falhou.append(code)
            continue
        try:
            q1pt = load_json_safe(q1pt_path)["questions"]
            q1en = load_json_safe(q1en_path)["questions"] if q1en_path.exists() else []
        except Exception as e:
            print(f"ERRO quiz_001: {e}")
            falhou.append(code)
            continue

        # quiz_002
        q2pt_path = QUIZZES_DIR / key / "quiz_002_pt.json"
        q2en_path = QUIZZES_DIR / key / "quiz_002_en.json"
        try:
            q2pt = load_json_safe(q2pt_path)["questions"] if q2pt_path.exists() else []
            q2en = load_json_safe(q2en_path)["questions"] if q2en_path.exists() else []
        except Exception as e:
            print(f"AVISO quiz_002: {e}")
            q2pt, q2en = [], []

        # flashcards
        fc_pt_path = DST_FC / key / "flashcards_pt.json"
        fc_en_path = DST_FC / key / "flashcards_en.json"
        try:
            fc_pt = load_json_safe(fc_pt_path)
            fc_en = load_json_safe(fc_en_path) if fc_en_path.exists() else {"cards": []}
            cards = merge_fc(fc_en, fc_pt)
        except Exception as e:
            print(f"ERRO flashcards: {e}")
            falhou.append(code)
            continue

        # badge
        if sec == 1:
            badge_fname = f"CFE_SID{code[-2:]}.png"
        else:
            badge_fname = f"CFE_{code}.png"
        badge_path = BADGES_DIR / badge_fname
        badge_b64 = base64.b64encode(badge_path.read_bytes()).decode() if badge_path.exists() else ""

        # gera HTML via gerador original
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("gerador", BASE / "gerar_mini_apps_cfe.py")
            gerador = importlib.util.load_from_spec(spec)
            spec.loader.exec_module(gerador)
            # monta q1es/q2es vazios (ES eliminado)
            html = gerador.generate_mini_app(domain, q1en, q1pt, [], q2en, q2pt, [], cards, badge_b64)
        except Exception as e:
            print(f"ERRO generate_mini_app: {e}")
            falhou.append(code)
            continue

        out = OUTPUT_DIR / key / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(str(out), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"OK ({len(html):,} chars)")
        ok += 1

    print(f"\n  Lote: {ok}/{len(domains)} gerados", end="")
    if falhou:
        print(f" | falharam: {', '.join(falhou)}")
    else:
        print(" | sem erros")
    return ok, falhou


# â•â•â• MAIN â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def main():
    arg_lote = None
    if "--lote" in sys.argv:
        idx = sys.argv.index("--lote")
        arg_lote = int(sys.argv[idx + 1])

    if arg_lote:
        if arg_lote < 1 or arg_lote > len(LOTES):
            print(f"Lote invalido. Use 1 a {len(LOTES)}.")
            sys.exit(1)
        lotes_para_rodar = [(arg_lote, LOTES[arg_lote - 1])]
    else:
        lotes_para_rodar = list(enumerate(LOTES, 1))

    print(f"NEXOR CFE â€” SYNC + GERAR MINI-APPS")
    print(f"Total dominios: {len(DOMAINS)} | Lote size: {LOTE_SIZE}")
    print("=" * 60)

    total_ok = 0
    total_falhou = []

    for num, lote in lotes_para_rodar:
        keys = [d["key"] for d in lote]
        print(f"\n{'='*60}")
        print(f"LOTE {num}/{len(LOTES)}: {keys[0]} â†’ {keys[-1]}")
        print(f"{'='*60}")
        sync_flashcards(lote)
        ok, falhou = gerar_mini_app_lote(lote)
        total_ok += ok
        total_falhou.extend(falhou)

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {total_ok}/{len(DOMAINS if not arg_lote else lotes_para_rodar[0][1])} mini-apps gerados")
    if total_falhou:
        print(f"FALHARAM: {', '.join(total_falhou)}")
    print("=" * 60)
    print("\nLEMBRETE: rode patch_quiz2_unlock.py apos concluir todos os lotes.")


if __name__ == "__main__":
    main()

