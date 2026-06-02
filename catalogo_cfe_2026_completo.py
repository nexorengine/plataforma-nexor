"""
NEXOR -- CATALOGO CFE 2026 COMPLETO v1
Substitui o bloco CFE no server.py pela estrutura
completa de 45 dominios da nova estrutura ACFE 2026.

USO:
    python catalogo_cfe_2026_completo.py
"""

import shutil
from datetime import datetime

SERVER_FILE = "server.py"
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# Trecho atual do CFE no server.py (a ser substituido)
OLD_CFE_BLOCK = '''"cfe": {
        "id": "cfe", "version": "CFE 2026", "last_updated": "2026-06", "name": "CFE / ACFE", "icon": "🔍", "color": "#e74c3c",
        "exam_minutes": 150, "exam_questions": 500, "bilingual": True,
        "domains": [
            {"id": "fraud_investigation", "name": "Fraud Investigation",
             "context": "CFE Fraud Examiners Manual 2024 — Fraud Investigation. Topics: planning investigations, interviewing (Reid Technique, PEACE Model), obtaining evidence, surveillance, investigation reports, legal considerations, digital evidence, chain of custody."},
            {"id": "financial_transactions", "name": "Financial Transactions & Fraud Schemes",
             "context": "CFE Fraud Examiners Manual 2024 — Financial Transactions & Fraud Schemes. Topics: asset misappropriation, corruption, bribery, financial statement fraud, money laundering, Beneish M-Score, Benford Law, data analytics."},
            {"id": "law_cfe", "name": "Law — US Federal Law",
             "context": "CFE Fraud Examiners Manual 2026 — Law. Topics: US federal fraud statutes (wire fraud 18 USC 1343, mail fraud 18 USC 1341, money laundering 18 USC 1956), FCPA anti-bribery and accounting provisions, SOX whistleblower protections, RICO, BSA/AML, Dodd-Frank, False Claims Act, Federal Sentencing Guidelines, PCAOB, SEC enforcement, DOJ prosecution procedures, expert witness testimony."},
            {"id": "prevention_deterrence", "name": "Fraud Prevention & Deterrence",
             "context": "CFE Fraud Examiners Manual 2026 — Section 3: Fraud Prevention and Deterrence. Topics: Fraud Triangle and Diamond, occupational fraud statistics (ACFE Report to the Nations), corporate governance, board and audit committee responsibilities, management and auditor duties, fraud risk assessment (COSO), internal controls, anti-fraud programs, whistleblower hotlines, pre-employment screening, ethics for fraud examiners (ACFE Code)."},
            {"id": "data_theft_ip", "name": "Theft of Data & Intellectual Property",
             "context": "CFE Exam 2026 — Section 1 Domain S1D07: Theft of Data and Intellectual Property. Topics: trade secret definition and protection, Economic Espionage Act (EEA), Defend Trade Secrets Act (DTSA), methods of data exfiltration (USB, cloud, email), insider threat scenarios, foreign state-sponsored economic espionage, forensic evidence in IP theft, chain of custody for digital evidence, civil vs criminal remedies, cross-border IP theft jurisdiction."},
            {"id": "insurance_fraud", "name": "Insurance Fraud",
             "context": "CFE Exam 2026 — Section 1 Domain S1D12: Insurance Fraud. Topics: hard fraud vs soft fraud, premium diversion, staged accident schemes, arson for profit, workers compensation fraud, healthcare-related insurance fraud, life insurance fraud, multiple-claim fraud, disability fraud, Special Investigations Units (SIU), National Insurance Crime Bureau (NICB), Examination Under Oath (EUO), detection methods and civil/criminal remedies."},
            {"id": "consumer_fraud", "name": "Consumer Fraud & Scams",
             "context": "CFE Exam 2026 — Section 1 Domain S1D13: Consumer Fraud and Scams. Topics: advance fee fraud (419 fraud), romance scams, lottery and prize scams, elder fraud, grandparent scams, telemarketing fraud, charity fraud, investment fraud targeting consumers, online marketplace fraud, impersonation fraud, cryptocurrency consumer fraud, FTC Act Section 5, state consumer protection laws, restitution remedies."},
            {"id": "bankruptcy_fraud", "name": "Bankruptcy Fraud",
             "context": "CFE Exam 2026 — Section 1 Domain S1D14: Bankruptcy Fraud. Topics: bankruptcy fraud statutes (18 USC 152-157), asset concealment in petitions, false statements and oaths, bust-out schemes, fraudulent transfers (actual and constructive), preferential transfers, badges of fraud, US Trustee Program, Rule 2004 examination, phantom creditor schemes, offshore account concealment, civil and criminal remedies."},
            {"id": "tax_fraud", "name": "Tax Fraud",
             "context": "CFE Exam 2026 — Section 1 Domain S1D15: Tax Fraud. Topics: tax avoidance vs evasion, IRC Section 7201 (willful evasion), payroll tax fraud (trust fund), offshore tax evasion (FBAR/FATCA), tax preparer fraud, refund fraud (SIRF), abusive tax shelters, investigative methods (net worth, bank deposit, expenditure), IRS Criminal Investigation (IRS-CI), civil fraud penalty (IRC 6663), voluntary disclosure programs."},
            {"id": "government_fraud", "name": "Government & Public Sector Fraud",
             "context": "CFE Exam 2026 — Section 1 Domain S1D17: Government and Public Sector Fraud. Topics: procurement fraud (pre-award and post-award), grant fraud, benefits fraud (welfare, unemployment, disability, SNAP), public official corruption, False Claims Act qui tam provisions, debarment procedures, Inspector General role, Single Audit Act, Davis-Bacon Act, Anti-Kickback Act, GAO standards."},
            {"id": "emerging_fraud", "name": "Emerging Fraud & Technology",
             "context": "CFE Exam 2026 — Section 1 Domain S1D20: Emerging Fraud Schemes and Technology. Topics: deepfake fraud (CEO fraud, voice cloning), AI-generated documents, synthetic identity fraud, cryptocurrency fraud (rug pulls, pump and dump, DeFi exploits), NFT wash trading, blockchain analytics, ESG fraud (greenwashing, carbon credits), remote work fraud, supply chain technology fraud, dark web facilitated fraud, algorithmic manipulation."}
        ]
    },'''

