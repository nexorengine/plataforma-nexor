"""
NEXOR -- GERADOR FLASHCARDS CFE -- TODOS OS DOMINIOS v1
Gera 50 flashcards EN para cada dominio CFE.
Pula dominios que ja tem flashcards.
Blocos de 10 cards por chamada -- sem truncamento.

USO:
    python gerar_flashcards_todos.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

QUIZZES_DIR   = r"static\quizzes\cfe"
FLASHCARD_DIR = r"static\flashcards\cfe"
MODEL         = "claude-sonnet-4-5"
MAX_TOKENS    = 8192

# 45 dominios (exclui corruption_bribery que ja tem)
DOMINIOS = [
    {"domain_id":"accounting_concepts","domain_code":"S1D01","domain_name":"S1D01 · Accounting Concepts & Financial Analysis","context":"CFE Exam 2026 — Accounting equation, balance sheet, income statement, cash flow, GAAP vs IFRS, accrual vs cash basis, financial ratios, red flags in financial statements, horizontal and vertical analysis."},
    {"domain_id":"auditor_responsibilities","domain_code":"S3D04","domain_name":"S3D04 · Management & Auditors Responsibilities","context":"CFE Exam 2026 — Management duty of care, internal audit function, external auditor fraud detection (SAS 99/ISA 240), audit committee oversight, CFE vs CPA roles, management override, Sarbanes-Oxley auditor requirements."},
    {"domain_id":"bankruptcy_fraud","domain_code":"S1D14","domain_name":"S1D14 · Bankruptcy Fraud","context":"CFE Exam 2026 — Bankruptcy fraud schemes, concealment of assets, false statements, fraudulent transfers, preference payments, bankruptcy trustee role, 18 USC 152, red flags."},
    {"domain_id":"cash_receipts_fraud","domain_code":"S1D03","domain_name":"S1D03 · Asset Misappropriation — Cash Receipts","context":"CFE Exam 2026 — Skimming, cash larceny, fraudulent write-offs, register disbursements, check tampering in receivables, accounts receivable lapping, detection methods."},
    {"domain_id":"collecting_evidence","domain_code":"S2D09","domain_name":"S2D09 · Collecting Evidence","context":"CFE Exam 2026 — Evidence collection methods, document requests, subpoenas, search warrants, digital evidence collection, chain of custody, preserving electronic evidence, interview as evidence."},
    {"domain_id":"consumer_fraud","domain_code":"S1D13","domain_name":"S1D13 · Consumer Fraud & Scams","context":"CFE Exam 2026 — Telemarketing fraud, advance fee schemes, lottery scams, charity fraud, identity theft targeting consumers, elder fraud, FTC enforcement, consumer protection laws."},
    {"domain_id":"corporate_governance","domain_code":"S3D03","domain_name":"S3D03 · Corporate Governance","context":"CFE Exam 2026 — Board of directors responsibilities, audit committee role, Sarbanes-Oxley key provisions, COSO framework, internal control components, tone at the top, governance best practices."},
    {"domain_id":"covert_operations","domain_code":"S2D14","domain_name":"S2D14 · Covert Operations","context":"CFE Exam 2026 — Undercover investigations, physical surveillance, electronic surveillance, entrapment standard, sting operations, privacy law, documentation standards, chain of custody."},
    {"domain_id":"criminal_behavior","domain_code":"S3D01","domain_name":"S3D01 · Understanding Criminal Behavior","context":"CFE Exam 2026 — Fraud Triangle (Cressey), Fraud Diamond (Wolfe/Hermanson), occupational vs organizational fraud, white-collar crime theories (Sutherland), moral disengagement, psychological profiles."},
    {"domain_id":"criminal_prosecutions","domain_code":"S2D05","domain_name":"S2D05 · Criminal Prosecutions","context":"CFE Exam 2026 — Elements of criminal fraud, grand jury process, indictment vs information, plea agreements, Federal Sentencing Guidelines, corporate criminal liability, DPA and NPA agreements."},
    {"domain_id":"data_analysis_tools","domain_code":"S2D11","domain_name":"S2D11 · Data Analysis & Reporting Tools","context":"CFE Exam 2026 — Benford Law, statistical sampling, regression analysis, data matching, ACL/IDEA software, AI in fraud detection, network analysis, continuous monitoring, gap and boundary testing."},
    {"domain_id":"data_theft_ip","domain_code":"S1D07","domain_name":"S1D07 · Theft of Data & Intellectual Property","context":"CFE Exam 2026 — Trade secret theft, Economic Espionage Act, DTSA, insider threats, data exfiltration methods, digital forensics, employee monitoring, non-compete agreements."},
    {"domain_id":"emerging_fraud","domain_code":"S1D20","domain_name":"S1D20 · Emerging Fraud & Technology","context":"CFE Exam 2026 — Cryptocurrency fraud, NFT scams, AI-generated deepfakes, metaverse fraud, supply chain attacks, synthetic identity fraud, emerging payment fraud, regulatory gaps."},
    {"domain_id":"ethics_fraud_examiners","domain_code":"S3D09","domain_name":"S3D09 · Ethics for Fraud Examiners","context":"CFE Exam 2026 — ACFE Code of Ethics (integrity, objectivity, confidentiality, competency), conflicts of interest, independence, professional skepticism, ACFE disciplinary process."},
    {"domain_id":"evidence_principles","domain_code":"S2D08","domain_name":"S2D08 · Basic Principles of Evidence","context":"CFE Exam 2026 — Direct vs circumstantial evidence, admissibility standards, hearsay rule and exceptions, best evidence rule, authentication, chain of custody, spoliation, Federal Rules of Evidence."},
    {"domain_id":"expert_witness","domain_code":"S2D16","domain_name":"S2D16 · Testifying as Expert Witness","context":"CFE Exam 2026 — Expert qualification standards, Daubert standard, Frye standard, direct examination, cross-examination, deposition preparation, court-appointed experts (Rule 706), litigation support reports."},
    {"domain_id":"financial_institution_fraud","domain_code":"S1D09","domain_name":"S1D09 · Financial Institution Fraud & Money Laundering","context":"CFE Exam 2026 — Bank fraud (18 USC 1344), mortgage fraud, money laundering stages, structuring/smurfing, BSA requirements, CTR/SAR filing, FinCEN, FATF recommendations, cryptocurrency AML."},
    {"domain_id":"financial_statement_fraud","domain_code":"S1D02","domain_name":"S1D02 · Financial Statement Fraud","context":"CFE Exam 2026 — Revenue recognition fraud, fictitious revenues, improper asset valuation, concealed liabilities, Beneish M-Score, Altman Z-Score, channel stuffing, round-tripping, audit red flags."},
    {"domain_id":"fraud_investigation","domain_code":"S2D01","domain_name":"S2D01 · Fraud Investigation","context":"CFE Exam 2026 — Investigation planning, hypothesis development, document examination, interview techniques, evidence collection, report writing, working with legal counsel, law enforcement coordination."},
    {"domain_id":"fraud_prevention_programs","domain_code":"S3D07","domain_name":"S3D07 · Fraud Prevention Programs","context":"CFE Exam 2026 — Anti-fraud program components, hotlines and whistleblower programs, background checks, job rotation, mandatory vacations, surprise audits, fraud awareness training."},
    {"domain_id":"fraud_risk_assessment","domain_code":"S3D05","domain_name":"S3D05 · Fraud Risk Assessment","context":"CFE Exam 2026 — Fraud risk assessment methodology, inherent vs residual risk, fraud risk factors (pressure, opportunity, rationalization), COSO ERM framework, risk matrices, fraud scenarios."},
    {"domain_id":"fraud_risk_management","domain_code":"S3D08","domain_name":"S3D08 · Fraud Risk Management","context":"CFE Exam 2026 — Enterprise fraud risk management, fraud response plan, incident response, remediation, fidelity bonds, crime insurance, continuous monitoring, KRIs, board reporting."},
    {"domain_id":"fraudulent_disbursements","domain_code":"S1D04","domain_name":"S1D04 · Asset Misappropriation — Disbursements","context":"CFE Exam 2026 — Billing schemes (shell companies, pass-through), payroll fraud (ghost employees), expense reimbursement fraud, check tampering (forged signatures, altered payees), detection methods."},
    {"domain_id":"government_fraud","domain_code":"S1D17","domain_name":"S1D17 · Government & Public Sector Fraud","context":"CFE Exam 2026 — False Claims Act, Medicare/Medicaid fraud, public corruption (18 USC 666), grant fraud, procurement fraud in government, qui tam provisions, government contractor fraud."},
    {"domain_id":"healthcare_fraud","domain_code":"S1D16","domain_name":"S1D16 · Health Care Fraud","context":"CFE Exam 2026 — Medicare/Medicaid fraud schemes, upcoding, unbundling, phantom billing, kickbacks (Anti-Kickback Statute), Stark Law violations, False Claims Act in healthcare, OIG exclusions."},
    {"domain_id":"identity_theft_cyberfraud","domain_code":"S1D08","domain_name":"S1D08 · Identity Theft & Cyberfraud","context":"CFE Exam 2026 — Identity theft (18 USC 1028), phishing/spear phishing, social engineering, BEC schemes, ransomware, deepfake fraud, SIM swapping, account takeover, cybercrime investigation."},
    {"domain_id":"individual_rights","domain_code":"S2D07","domain_name":"S2D07 · Individual Rights During Examinations","context":"CFE Exam 2026 — Fifth Amendment privilege, Miranda in private investigations, Weingarten rights, Garrity rights, attorney-client privilege, Dodd-Frank whistleblower protections, SOX Section 806."},
    {"domain_id":"insurance_fraud","domain_code":"S1D12","domain_name":"S1D12 · Insurance Fraud","context":"CFE Exam 2026 — Property/casualty fraud, workers compensation fraud, healthcare insurance fraud, arson for profit, staged accidents, soft fraud vs hard fraud, SIU investigations, red flags."},
    {"domain_id":"international_fraud","domain_code":"S1D19","domain_name":"S1D19 · International & Cross-Border Fraud","context":"CFE Exam 2026 — FCPA anti-bribery and accounting provisions, third-party due diligence, UK Bribery Act, OECD Convention, FATF, cross-border money laundering, MLAT, offshore shell companies."},
    {"domain_id":"interview_techniques","domain_code":"S2D13","domain_name":"S2D13 · Interview Theory & Application","context":"CFE Exam 2026 — Cognitive interview techniques, Reid technique, PEACE model, admission-seeking interviews, kinesics and non-verbal cues, written statements, legal considerations, Miranda warnings."},
    {"domain_id":"inventory_fraud","domain_code":"S1D05","domain_name":"S1D05 · Asset Misappropriation — Inventory & Assets","context":"CFE Exam 2026 — Inventory theft, false receiving reports, fictitious inventory, non-cash asset misappropriation, misuse of company resources, detection methods, physical count reconciliation."},
    {"domain_id":"investigation_planning","domain_code":"S2D01","domain_name":"S2D01 · Planning & Conducting Fraud Examination","context":"CFE Exam 2026 — Fraud examination vs audit, scope definition, predication requirements, conflict of interest checks, team assembly, confidentiality, legal counsel coordination, law enforcement liaison."},
    {"domain_id":"law_cfe","domain_code":"S2D03","domain_name":"S2D03 · Law Related to Fraud","context":"CFE Exam 2026 — Federal fraud statutes (wire fraud, mail fraud, bank fraud, RICO), computer fraud (CFAA), money laundering statutes, conspiracy, aiding and abetting, statutes of limitations."},
    {"domain_id":"legal_issues_investigations","domain_code":"S2D02","domain_name":"S2D02 · Legal Issues in Investigations","context":"CFE Exam 2026 — Employee rights in workplace investigations, privacy expectations, lawful monitoring, search and seizure in private sector, defamation risks, legal holds, attorney-client privilege."},
    {"domain_id":"legal_system_overview","domain_code":"S2D04","domain_name":"S2D04 · Overview of the Legal System","context":"CFE Exam 2026 — Federal vs state court systems, civil vs criminal proceedings, burden of proof standards, discovery process, rules of evidence, expert witness role, settlement vs trial."},
    {"domain_id":"non_criminal_actions","domain_code":"S2D06","domain_name":"S2D06 · Non-Criminal Actions","context":"CFE Exam 2026 — Civil fraud claims, compensatory vs punitive damages, disgorgement, civil RICO, SEC enforcement, debarment, civil False Claims Act (qui tam), asset freezing, civil forfeiture."},
    {"domain_id":"occupational_fraud","domain_code":"S3D02","domain_name":"S3D02 · Occupational Fraud","context":"CFE Exam 2026 — ACFE Report to the Nations, fraud by category (asset misappropriation vs corruption vs financial statement), fraud by industry and organization size, detection methods comparison."},
    {"domain_id":"payment_fraud","domain_code":"S1D11","domain_name":"S1D11 · Payment Fraud","context":"CFE Exam 2026 — Check fraud, ACH fraud, wire transfer fraud, credit card fraud, payment card skimming, BEC wire transfer schemes, NACHA rules, real-time payment fraud, detection controls."},
    {"domain_id":"prevention_deterrence","domain_code":"S3D06","domain_name":"S3D06 · Internal Controls & Anti-Fraud Programs","context":"CFE Exam 2026 — COSO internal control framework, segregation of duties, authorization controls, reconciliation controls, physical safeguards, IT general controls, control testing, PCAOB standards."},
    {"domain_id":"procurement_contract_fraud","domain_code":"S1D18","domain_name":"S1D18 · Procurement & Contract Fraud","context":"CFE Exam 2026 — Bid rigging (complementary bidding, suppression, rotation), specification rigging, sole source abuse, cost mischarging, defective pricing (TINA), product substitution, change order fraud."},
    {"domain_id":"report_writing","domain_code":"S2D15","domain_name":"S2D15 · Report Writing","context":"CFE Exam 2026 — Fraud examination report structure, statement of facts vs legal conclusions, avoiding defamation, expert opinion standards, litigation support reports, confidentiality, audience-appropriate formats."},
    {"domain_id":"securities_fraud","domain_code":"S1D10","domain_name":"S1D10 · Securities & Investment Fraud","context":"CFE Exam 2026 — Ponzi schemes, pump and dump, insider trading (SEC Rule 10b-5), market manipulation, investment adviser fraud, affinity fraud, SEC enforcement, Dodd-Frank whistleblower."},
    {"domain_id":"sources_information","domain_code":"S2D10","domain_name":"S2D10 · Sources of Information","context":"CFE Exam 2026 — Public records (court, corporate filings, SEC EDGAR), nonpublic records access, social media evidence, OSINT, dark web intelligence, skip tracing, international records."},
    {"domain_id":"tax_fraud","domain_code":"S1D15","domain_name":"S1D15 · Tax Fraud","context":"CFE Exam 2026 — Tax evasion vs avoidance, unreported income, false deductions, offshore tax schemes, employment tax fraud, IRS criminal investigation, net worth method, voluntary disclosure."},
    {"domain_id":"tracing_assets","domain_code":"S2D12","domain_name":"S2D12 · Tracing Illicit Transactions & Assets","context":"CFE Exam 2026 — Net worth method, expenditure method, bank deposit method, asset search techniques, corporate ownership tracing, wire transfer tracing, cryptocurrency analytics, FBAR/FATCA, international asset recovery."},
]

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

def generate_block(client, domain, num_start):
    prompt = f"""You are an expert CFE exam flashcard writer.

