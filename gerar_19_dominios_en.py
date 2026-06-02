"""
NEXOR -- GERADOR 19 DOMINIOS CFE -- APENAS EN v1
Gera quiz_001_en.json para os 19 dominios CFE vazios.
Blocos de 10 questoes por chamada -- sem truncamento.
FractalLearning v1: 10 Easy + 30 Standard + 10 Hard = 50q

USO:
    python gerar_19_dominios_en.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

DOMINIOS = [
    {
        "domain_id": "ethics_fraud_examiners",
        "domain_code": "S3D09",
        "domain_name": "S3D09 · Ethics for Fraud Examiners",
        "context": "CFE Exam 2026 S3D09 — Ethics for Fraud Examiners. ACFE Code of Professional Ethics: integrity, objectivity, confidentiality, competency. Confidentiality obligations and exceptions. Independence and objectivity. Conflicts of interest. Professional competence. Professional skepticism. Ethical decision-making frameworks. ACFE disciplinary process and sanctions."
    },
    {
        "domain_id": "evidence_principles",
        "domain_code": "S2D08",
        "domain_name": "S2D08 · Basic Principles of Evidence",
        "context": "CFE Exam 2026 S2D08 — Basic Principles of Evidence. Direct vs circumstantial vs documentary evidence. Admissibility standards. Hearsay rule and exceptions (business records, admissions). Best evidence rule. Authentication requirements. Chain of custody. Spoliation of evidence. Federal Rules of Evidence key provisions."
    },
    {
        "domain_id": "expert_witness",
        "domain_code": "S2D16",
        "domain_name": "S2D16 · Testifying as Expert Witness",
        "context": "CFE Exam 2026 S2D16 — Testifying as Expert Witness. Expert qualification standards. Daubert standard (federal courts). Frye standard (general acceptance). Direct examination techniques. Cross-examination preparation. Deposition preparation. Maintaining objectivity. Court-appointed experts (Rule 706). Report writing for litigation support."
    },
    {
        "domain_id": "financial_institution_fraud",
        "domain_code": "S1D09",
        "domain_name": "S1D09 · Financial Institution Fraud & Money Laundering",
        "context": "CFE Exam 2026 S1D09 — Financial Institution Fraud and Money Laundering. Bank fraud (18 USC 1344). Mortgage fraud. Credit card fraud. Money laundering stages (placement/layering/integration). Structuring/smurfing. BSA requirements (CTR $10k threshold, SAR filing). FinCEN. FATF 40 recommendations. Cryptocurrency money laundering."
    },
    {
        "domain_id": "fraud_risk_management",
        "domain_code": "S3D08",
        "domain_name": "S3D08 · Fraud Risk Management",
        "context": "CFE Exam 2026 S3D08 — Fraud Risk Management. Enterprise fraud risk management framework. Fraud response plan. Incident response triggers. Remediation after fraud. Lessons learned. Fidelity bonds and crime insurance. Cyber insurance. Continuous monitoring. Fraud risk indicators (KRIs). Board-level fraud risk reporting."
    },
    {
        "domain_id": "fraudulent_disbursements",
        "domain_code": "S1D04",
        "domain_name": "S1D04 · Asset Misappropriation — Disbursements",
        "context": "CFE Exam 2026 S1D04 — Asset Misappropriation Fraudulent Disbursements. Billing schemes (shell companies, personal purchases, pass-through). Payroll fraud (ghost employees, falsified wages, commission schemes). Expense reimbursement fraud. Check tampering (forged signatures, altered payees). Pay-and-return schemes. Detection methods and internal controls."
    },
    {
        "domain_id": "identity_theft_cyberfraud",
        "domain_code": "S1D08",
        "domain_name": "S1D08 · Identity Theft & Cyberfraud",
        "context": "CFE Exam 2026 S1D08 — Identity Theft and Cyberfraud. Identity theft (18 USC 1028). Phishing/spear phishing/whaling. Social engineering. Business email compromise (BEC). Ransomware. Deepfake fraud. SIM swapping. Account takeover. Cybercrime prevention. Digital evidence in cybercrime investigations."
    },
    {
        "domain_id": "individual_rights",
        "domain_code": "S2D07",
        "domain_name": "S2D07 · Individual Rights During Examinations",
        "context": "CFE Exam 2026 S2D07 — Individual Rights During Examinations. Fifth Amendment privilege. Miranda rights in private investigations. Weingarten rights (union representation). Garrity rights (public employees). Attorney-client privilege. Dodd-Frank whistleblower protections. SOX Section 806 protections. Employee cooperation duties. Compelled statements and use immunity."
    },
    {
        "domain_id": "international_fraud",
        "domain_code": "S1D19",
        "domain_name": "S1D19 · International & Cross-Border Fraud",
        "context": "CFE Exam 2026 S1D19 — International and Cross-Border Fraud. FCPA anti-bribery and accounting provisions. Third-party liability and due diligence. OECD Anti-Bribery Convention. UK Bribery Act (broader than FCPA). FATF recommendations. Cross-border money laundering. Mutual Legal Assistance Treaties (MLAT). Offshore financial centers and shell companies."
    },
    {
        "domain_id": "inventory_fraud",
        "domain_code": "S1D05",
        "domain_name": "S1D05 · Asset Misappropriation — Inventory & Assets",
        "context": "CFE Exam 2026 S1D05 — Asset Misappropriation Inventory and Other Assets. Inventory theft and misuse. Purchasing and receiving fraud. False inventory counts. Non-cash asset misappropriation (equipment, IP). Misuse of company resources. Detection methods (physical counts, reconciliations). Internal controls for inventory."
    },
    {
        "domain_id": "investigation_planning",
        "domain_code": "S2D01",
        "domain_name": "S2D01 · Planning & Conducting Fraud Examination",
        "context": "CFE Exam 2026 S2D01 — Planning and Conducting a Fraud Examination. Difference between fraud examination and financial audit. Scope definition. Conflict of interest checks. Team assembly. Hypothesis development. Predication requirements. Confidentiality requirements. Coordination with legal counsel and law enforcement."
    },
    {
        "domain_id": "legal_issues_investigations",
        "domain_code": "S2D02",
        "domain_name": "S2D02 · Legal Issues in Investigations",
        "context": "CFE Exam 2026 S2D02 — Legal Issues in Investigations. Employee rights during workplace investigations. Privacy expectations. Lawful monitoring of employees. Search and seizure (Fourth Amendment in private sector). Defamation risks in investigations. Legal holds and document preservation. Attorney-client privilege in corporate investigations."
    },
    {
        "domain_id": "non_criminal_actions",
        "domain_code": "S2D06",
        "domain_name": "S2D06 · Non-Criminal Actions",
        "context": "CFE Exam 2026 S2D06 — Non-Criminal Actions Civil and Administrative. Civil fraud claims and elements. Compensatory vs punitive damages. Disgorgement. Injunctive relief. Civil RICO (treble damages). SEC enforcement actions. Debarment. Civil False Claims Act (qui tam). Asset freezing orders. Civil forfeiture."
    },
    {
        "domain_id": "occupational_fraud",
        "domain_code": "S3D02",
        "domain_name": "S3D02 · Occupational Fraud",
        "context": "CFE Exam 2026 S3D02 — Occupational Fraud. ACFE Report to the Nations statistics. Fraud by category (asset misappropriation vs corruption vs financial statement). Fraud by industry and organization size. Fraud by perpetrator position and tenure. Detection method comparison (tips vs internal audit vs management review). Cost of fraud. Anti-fraud control effectiveness."
    },
    {
        "domain_id": "procurement_contract_fraud",
        "domain_code": "S1D18",
        "domain_name": "S1D18 · Procurement & Contract Fraud",
        "context": "CFE Exam 2026 S1D18 — Procurement and Contract Fraud. Bid manipulation (complementary bidding, bid suppression, rotation). Specification rigging. Sole source abuse. Cost mischarging. Defective pricing (TINA). Product substitution. Subcontractor pass-through. Change order fraud. False claims in contract performance."
    },
    {
        "domain_id": "report_writing",
        "domain_code": "S2D15",
        "domain_name": "S2D15 · Report Writing",
        "context": "CFE Exam 2026 S2D15 — Report Writing. Structure of fraud examination report (executive summary, body, conclusions, exhibits). Statement of facts vs legal conclusions. Avoiding defamatory statements. Expert opinion standards. Litigation support report requirements. Confidentiality. Audience-appropriate formats. Documenting findings with supporting evidence."
    },
    {
        "domain_id": "securities_fraud",
        "domain_code": "S1D10",
        "domain_name": "S1D10 · Securities & Investment Fraud",
        "context": "CFE Exam 2026 S1D10 — Securities and Investment Fraud. Ponzi schemes. Pyramid schemes vs legitimate MLM. Pump and dump schemes. Insider trading (SEC Rule 10b-5, material nonpublic information). Market manipulation. Investment adviser fraud. Affinity fraud. SEC enforcement powers. Madoff case study. Dodd-Frank Section 922 whistleblower."
    },
    {
        "domain_id": "sources_information",
        "domain_code": "S2D10",
        "domain_name": "S2D10 · Sources of Information",
        "context": "CFE Exam 2026 S2D10 — Sources of Information. Public records (court, corporate filings, property, SEC EDGAR). Nonpublic records access (bank, credit, employment). Social media evidence collection. OSINT techniques and tools. Dark web intelligence. International records access. Skip tracing. Interviewing as information source."
    },
    {
        "domain_id": "tracing_assets",
        "domain_code": "S2D12",
        "domain_name": "S2D12 · Tracing Illicit Transactions & Assets",
        "context": "CFE Exam 2026 S2D12 — Tracing Illicit Transactions and Assets. Net worth method. Expenditure method. Bank deposit method. Specific item method. Asset search techniques. Corporate ownership tracing. Wire transfer tracing. Cryptocurrency tracing and blockchain analytics. FBAR/FATCA data. International asset recovery."
    }
]

METODO = """
NEXOR METHOD — APPLY:
- Professional scenario in stem (Standard/Hard)
- Complete focused lead-in question
- 4 homogeneous options in length
- Correct answer is NOT the longest
- Genuinely plausible distractors
- No absolutes (always/never/all)
- No "all of the above" / "none of the above"
- justification_correct: explains the technical/legal PRINCIPLE
- justification_wrong: explains each distractor specifically
- US law scope only
"""

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

def generate_block(client, domain, level, num_start, used_tags):
    tags_str = ", ".join(list(used_tags)[:15]) if used_tags else "none"

    if level == "EASY":
        diff_desc = "EASY (Bloom 1-2): Direct definition or basic concept. Simple stem, no scenario needed."
    elif level == "STANDARD":
        diff_desc = "STANDARD (Bloom 3): Application in realistic professional scenario. Present situation then ask what the CFE should do."
    else:
        diff_desc = "HARD (Bloom 4-5): Complex scenario with multiple variables requiring analysis."

    prompt = f"""You are an expert CFE exam question writer.

