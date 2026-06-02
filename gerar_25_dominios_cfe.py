"""
NEXOR -- GERADOR 25 DOMINIOS VAZIOS CFE v1
Gera quiz_001 completo (50q × EN/PT/ES) para os 25 dominios CFE
que ainda nao tem nenhum quiz.

METODOLOGIA:
  · Blocos de 10 questoes por chamada de API
  · 5 blocos por idioma = 50 questoes
  · Sem truncamento
  · FractalLearning v1: 10 Easy + 30 Standard + 10 Hard

USO:
    python gerar_25_dominios_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil
import time

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# 25 dominios vazios
DOMINIOS = [
    {
        "domain_id": "accounting_concepts",
        "domain_code": "S1D01",
        "domain_name": "S1D01 · Accounting Concepts & Financial Analysis",
        "context": "CFE Exam 2026 S1D01 — Accounting Concepts and Financial Statement Analysis. Topics: accounting equation, balance sheet, income statement, cash flow statement, GAAP vs IFRS, accrual vs cash basis, financial ratios (liquidity, profitability, leverage), management vs auditor responsibilities, red flags in financial statement analysis, horizontal and vertical analysis."
    },
    {
        "domain_id": "auditor_responsibilities",
        "domain_code": "S3D04",
        "domain_name": "S3D04 · Management & Auditors Responsibilities",
        "context": "CFE Exam 2026 S3D04 — Management and Auditors Responsibilities. Topics: management duty of care, internal audit function and independence, external auditor fraud detection responsibilities (SAS 99/ISA 240), audit committee oversight, CFE vs CPA roles in fraud detection, management override of controls, auditor independence standards, Sarbanes-Oxley auditor requirements."
    },
    {
        "domain_id": "cash_receipts_fraud",
        "domain_code": "S1D03",
        "domain_name": "S1D03 · Asset Misappropriation — Cash Receipts",
        "context": "CFE Exam 2026 S1D03 — Asset Misappropriation Cash Receipts. Topics: skimming (unrecorded sales, understated receivables, cash register manipulation), cash larceny (theft of deposited cash), fraudulent write-offs and discounts, register disbursement schemes, check tampering in receivables, accounts receivable lapping schemes, detection methods and internal controls."
    },
    {
        "domain_id": "covert_operations",
        "domain_code": "S2D14",
        "domain_name": "S2D14 · Covert Operations",
        "context": "CFE Exam 2026 S2D14 — Covert Operations. Topics: undercover investigations (planning, legal authority, risks), physical surveillance techniques and legal limitations, electronic surveillance (wiretapping, GPS tracking), entrapment standard and legal defense, sting operations in fraud investigations, privacy law considerations (federal and state), documentation standards for covert evidence, chain of custody in covert ops."
    },
    {
        "domain_id": "criminal_behavior",
        "domain_code": "S3D01",
        "domain_name": "S3D01 · Understanding Criminal Behavior",
        "context": "CFE Exam 2026 S3D01 — Understanding Criminal Behavior and White-Collar Crime. Topics: Fraud Triangle (pressure/opportunity/rationalization by Cressey), Fraud Diamond (capability by Wolfe and Hermanson), occupational vs organizational fraud, sociological theories of white-collar crime (Sutherland), moral disengagement mechanisms, psychological profiles of fraudsters, effects of white-collar crime on organizations and society."
    },
    {
        "domain_id": "criminal_prosecutions",
        "domain_code": "S2D05",
        "domain_name": "S2D05 · Criminal Prosecutions",
        "context": "CFE Exam 2026 S2D05 — Criminal Prosecutions. Topics: elements of criminal fraud offenses, grand jury process and secrecy, indictment vs information, plea agreements and cooperation, Federal Sentencing Guidelines (Chapter 8 organizational guidelines), corporate criminal liability (respondeat superior), Deferred Prosecution Agreements (DPA) and Non-Prosecution Agreements (NPA), parallel civil and criminal proceedings."
    },
    {
        "domain_id": "data_analysis_tools",
        "domain_code": "S2D11",
        "domain_name": "S2D11 · Data Analysis & Reporting Tools",
        "context": "CFE Exam 2026 S2D11 — Data Analysis and Reporting Tools. Topics: Benford Law application in fraud detection (chi-square test, MAD), statistical sampling methods, regression analysis, data matching and duplicate testing, ACL/Galvanize and IDEA/CaseWare analytics software, AI and machine learning in fraud detection, network analysis for fraud schemes, continuous monitoring systems, gap and boundary testing."
    },
    {
        "domain_id": "ethics_fraud_examiners",
        "domain_code": "S3D09",
        "domain_name": "S3D09 · Ethics for Fraud Examiners",
        "context": "CFE Exam 2026 S3D09 — Ethics for Fraud Examiners. Topics: ACFE Code of Professional Ethics (four principles: integrity, objectivity, confidentiality, competency), confidentiality obligations and exceptions, independence and objectivity requirements, conflicts of interest identification and disclosure, professional competence maintenance, professional skepticism in investigations, ethical decision-making frameworks, ACFE disciplinary process and sanctions."
    },
    {
        "domain_id": "evidence_principles",
        "domain_code": "S2D08",
        "domain_name": "S2D08 · Basic Principles of Evidence",
        "context": "CFE Exam 2026 S2D08 — Basic Principles of Evidence. Topics: direct vs circumstantial vs documentary evidence, admissibility standards (relevance, materiality, competence), hearsay rule and exceptions (business records, admissions), best evidence rule, authentication requirements, chain of custody requirements, spoliation of evidence (sanctions and adverse inference), Federal Rules of Evidence key provisions."
    },
    {
        "domain_id": "expert_witness",
        "domain_code": "S2D16",
        "domain_name": "S2D16 · Testifying as Expert Witness",
        "context": "CFE Exam 2026 S2D16 — Testifying as an Expert Witness. Topics: expert qualification standards (education, experience, publications), Daubert standard for expert testimony (federal courts), Frye standard (general acceptance), direct examination techniques, cross-examination preparation and handling, deposition preparation and strategy, maintaining objectivity under pressure, court-appointed experts (Rule 706), report writing for litigation support."
    },
    {
        "domain_id": "financial_institution_fraud",
        "domain_code": "S1D09",
        "domain_name": "S1D09 · Financial Institution Fraud & Money Laundering",
        "context": "CFE Exam 2026 S1D09 — Financial Institution Fraud and Money Laundering. Topics: bank fraud (18 USC 1344), mortgage fraud schemes, credit card fraud, money laundering stages (placement/layering/integration), structuring/smurfing violations, BSA requirements (CTR threshold $10,000, SAR filing obligations), FinCEN reporting, FATF 40 recommendations, cryptocurrency money laundering, correspondent banking risks."
    },
    {
        "domain_id": "fraud_risk_management",
        "domain_code": "S3D08",
        "domain_name": "S3D08 · Fraud Risk Management",
        "context": "CFE Exam 2026 S3D08 — Fraud Risk Management. Topics: enterprise fraud risk management framework, fraud response plan components, incident response triggers and escalation, remediation steps after fraud discovery, lessons learned implementation, fidelity bonds and crime insurance coverage, cyber insurance for fraud losses, continuous monitoring programs, fraud risk indicators (KRIs), board-level fraud risk reporting."
    },
    {
        "domain_id": "fraudulent_disbursements",
        "domain_code": "S1D04",
        "domain_name": "S1D04 · Asset Misappropriation — Disbursements",
        "context": "CFE Exam 2026 S1D04 — Asset Misappropriation Fraudulent Disbursements. Topics: billing schemes (shell companies, personal purchases, pass-through schemes), payroll fraud (ghost employees, falsified wages, commission schemes), expense reimbursement fraud (personal expenses, inflated claims, fictitious expenses), check tampering (forged signatures, altered payees, concealed checks), pay-and-return schemes, detection methods and internal controls."
    },
    {
        "domain_id": "identity_theft_cyberfraud",
        "domain_code": "S1D08",
        "domain_name": "S1D08 · Identity Theft & Cyberfraud",
        "context": "CFE Exam 2026 S1D08 — Identity Theft and Cyberfraud. Topics: identity theft (18 USC 1028), phishing/spear phishing/whaling techniques, social engineering tactics, business email compromise (BEC) schemes, ransomware attacks and extortion, deepfake fraud in financial transactions, SIM swapping attacks, account takeover fraud, cybercrime prevention measures, digital evidence in cybercrime investigations."
    },
    {
        "domain_id": "individual_rights",
        "domain_code": "S2D07",
        "domain_name": "S2D07 · Individual Rights During Examinations",
        "context": "CFE Exam 2026 S2D07 — Individual Rights During Examinations. Topics: Fifth Amendment privilege against self-incrimination, Miranda rights (when applicable in private investigations), Weingarten rights (union representation), Garrity rights (public employees), attorney-client privilege in investigations, Dodd-Frank whistleblower protections, SOX Section 806 whistleblower protections, employee cooperation duties vs rights, compelled statements and use immunity."
    },
    {
        "domain_id": "international_fraud",
        "domain_code": "S1D19",
        "domain_name": "S1D19 · International & Cross-Border Fraud",
        "context": "CFE Exam 2026 S1D19 — International and Cross-Border Fraud. Topics: FCPA anti-bribery provisions and accounting provisions, FCPA facilitating payments exception (eliminated in practice), third-party liability and due diligence, OECD Anti-Bribery Convention, UK Bribery Act (broader than FCPA, no facilitation exception), FATF recommendations for international AML, cross-border money laundering techniques, Mutual Legal Assistance Treaties (MLAT), offshore financial centers and shell companies."
    },
    {
        "domain_id": "inventory_fraud",
        "domain_code": "S1D05",
        "domain_name": "S1D05 · Asset Misappropriation — Inventory & Assets",
        "context": "CFE Exam 2026 S1D05 — Asset Misappropriation Inventory and Other Assets. Topics: inventory theft and misuse schemes, purchasing and receiving fraud (false receiving reports, bid rigging), false inventory counts and fictitious inventory, non-cash asset misappropriation (equipment, intellectual property), misuse of company resources (vehicles, computers, personnel), detection methods (physical counts, reconciliations), internal controls for inventory protection."
    },
    {
        "domain_id": "investigation_planning",
        "domain_code": "S2D01",
        "domain_name": "S2D01 · Planning & Conducting Fraud Examination",
        "context": "CFE Exam 2026 S2D01 — Planning and Conducting a Fraud Examination. Topics: difference between fraud examination and financial audit, scope definition and examination plan, conflict of interest checks before accepting engagement, team assembly and expertise requirements, hypothesis development methodology, predication requirements (minimum basis to begin), confidentiality requirements during investigation, coordination with legal counsel and law enforcement."
    },
    {
        "domain_id": "legal_issues_investigations",
        "domain_code": "S2D02",
        "domain_name": "S2D02 · Legal Issues in Investigations",
        "context": "CFE Exam 2026 S2D02 — Legal Issues in Conducting Investigations. Topics: employee rights during workplace investigations, privacy expectations (reasonable expectation of privacy), lawful monitoring of employees (computers, email, phone), search and seizure principles (Fourth Amendment in private sector), defamation risks (libel, slander) in investigations, legal holds and document preservation obligations, attorney-client privilege in corporate investigations."
    },
    {
        "domain_id": "non_criminal_actions",
        "domain_code": "S2D06",
        "domain_name": "S2D06 · Non-Criminal Actions",
        "context": "CFE Exam 2026 S2D06 — Non-Criminal Actions Civil and Administrative. Topics: civil fraud claims and elements, compensatory vs punitive damages in fraud cases, disgorgement of ill-gotten gains, injunctive relief in fraud cases, civil RICO claims (treble damages), SEC enforcement actions (administrative vs judicial), debarment from government contracting, civil False Claims Act (qui tam provisions), asset freezing orders, civil forfeiture."
    },
    {
        "domain_id": "occupational_fraud",
        "domain_code": "S3D02",
        "domain_name": "S3D02 · Occupational Fraud",
        "context": "CFE Exam 2026 S3D02 — Occupational Fraud. Topics: ACFE Report to the Nations statistics (median loss, detection methods, industry analysis), fraud by category (asset misappropriation vs corruption vs financial statement fraud), fraud by industry and organization size, fraud by perpetrator position and tenure, detection method comparison (tips vs internal audit vs management review vs accident), cost of fraud to organizations, anti-fraud control effectiveness data."
    },
    {
        "domain_id": "procurement_contract_fraud",
        "domain_code": "S1D18",
        "domain_name": "S1D18 · Procurement & Contract Fraud",
        "context": "CFE Exam 2026 S1D18 — Procurement and Contract Fraud. Topics: bid manipulation schemes (complementary bidding, bid suppression, bid rotation), specification rigging to favor specific vendors, sole source abuse, cost mischarging on government contracts, defective pricing (Truth in Negotiations Act/TINA), product substitution fraud, subcontractor pass-through schemes, change order fraud, false claims in contract performance."
    },
    {
        "domain_id": "report_writing",
        "domain_code": "S2D15",
        "domain_name": "S2D15 · Report Writing",
        "context": "CFE Exam 2026 S2D15 — Report Writing. Topics: structure of fraud examination report (executive summary, body, conclusions, exhibits), statement of facts vs legal conclusions (avoiding unauthorized legal opinions), avoiding defamatory statements in reports, expert opinion standards and limitations, litigation support report requirements, confidentiality of investigation reports, audience-appropriate report formats, documenting findings with supporting evidence references."
    },
    {
        "domain_id": "securities_fraud",
        "domain_code": "S1D10",
        "domain_name": "S1D10 · Securities & Investment Fraud",
        "context": "CFE Exam 2026 S1D10 — Securities and Investment Fraud. Topics: Ponzi schemes (structure, detection, collapse indicators), pyramid schemes vs legitimate MLM, pump and dump schemes, insider trading (SEC Rule 10b-5, material nonpublic information), market manipulation techniques, investment adviser fraud, affinity fraud targeting communities, SEC enforcement powers and remedies, Madoff case study, whistleblower provisions (Dodd-Frank Section 922)."
    },
    {
        "domain_id": "sources_information",
        "domain_code": "S2D10",
        "domain_name": "S2D10 · Sources of Information",
        "context": "CFE Exam 2026 S2D10 — Sources of Information. Topics: public records (court records, corporate filings, property records, SEC EDGAR), nonpublic records access (bank records, credit reports, employment records — legal requirements), social media evidence collection and preservation, OSINT techniques and tools, dark web intelligence (legal and ethical considerations), international records access challenges, skip tracing techniques, interviewing as information source."
    },
    {
        "domain_id": "tracing_assets",
        "domain_code": "S2D12",
        "domain_name": "S2D12 · Tracing Illicit Transactions & Assets",
        "context": "CFE Exam 2026 S2D12 — Tracing Illicit Transactions and Assets. Topics: net worth method (assets vs liabilities over time), expenditure method (spending vs known income), bank deposit method, specific item method, asset search techniques (real property, vehicles, financial accounts), corporate ownership tracing (layered entities), wire transfer tracing, cryptocurrency tracing and blockchain analytics, FBAR/FATCA data in asset tracing, international asset recovery."
    }
]

METODO_NEXOR = """
MÉTODO NEXOR DE FORMULAÇÃO — APLICAR OBRIGATORIAMENTE:
- Cenário profissional realista no stem (Standard/Hard)
- Lead-in como pergunta completa e focada
- 4 opções de comprimento homogêneo
- Opção correta NUNCA a mais longa
- Distrátores genuinamente plausíveis
- Sem absolutos (sempre/nunca/todos)
- Proibido "todas as anteriores" / "nenhuma das anteriores"
- justification_correct: explica o PRINCÍPIO técnico/legal
- justification_wrong: explica cada distrator especificamente
- US law scope only. No Brazilian law.
"""

LANG_CONFIG = {
    "pt": "Portugues (Brasil)",
    "es": "Espanol neutro latinoamericano",
}

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

def generate_block(client, domain, level, topics_done, num_start, block_size=10):
    """Gera um bloco de 10 questoes EN."""

    # Distribuicao por nivel
    if level == "EASY":
        difficulty_instruction = "EASY (Bloom 1-2): Direct definition or basic concept identification. Simple stem, no scenario needed."
    elif level == "STANDARD":
        difficulty_instruction = "STANDARD (Bloom 3): Application in a realistic professional scenario. Present situation then ask what the CFE should do."
    else:
        difficulty_instruction = "HARD (Bloom 4-5): Complex scenario with multiple variables, competing considerations, or ambiguous facts requiring analysis."

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

DOMAIN: {domain['domain_name']}
CONTEXT: {domain['context']}

{METODO_NEXOR}

DIFFICULTY FOR THIS BLOCK: {level}
{difficulty_instruction}

Generate exactly {block_size} questions.
Start numbering from num={num_start}.
Cover DIFFERENT topics — avoid repeating: {', '.join(list(topics_done)[:15]) if topics_done else 'none yet'}

Return ONLY valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full question text",
  "tag": "snake_case_topic_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "{level}",
  "justification_correct": "Detailed principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

    result = call_api(client, prompt)
    for i, q in enumerate(result):
        q["num"] = num_start + i
        q["difficulty"] = level
    return result

def translate_block(client, questions, lang_name):
    """Traduz um bloco de 10 questoes."""
    prompt = f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: text, options, justification_correct, justification_wrong
2. DO NOT modify: num, tag, correct, difficulty
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep legal terms in English: FCPA, SOX, RICO, BSA, SAR, CTR, NACHA, etc.
5. Return ONLY JSON array, no markdown

Input:
{json.dumps(questions, ensure_ascii=False, indent=2)}"""

    result = call_api(client, prompt)
    for i, q in enumerate(result):
        if i < len(questions):
            q["num"]        = questions[i]["num"]
            q["tag"]        = questions[i]["tag"]
            q["correct"]    = questions[i]["correct"]
            q["difficulty"] = questions[i]["difficulty"]
    return result

