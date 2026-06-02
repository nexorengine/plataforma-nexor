"""
NEXOR -- GERADOR CFE 3 DOMINIOS VAZIOS v1
Gera quiz_001_en para os 3 dominios CFE 2026 sem cobertura:
  S1D11 · Payment Fraud
  S1D16 · Health Care Fraud
  S2D04 · Overview of the Legal System

Aplica o Metodo NEXOR FractalLearning v1.
Distribuicao: 10 Easy + 30 Standard + 10 Hard = 50q por quiz.

USO:
    python gerar_3_dominios_cfe.py
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

METODO_NEXOR = """
MÉTODO NEXOR DE FORMULAÇÃO — APLICAR OBRIGATORIAMENTE:

STEM:
- Cenário profissional realista antes do lead-in (Standard/Hard)
- Lead-in como pergunta completa e focada
- Sem informação irrelevante, sem negativo duplo

OPÇÕES:
- 4 opções de comprimento homogêneo (±20% variação)
- Opção correta NUNCA a mais longa
- Todos os distrátores plausíveis
- Sem absolutos (sempre, nunca, todos), sem clang association
- Proibido "todas as anteriores" / "nenhuma das anteriores"

NÍVEL COGNITIVO:
- EASY:     Bloom 1-2 — definição ou compreensão básica
- STANDARD: Bloom 3   — aplicação em cenário profissional
- HARD:     Bloom 4-5 — análise complexa com múltiplas variáveis

JUSTIFICATIVAS:
- justification_correct: explica o PRINCÍPIO técnico/legal
- justification_wrong: explica especificamente cada distrator
"""

DOMINIOS = [
    {
        "domain_id":   "payment_fraud",
        "domain_code": "S1D11",
        "domain_name": "Payment Fraud",
        "section":     "Fraud Schemes and Financial Crimes",
        "description": """CFE Exam 2026 S1D11 — Payment Fraud.
Topics: ACH fraud (origination fraud, account takeover),
wire transfer fraud (SWIFT fraud, authorized push payment fraud, business email compromise in wire context),
check fraud (counterfeiting, alteration, check washing),
card-not-present fraud (CNP) in e-commerce,
payment diversion fraud (vendor impersonation, invoice fraud),
real-time payment fraud risks,
overpayment check scams,
internal controls for payment protection,
detection methods for payment fraud schemes.
US law context: wire fraud (18 USC 1343), bank fraud (18 USC 1344).""",
        "topics_easy": [
            "Definition of ACH fraud and types of ACH schemes",
            "Definition of wire transfer fraud and key characteristics",
            "Definition of check washing and how it works",
            "Definition of card-not-present (CNP) fraud",
            "Definition of payment diversion fraud",
            "Basic red flags of vendor impersonation in payment fraud",
            "Definition of authorized push payment (APP) fraud",
            "Basic characteristics of overpayment check scams",
            "Role of positive pay in check fraud prevention",
            "Basic internal controls to prevent payment fraud"
        ],
        "topics_standard": [
            "Investigating an ACH origination fraud at a financial institution",
            "Identifying red flags of business email compromise in wire transfer context",
            "Applying detection methods to a suspected check washing scheme",
            "Investigating a vendor impersonation payment diversion scheme",
            "Documenting evidence in a CNP fraud investigation",
            "Applying positive pay controls to prevent check fraud",
            "Investigating account takeover fraud in ACH transactions",
            "Detecting duplicate payment schemes in accounts payable",
            "Applying dual control procedures to prevent wire fraud",
            "Investigating a SWIFT messaging fraud at a correspondent bank",
            "Detecting invoice fraud through vendor master file manipulation",
            "Applying real-time payment fraud controls in a corporate environment",
            "Investigating authorized push payment fraud targeting employees",
            "Detecting check kiting across multiple bank accounts",
            "Applying reconciliation controls to detect payment fraud",
            "Investigating payroll diversion fraud via direct deposit changes",
            "Detecting ghost vendor schemes in payment fraud",
            "Applying data analytics to identify duplicate payments",
            "Investigating payment fraud enabled by compromised credentials",
            "Detecting ACH debit fraud targeting corporate accounts",
            "Applying fraud controls to prevent real-time payment fraud",
            "Investigating overpayment scams targeting accounts payable staff",
            "Detecting forged endorsement schemes in check fraud",
            "Applying NACHA rules in ACH fraud investigations",
            "Investigating wire transfer fraud in international transactions",
            "Detecting payment fraud through exception reporting systems",
            "Applying UCC Article 4A to wire transfer fraud liability",
            "Investigating countercheck fraud schemes",
            "Detecting payment fraud in electronic funds transfer systems",
            "Applying segregation of duties to payment authorization controls"
        ],
        "topics_hard": [
            "Complex BEC-enabled wire fraud with multi-layered social engineering and account takeover",
            "Evaluating corporate liability for authorized push payment fraud vs. bank liability",
            "Analyzing systematic ACH fraud scheme exploiting origination controls weaknesses",
            "Distinguishing legitimate payment errors from fraudulent payment manipulation",
            "Evaluating adequacy of payment fraud controls against NACHA and Reg E standards",
            "Complex check fraud ring using counterfeiting, washing, and kiting simultaneously",
            "Analyzing jurisdictional issues in cross-border wire transfer fraud investigation",
            "Evaluating proportionality of civil vs criminal remedies in payment fraud cases",
            "Complex vendor impersonation fraud involving compromised email and ERP systems",
            "Analyzing systemic payment fraud vulnerabilities in a corporate treasury function"
        ]
    },
    {
        "domain_id":   "healthcare_fraud",
        "domain_code": "S1D16",
        "domain_name": "Health Care Fraud",
        "section":     "Fraud Schemes and Financial Crimes",
        "description": """CFE Exam 2026 S1D16 — Health Care Fraud.
