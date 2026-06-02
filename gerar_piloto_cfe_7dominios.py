"""
NEXOR -- GERADOR PILOTO CFE 7 DOMINIOS ZERADOS v1
Gera quiz_001_en para cada um dos 7 dominios sem cobertura.
Aplica o Metodo NEXOR de Formulacao de Itens (FractalLearning v1).
Distribuicao: 10 Easy + 30 Standard + 10 Hard = 50 questoes por quiz.

DOMINIOS ALVO:
  S1D07 · Theft of Data and Intellectual Property
  S1D12 · Insurance Fraud
  S1D13 · Consumer Fraud and Scams
  S1D14 · Bankruptcy Fraud
  S1D15 · Tax Fraud
  S1D17 · Government and Public Sector Fraud
  S1D20 · Emerging Fraud Schemes and Technology

USO:
    python gerar_piloto_cfe_7dominios.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")

# Bloco padrao do Metodo NEXOR de Formulacao de Itens
METODO_NEXOR = """
MÉTODO NEXOR DE FORMULAÇÃO — APLICAR OBRIGATORIAMENTE:

STEM:
- Apresentar cenário profissional realista antes do lead-in
- Lead-in deve ser uma pergunta completa e focada
- Sem informação irrelevante, sem negativo duplo
- O candidato deve conseguir formular a resposta mentalmente ANTES de ler as opções

OPÇÕES:
- 4 opções de comprimento homogêneo (±20% variação máxima)
- A opção correta NUNCA pode ser sistematicamente a mais longa
- Todos os distrátores devem ser plausíveis para quem não domina completamente o tópico
- Sem absolutos desnecessários (sempre, nunca, todos, nenhum)
- Sem clang association (palavras-chave do stem não podem aparecer APENAS na opção correta)
- Sem convergência (proibido 3 opções similares + 1 diferente)
- Proibido "todas as anteriores" e "nenhuma das anteriores"