DOMAIN: {domain['domain_name']}
CONTEXT: {domain['context']}

{METODO}

DIFFICULTY: {level}
{diff_desc}

Generate exactly 10 questions.
Start numbering from num={num_start}.
Cover DIFFERENT topics — avoid: {tags_str}

Return ONLY valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full question",
  "tag": "snake_case_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "{level}",
  "justification_correct": "Principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

    qs = call_api(client, prompt)
    for i, q in enumerate(qs):
        q["num"] = num_start + i
        q["difficulty"] = level
    return qs

def generate_domain(client, domain):
    print(f"\n  {domain['domain_code']} · {domain['domain_id']}")
    print(f"  {'─'*55}")

    all_qs = []
    used_tags = set()

    blocks = [
        ("EASY",     1,  "Q01-Q10"),
        ("STANDARD", 11, "Q11-Q20"),
        ("STANDARD", 21, "Q21-Q30"),
        ("STANDARD", 31, "Q31-Q40"),
        ("HARD",     41, "Q41-Q50"),
    ]

    for level, num_start, label in blocks:
        print(f"  Bloco {label} · {level}... ", end="", flush=True)
        try:
            qs = generate_block(client, domain, level, num_start, used_tags)
            all_qs.extend(qs)
            for q in qs:
                used_tags.add(q.get("tag", ""))
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            print(f"ERRO: {e}")
            return False

    if len(all_qs) < 45:
        print(f"  INSUFICIENTE: {len(all_qs)}q — pulando")
        return False

    for i, q in enumerate(all_qs):
        q["num"] = i + 1

    path = Path(QUIZZES_DIR) / domain["domain_id"] / "quiz_001_en.json"
    save_json(str(path), {
        "cert_id":     "cfe",
        "domain_id":   domain["domain_id"],
        "domain_code": domain["domain_code"],
        "quiz_num":    1,
        "domain_name": domain["domain_name"],
        "cert_name":   "Certified Fraud Examiner",
        "lang":        "en",
        "questions":   all_qs
    })
    print(f"  EN: {len(all_qs)}q salvo ✅")
    return True

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR 19 DOMINIOS CFE -- APENAS EN v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Blocos de 10q · 10 Easy + 30 Standard + 10 Hard")
    print("=" * 70)

    client = anthropic.Anthropic()
    ok = 0
    falhou = []

    for i, domain in enumerate(DOMINIOS):
        print(f"\n  [{i+1}/{len(DOMINIOS)}]", end="")
        if generate_domain(client, domain):
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