Topics: billing for services not rendered,
upcoding (billing higher-complexity codes),
unbundling (billing separate codes for bundled services),
kickbacks in healthcare (Anti-Kickback Statute — 42 USC 1320a-7b),
Stark Law — physician self-referral prohibition,
phantom billing and ghost patients,
durable medical equipment (DME) fraud,
prescription drug fraud and diversion,
Medicare and Medicaid fraud schemes,
False Claims Act application to healthcare,
HealthSouth case study,
Corporate Integrity Agreements (CIA),
Office of Inspector General (OIG) role,
detection methods for healthcare fraud.""",
        "topics_easy": [
            "Definition of upcoding in healthcare billing fraud",
            "Definition of unbundling in healthcare claims fraud",
            "Definition of billing for services not rendered",
            "Basic provisions of the Anti-Kickback Statute (42 USC 1320a-7b)",
            "Basic provisions of the Stark Law (physician self-referral)",
            "Definition of durable medical equipment (DME) fraud",
            "Role of the OIG in healthcare fraud detection",
            "Basic characteristics of phantom billing schemes",
            "Definition of prescription drug diversion fraud",
            "Basic red flags of Medicare and Medicaid fraud"
        ],
        "topics_standard": [
            "Investigating an upcoding scheme at a medical practice",
            "Identifying kickback violations under the Anti-Kickback Statute",
            "Applying Stark Law to a physician self-referral investigation",
            "Investigating billing for services not rendered at a clinic",
            "Documenting DME fraud evidence for OIG referral",
            "Applying the False Claims Act to a healthcare fraud case",
            "Detecting unbundling fraud in hospital claims data",
            "Investigating prescription drug diversion by healthcare employees",
            "Applying data analytics to detect phantom billing schemes",
            "Investigating Medicare fraud through ghost patient schemes",
            "Detecting healthcare fraud through claims pattern analysis",
            "Applying Corporate Integrity Agreement requirements post-settlement",
            "Investigating Medicaid fraud involving falsified beneficiary records",
            "Detecting lab test fraud (ordering unnecessary tests for kickbacks)",
            "Applying safe harbor regulations to healthcare arrangements",
            "Investigating home health fraud (billing for patients not homebound)",
            "Detecting ambulance fraud (billing for non-emergency transport)",
            "Applying the False Claims Act reverse false claims to healthcare",
            "Investigating pharmaceutical manufacturer kickback schemes",
            "Detecting coordination of benefits fraud in dual-eligible patients",
            "Applying the OIG Work Plan to identify high-risk fraud areas",
            "Investigating mental health billing fraud schemes",
            "Detecting fraudulent credentialing in healthcare provider enrollment",
            "Applying medical necessity standards in fraud investigations",
            "Investigating hospice fraud (billing for ineligible patients)",
            "Detecting telemedicine fraud schemes post-COVID",
            "Applying exclusion screening requirements to healthcare entities",
            "Investigating nursing home fraud and abuse schemes",
            "Detecting fraudulent billing in outpatient surgical centers",
            "Applying whistleblower protections in healthcare fraud reporting"
        ],
        "topics_hard": [
            "Complex kickback scheme involving physician-owned distributorships and device manufacturers",
            "Evaluating Stark Law self-referral violations with multiple financial relationships",
            "Analyzing False Claims Act liability for healthcare executives in systemic billing fraud",
            "Distinguishing aggressive billing practices from fraudulent upcoding",
            "Evaluating adequacy of healthcare compliance programs against OIG guidelines",
            "Complex Medicare Advantage fraud involving risk score manipulation",
            "Analyzing criminal vs. civil exposure in parallel healthcare fraud investigations",
            "Evaluating proportionality of Corporate Integrity Agreements in settlement",
            "Complex pharmaceutical fraud involving both kickbacks and off-label promotion",
            "Analyzing systemic fraud indicators across a multi-site healthcare organization"
        ]
    },
    {
        "domain_id":   "legal_system_overview",
        "domain_code": "S2D04",
        "domain_name": "Overview of the Legal System",
        "section":     "Fraud Investigations and Legal Issues",
        "description": """CFE Exam 2026 S2D04 — Overview of the Legal System.
