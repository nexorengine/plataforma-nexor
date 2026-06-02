"""
NEXOR -- REPOSICIONADOR LEGADO CFE 2026 v1
Lê o JSON de curadoria e reposiciona as questões VALIDADAS
e LEGACY_REVIEW nos novos domínios da estrutura CFE 2026.
Cria quiz_001_en.json em cada domínio destino com as questões
do legado já classificadas por dificuldade.

USO:
    python reposicionar_legado_cfe.py
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

QUIZZES_DIR  = r"static\quizzes\cfe"
TIMESTAMP    = datetime.now().strftime("%Y%m%d_%H%M")
CURADORIA_JSON = None  # detectado automaticamente

# Dominios que já têm quiz_001 gerado pelo piloto — não sobrescrever
DOMINIOS_COM_PILOTO = {
    "data_theft_ip",
    "insurance_fraud",
    "consumer_fraud",
    "bankruptcy_fraud",
    "tax_fraud",
    "government_fraud",
    "emerging_fraud",
}

# Mapa dominio_id → nome display
NOMES_DOMINIOS = {
    "accounting_concepts":        "S1D01 · Accounting Concepts & Financial Analysis",
    "financial_statement_fraud":  "S1D02 · Financial Statement Fraud",
    "cash_receipts_fraud":        "S1D03 · Asset Misappropriation — Cash Receipts",
    "fraudulent_disbursements":   "S1D04 · Asset Misappropriation — Disbursements",
    "inventory_fraud":            "S1D05 · Asset Misappropriation — Inventory & Assets",
    "corruption_bribery":         "S1D06 · Corruption, Bribery & Conflicts of Interest",
    "data_theft_ip":              "S1D07 · Theft of Data & Intellectual Property",
    "identity_theft_cyberfraud":  "S1D08 · Identity Theft & Cyberfraud",
    "financial_institution_fraud":"S1D09 · Financial Institution Fraud & Money Laundering",
    "securities_fraud":           "S1D10 · Securities & Investment Fraud",
    "payment_fraud":              "S1D11 · Payment Fraud",
    "insurance_fraud":            "S1D12 · Insurance Fraud",
    "consumer_fraud":             "S1D13 · Consumer Fraud & Scams",
    "bankruptcy_fraud":           "S1D14 · Bankruptcy Fraud",
    "tax_fraud":                  "S1D15 · Tax Fraud",
    "healthcare_fraud":           "S1D16 · Health Care Fraud",
    "government_fraud":           "S1D17 · Government & Public Sector Fraud",
    "procurement_contract_fraud": "S1D18 · Procurement & Contract Fraud",
    "international_fraud":        "S1D19 · International & Cross-Border Fraud",
    "emerging_fraud":             "S1D20 · Emerging Fraud & Technology",
    "investigation_planning":     "S2D01 · Planning & Conducting Fraud Examination",
    "legal_issues_investigations":"S2D02 · Legal Issues in Investigations",
    "law_cfe":                    "S2D03 · Law Related to Fraud",
    "legal_system_overview":      "S2D04 · Overview of the Legal System",
    "criminal_prosecutions":      "S2D05 · Criminal Prosecutions",
    "non_criminal_actions":       "S2D06 · Non-Criminal Actions",
    "individual_rights":          "S2D07 · Individual Rights During Examinations",
    "evidence_principles":        "S2D08 · Basic Principles of Evidence",
    "collecting_evidence":        "S2D09 · Collecting Evidence",
    "sources_information":        "S2D10 · Sources of Information",
    "data_analysis_tools":        "S2D11 · Data Analysis & Reporting Tools",
    "tracing_assets":             "S2D12 · Tracing Illicit Transactions & Assets",
    "interview_techniques":       "S2D13 · Interview Theory & Application",
    "covert_operations":          "S2D14 · Covert Operations",
    "report_writing":             "S2D15 · Report Writing",
    "expert_witness":             "S2D16 · Testifying as Expert Witness",
    "criminal_behavior":          "S3D01 · Understanding Criminal Behavior",
    "occupational_fraud":         "S3D02 · Occupational Fraud",
    "corporate_governance":       "S3D03 · Corporate Governance",
    "auditor_responsibilities":   "S3D04 · Management & Auditors Responsibilities",
    "fraud_risk_assessment":      "S3D05 · Fraud Risk Assessment",
    "prevention_deterrence":      "S3D06 · Internal Controls & Anti-Fraud Programs",
    "fraud_prevention_programs":  "S3D07 · Fraud Prevention Programs",
    "fraud_risk_management":      "S3D08 · Fraud Risk Management",
    "ethics_fraud_examiners":     "S3D09 · Ethics for Fraud Examiners",
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_curadoria_json():
    """Encontra o JSON de curadoria mais recente."""
    files = sorted(Path(".").glob("curadoria_resultado_*.json"), reverse=True)
    if not files:
        raise FileNotFoundError("Nenhum arquivo curadoria_resultado_*.json encontrado.")
    return str(files[0])

def load_original_question(source, num):
    """Carrega a questao original do arquivo fonte."""
    parts = source.split("/")
    domain_id  = parts[0]
    quiz_fname = parts[1]
    path = Path(QUIZZES_DIR) / domain_id / quiz_fname
    if not path.exists():
        return None
    data = load_json(str(path))
    for q in data.get("questions", []):
        if q.get("num") == num:
            return q
    return None

def main():
    print("=" * 70)
    print("  NEXOR -- REPOSICIONADOR LEGADO CFE 2026 v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    # Encontra JSON de curadoria
    curadoria_file = find_curadoria_json()
    print(f"\n  Curadoria: {curadoria_file}")
    curadoria = load_json(curadoria_file)

    questoes = curadoria.get("questoes_validadas", [])
    print(f"  Questoes a reposicionar: {len(questoes)}")
    print(f"  (VALIDADAS + LEGACY_REVIEW)")

    # Agrupa por dominio destino
    por_dominio = defaultdict(list)
    for q_info in questoes:
        dest_id = q_info.get("dest_id", "unknown")
        if dest_id and dest_id != "unknown":
            por_dominio[dest_id].append(q_info)

    print(f"\n  Dominios destino com questoes: {len(por_dominio)}")

    # Processa cada dominio destino
    log_lines = [f"NEXOR -- REPOSICIONAMENTO -- {TIMESTAMP}", ""]
    total_reposicionadas = 0
    total_puladas = 0

    for dest_id, q_infos in sorted(por_dominio.items()):
        n = len(q_infos)
        dest_path = Path(QUIZZES_DIR) / dest_id

        # Verifica se dominio tem piloto — adiciona como quiz_002
        if dest_id in DOMINIOS_COM_PILOTO:
            # Verifica qual o proximo numero de quiz disponivel
            existing = sorted(dest_path.glob("quiz_*_en.json")) if dest_path.exists() else []
            nums = []
            for f in existing:
                try:
                    n_str = f.name.split("_")[1]
                    nums.append(int(n_str))
                except:
                    pass
            next_num = max(nums) + 1 if nums else 1
            quiz_fname = f"quiz_{next_num:03d}_en.json"
            label = f"quiz_{next_num:03d} (piloto existe)"
        else:
            # Verifica se ja tem quiz_001
            quiz_001_path = dest_path / "quiz_001_en.json"
            if quiz_001_path.exists():
                existing = sorted(dest_path.glob("quiz_*_en.json"))
                nums = []
                for f in existing:
                    try:
                        n_str = f.name.split("_")[1]
                        nums.append(int(n_str))
                    except:
                        pass
                next_num = max(nums) + 1 if nums else 2
                quiz_fname = f"quiz_{next_num:03d}_en.json"
                label = f"quiz_{next_num:03d} (quiz_001 existe)"
            else:
                quiz_fname = "quiz_001_en.json"
                label = "quiz_001 (novo)"

        print(f"\n  {dest_id} → {label} ({n}q)")

        # Carrega questoes originais
        questions_out = []
        for i, q_info in enumerate(q_infos):
            orig = load_original_question(q_info["source"], q_info["num"])
            if not orig:
                print(f"    SKIP Q{q_info['num']} — original nao encontrado")
                total_puladas += 1
                continue

            # Adiciona metadados de classificacao
            orig["num"]        = i + 1
            orig["difficulty"] = q_info.get("difficulty", "STANDARD")
            orig["legacy"]     = True
            orig["legacy_source"] = q_info["source"]
            questions_out.append(orig)

        if not questions_out:
            print(f"    SKIP — nenhuma questao carregada")
            log_lines.append(f"  SKIP {dest_id}: nenhuma questao")
            continue

        # Monta quiz
        dest_name = NOMES_DOMINIOS.get(dest_id, dest_id)
        quiz_data = {
            "cert_id":     "cfe",
            "domain_id":   dest_id,
            "quiz_num":    int(quiz_fname.split("_")[1]),
            "domain_name": dest_name,
            "cert_name":   "Certified Fraud Examiner",
            "lang":        "en",
            "source":      "legacy_curated",
            "questions":   questions_out
        }

        out_path = dest_path / quiz_fname
        dest_path.mkdir(parents=True, exist_ok=True)

        # Backup se existir
        if out_path.exists():
            shutil.copy2(str(out_path), str(out_path) + f".bak_{TIMESTAMP}")

        save_json(str(out_path), quiz_data)
        total_reposicionadas += len(questions_out)
        log_lines.append(f"  OK {dest_id}/{quiz_fname}: {len(questions_out)}q")
        print(f"    Salvo: {out_path} ({len(questions_out)}q)")

    # Salva log
    log_file = f"reposicionamento_log_{TIMESTAMP}.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  Questoes reposicionadas : {total_reposicionadas}")
    print(f"  Questoes puladas        : {total_puladas}")
    print(f"  Log                     : {log_file}")
    print("=" * 70)
    print()
    print("  PROXIMO PASSO:")
    print("  1. Verificar no dashboard os novos quizzes")
    print("  2. python verificar_duplicatas.py")
    print("  3. Reiniciar servidor para atualizar catalogo")

if __name__ == "__main__":
    main()
