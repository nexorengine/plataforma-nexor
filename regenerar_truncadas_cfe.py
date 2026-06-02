"""
NEXOR -- REGENERADOR TRUNCADAS CFE v1
Identifica questoes truncadas nos dominios legacy CFE,
regenera cada uma usando a tag como ancora de topico,
classifica a dificuldade e injeta no dominio correto.

DOMINIOS LEGACY:
  financial_transactions
  fraud_investigation
  law / law_cfe

USO:
    python regenerar_truncadas_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import shutil

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")
REPORT_FILE = f"regeneracao_truncadas_{TIMESTAMP}.txt"

# Dominios legacy a processar
LEGACY_DOMAINS = [
    "financial_transactions",
    "fraud_investigation",
    "law",
    "law_cfe",
    "prevention_deterrence",
]

# Mapa tag -> dominio destino CFE 2026
# Baseado no mapeamento da curadoria
TAG_TO_DOMAIN = {
    # S1 - Fraud Schemes
    "financial_statement": "financial_statement_fraud",
    "revenue_recognition": "financial_statement_fraud",
    "channel_stuffing": "financial_statement_fraud",
    "round_tripping": "financial_statement_fraud",
    "beneish": "financial_statement_fraud",
    "earnings_management": "financial_statement_fraud",
    "skimming": "cash_receipts_fraud",
    "cash_larceny": "cash_receipts_fraud",
    "lapping": "cash_receipts_fraud",
    "register_disbursement": "cash_receipts_fraud",
    "billing_scheme": "fraudulent_disbursements",
    "payroll_fraud": "fraudulent_disbursements",
    "ghost_employee": "fraudulent_disbursements",
    "expense_reimbursement": "fraudulent_disbursements",
    "check_tampering": "fraudulent_disbursements",
    "inventory": "inventory_fraud",
    "corruption": "corruption_bribery",
    "bribery": "corruption_bribery",
    "kickback": "corruption_bribery",
    "bid_rigging": "corruption_bribery",
    "conflict_of_interest": "corruption_bribery",
    "data_theft": "data_theft_ip",
    "trade_secret": "data_theft_ip",
    "intellectual_property": "data_theft_ip",
    "insider_threat": "data_theft_ip",
    "identity_theft": "identity_theft_cyberfraud",
    "phishing": "identity_theft_cyberfraud",
    "bec": "identity_theft_cyberfraud",
    "ransomware": "identity_theft_cyberfraud",
    "cyber": "identity_theft_cyberfraud",
    "money_laundering": "financial_institution_fraud",
    "aml": "financial_institution_fraud",
    "bsa": "financial_institution_fraud",
    "ctr": "financial_institution_fraud",
    "sar": "financial_institution_fraud",
    "structuring": "financial_institution_fraud",
    "mortgage_fraud": "financial_institution_fraud",
    "bank_fraud": "financial_institution_fraud",
    "ponzi": "securities_fraud",
    "pyramid": "securities_fraud",
    "pump_and_dump": "securities_fraud",
    "insider_trading": "securities_fraud",
    "securities": "securities_fraud",
    "check_kiting": "payment_fraud",
    "payment": "payment_fraud",
    "wire_transfer": "payment_fraud",
    "ach": "payment_fraud",
    "insurance": "insurance_fraud",
    "consumer_fraud": "consumer_fraud",
    "elder_fraud": "consumer_fraud",
    "advance_fee": "consumer_fraud",
    "bankruptcy": "bankruptcy_fraud",
    "tax": "tax_fraud",
    "irs": "tax_fraud",
    "fbar": "tax_fraud",
    "healthcare": "healthcare_fraud",
    "medicare": "healthcare_fraud",
    "medicaid": "healthcare_fraud",
    "upcoding": "healthcare_fraud",
    "anti_kickback": "healthcare_fraud",
    "stark": "healthcare_fraud",
    "government_fraud": "government_fraud",
    "procurement": "procurement_contract_fraud",
    "false_claims": "government_fraud",
    "fcpa": "international_fraud",
    "oecd": "international_fraud",
    "cross_border": "international_fraud",
    "deepfake": "emerging_fraud",
    "cryptocurrency": "emerging_fraud",
    "ai_fraud": "emerging_fraud",
    "esg_fraud": "emerging_fraud",
    # S2 - Investigations
    "investigation_plan": "investigation_planning",
    "predication": "investigation_planning",
    "legal_issue": "legal_issues_investigations",
    "privacy": "legal_issues_investigations",
    "wire_fraud": "law_cfe",
    "mail_fraud": "law_cfe",
    "rico": "law_cfe",
    "sox": "law_cfe",
    "dodd_frank": "law_cfe",
    "cfaa": "law_cfe",
    "federal_sentencing": "law_cfe",
    "criminal_prosecution": "criminal_prosecutions",
    "grand_jury": "criminal_prosecutions",
    "dpa": "criminal_prosecutions",
    "civil_action": "non_criminal_actions",
    "sec_enforcement": "non_criminal_actions",
    "fifth_amendment": "individual_rights",
    "whistleblower": "individual_rights",
    "miranda": "individual_rights",
    "evidence": "evidence_principles",
    "chain_of_custody": "evidence_principles",
    "hearsay": "evidence_principles",
    "digital_evidence": "collecting_evidence",
    "forensic_imaging": "collecting_evidence",
    "subpoena": "collecting_evidence",
    "public_records": "sources_information",
    "osint": "sources_information",
    "benfords_law": "data_analysis_tools",
    "data_analytics": "data_analysis_tools",
    "benford": "data_analysis_tools",
    "net_worth": "tracing_assets",
    "asset_tracing": "tracing_assets",
    "blockchain": "tracing_assets",
    "interview": "interview_techniques",
    "deception": "interview_techniques",
    "behavioral": "interview_techniques",
    "surveillance": "covert_operations",
    "undercover": "covert_operations",
    "report_writing": "report_writing",
    "expert_witness": "expert_witness",
    "daubert": "expert_witness",
    # S3 - Prevention
    "fraud_triangle": "criminal_behavior",
    "white_collar": "criminal_behavior",
    "occupational_fraud": "occupational_fraud",
    "report_to_nations": "occupational_fraud",
    "corporate_governance": "corporate_governance",
    "board": "corporate_governance",
    "audit_committee": "corporate_governance",
    "tone_at_top": "corporate_governance",
    "coso": "corporate_governance",
    "auditor_responsibility": "auditor_responsibilities",
    "internal_audit": "auditor_responsibilities",
    "sas_99": "auditor_responsibilities",
    "fraud_risk": "fraud_risk_assessment",
    "risk_assessment": "fraud_risk_assessment",
    "internal_control": "prevention_deterrence",
    "segregation_of_duties": "prevention_deterrence",
    "hotline": "fraud_prevention_programs",
    "awareness_training": "fraud_prevention_programs",
    "background_check": "fraud_prevention_programs",
    "fraud_response": "fraud_risk_management",
    "fidelity_bond": "fraud_risk_management",
    "ethics": "ethics_fraud_examiners",
    "acfe_code": "ethics_fraud_examiners",
}

# Contexto por dominio destino para o prompt
DOMAIN_CONTEXT = {
    "financial_statement_fraud": "Financial Statement Fraud — revenue manipulation, fictitious revenues, Beneish M-Score",
    "cash_receipts_fraud": "Asset Misappropriation Cash Receipts — skimming, lapping, register schemes",
    "fraudulent_disbursements": "Asset Misappropriation Disbursements — billing schemes, payroll fraud, check tampering",
    "inventory_fraud": "Asset Misappropriation Inventory — theft, purchasing schemes",
    "corruption_bribery": "Corruption Bribery Conflicts of Interest — kickbacks, bid rigging, FCPA",
    "data_theft_ip": "Theft of Data and Intellectual Property — EEA, DTSA, insider threats",
    "identity_theft_cyberfraud": "Identity Theft and Cyberfraud — BEC, phishing, ransomware",
    "financial_institution_fraud": "Financial Institution Fraud and Money Laundering — BSA, CTR, SAR",
    "securities_fraud": "Securities and Investment Fraud — Ponzi, pump and dump, insider trading",
    "payment_fraud": "Payment Fraud — ACH, wire transfer, check fraud, CNP",
    "insurance_fraud": "Insurance Fraud — staged accidents, workers comp, SIU",
    "consumer_fraud": "Consumer Fraud — advance fee, romance scams, elder fraud",
    "bankruptcy_fraud": "Bankruptcy Fraud — 18 USC 152-157, asset concealment, bust-out",
    "tax_fraud": "Tax Fraud — IRC 7201, FBAR, FATCA, IRS-CI",
    "healthcare_fraud": "Health Care Fraud — upcoding, Anti-Kickback Statute, Stark Law",
    "government_fraud": "Government Public Sector Fraud — procurement fraud, False Claims Act",
    "procurement_contract_fraud": "Procurement Contract Fraud — bid rigging, cost mischarging",
    "international_fraud": "International Cross-Border Fraud — FCPA, OECD, UK Bribery Act",
    "emerging_fraud": "Emerging Fraud Technology — deepfakes, cryptocurrency, AI fraud",
    "investigation_planning": "Planning and Conducting Fraud Examination — scope, predication",
    "legal_issues_investigations": "Legal Issues in Investigations — employee rights, privacy",
    "law_cfe": "Law Related to Fraud — wire fraud, RICO, SOX, FCPA, False Claims Act",
    "legal_system_overview": "Overview of the Legal System — jurisdiction, burden of proof",
    "criminal_prosecutions": "Criminal Prosecutions — grand jury, plea agreements, DPA",
    "non_criminal_actions": "Non-Criminal Actions — civil fraud, SEC enforcement, disgorgement",
    "individual_rights": "Individual Rights — Fifth Amendment, Miranda, whistleblower protections",
    "evidence_principles": "Basic Principles of Evidence — admissibility, chain of custody, hearsay",
    "collecting_evidence": "Collecting Evidence — forensic imaging, subpoenas, e-discovery",
    "sources_information": "Sources of Information — public records, OSINT, social media",
    "data_analysis_tools": "Data Analysis Tools — Benford Law, data analytics, AI detection",
    "tracing_assets": "Tracing Illicit Transactions — net worth method, cryptocurrency tracing",
    "interview_techniques": "Interview Theory — cognitive interview, behavioral analysis, admission-seeking",
    "covert_operations": "Covert Operations — surveillance, undercover, entrapment standard",
    "report_writing": "Report Writing — structure, avoiding legal conclusions, expert opinion",
    "expert_witness": "Testifying as Expert Witness — Daubert standard, cross-examination",
    "criminal_behavior": "Understanding Criminal Behavior — Fraud Triangle, white-collar crime",
    "occupational_fraud": "Occupational Fraud — ACFE Report to the Nations, detection methods",
    "corporate_governance": "Corporate Governance — board duties, audit committee, COSO",
    "auditor_responsibilities": "Management and Auditors Responsibilities — SAS 99, ISA 240",
    "fraud_risk_assessment": "Fraud Risk Assessment — COSO methodology, risk factors",
    "prevention_deterrence": "Internal Controls — segregation of duties, COSO framework",
    "fraud_prevention_programs": "Fraud Prevention Programs — hotlines, training, background checks",
    "fraud_risk_management": "Fraud Risk Management — response plan, insurance, lessons learned",
    "ethics_fraud_examiners": "Ethics for Fraud Examiners — ACFE Code, independence, confidentiality",
}

METODO_NEXOR = """
MÉTODO NEXOR — APLICAR:
- Cenário profissional no stem (Standard/Hard)
- Lead-in como pergunta completa
- 4 opções homogêneas em comprimento
- Correta não é a mais longa
- Sem absolutos, sem clang, sem convergência
- justification_correct: explica o princípio técnico
- justification_wrong: explica cada distrator
"""

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def is_truncated(q):
    """Detecta se uma questao esta truncada."""
    text = q.get("text", "")
    just_c = q.get("justification_correct", "")
    just_w = q.get("justification_wrong", "")
    options = q.get("options", [])

    # Texto muito curto ou cortado
    if len(text) < 80:
        return True
    # Justificativa muito curta
    if len(just_c) < 50 or len(just_w) < 30:
        return True
    # Opcoes incompletas
    if len(options) < 4:
        return True
    # Texto ou justificativa cortados no meio (sem pontuacao final)
    if text and text[-1] not in ".?!\"'":
        return True
    return False

def guess_dest_domain(tag):
    """Deduz o dominio destino a partir da tag."""
    tag_lower = tag.lower().replace(" ", "_").replace("-", "_")
    for key, domain in TAG_TO_DOMAIN.items():
        if key in tag_lower:
            return domain
    return "law_cfe"  # fallback

def classify_difficulty(tag, text):
    """Classifica a dificuldade baseado na tag e texto."""
    tag_lower = tag.lower()
    text_lower = text.lower()
    # Hard: cenarios complexos, analise, avaliacao
    hard_indicators = ["complex", "evaluate", "distinguish", "analyze", "competing", "multiple"]
    if any(h in text_lower for h in hard_indicators):
        return "HARD"
    # Easy: definicoes
    easy_indicators = ["definition", "define", "what is", "basic", "which of the following is not"]
    if any(e in text_lower[:100] for e in easy_indicators):
        return "EASY"
    return "STANDARD"

def regenerate_question(client, tag, dest_domain, num):
    """Regenera uma questao truncada usando a tag como topico."""
    domain_ctx = DOMAIN_CONTEXT.get(dest_domain, dest_domain)

    prompt = f"""You are an expert CFE exam question writer.