Topics: US federal court structure and jurisdiction (district courts, circuit courts, Supreme Court),
state court systems and jurisdiction,
subject matter jurisdiction vs. personal jurisdiction,
burden of proof standards (beyond reasonable doubt, preponderance of evidence, clear and convincing),
adversarial system — roles of parties, judge, jury,
civil law jurisdictions — inquisitorial systems,
international legal systems overview,
statute of limitations for federal fraud offenses,
venue and forum selection in fraud cases,
appeals process overview,
distinction between civil, criminal, and administrative proceedings.""",
        "topics_easy": [
            "Structure of the US federal court system — district, circuit, Supreme Court",
            "Difference between subject matter jurisdiction and personal jurisdiction",
            "Definition of burden of proof — beyond reasonable doubt vs. preponderance",
            "Difference between civil law and common law legal systems",
            "Definition of statute of limitations in fraud cases",
            "Roles of judge and jury in the adversarial system",
            "Definition of venue and its importance in fraud cases",
            "Difference between criminal, civil, and administrative proceedings",
            "Definition of the appeals process in federal courts",
            "Basic characteristics of inquisitorial vs. adversarial legal systems"
        ],
        "topics_standard": [
            "Applying federal subject matter jurisdiction to a wire fraud case",
            "Identifying the correct burden of proof standard in a civil fraud claim",
            "Applying statute of limitations rules to a federal fraud investigation",
            "Determining proper venue in a multi-district fraud case",
            "Distinguishing criminal prosecution from civil fraud litigation strategy",
            "Applying personal jurisdiction principles in cross-border fraud cases",
            "Analyzing the role of grand jury in federal fraud prosecutions",
            "Applying the clear and convincing evidence standard in civil fraud",
            "Determining federal vs. state court jurisdiction in a fraud matter",
            "Applying forum selection in international fraud litigation",
            "Analyzing the appeals process in a federal fraud conviction",
            "Applying the preponderance standard in civil RICO fraud claims",
            "Determining jurisdiction in a securities fraud case",
            "Applying the exhaustion of remedies doctrine in administrative fraud",
            "Analyzing the difference between interlocutory and final appeals",
            "Applying diversity jurisdiction in cross-state fraud litigation",
            "Determining proper court for a False Claims Act qui tam case",
            "Analyzing concurrent federal and state jurisdiction in fraud cases",
            "Applying class action procedures to consumer fraud litigation",
            "Determining the applicable statute of limitations for FCPA violations",
            "Analyzing the role of magistrate judges in fraud cases",
            "Applying the doctrine of res judicata in fraud litigation",
            "Determining extraterritorial jurisdiction in international fraud",
            "Analyzing the right to jury trial in civil fraud cases",
            "Applying the doctrine of collateral estoppel in parallel proceedings",
            "Determining admissibility standards across different court systems",
            "Analyzing the role of amicus curiae in fraud-related appeals",
            "Applying sovereign immunity concepts in government fraud cases",
            "Determining standing requirements in False Claims Act litigation",
            "Analyzing the impact of forum non conveniens in international fraud"
        ],
        "topics_hard": [
            "Complex multi-district fraud litigation with competing jurisdictional claims",
            "Evaluating strategic choice between criminal referral and civil fraud action",
            "Analyzing statute of limitations tolling in a concealed fraud scheme",
            "Distinguishing parallel administrative, civil, and criminal proceedings strategy",
            "Evaluating venue selection impact on fraud case outcome",
            "Complex international fraud case with competing jurisdictional frameworks",
            "Analyzing constitutional limitations on extraterritorial fraud jurisdiction",
            "Evaluating the impact of forum selection clauses in fraud cases",
            "Complex qui tam litigation with jurisdictional first-to-file bar issues",
            "Analyzing the interaction between federal and state fraud statutes"
        ]
    }
]

LANG_CONFIG = {
    "pt": {"lang_name": "Portugues (Brasil)"},
    "es": {"lang_name": "Espanol (neutro latinoamericano)"},
}

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup(path):
    if os.path.exists(path):
        shutil.copy2(path, path + f".bak_{TIMESTAMP}")

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def build_prompt(domain, topics, level, num_start):
    level_map = {
        "EASY":     "Bloom Level 1-2: Direct definition or basic concept. Simple stem, no scenario needed.",
        "STANDARD": "Bloom Level 3: Application in a realistic professional scenario. Present situation then ask what the CFE should do.",
        "HARD":     "Bloom Level 4-5: Complex scenario with multiple variables, competing considerations, or ambiguous facts."
    }
    topics_str = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))

    return f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

CERTIFICATION: CFE (ACFE) 2026 Exam
SECTION: {domain['section']}
DOMAIN: {domain['domain_name']} ({domain['domain_code']})
DOMAIN SCOPE: {domain['description']}

DIFFICULTY: {level}
COGNITIVE LEVEL: {level_map[level]}

{METODO_NEXOR}

Generate exactly {len(topics)} questions in English.
Start numbering from num={num_start}.

TOPICS (one per topic, in order):
{topics_str}

US law scope only. No Brazilian law.

Return ONLY valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full question text",
  "tag": "snake_case_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "{level}",
  "justification_correct": "Detailed principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

def build_translation_prompt(questions, lang_name):
    return f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct", "difficulty"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep legal terms in English: FCPA, SOX, ACH, NACHA, OIG, Stark Law, etc.
5. Return ONLY JSON array, no markdown

Input:
{json.dumps(questions, ensure_ascii=False, indent=2)}"""