def generate_quiz(client, domain):
    """Gera quiz_001 completo para um dominio."""
    print(f"\n  {domain['domain_code']} · {domain['domain_name']}")
    print(f"  {'─'*60}")

    all_en = []
    topics_done = set()

    # Bloco 1: 10 EASY (Q1-Q10)
    print(f"  Bloco 1/5 · EASY (Q1-Q10)... ", end="", flush=True)
    try:
        qs = generate_block(client, domain, "EASY", topics_done, 1)
        all_en.extend(qs)
        for q in qs: topics_done.add(q.get("tag",""))
        print(f"OK ({len(qs)}q)")
    except Exception as e:
        print(f"ERRO: {e}")
        return False

    # Blocos 2-4: 30 STANDARD (Q11-Q40)
    for bloco_num, num_start in [(2, 11), (3, 21), (4, 31)]:
        label = f"STANDARD (Q{num_start}-Q{num_start+9})"
        print(f"  Bloco {bloco_num}/5 · {label}... ", end="", flush=True)
        try:
            qs = generate_block(client, domain, "STANDARD", topics_done, num_start)
            all_en.extend(qs)
            for q in qs: topics_done.add(q.get("tag",""))
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            print(f"ERRO: {e}")
            return False

    # Bloco 5: 10 HARD (Q41-Q50)
    print(f"  Bloco 5/5 · HARD (Q41-Q50)... ", end="", flush=True)
    try:
        qs = generate_block(client, domain, "HARD", topics_done, 41)
        all_en.extend(qs)
        print(f"OK ({len(qs)}q)")
    except Exception as e:
        print(f"ERRO: {e}")
        return False

    # Renumera
    for i, q in enumerate(all_en):
        q["num"] = i + 1

    if len(all_en) < 40:
        print(f"  INSUFICIENTE: apenas {len(all_en)}q — pulando")
        return False

    # Salva EN
    en_path = Path(QUIZZES_DIR) / domain["domain_id"] / "quiz_001_en.json"
    quiz_en = {
        "cert_id":     "cfe",
        "domain_id":   domain["domain_id"],
        "domain_code": domain["domain_code"],
        "quiz_num":    1,
        "domain_name": domain["domain_name"],
        "cert_name":   "Certified Fraud Examiner",
        "lang":        "en",
        "questions":   all_en
    }
    save_json(str(en_path), quiz_en)
    print(f"  EN: {len(all_en)}q salvo ✅")

    # Traduz PT e ES em blocos de 10
    for lang_code, lang_name in LANG_CONFIG.items():
        print(f"  {lang_code.upper()}: traduzindo em blocos... ", end="", flush=True)
        translated = []
        for i in range(0, len(all_en), 10):
            bloco = all_en[i:i+10]
            try:
                t = translate_block(client, bloco, lang_name)
                translated.extend(t)
                print(".", end="", flush=True)
            except Exception as e:
                print(f"ERR({e})", end="", flush=True)
                translated.extend(bloco)

        for i, q in enumerate(translated):
            q["num"] = i + 1

        lang_path = Path(QUIZZES_DIR) / domain["domain_id"] / f"quiz_001_{lang_code}.json"
        quiz_lang = {**quiz_en, "lang": lang_code, "questions": translated}
        save_json(str(lang_path), quiz_lang)
        print(f" {len(translated)}q ✅")

    return True

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR 25 DOMINIOS VAZIOS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Blocos de 10q · FractalLearning v1")
    print(f"  10 Easy + 30 Standard + 10 Hard = 50q por dominio")
    print("=" * 70)

    client = anthropic.Anthropic()

    ok = 0
    falhou = []

    for i, domain in enumerate(DOMINIOS):
        print(f"\n  [{i+1}/{len(DOMINIOS)}]", end="")
        success = generate_quiz(client, domain)
        if success:
            ok += 1
        else:
            falhou.append(domain["domain_id"])

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(DOMINIOS)} dominios gerados")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