NÍVEL COGNITIVO (Bloom's Taxonomy):
- EASY:     Bloom Nível 1-2 — definição direta ou compreensão básica de conceito
- STANDARD: Bloom Nível 3   — aplicação em cenário profissional realista
- HARD:     Bloom Nível 4-5 — análise de situação complexa ou avaliação com trade-offs

JUSTIFICATIVAS:
- justification_correct: explica o PRINCÍPIO técnico/legal/normativo (não apenas confirma)
- justification_wrong: explica especificamente por que cada distrator está incorreto
"""

# Configuracao dos 7 dominios zerados
DOMINIOS = [
    {
        "domain_id": "data_theft_ip",
        "domain_code": "S1D07",
        "domain_name": "Theft of Data and Intellectual Property",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers theft and misappropriation of data and intellectual property.
Topics include: trade secret theft, IP misappropriation methods, insider threats to data,
data exfiltration techniques, economic espionage, theft of proprietary algorithms and source code,
detection methods, legal frameworks (EEA - Economic Espionage Act, DTSA - Defend Trade Secrets Act),
civil and criminal remedies, prevention controls.""",
        "topics_easy": [
            "Definition of trade secret under the Defend Trade Secrets Act",
            "Economic Espionage Act — basic criminal provisions",
            "Definition of intellectual property categories (patents, trademarks, copyrights, trade secrets)",
            "Common methods of data exfiltration by insiders",
            "Basic indicators of trade secret theft",
            "Definition of misappropriation under DTSA",
            "Role of non-disclosure agreements in IP protection",
            "Categories of information qualifying as trade secrets",
            "Basic access controls to protect intellectual property",
            "Definition of economic espionage vs. trade secret theft"
        ],
        "topics_standard": [
            "Insider threat scenarios involving data theft before employee departure",
            "Applying DTSA remedies in a civil trade secret misappropriation case",
            "Identifying red flags of IP theft in a corporate investigation",
            "Forensic evidence collection in a trade secret theft case",
            "Responding to suspected data exfiltration via cloud storage",
            "Distinguishing between legitimate competitive intelligence and IP theft",
            "Applying Economic Espionage Act to foreign-sponsored theft scenarios",
            "Investigating source code theft by a departing software developer",
            "Data loss prevention (DLP) controls in IP protection programs",
            "Chain of custody for digital evidence in trade secret cases",
            "Coordinating with law enforcement in economic espionage investigations",
            "Non-compete and non-solicitation agreements in IP protection",
            "Investigating USB device misuse for data exfiltration",
            "Email monitoring and privacy considerations in IP investigations",
            "Applying misappropriation standards to customer list theft",
            "Trade secret protection in mergers and acquisitions due diligence",
            "Whistleblower protections in IP theft reporting (DTSA provisions)",
            "Investigating theft of manufacturing processes and formulas",
            "Digital forensics in cloud-based IP theft investigations",
            "Role of non-disclosure agreements as evidence in IP cases",
            "Identifying exfiltration through authorized access channels",
            "Responding to competitor recruitment of key employees with IP knowledge",
            "Documenting trade secret misappropriation for litigation",
            "Preventive controls for source code and algorithm protection",
            "Investigating IP theft through third-party vendor relationships",
            "Applying DTSA ex parte seizure provisions",
            "Cross-border data theft investigations — jurisdiction challenges",
            "Protecting customer data as trade secret in fraud investigations",
            "Distinguishing civil vs. criminal remedies in trade secret cases",
            "Role of security clearances in economic espionage investigations"
        ],
        "topics_hard": [
            "Complex insider threat scenario involving authorized access and IP exfiltration over time",
            "Evaluating competing claims of trade secret ownership in a corporate spin-off",
            "Analyzing a multi-jurisdiction economic espionage case with foreign state actors",
            "Distinguishing inevitable disclosure doctrine from actual misappropriation",
            "Evaluating proportionality of remedies in trade secret injunction cases",
            "Analyzing state-sponsored IP theft under both EEA and DTSA frameworks",
            "Assessing adequacy of trade secret protection measures for litigation",
            "Complex scenario involving IP theft via legitimate cloud collaboration tools",
            "Evaluating reverse engineering as a defense to trade secret misappropriation",
            "Analyzing trade secret protection failure and organizational liability"
        ]
    },
    {
        "domain_id": "insurance_fraud",
        "domain_code": "S1D12",
        "domain_name": "Insurance Fraud",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers fraud schemes in the insurance industry.
Topics include: premium diversion, claims fraud (staged accidents, arson, inflated claims),
agent and broker fraud, workers compensation fraud, life insurance fraud,
healthcare-related insurance schemes, fraud detection techniques, SIU (Special Investigations Unit) role,
regulatory framework, civil and criminal remedies for insurance fraud.""",
        "topics_easy": [
            "Definition of premium diversion in insurance fraud",
            "Common types of insurance fraud schemes (hard fraud vs. soft fraud)",
            "Role of Special Investigations Units (SIU) in insurance companies",
            "Definition of staged accident schemes",
            "Basic indicators of fraudulent insurance claims",
            "Definition of arson for profit as insurance fraud",
            "Workers compensation fraud — basic scheme types",
            "Role of insurance regulators in fraud prevention",
            "Definition of churning in insurance agent fraud",
            "Basic red flags in life insurance fraud applications"
        ],
        "topics_standard": [
            "Investigating a staged automobile accident insurance claim",
            "Identifying red flags in a workers compensation claim investigation",
            "Applying fraud indicators to a suspicious property damage claim",
            "Investigating premium diversion by an insurance agent",
            "Documenting evidence in a suspected arson-for-profit scheme",
            "Interviewing claimants in insurance fraud investigations",
            "Coordinating with law enforcement in insurance fraud cases",
            "Applying social media evidence in insurance fraud investigations",
            "Investigating medical provider collusion in personal injury fraud",
            "Detecting ghost employee schemes in workers compensation fraud",
            "Analyzing claim patterns for systematic fraud detection",
            "Investigating life insurance fraud with forged beneficiary designations",
            "Applying subrogation principles in fraud recovery",
            "Detecting multiple-claim fraud across insurers using data analytics",
            "Investigating disability fraud with surveillance evidence",
            "Applying SIU best practices in a complex fraud investigation",
            "Evaluating recorded statements in insurance fraud investigations",
            "Detecting bid rigging in contractor insurance claims",
            "Investigating crop insurance fraud in agricultural fraud schemes",
            "Applying the National Insurance Crime Bureau (NICB) resources",
            "Detecting application fraud and material misrepresentation",
            "Investigating slip-and-fall staged accident schemes",
            "Analyzing medical records for healthcare insurance fraud indicators",
            "Fraud detection in commercial property insurance claims",
            "Investigating organized retail theft and insurance claims",
            "Applying anti-fraud warranty provisions in claim investigations",
            "Detecting fraud in business interruption insurance claims",
            "Investigating title insurance fraud in real estate transactions",
            "Applying Examination Under Oath (EUO) procedures in fraud cases",
            "Detecting phantom vehicle schemes in automobile insurance fraud"
        ],
        "topics_hard": [
            "Complex organized fraud ring involving multiple staged accidents and medical providers",
            "Evaluating the adequacy of SIU investigation procedures against regulatory standards",
            "Analyzing a cross-state insurance fraud conspiracy with multiple scheme types",
            "Distinguishing legitimate claim disputes from fraudulent misrepresentation",
            "Evaluating anti-fraud program effectiveness against NICB and NAIC standards",
            "Complex workers compensation fraud involving employer-employee collusion",
            "Analyzing legal exposure for insurer bad faith in fraud investigation overreach",
            "Evaluating proportionality of civil vs. criminal referral in insurance fraud",
            "Complex life insurance fraud with multiple policy stacking and identity theft",
            "Analyzing systemic fraud indicators across an insurer's entire claims portfolio"
        ]
    },
    {
        "domain_id": "consumer_fraud",
        "domain_code": "S1D13",
        "domain_name": "Consumer Fraud and Scams",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers fraud schemes targeting individual consumers.
Topics include: advance fee fraud (419 fraud), romance scams, lottery and prize scams,
elder fraud, telemarketing fraud, charity fraud, investment fraud targeting consumers,
identity theft as consumer fraud, online shopping fraud, phishing targeting consumers,
FTC enforcement, civil and criminal remedies, prevention and awareness programs.""",
        "topics_easy": [
            "Definition of advance fee fraud (419 fraud)",
            "Basic characteristics of romance scams",
            "Common types of lottery and prize scams",
            "Definition of elder fraud and why elderly are targeted",
            "Basic indicators of charity fraud",
            "Definition of telemarketing fraud",
            "Basic characteristics of pyramid schemes targeting consumers",
            "Role of the Federal Trade Commission (FTC) in consumer fraud",
            "Definition of phishing as consumer fraud",
            "Basic characteristics of online shopping fraud"
        ],
        "topics_standard": [
            "Investigating an advance fee fraud scheme targeting a victim",
            "Identifying red flags in a suspected romance scam investigation",
            "Applying elder fraud indicators in a financial exploitation case",
            "Investigating charitable organization fraud",
            "Documenting consumer fraud evidence for FTC referral",
            "Applying anti-fraud controls to prevent telemarketing fraud",
            "Investigating pyramid scheme consumer victimization",
            "Tracing funds in an advance fee fraud case",
            "Identifying social engineering tactics in consumer fraud",
            "Investigating online marketplace fraud schemes",
            "Applying consumer protection laws in fraud investigations",
            "Detecting grandparent scams targeting elderly victims",
            "Investigating investment fraud targeting retail consumers",
            "Applying Do Not Call Registry violations in telemarketing fraud",
            "Investigating fake charity fraud after natural disasters",
            "Detecting counterfeit goods fraud schemes",
            "Investigating work-from-home scams as consumer fraud",
            "Applying FTC Act Section 5 to unfair and deceptive practices",
            "Detecting overpayment check scams",
            "Investigating home improvement fraud targeting consumers",
            "Applying elder financial exploitation statutes in investigations",
            "Detecting subscription trap and negative option fraud",
            "Investigating travel and vacation fraud schemes",
            "Applying restitution remedies in consumer fraud cases",
            "Detecting impersonation fraud (government agency scams)",
            "Investigating cryptocurrency-based consumer fraud",
            "Applying state consumer protection laws alongside FTC enforcement",
            "Detecting predatory lending as consumer fraud",
            "Investigating funeral and cemetery fraud targeting bereaved consumers",
            "Detecting franchise and business opportunity fraud"
        ],
        "topics_hard": [
            "Complex organized consumer fraud ring operating across multiple states",
            "Evaluating FTC enforcement priorities against emerging consumer fraud schemes",
            "Analyzing jurisdictional challenges in cross-border consumer fraud investigations",
            "Distinguishing civil consumer fraud remedies from criminal prosecution thresholds",
            "Evaluating the adequacy of consumer fraud prevention programs for vulnerable populations",
            "Complex elder financial abuse case involving multiple perpetrators and financial institutions",
            "Analyzing cryptocurrency consumer fraud with layered blockchain transactions",
            "Evaluating proportionality of class action vs. individual consumer fraud remedies",
            "Complex charity fraud investigation with international fund flows",
            "Analyzing systemic consumer fraud enabled by fintech platform vulnerabilities"
        ]
    },
    {
        "domain_id": "bankruptcy_fraud",
        "domain_code": "S1D14",
        "domain_name": "Bankruptcy Fraud",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers fraud schemes in bankruptcy proceedings.
Topics include: concealment of assets, false statements in bankruptcy petitions,
bust-out schemes, fraudulent transfers (preferences and fraudulent conveyances),
multiple filings, bribery of bankruptcy trustees, bankruptcy fraud statutes (18 USC 152-157),
US Trustee Program role, detection methods, civil and criminal remedies.""",
        "topics_easy": [
            "Definition of bankruptcy fraud under 18 USC 152",
            "Common types of asset concealment in bankruptcy",
            "Definition of a bust-out scheme",
            "Basic characteristics of fraudulent transfers in bankruptcy",
            "Role of the US Trustee Program in bankruptcy fraud detection",
            "Definition of preferential transfers in bankruptcy",
            "Basic red flags of bankruptcy fraud in petition review",
            "Definition of multiple bankruptcy filing fraud",
            "Basic provisions of 18 USC 157 (scheme to defraud in bankruptcy)",
            "Role of bankruptcy trustees in fraud detection"
        ],
        "topics_standard": [
            "Investigating asset concealment in a personal bankruptcy filing",
            "Identifying fraudulent transfer indicators in a business bankruptcy",
            "Applying preferential transfer avoidance in bankruptcy investigations",
            "Investigating a bust-out scheme targeting creditors",
            "Documenting false statements in bankruptcy petition for prosecution",
            "Tracing concealed assets in a bankruptcy fraud investigation",
            "Applying US Trustee referral procedures for bankruptcy fraud",
            "Investigating insider transactions preceding bankruptcy filing",
            "Detecting undervalued asset transfers to related parties",
            "Applying the look-back period for fraudulent transfer avoidance",
            "Investigating false oath in bankruptcy creditor meeting (341 hearing)",
            "Detecting hidden offshore accounts in bankruptcy proceedings",
            "Investigating serial bankruptcy filers (automatic stay abuse)",
            "Applying Uniform Fraudulent Transfer Act standards",
            "Detecting concealed business interests in bankruptcy schedules",
            "Investigating bribery of bankruptcy professionals",
            "Applying criminal and civil remedies in bust-out scheme cases",
            "Detecting fraudulent appraisals in bankruptcy asset valuation",
            "Investigating pre-bankruptcy asset stripping schemes",
            "Applying the badges of fraud in fraudulent transfer analysis",
            "Detecting concealed income in bankruptcy means test fraud",
            "Investigating preference payments to insiders vs. arm's length creditors",
            "Applying Rule 2004 examination in bankruptcy fraud investigation",
            "Detecting phantom creditor schemes in bankruptcy proceedings",
            "Investigating fraudulent homestead exemption claims",
            "Applying criminal bankruptcy fraud statutes to corporate reorganizations",
            "Detecting income concealment through cash-based businesses",
            "Investigating fraudulent business entity transfers pre-bankruptcy",
            "Applying civil RICO to organized bankruptcy fraud schemes",
            "Detecting fraudulent reaffirmation agreements in bankruptcy"
        ],
        "topics_hard": [
            "Complex corporate bankruptcy fraud involving pre-planned asset stripping",
            "Evaluating fraudulent transfer claims with competing creditor priorities",
            "Analyzing multi-entity bankruptcy fraud with related party transactions",
            "Distinguishing legitimate business restructuring from fraudulent pre-bankruptcy planning",
            "Evaluating the adequacy of bankruptcy trustee fraud investigation procedures",
            "Complex bust-out scheme with multiple corporate entities and jurisdictions",
            "Analyzing criminal exposure for bankruptcy fraud enablers (attorneys, accountants)",
            "Evaluating fraudulent transfer avoidance in leveraged buyout transactions",
            "Complex asset concealment using cryptocurrency in bankruptcy proceedings",
            "Analyzing competing standards for fraudulent intent in bankruptcy fraud cases"
        ]
    },
    {
        "domain_id": "tax_fraud",
        "domain_code": "S1D15",
        "domain_name": "Tax Fraud",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers fraud schemes involving tax evasion and tax fraud.
Topics include: underreporting income, inflated deductions, payroll tax fraud (trust fund),
offshore tax evasion, tax preparer fraud, employment tax fraud, frivolous tax arguments,
refund fraud, IRS Criminal Investigation (IRS-CI) enforcement, FBAR requirements,
FATCA, civil and criminal tax fraud penalties (26 USC and 18 USC 1349), detection methods.""",
        "topics_easy": [
            "Difference between tax avoidance and tax evasion",
            "Definition of tax fraud under IRC Section 7201",
            "Basic characteristics of payroll tax fraud (trust fund tax)",
            "Definition of FBAR filing requirements for offshore accounts",
            "Basic indicators of underreported income in tax fraud",
            "Role of IRS Criminal Investigation (IRS-CI) in tax fraud",
            "Definition of tax preparer fraud",
            "Basic characteristics of refund fraud schemes",
            "Definition of FATCA and its anti-evasion purpose",
            "Basic civil vs. criminal penalties for tax fraud"
        ],
        "topics_standard": [
            "Investigating unreported income through lifestyle analysis",
            "Applying the net worth method to detect tax fraud",
            "Identifying red flags of payroll tax fraud in a business",
            "Investigating offshore account tax evasion and FBAR violations",
            "Documenting tax fraud evidence for IRS-CI referral",
            "Applying the bank deposit method in tax fraud investigation",
            "Detecting inflated deduction fraud in business tax returns",
            "Investigating employment tax fraud (trust fund recovery penalty)",
            "Applying FATCA reporting requirements in fraud detection",
            "Detecting cash business income skimming as tax fraud",
            "Investigating tax preparer fraud and return falsification",
            "Applying the expenditure method in tax fraud reconstruction",
            "Detecting fraudulent charitable deduction schemes",
            "Investigating refund fraud using stolen taxpayer identities",
            "Applying badges of fraud to establish willful tax evasion",
            "Detecting corporate income tax fraud through fictitious expenses",
            "Investigating offshore tax evasion through shell companies",
            "Applying John Doe summons in offshore account investigations",
            "Detecting fraudulent depreciation and cost basis manipulation",
            "Investigating tax fraud in cash-intensive businesses",
            "Applying tax treaty provisions in international tax fraud",
            "Detecting payroll skimming combined with tax fraud",
            "Investigating abusive tax shelter schemes",
            "Applying the specific item method in tax fraud cases",
            "Detecting false W-2 and 1099 reporting in tax fraud",
            "Investigating Earned Income Tax Credit (EITC) fraud",
            "Applying civil fraud penalty standards (75% penalty under IRC 6663)",
            "Detecting tax fraud in related-party transactions",
            "Investigating sales tax fraud in retail businesses",
            "Applying IRS voluntary disclosure programs in tax evasion cases"
        ],
        "topics_hard": [
            "Complex offshore tax evasion with multiple foreign entities and nominee ownership",
            "Evaluating competing tax fraud theories in a complex corporate case",
            "Analyzing willfulness standard in tax evasion vs. tax negligence",
            "Distinguishing legal tax planning from fraudulent tax avoidance",
            "Evaluating the adequacy of tax compliance programs against IRS standards",
            "Complex payroll tax fraud with employer-accountant collusion",
            "Analyzing criminal exposure for tax fraud enablers (return preparers, promoters)",
            "Evaluating privilege and self-incrimination issues in tax investigations",
            "Complex international tax fraud using treaty shopping and transfer pricing",
            "Analyzing tax fraud in cryptocurrency transactions with unreported gains"
        ]
    },
    {
        "domain_id": "government_fraud",
        "domain_code": "S1D17",
        "domain_name": "Government and Public Sector Fraud",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers fraud schemes targeting government entities and public programs.
Topics include: procurement fraud (pre-award and post-award), grant fraud, benefits fraud
(welfare, unemployment, disability), public corruption, bribery of public officials,
government contractor fraud, False Claims Act (qui tam), program integrity fraud,
deficit spending fraud, abuse of authority, detection methods, Inspector General role,
GAO standards, state and federal enforcement.""",
        "topics_easy": [
            "Definition of procurement fraud in government contracting",
            "Role of Inspector General offices in government fraud detection",
            "Basic characteristics of bid rigging in government procurement",
            "Definition of grant fraud in federal programs",
            "Basic indicators of benefits fraud (welfare, unemployment)",
            "Role of the False Claims Act in government fraud recovery",
            "Definition of public corruption and bribery of public officials",
            "Basic characteristics of cost mischarging in government contracts",
            "Role of the Government Accountability Office (GAO) in fraud oversight",
            "Definition of program integrity fraud in government benefits"
        ],
        "topics_standard": [
            "Investigating bid rigging in a government construction contract",
            "Applying False Claims Act qui tam provisions in a contractor fraud case",
            "Identifying red flags of cost mischarging in a government contract",
            "Investigating grant fraud in a federally funded research program",
            "Documenting bribery of public officials for contract awards",
            "Applying the Single Audit Act in grant fraud investigations",
            "Detecting product substitution fraud in defense contracts",
            "Investigating unemployment insurance fraud schemes",
            "Applying debarment procedures in government contractor fraud",
            "Detecting ghost employee schemes in public sector payroll",
            "Investigating procurement fraud through change order manipulation",
            "Applying the False Claims Act reverse false claims provision",
            "Detecting public official conflicts of interest in contracting",
            "Investigating Medicaid/Medicare fraud as government program fraud",
            "Applying the Anti-Kickback Act to government contractor relationships",
            "Detecting progress payment fraud in long-term government contracts",
            "Investigating disability benefits fraud through lifestyle analysis",
            "Applying Inspector General subpoena authority in investigations",
            "Detecting sole source contract abuse in procurement fraud",
            "Investigating fraud in federally funded grant programs",
            "Applying the Hatch Act to political activity fraud in government",
            "Detecting specification manipulation in procurement (pre-award fraud)",
            "Investigating SNAP (food stamp) fraud and trafficking",
            "Applying the Davis-Bacon Act to prevailing wage fraud",
            "Detecting unauthorized commitment fraud in government contracting",
            "Investigating public official corruption in licensing and permits",
            "Applying qui tam protections for whistleblowers in government fraud",
            "Detecting subcontractor pass-through scheme in prime contracts",
            "Investigating improper disposal of government property",
            "Applying criminal and civil remedies in government contractor fraud"
        ],
        "topics_hard": [
            "Complex government contractor fraud involving cost mischarging and defective pricing",
            "Evaluating False Claims Act damages and penalties in a multi-year fraud scheme",
            "Analyzing public corruption network involving contracting officers and contractors",
            "Distinguishing legitimate sole source justification from fraudulent procurement",
            "Evaluating the adequacy of government contractor compliance programs",
            "Complex grant fraud involving multiple subrecipients and indirect cost manipulation",
            "Analyzing criminal exposure for government fraud enablers (consultants, attorneys)",
            "Evaluating qui tam relator standing and original source requirements",
            "Complex procurement fraud involving multiple schemes across contract lifecycle",
            "Analyzing systemic fraud indicators in a government agency's procurement function"
        ]
    },
    {
        "domain_id": "emerging_fraud",
        "domain_code": "S1D20",
        "domain_name": "Emerging Fraud Schemes and Technology",
        "section": "Fraud Schemes and Financial Crimes",
        "description": """This domain covers emerging and technology-enabled fraud schemes.
Topics include: AI-enabled fraud (deepfakes, synthetic identity, AI-generated documents),
cryptocurrency fraud (rug pulls, pump and dump, wallet theft, DeFi fraud),
NFT fraud, ESG fraud (greenwashing), remote work fraud schemes,
supply chain fraud enabled by technology, social media fraud,
metaverse and virtual world fraud, algorithmic manipulation fraud,
dark web facilitated fraud, detection methods for emerging schemes.""",
        "topics_easy": [
            "Definition of deepfake fraud and its primary use in fraud schemes",
            "Basic characteristics of cryptocurrency pump and dump schemes",
            "Definition of synthetic identity fraud",
            "Basic characteristics of NFT wash trading as fraud",
            "Definition of ESG fraud (greenwashing)",
            "Basic indicators of remote work fraud schemes",
            "Definition of rug pull in cryptocurrency fraud",
            "Basic characteristics of social media impersonation fraud",
            "Definition of supply chain fraud enabled by technology",
            "Basic characteristics of AI-generated document fraud"
        ],
        "topics_standard": [
            "Investigating a deepfake-enabled CEO fraud (business email compromise)",
            "Identifying red flags of cryptocurrency investment fraud",
            "Applying blockchain analytics in cryptocurrency fraud investigation",
            "Investigating a rug pull scheme in decentralized finance (DeFi)",
            "Documenting ESG fraud evidence for regulatory referral",
            "Applying synthetic identity detection in financial institution fraud",
            "Detecting AI-generated financial statement manipulation",
            "Investigating NFT wash trading and market manipulation",
            "Applying dark web evidence in fraud investigations",
            "Detecting remote work expense fraud and timekeeping fraud",
            "Investigating social media-enabled investment fraud",
            "Applying cryptocurrency tracing in fraud recovery",
            "Detecting algorithmic manipulation in financial markets",
            "Investigating greenwashing fraud in corporate ESG reporting",
            "Applying AI detection tools in document fraud investigation",
            "Detecting supply chain fraud using falsified digital records",
            "Investigating metaverse and virtual asset fraud schemes",
            "Applying OSINT techniques in emerging fraud investigations",
            "Detecting SIM swapping as enabler of financial fraud",
            "Investigating voice cloning in fraud schemes",
            "Applying blockchain immutability as evidence in fraud cases",
            "Detecting pump and dump schemes in cryptocurrency markets",
            "Investigating credential stuffing attacks enabling account fraud",
            "Applying emerging regulatory frameworks to cryptocurrency fraud",
            "Detecting fraudulent carbon credit schemes (ESG fraud)",
            "Investigating romance scams enabled by AI personas",
            "Applying digital forensics in cryptocurrency wallet theft",
            "Detecting insider trading enabled by AI-generated research",
            "Investigating supply chain vendor impersonation using deepfakes",
            "Applying Benford's Law to detect AI-generated financial data manipulation"
        ],
        "topics_hard": [
            "Complex DeFi fraud scheme involving multiple smart contract exploits",
            "Evaluating regulatory gaps in cryptocurrency fraud enforcement",
            "Analyzing AI-enabled fraud that bypasses traditional detection controls",
            "Distinguishing legitimate AI use in finance from AI-enabled manipulation",
            "Evaluating the adequacy of anti-fraud controls against emerging technology threats",
            "Complex synthetic identity fraud ring using AI-generated credentials",
            "Analyzing ESG fraud with multiple layers of greenwashing across subsidiaries",
            "Evaluating proportionality of blockchain tracing evidence in criminal proceedings",
            "Complex cross-chain cryptocurrency fraud with mixer obfuscation",
            "Analyzing systemic vulnerability to deepfake fraud in organizational controls"
        ]
    }
]

LANG_CONFIG = {
    "pt": {"lang_name": "Portugues (Brasil)", "domain_name_suffix": ""},
    "es": {"lang_name": "Espanol (neutro latinoamericano)", "domain_name_suffix": ""},
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup(path):
    if os.path.exists(path):
        bak = path + f".bak_{TIMESTAMP}"
        shutil.copy2(path, bak)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def build_generation_prompt(domain, topics, level, num_start):
    level_instruction = {
        "EASY": "Bloom Level 1-2: Direct definition or basic concept comprehension. No scenario needed. Simple, clear stem.",
        "STANDARD": "Bloom Level 3: Application in a realistic professional scenario. Present a situation then ask what the fraud examiner should do, identify, or conclude.",
        "HARD": "Bloom Level 4-5: Analysis or evaluation of a complex situation with multiple variables, competing considerations, or ambiguous facts requiring synthesis."
    }

    topics_str = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))

    return f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

CERTIFICATION: CFE (Certified Fraud Examiner) — ACFE 2026 Exam
SECTION: {domain['section']}
DOMAIN: {domain['domain_name']} ({domain['domain_code']})
DOMAIN DESCRIPTION: {domain['description']}

DIFFICULTY LEVEL: {level}
COGNITIVE REQUIREMENT: {level_instruction[level]}

{METODO_NEXOR}

Generate exactly {len(topics)} exam questions in English.
Start numbering from num={num_start}.

TOPICS TO COVER (one question per topic, in this exact order):
{topics_str}

IMPORTANT: All questions must be within the CFE exam scope.
US law references where applicable (EEA, DTSA, False Claims Act, IRC, etc.)
Avoid any reference to Brazilian law or Brazilian-specific regulations.

Return ONLY a valid JSON array, no markdown, no explanation:
[{{
  "num": {num_start},
  "text": "Full question text with scenario if Standard/Hard",
  "tag": "concise_snake_case_topic_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "justification_correct": "Detailed explanation of WHY this is correct, citing specific legal/professional standard",
  "justification_wrong": "Specific explanation of why each incorrect option is wrong"
}}]"""

def build_translation_prompt(questions, lang_name):
    block_json = json.dumps(questions, ensure_ascii=False, indent=2)
    return f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes exactly: "A. ", "B. ", "C. ", "D. "
4. Keep legal/technical terms in English when standard: FCPA, EEA, DTSA, FTC, IRS, etc.
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""

def generate_level(client, domain, topics, level, num_start):
    """Gera questoes de um nivel em blocos de 10."""
    all_qs = []
    block_size = 10

    for i in range(0, len(topics), block_size):
        bloco = topics[i:i+block_size]
        ns = num_start + i
        print(f"    [{level}] Q{ns}-Q{ns+len(bloco)-1}... ", end="", flush=True)

        try:
            qs = call_api(client, build_generation_prompt(domain, bloco, level, ns))
            for j, q in enumerate(qs):
                q["num"] = ns + j
                q["difficulty"] = level
            all_qs.extend(qs)
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            print(f"\n      Erro bloco: {e}. Individual...")
            for k, topic in enumerate(bloco):
                print(f"      Q{ns+k}... ", end="", flush=True)
                try:
                    qs2 = call_api(client, build_generation_prompt(domain, [topic], level, ns+k))
                    qs2[0]["num"] = ns + k
                    qs2[0]["difficulty"] = level
                    all_qs.append(qs2[0])
                    print("OK")
                except Exception as e2:
                    print(f"FALHOU: {e2}")

    return all_qs

def translate_block(client, questions, lang_name):
    """Traduz em blocos de 5."""
    translated = []
    for i in range(0, len(questions), 5):
        bloco = questions[i:i+5]
        print(f".", end="", flush=True)
        try:
            result = call_api(client, build_translation_prompt(bloco, lang_name))
            translated.extend(result)
        except Exception as e:
            print(f"\n      Erro traducao: {e}")
            translated.extend(bloco)
    return translated

def process_domain(client, domain):
    """Processa um dominio completo: gera EN + traduz PT/ES."""
    domain_id  = domain["domain_id"]
    domain_code = domain["domain_code"]
    domain_name = domain["domain_name"]

    print(f"\n  {domain_code} · {domain_name}")
    print(f"  {'─'*60}")

    # Gera EN
    all_en = []

    # EASY: 10 questoes (Q1-Q10)
    easy_qs = generate_level(client, domain, domain["topics_easy"], "EASY", 1)
    all_en.extend(easy_qs)

    # STANDARD: 30 questoes (Q11-Q40)
    std_qs = generate_level(client, domain, domain["topics_standard"], "STANDARD", len(all_en)+1)
    all_en.extend(std_qs)

    # HARD: 10 questoes (Q41-Q50)
    hard_qs = generate_level(client, domain, domain["topics_hard"], "HARD", len(all_en)+1)
    all_en.extend(hard_qs)

    # Renumera sequencialmente
    for i, q in enumerate(all_en):
        q["num"] = i + 1

    # Salva EN
    en_path = Path(QUIZZES_DIR) / domain_id / "quiz_001_en.json"
    quiz_en = {
        "cert_id":     "cfe",
        "domain_id":   domain_id,
        "domain_code": domain_code,
        "quiz_num":    1,
        "domain_name": domain_name,
        "cert_name":   "Certified Fraud Examiner",
        "section":     domain["section"],
        "lang":        "en",
        "questions":   all_en
    }
    backup(str(en_path))
    save_json(str(en_path), quiz_en)
    print(f"\n  EN salvo: {en_path} ({len(all_en)}q)")
    print(f"  Distribuicao: {len(easy_qs)} Easy · {len(std_qs)} Standard · {len(hard_qs)} Hard")

    # Traduz PT e ES
    for lang_code, lang_cfg in LANG_CONFIG.items():
        print(f"  Traduzindo para {lang_code.upper()} ", end="", flush=True)
        translated = translate_block(client, all_en, lang_cfg["lang_name"])

        for i, q in enumerate(translated):
            q["num"] = i + 1
            if "difficulty" not in q:
                q["difficulty"] = all_en[i].get("difficulty", "STANDARD")

        lang_path = Path(QUIZZES_DIR) / domain_id / f"quiz_001_{lang_code}.json"
        quiz_lang = {
            "cert_id":     "cfe",
            "domain_id":   domain_id,
            "domain_code": domain_code,
            "quiz_num":    1,
            "domain_name": domain_name,
            "cert_name":   "Certified Fraud Examiner",
            "section":     domain["section"],
            "lang":        lang_code,
            "questions":   translated
        }
        save_json(str(lang_path), quiz_lang)
        print(f"\n  {lang_code.upper()} salvo: {lang_path} ({len(translated)}q)")

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR PILOTO CFE 7 DOMINIOS ZERADOS v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Metodo: FractalLearning™ v1 + Psicometria NEXOR")
    print("=" * 70)
    print(f"\n  Dominios: {len(DOMINIOS)}")
    print(f"  Questoes por quiz: 50 (10 Easy + 30 Standard + 10 Hard)")
    print(f"  Total EN: {len(DOMINIOS) * 50} questoes")
    print(f"  Total com traducoes: {len(DOMINIOS) * 50 * 3} questoes")

    client = anthropic.Anthropic()

    for domain in DOMINIOS:
        process_domain(client, domain)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("  Avalie uma amostra de cada dominio antes de escalar")
    print("=" * 70)

if __name__ == "__main__":
    main()