DOMAIN: {domain['domain_name']}
CONTEXT: {domain['context']}

Create exactly 10 flashcards for CFE exam preparation.
Start numbering from id={num_start}.

RULES:
- FRONT: Clear concise question or term (max 120 chars)
- BACK: Precise definition/answer (2-4 sentences) + practical example when useful
- Cover DIFFERENT topics across the 10 cards
- Keep legal terms in English: FCPA, SOX, RICO, BSA, SAR, CFE, GAAP, etc.
- Focus on what CFE candidates need for the exam

Return ONLY valid JSON array, no markdown:
[{{
  "id": {num_start},
  "topic": "snake_case_topic",
  "front": {{"en": "Question or term"}},
  "back": {{"en": "Definition and example"}}
}}]"""

    result = call_api(client, prompt)
    for i, card in enumerate(result):
        card["id"] = num_start + i
    return result

def generate_domain_flashcards(client, domain):
    out_path = Path(FLASHCARD_DIR) / domain["domain_id"] / "flashcards_en.json"

    # Pula se ja existe
    if out_path.exists():
        data = json.load(open(str(out_path), encoding="utf-8"))
        if len(data.get("cards", [])) >= 45:
            print(f"  SKIP {domain['domain_code']} (ja tem {len(data['cards'])} cards)")
            return True

    print(f"\n  {domain['domain_code']} · {domain['domain_id']}")
    all_cards = []

    for i in range(5):
        num_start = i * 10 + 1
        end = num_start + 9
        print(f"  Bloco {i+1}/5 · Card {num_start}-{end}... ", end="", flush=True)
        try:
            cards = generate_block(client, domain, num_start)
            all_cards.extend(cards)
            print(f"OK ({len(cards)})")
        except Exception as e:
            print(f"ERRO: {e}")
            return False

    for i, card in enumerate(all_cards):
        card["id"] = i + 1

    save_json(str(out_path), {
        "cert_id":     "cfe",
        "domain_id":   domain["domain_id"],
        "domain_code": domain["domain_code"],
        "domain_name": domain["domain_name"],
        "lang":        "en",
        "total":       len(all_cards),
        "cards":       all_cards
    })
    print(f"  EN: {len(all_cards)} cards salvos ✅")
    return True

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR FLASHCARDS CFE -- TODOS OS DOMINIOS v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  {len(DOMINIOS)} dominios · 50 cards cada · Blocos de 10")
    print("=" * 70)

    client = anthropic.Anthropic()
    ok = 0
    falhou = []

    for i, domain in enumerate(DOMINIOS):
        print(f"\n  [{i+1}/{len(DOMINIOS)}]", end="")
        if generate_domain_flashcards(client, domain):
            ok += 1
        else:
            falhou.append(domain["domain_id"])

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(DOMINIOS)} dominios")
    if falhou:
        print(f"  FALHARAM: {', '.join(falhou)}")
    print(f"  Proximo: python traduzir_flashcards_todos_pt.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