Domain: {domain_ctx}
Topic tag: {tag}

{METODO_NEXOR}

Generate exactly 1 complete CFE exam question about: {tag}
Level: STANDARD (Bloom Level 3 — application in professional scenario)
US law scope only.

Return ONLY a JSON array with one object, no markdown:
[{{
  "num": {num},
  "text": "Complete scenario-based question",
  "tag": "{tag}",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "STANDARD",
  "justification_correct": "Detailed principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

    try:
        result = call_api(client, prompt)
        if isinstance(result, list) and result:
            result[0]["num"] = num
            return result[0]
    except Exception as e:
        print(f" ERRO: {e}")
    return None

def translate_question(client, question, lang_name):
    prompt = f"""Translate this CFE question from English to {lang_name}.
Rules: translate only text/options/justifications. Keep num/tag/correct/difficulty unchanged.
Keep legal terms in English. Return ONLY JSON array, no markdown.
Input: {json.dumps([question], ensure_ascii=False)}"""
    try:
        result = call_api(client, prompt)
        if isinstance(result, list) and result:
            q = result[0]
            q["num"] = question["num"]
            q["tag"] = question["tag"]
            q["correct"] = question["correct"]
            return q
    except:
        pass
    return question

def inject_into_domain(dest_domain, new_question):
    """Injeta a questao regenerada no dominio destino."""
    dest_path = Path(QUIZZES_DIR) / dest_domain
    en_files = sorted(dest_path.glob("quiz_*_en.json")) if dest_path.exists() else []

    if not en_files:
        # Cria quiz_002 (quiz_001 pode ser piloto ou legado)
        quiz_num = 2
    else:
        # Adiciona ao ultimo quiz disponivel se tiver espaco
        last_file = en_files[-1]
        last_data = load_json(str(last_file))
        if len(last_data["questions"]) < 50:
            # Adiciona ao quiz existente
            num = len(last_data["questions"]) + 1
            new_question["num"] = num
            last_data["questions"].append(new_question)
            save_json(str(last_file), last_data)
            return str(last_file), num
        else:
            # Cria proximo quiz
            try:
                quiz_num = int(last_file.name.split("_")[1]) + 1
            except:
                quiz_num = len(en_files) + 1

    # Cria novo quiz
    quiz_fname = f"quiz_{quiz_num:03d}_en.json"
    new_question["num"] = 1
    quiz_data = {
        "cert_id":     "cfe",
        "domain_id":   dest_domain,
        "quiz_num":    quiz_num,
        "domain_name": dest_domain.replace("_", " ").title(),
        "cert_name":   "Certified Fraud Examiner",
        "lang":        "en",
        "questions":   [new_question]
    }
    out_path = dest_path / quiz_fname
    dest_path.mkdir(parents=True, exist_ok=True)
    save_json(str(out_path), quiz_data)
    return str(out_path), 1

def main():
    print("=" * 70)
    print("  NEXOR -- REGENERADOR TRUNCADAS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    # Coleta truncadas
    print("\n  Identificando questoes truncadas...")
    truncadas = []
    base = Path(QUIZZES_DIR)

    for domain_id in LEGACY_DOMAINS:
        domain_path = base / domain_id
        if not domain_path.exists():
            continue
        for quiz_file in sorted(domain_path.glob("quiz_*_en.json")):
            try:
                data = load_json(str(quiz_file))
                for q in data.get("questions", []):
                    if is_truncated(q):
                        q["_source_domain"] = domain_id
                        q["_source_file"]   = quiz_file.name
                        truncadas.append(q)
            except Exception as e:
                print(f"  Erro: {quiz_file}: {e}")

    print(f"  Truncadas encontradas: {len(truncadas)}")

    if not truncadas:
        print("  Nenhuma truncada encontrada.")
        return

    # Regenera em lotes
    print(f"\n  Regenerando {len(truncadas)} questoes...")
    log_lines  = [f"NEXOR -- REGENERACAO TRUNCADAS -- {TIMESTAMP}", ""]
    regeneradas = 0
    falhas      = 0
    by_domain   = defaultdict(int)

    for i, q in enumerate(truncadas):
        tag         = q.get("tag", "unknown")
        dest_domain = guess_dest_domain(tag)

        print(f"  [{i+1}/{len(truncadas)}] {tag[:40]}... ", end="", flush=True)

        new_q = regenerate_question(client, tag, dest_domain, 1)

        if new_q:
            # Injeta no dominio destino EN
            out_file, num = inject_into_domain(dest_domain, new_q)

            # Traduz e injeta PT e ES
            for lang_code, lang_name in [("pt","Portugues (Brasil)"),("es","Espanol neutro")]:
                translated = translate_question(client, new_q, lang_name)
                lang_file  = out_file.replace("_en.json", f"_{lang_code}.json")
                if os.path.exists(lang_file):
                    lang_data = load_json(lang_file)
                    translated["num"] = len(lang_data["questions"]) + 1
                    lang_data["questions"].append(translated)
                    save_json(lang_file, lang_data)
                else:
                    quiz_num = int(Path(out_file).name.split("_")[1])
                    translated["num"] = 1
                    lang_quiz = {
                        "cert_id": "cfe", "domain_id": dest_domain,
                        "quiz_num": quiz_num, "lang": lang_code,
                        "questions": [translated]
                    }
                    save_json(lang_file, lang_quiz)

            regeneradas += 1
            by_domain[dest_domain] += 1
            log_lines.append(f"  OK Q{num} → {dest_domain} | tag: {tag}")
            print(f"OK → {dest_domain}")
        else:
            falhas += 1
            log_lines.append(f"  FALHA | tag: {tag}")
            print("FALHA")

    # Salva log
    log_lines += [
        "",
        f"Regeneradas: {regeneradas}",
        f"Falhas: {falhas}",
        "",
        "Por dominio destino:",
    ]
    for d, n in sorted(by_domain.items()):
        log_lines.append(f"  {d}: {n}q")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  Regeneradas : {regeneradas}")
    print(f"  Falhas      : {falhas}")
    print(f"  Relatorio   : {REPORT_FILE}")
    print("=" * 70)
    print()
    print("  PROXIMO PASSO:")
    print("  python verificar_duplicatas.py")

if __name__ == "__main__":
    main()