# Novo bloco CFE completo com todos os 45 dominios
NEW_CFE_BLOCK = '''"cfe": {
        "id": "cfe", "version": "CFE 2026", "last_updated": "2026-06", "name": "CFE / ACFE", "icon": "🔍", "color": "#e74c3c",
        "exam_minutes": 375, "exam_questions": 310, "bilingual": True,
        "domains": [

            // ── SECAO 1: FRAUD SCHEMES AND FINANCIAL CRIMES ──────────────────
            {"id": "financial_transactions", "name": "S1 · Financial Transactions & Fraud Schemes",
             "context": "CFE Exam 2026 Section 1 — Financial Transactions and Fraud Schemes. Topics: accounting concepts, financial statement fraud (revenue recognition, channel stuffing, round-tripping), asset misappropriation (cash receipts, fraudulent disbursements, inventory), corruption and bribery, money laundering, securities fraud, payment fraud. Benford Law, Beneish M-Score, data analytics for detection."},
            {"id": "accounting_concepts", "name": "S1D01 · Accounting Concepts & Financial Analysis",
             "context": "CFE Exam 2026 S1D01 — Accounting Concepts and Financial Statement Analysis. Topics: accounting equation, balance sheet, income statement, cash flow statement, GAAP vs IFRS, accrual vs cash basis, financial ratios, management vs auditor responsibilities, red flags in financial statement analysis."},
            {"id": "financial_statement_fraud", "name": "S1D02 · Financial Statement Fraud",
             "context": "CFE Exam 2026 S1D02 — Financial Statement Fraud. Topics: revenue recognition manipulation, fictitious revenues, channel stuffing, round-tripping, concealed liabilities, improper asset valuation, timing differences, related party fraud, off-balance-sheet fraud, Beneish M-Score, Enron/WorldCom/HealthSouth case studies."},
            {"id": "cash_receipts_fraud", "name": "S1D03 · Asset Misappropriation — Cash Receipts",
             "context": "CFE Exam 2026 S1D03 — Asset Misappropriation Cash Receipts. Topics: skimming (unrecorded sales, understated receivables), cash larceny, fraudulent write-offs, register disbursement schemes, check tampering, accounts receivable lapping, detection methods."},
            {"id": "fraudulent_disbursements", "name": "S1D04 · Asset Misappropriation — Disbursements",
             "context": "CFE Exam 2026 S1D04 — Asset Misappropriation Fraudulent Disbursements. Topics: billing schemes (shell companies, personal purchases), payroll fraud (ghost employees, falsified wages), expense reimbursement fraud, check tampering, pay-and-return schemes, detection and internal controls."},
            {"id": "inventory_fraud", "name": "S1D05 · Asset Misappropriation — Inventory & Assets",
             "context": "CFE Exam 2026 S1D05 — Asset Misappropriation Inventory and Other Assets. Topics: inventory theft and misuse, purchasing and receiving schemes, false inventory counts, non-cash asset misappropriation, misuse of company resources, detection methods."},
            {"id": "corruption_bribery", "name": "S1D06 · Corruption, Bribery & Conflicts of Interest",
             "context": "CFE Exam 2026 S1D06 — Corruption Bribery and Conflicts of Interest. Topics: bribery schemes, kickbacks in procurement, bid rigging (complementary bidding, bid suppression, rotation), conflicts of interest, illegal gratuities, economic extortion, shell company corruption, Tyco case study."},
            {"id": "data_theft_ip", "name": "S1D07 · Theft of Data & Intellectual Property",
             "context": "CFE Exam 2026 S1D07 — Theft of Data and Intellectual Property. Topics: trade secret definition, Economic Espionage Act (EEA), Defend Trade Secrets Act (DTSA), data exfiltration methods, insider threats, foreign state-sponsored espionage, forensic evidence in IP theft, civil vs criminal remedies."},
            {"id": "identity_theft_cyberfraud", "name": "S1D08 · Identity Theft & Cyberfraud",
             "context": "CFE Exam 2026 S1D08 — Identity Theft and Cyberfraud. Topics: identity theft (18 USC 1028), phishing/spear phishing/whaling, social engineering, business email compromise (BEC), ransomware, deepfake fraud, SIM swapping, account takeover, cybercrime prevention."},
            {"id": "financial_institution_fraud", "name": "S1D09 · Financial Institution Fraud & Money Laundering",
             "context": "CFE Exam 2026 S1D09 — Financial Institution Fraud and Money Laundering. Topics: bank fraud (18 USC 1344), mortgage fraud, credit card fraud, money laundering (placement/layering/integration), structuring/smurfing, BSA/CTR/SAR requirements, FinCEN, FATF recommendations, cryptocurrency laundering."},
            {"id": "securities_fraud", "name": "S1D10 · Securities & Investment Fraud",
             "context": "CFE Exam 2026 S1D10 — Securities and Investment Fraud. Topics: Ponzi schemes, pyramid schemes, pump and dump, insider trading (SEC Rule 10b-5), market manipulation, investment adviser fraud, affinity fraud, SEC enforcement, Madoff case study."},
            {"id": "payment_fraud", "name": "S1D11 · Payment Fraud",
             "context": "CFE Exam 2026 S1D11 — Payment Fraud. Topics: ACH fraud, wire transfer fraud, check fraud (counterfeiting, alteration, washing), card-not-present fraud, payment diversion, vendor impersonation and invoice fraud, real-time payment fraud, overpayment scams."},
            {"id": "insurance_fraud", "name": "S1D12 · Insurance Fraud",
             "context": "CFE Exam 2026 S1D12 — Insurance Fraud. Topics: hard fraud vs soft fraud, premium diversion, staged accidents, arson for profit, workers compensation fraud, healthcare insurance fraud, life insurance fraud, SIU role, NICB resources, EUO procedures."},
            {"id": "consumer_fraud", "name": "S1D13 · Consumer Fraud & Scams",
             "context": "CFE Exam 2026 S1D13 — Consumer Fraud and Scams. Topics: advance fee fraud, romance scams, lottery scams, elder fraud, telemarketing fraud, charity fraud, online marketplace fraud, cryptocurrency consumer fraud, FTC Act Section 5."},
            {"id": "bankruptcy_fraud", "name": "S1D14 · Bankruptcy Fraud",
             "context": "CFE Exam 2026 S1D14 — Bankruptcy Fraud. Topics: 18 USC 152-157, asset concealment, false statements, bust-out schemes, fraudulent transfers, preferential transfers, badges of fraud, US Trustee Program, Rule 2004 examination."},
            {"id": "tax_fraud", "name": "S1D15 · Tax Fraud",
             "context": "CFE Exam 2026 S1D15 — Tax Fraud. Topics: IRC 7201, payroll tax fraud, offshore evasion (FBAR/FATCA), tax preparer fraud, refund fraud, net worth method, bank deposit method, IRS-CI, civil fraud penalty IRC 6663."},
            {"id": "healthcare_fraud", "name": "S1D16 · Health Care Fraud",
             "context": "CFE Exam 2026 S1D16 — Health Care Fraud. Topics: billing for services not rendered, upcoding, unbundling, kickbacks (Anti-Kickback Statute), Stark Law, Medicare/Medicaid fraud, False Claims Act in healthcare, HealthSouth case study."},
            {"id": "government_fraud", "name": "S1D17 · Government & Public Sector Fraud",
             "context": "CFE Exam 2026 S1D17 — Government and Public Sector Fraud. Topics: procurement fraud (pre/post-award), grant fraud, benefits fraud, public corruption, False Claims Act qui tam, debarment, Inspector General role, Single Audit Act."},
            {"id": "procurement_contract_fraud", "name": "S1D18 · Procurement & Contract Fraud",
             "context": "CFE Exam 2026 S1D18 — Procurement and Contract Fraud. Topics: bid manipulation, specification rigging, sole source abuse, cost mischarging, defective pricing (TINA), product substitution, subcontractor pass-through, change order fraud."},
            {"id": "international_fraud", "name": "S1D19 · International & Cross-Border Fraud",
             "context": "CFE Exam 2026 S1D19 — International and Cross-Border Fraud. Topics: FCPA anti-bribery and accounting provisions, facilitating payments exception, third party liability, OECD Anti-Bribery Convention, UK Bribery Act, FATF, cross-border money laundering, MLAT, offshore financial centers."},
            {"id": "emerging_fraud", "name": "S1D20 · Emerging Fraud & Technology",
             "context": "CFE Exam 2026 S1D20 — Emerging Fraud Schemes and Technology. Topics: deepfakes, AI-generated documents, synthetic identity fraud, cryptocurrency fraud (rug pulls, DeFi exploits), NFT wash trading, blockchain analytics, ESG fraud, remote work fraud, dark web fraud, algorithmic manipulation."},

            // ── SECAO 2: FRAUD INVESTIGATIONS AND LEGAL ISSUES ───────────────
            {"id": "fraud_investigation", "name": "S2 · Fraud Investigation (Legacy)",
             "context": "CFE Fraud Examiners Manual 2026 Section 2 — Fraud Investigations and Legal Issues. Topics: investigation planning, evidence collection, digital forensics, interviewing techniques, report writing, legal considerations, expert testimony, data analysis. Legacy domain covering full Section 2 content."},
            {"id": "investigation_planning", "name": "S2D01 · Planning & Conducting Fraud Examination",
             "context": "CFE Exam 2026 S2D01 — Planning and Conducting a Fraud Examination. Topics: difference between fraud exam and audit, scope definition, conflict of interest checks, team assembly, hypothesis development, predication, confidentiality, coordination with legal counsel."},
            {"id": "legal_issues_investigations", "name": "S2D02 · Legal Issues in Investigations",
             "context": "CFE Exam 2026 S2D02 — Legal Issues in Conducting Investigations. Topics: employee rights, privacy expectations, lawful monitoring, search and seizure, Fourth Amendment in private investigations, defamation risks, legal holds, attorney-client privilege."},
            {"id": "law_cfe", "name": "S2D03 · Law Related to Fraud",
             "context": "CFE Exam 2026 S2D03 — The Law Related to Fraud. Topics: wire fraud (18 USC 1343), mail fraud (18 USC 1341), money laundering (18 USC 1956), RICO, conspiracy (18 USC 371), FCPA, SOX, Dodd-Frank whistleblower, False Claims Act, CFAA, Federal Sentencing Guidelines."},
            {"id": "legal_system_overview", "name": "S2D04 · Overview of the Legal System",
             "context": "CFE Exam 2026 S2D04 — Overview of the Legal System. Topics: US federal and state court structure, jurisdiction, burden of proof standards, adversarial vs inquisitorial systems, statute of limitations, appeals process."},
            {"id": "criminal_prosecutions", "name": "S2D05 · Criminal Prosecutions",
             "context": "CFE Exam 2026 S2D05 — Criminal Prosecutions. Topics: elements of criminal fraud, grand jury, indictment vs information, plea agreements, Federal Sentencing Guidelines, corporate criminal liability, respondeat superior, DPA/NPA, parallel proceedings."},
            {"id": "non_criminal_actions", "name": "S2D06 · Non-Criminal Actions",
             "context": "CFE Exam 2026 S2D06 — Non-Criminal Actions Civil and Administrative. Topics: civil fraud claims, compensatory vs punitive damages, disgorgement, injunctive relief, civil RICO, SEC enforcement actions, debarment, civil False Claims Act, asset freezing."},
            {"id": "individual_rights", "name": "S2D07 · Individual Rights During Examinations",
             "context": "CFE Exam 2026 S2D07 — Individual Rights During Examinations. Topics: Fifth Amendment privilege, Miranda rights, Weingarten rights, Garrity rights, attorney-client privilege, Dodd-Frank/SOX whistleblower protections, employee cooperation duties."},
            {"id": "evidence_principles", "name": "S2D08 · Basic Principles of Evidence",
             "context": "CFE Exam 2026 S2D08 — Basic Principles of Evidence. Topics: direct vs circumstantial vs documentary evidence, admissibility standards, hearsay rule and exceptions, best evidence rule, authentication, chain of custody, spoliation, Federal Rules of Evidence."},
            {"id": "collecting_evidence", "name": "S2D09 · Collecting Evidence",
             "context": "CFE Exam 2026 S2D09 — Collecting Evidence. Topics: document requests, subpoenas, physical evidence handling, digital evidence collection, forensic imaging (bit-stream), metadata, mobile device evidence, cloud evidence challenges, e-discovery, legal holds."},
            {"id": "sources_information", "name": "S2D10 · Sources of Information",
             "context": "CFE Exam 2026 S2D10 — Sources of Information. Topics: public records (court, corporate, property, SEC/EDGAR), nonpublic records (bank, credit, employment), social media evidence, OSINT techniques, dark web intelligence, international records access."},
            {"id": "data_analysis_tools", "name": "S2D11 · Data Analysis & Reporting Tools",
             "context": "CFE Exam 2026 S2D11 — Data Analysis and Reporting Tools. Topics: Benford Law application, statistical sampling, regression analysis, data matching, ACL/IDEA analytics software, AI and machine learning in fraud detection, network analysis, continuous monitoring."},
            {"id": "tracing_assets", "name": "S2D12 · Tracing Illicit Transactions & Assets",
             "context": "CFE Exam 2026 S2D12 — Tracing Illicit Transactions and Assets. Topics: net worth method, expenditure method, bank deposit method, specific item method, asset search, corporate ownership tracing, wire transfer tracing, cryptocurrency tracing, blockchain analytics, FBAR/FATCA data."},
            {"id": "interview_techniques", "name": "S2D13 · Interview Theory & Application",
             "context": "CFE Exam 2026 S2D13 — Interview Theory and Application. Topics: interview planning, rapport building, cognitive interview technique, questioning sequences (open/closed/leading), behavioral analysis, deception detection, admission-seeking interview, documenting results."},
            {"id": "covert_operations", "name": "S2D14 · Covert Operations",
             "context": "CFE Exam 2026 S2D14 — Covert Operations. Topics: undercover investigations, physical and electronic surveillance, entrapment standard, sting operations, legal limitations on covert activities, privacy law considerations, documentation standards."},
            {"id": "report_writing", "name": "S2D15 · Report Writing",
             "context": "CFE Exam 2026 S2D15 — Report Writing. Topics: structure of fraud examination report, executive summary, statement of facts vs conclusions, avoiding legal conclusions, avoiding defamation, expert opinion standards, litigation support reports, confidentiality."},
            {"id": "expert_witness", "name": "S2D16 · Testifying as Expert Witness",
             "context": "CFE Exam 2026 S2D16 — Testifying as an Expert Witness. Topics: expert qualification standards, Daubert standard, Frye standard, direct examination, cross-examination, deposition preparation, maintaining objectivity, court-appointed experts."},

            // ── SECAO 3: FRAUD PREVENTION AND DETERRENCE ─────────────────────
            {"id": "criminal_behavior", "name": "S3D01 · Understanding Criminal Behavior",
             "context": "CFE Exam 2026 S3D01 — Understanding Criminal Behavior and White-Collar Crime. Topics: Fraud Triangle (pressure, opportunity, rationalization), Fraud Diamond (capability), occupational vs organizational fraud, sociological theories, moral disengagement, effects of white-collar crime."},
            {"id": "occupational_fraud", "name": "S3D02 · Occupational Fraud",
             "context": "CFE Exam 2026 S3D02 — Occupational Fraud. Topics: ACFE Report to the Nations statistics, fraud by category/industry/position/tenure, detection methods comparison (tip vs audit vs accident), cost of fraud, anti-fraud control effectiveness."},
            {"id": "corporate_governance", "name": "S3D03 · Corporate Governance",
             "context": "CFE Exam 2026 S3D03 — Corporate Governance. Topics: board of directors fiduciary duties, audit committee composition and independence, tone at the top, ethics programs, COSO framework, OECD principles, Treadway Commission, SOX governance requirements."},
            {"id": "auditor_responsibilities", "name": "S3D04 · Management & Auditors Responsibilities",
             "context": "CFE Exam 2026 S3D04 — Management and Auditors Responsibilities. Topics: management duty of care, internal audit function, external auditor fraud detection (SAS 99/ISA 240), audit committee oversight, CFE vs CPA roles, management override of controls, auditor independence."},
            {"id": "fraud_risk_assessment", "name": "S3D05 · Fraud Risk Assessment",
             "context": "CFE Exam 2026 S3D05 — Fraud Risk Assessment. Topics: fraud risk assessment methodology (ACFE and COSO), inherent vs residual risk, fraud risk factor identification, risk prioritization matrix, fraud risk response, continuous monitoring, board reporting."},
            {"id": "prevention_deterrence", "name": "S3D06 · Internal Controls & Anti-Fraud Programs",
             "context": "CFE Exam 2026 S3D06 — Internal Controls and Anti-Fraud Programs. Topics: preventive vs detective vs corrective controls, segregation of duties, authorization controls, physical and logical access controls, reconciliation procedures, COSO Internal Control Framework, IT general controls."},
            {"id": "fraud_prevention_programs", "name": "S3D07 · Fraud Prevention Programs",
             "context": "CFE Exam 2026 S3D07 — Fraud Prevention Programs. Topics: fraud awareness training, whistleblower hotline implementation, anonymous reporting, pre-employment screening, background checks, vendor due diligence, job rotation, mandatory vacation, surprise audits, DLP programs."},
            {"id": "fraud_risk_management", "name": "S3D08 · Fraud Risk Management",
             "context": "CFE Exam 2026 S3D08 — Fraud Risk Management. Topics: enterprise fraud risk management framework, fraud response plan, incident response triggers, remediation after fraud, lessons learned, fidelity bonds, crime insurance, cyber insurance, continuous monitoring."},
            {"id": "ethics_fraud_examiners", "name": "S3D09 · Ethics for Fraud Examiners",
             "context": "CFE Exam 2026 S3D09 — Ethics for Fraud Examiners. Topics: ACFE Code of Professional Ethics (four principles), confidentiality obligations, independence and objectivity, conflicts of interest, professional competence, professional skepticism, ethical decision-making frameworks, ACFE disciplinary process."}
        ]
    },'''