def generate_level(client, domain, topics, level, num_start):
    all_qs = []
    block_size = 10
    for i in range(0, len(topics), block_size):
        bloco = topics[i:i+block_size]
        ns = num_start + i
        print(f"    [{level}] Q{ns}-Q{ns+len(bloco)-1}... ", end="", flush=True)
        try:
            qs = call_api(client, build_prompt(domain, bloco, level, ns))
            for j, q in enumerate(qs):
                q["num"] = ns + j
                q["difficulty"] = level
            all_qs.extend(qs)
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            print(f"\n      Erro: {e}. Individual...")
            for k, topic in enumerate(bloco):
                print(f"      Q{ns+k}... ", end="", flush=True)
                try:
                    p2 = build_prompt(domain, [topic], level, ns+k)
                    qs2 = call_api(client, p2)
                    qs2[0]["num"] = ns + k
                    qs2[0]["difficulty"] = level
                    all_qs.append(qs2[0])
                    print("OK")
                except Exception as e2:
                    print(f"FALHOU: {e2}")
    return all_qs

def translate_block(client, questions, lang_name):
    translated = []
    for i in range(0, len(questions), 5):
        bloco = questions[i:i+5]
        print(".", end="", flush=True)
        try:
            result = call_api(client, build_translation_prompt(bloco, lang_name))
            translated.extend(result)
        except:
            translated.extend(bloco)
    return translated

def process_domain(client, domain):
    print(f"\n  {domain['domain_code']} · {domain['domain_name']}")
    print(f"  {'─'*60}")

    all_en = []
    easy_qs = generate_level(client, domain, domain["topics_easy"], "EASY", 1)
    all_en.extend(easy_qs)
    std_qs = generate_level(client, domain, domain["topics_standard"], "STANDARD", len(all_en)+1)
    all_en.extend(std_qs)
    hard_qs = generate_level(client, domain, domain["topics_hard"], "HARD", len(all_en)+1)
    all_en.extend(hard_qs)

    for i, q in enumerate(all_en):
        q["num"] = i + 1

    en_path = Path(QUIZZES_DIR) / domain["domain_id"] / "quiz_001_en.json"
    backup(str(en_path))
    quiz_en = {
        "cert_id":     "cfe",
        "domain_id":   domain["domain_id"],
        "domain_code": domain["domain_code"],
        "quiz_num":    1,
        "domain_name": domain["domain_name"],
        "cert_name":   "Certified Fraud Examiner",
        "section":     domain["section"],
        "lang":        "en",
        "questions":   all_en
    }
    save_json(str(en_path), quiz_en)
    print(f"\n  EN: {len(all_en)}q ({len(easy_qs)} Easy · {len(std_qs)} Standard · {len(hard_qs)} Hard)")

    for lang_code, lang_cfg in LANG_CONFIG.items():
        print(f"  {lang_code.upper()} ", end="", flush=True)
        translated = translate_block(client, all_en, lang_cfg["lang_name"])
        for i, q in enumerate(translated):
            q["num"] = i + 1
        lang_path = Path(QUIZZES_DIR) / domain["domain_id"] / f"quiz_001_{lang_code}.json"
        quiz_lang = {**quiz_en, "lang": lang_code, "questions": translated}
        save_json(str(lang_path), quiz_lang)
        print(f"\n  {lang_code.upper()}: {len(translated)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR CFE 3 DOMINIOS VAZIOS v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  FractalLearning v1 · 10 Easy + 30 Standard + 10 Hard")
    print("=" * 70)

    client = anthropic.Anthropic()

    for domain in DOMINIOS:
        process_domain(client, domain)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