def main():
    print("=" * 70)
    print("  NEXOR -- CATALOGO CFE 2026 COMPLETO v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("  45 dominios da nova estrutura ACFE 2026")
    print("=" * 70)

    # Backup
    bak = f"{SERVER_FILE}.bak_{TIMESTAMP}"
    shutil.copy2(SERVER_FILE, bak)
    print(f"\n  Backup: {bak}")

    # Le arquivo
    with open(SERVER_FILE, encoding="utf-8") as f:
        content = f.read()

    if OLD_CFE_BLOCK in content:
        content = content.replace(OLD_CFE_BLOCK, NEW_CFE_BLOCK)
        with open(SERVER_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("  OK — catalogo CFE 2026 completo atualizado")
        print("  45 dominios registrados no server.py")
    else:
        print("  ERRO — bloco CFE nao encontrado exatamente")
        print("  Verifique manualmente o server.py")
        print()
        print("  DICA: o bloco pode ter sido modificado por")
        print("  execucoes anteriores. Verifique as linhas 288-301")
        print("  do server.py e ajuste o OLD_CFE_BLOCK no script.")

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  PROXIMO PASSO: reiniciar o servidor")
    print("  taskkill /f /im python.exe")
    print("  uvicorn server:app --port 8765 --reload")
    print("=" * 70)


if __name__ == "__main__":
    main()
