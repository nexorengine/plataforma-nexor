"""
NEXOR -- CURADORIA LEGADO CFE 2026 v1
Mapeia questoes dos dominios legacy para a nova estrutura CFE 2026.
Classifica Easy/Standard/Hard.
Gera relatorio de cobertura e reposiciona questoes validadas.

DOMINIOS LEGACY:
  financial_transactions (S1 legacy)
  fraud_investigation    (S2 legacy)
  law / law_cfe          (S2D03 legacy)
  prevention_deterrence  (S3 legacy)

USO:
    python curadoria_legado_cfe.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
from collections import defaultdict

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 4096
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")
REPORT_FILE = f"curadoria_legado_cfe_{TIMESTAMP}.txt"
JSON_FILE   = f"curadoria_resultado_{TIMESTAMP}.json"

# Dominios legacy a auditar
LEGACY_DOMAINS = [
    "financial_transactions",
    "fraud_investigation",
    "law",
    "law_cfe",
    "prevention_deterrence",
]

# Mapa de dominios destino CFE 2026
DOMINIOS_DESTINO = {
    "S1D01": "accounting_concepts",
    "S1D02": "financial_statement_fraud",
    "S1D03": "cash_receipts_fraud",
    "S1D04": "fraudulent_disbursements",
    "S1D05": "inventory_fraud",
    "S1D06": "corruption_bribery",
    "S1D07": "data_theft_ip",
    "S1D08": "identity_theft_cyberfraud",
    "S1D09": "financial_institution_fraud",
    "S1D10": "securities_fraud",
    "S1D11": "payment_fraud",
    "S1D12": "insurance_fraud",
    "S1D13": "consumer_fraud",
    "S1D14": "bankruptcy_fraud",
    "S1D15": "tax_fraud",
    "S1D16": "healthcare_fraud",
    "S1D17": "government_fraud",
    "S1D18": "procurement_contract_fraud",
    "S1D19": "international_fraud",
    "S1D20": "emerging_fraud",
    "S2D01": "investigation_planning",
    "S2D02": "legal_issues_investigations",
    "S2D03": "law_cfe",
    "S2D04": "legal_system_overview",
    "S2D05": "criminal_prosecutions",
    "S2D06": "non_criminal_actions",
    "S2D07": "individual_rights",
    "S2D08": "evidence_principles",
    "S2D09": "collecting_evidence",
    "S2D10": "sources_information",
    "S2D11": "data_analysis_tools",
    "S2D12": "tracing_assets",
    "S2D13": "interview_techniques",
    "S2D14": "covert_operations",
    "S2D15": "report_writing",
    "S2D16": "expert_witness",
    "S3D01": "criminal_behavior",
    "S3D02": "occupational_fraud",
    "S3D03": "corporate_governance",
    "S3D04": "auditor_responsibilities",
    "S3D05": "fraud_risk_assessment",
    "S3D06": "prevention_deterrence",
    "S3D07": "fraud_prevention_programs",
    "S3D08": "fraud_risk_management",
    "S3D09": "ethics_fraud_examiners",
}

VALID_CODES = set(DOMINIOS_DESTINO.keys())

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

def classify_batch(client, questions_batch):
    """Classifica um lote de questoes — dominio destino + dificuldade + qualidade."""

    dominios_str = "\n".join(f"  {code}: {DOMINIOS_DESTINO[code]}" for code in sorted(DOMINIOS_DESTINO))

    questions_summary = []
    for q in questions_batch:
        questions_summary.append({
            "num": q.get("num"),
            "tag": q.get("tag", ""),
            "text": q.get("text", "")[:200],
            "source_domain": q.get("_source_domain", ""),
        })

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam content classifier.

Classify each CFE exam question below into:
1. The correct domain of the new CFE Exam 2026 structure
2. Difficulty level
3. Quality assessment

NEW CFE EXAM 2026 DOMAINS:
{dominios_str}

DIFFICULTY LEVELS:
- EASY: Bloom Level 1-2, direct definition or basic concept
- STANDARD: Bloom Level 3, application in professional scenario
- HARD: Bloom Level 4-5, analysis of complex situation

QUALITY ASSESSMENT:
- VALIDATED: correct content, good quality, ready to use
- LEGACY_REVIEW: correct content but weak quality (vague, too simple, poor distractors)
- DISCARD: wrong scope (Brazilian law, LGPD, wrong jurisdiction), truncated, or empty text

Questions to classify:
{json.dumps(questions_summary, ensure_ascii=False, indent=2)}

Return ONLY a valid JSON array:
[{{
  "num": 1,
  "domain_code": "S1D06",
  "difficulty": "STANDARD",
  "quality": "VALIDATED",
  "reason": "brief reason only if LEGACY_REVIEW or DISCARD"
}}]"""

    try:
        return call_api(client, prompt)
    except Exception as e:
        print(f"\n    Erro API: {e}")
        return []

def collect_legacy_questions():
    """Coleta todas as questoes EN dos dominios legacy."""
    all_questions = []
    base = Path(QUIZZES_DIR)

    for domain_id in LEGACY_DOMAINS:
        domain_path = base / domain_id
        if not domain_path.exists():
            continue

        for quiz_file in sorted(domain_path.glob("quiz_*_en.json")):
            try:
                data = load_json(str(quiz_file))
                for q in data.get("questions", []):
                    q["_source_domain"] = domain_id
                    q["_source_file"]   = quiz_file.name
                    all_questions.append(q)
            except Exception as e:
                print(f"  Erro ao ler {quiz_file}: {e}")

    return all_questions

def main():
    print("=" * 70)
    print("  NEXOR -- CURADORIA LEGADO CFE 2026 v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    # 1. Coleta questoes legacy
    print("\n  Coletando questoes dos dominios legacy...")
    all_questions = collect_legacy_questions()
    print(f"  Total questoes EN coletadas: {len(all_questions)}")

    # 2. Classifica em lotes de 20
    print(f"\n  Classificando em lotes de 20...")
    all_results = {}
    batch_size = 20

    for i in range(0, len(all_questions), batch_size):
        batch = all_questions[i:i+batch_size]
        end = min(i+batch_size, len(all_questions))
        print(f"  Q{i+1}-Q{end}... ", end="", flush=True)

        results = classify_batch(client, batch)
        for r in results:
            # Usa combinacao source_file + num como chave unica
            q = batch[results.index(r)] if results.index(r) < len(batch) else None
            if q:
                key = f"{q['_source_domain']}/{q['_source_file']}/{q['num']}"
                all_results[key] = r
        print(f"OK ({len(results)} classificadas)")

    # 3. Compila resultados
    por_dominio_destino = defaultdict(list)
    validadas   = []
    legacy_rev  = []
    descartar   = []
    sem_resultado = []

    for q in all_questions:
        key = f"{q['_source_domain']}/{q['_source_file']}/{q['num']}"
        r = all_results.get(key)

        if not r:
            sem_resultado.append(q)
            continue

        domain_code = r.get("domain_code", "UNKNOWN")
        difficulty  = r.get("difficulty", "STANDARD")
        quality     = r.get("quality", "LEGACY_REVIEW")
        reason      = r.get("reason", "")

        q["_dest_domain_code"] = domain_code
        q["_dest_domain_id"]   = DOMINIOS_DESTINO.get(domain_code, "unknown")
        q["_difficulty"]       = difficulty
        q["_quality"]          = quality
        q["_reason"]           = reason

        if quality == "VALIDATED":
            validadas.append(q)
            por_dominio_destino[domain_code].append(q)
        elif quality == "LEGACY_REVIEW":
            legacy_rev.append(q)
            por_dominio_destino[domain_code].append(q)
        else:
            descartar.append(q)

    # 4. Gera relatorio
    report_lines = [
        f"NEXOR -- CURADORIA LEGADO CFE 2026 -- {TIMESTAMP}",
        f"Total questoes analisadas: {len(all_questions)}",
        "=" * 70,
        "",
        f"VALIDADAS      : {len(validadas)}",
        f"LEGACY_REVIEW  : {len(legacy_rev)}",
        f"DESCARTAR      : {len(descartar)}",
        f"SEM RESULTADO  : {len(sem_resultado)}",
        "",
        "=" * 70,
        "COBERTURA POR DOMINIO DESTINO (VALIDADAS + LEGACY_REVIEW):",
        "=" * 70,
    ]

    cobertura_json = {}
    dominios_vazios = []
    dominios_rasos  = []

    for code in sorted(DOMINIOS_DESTINO.keys()):
        domain_id = DOMINIOS_DESTINO[code]
        qs = por_dominio_destino.get(code, [])
        n_val  = sum(1 for q in qs if q["_quality"] == "VALIDATED")
        n_rev  = sum(1 for q in qs if q["_quality"] == "LEGACY_REVIEW")
        n_tot  = n_val + n_rev

        if n_tot == 0:
            status = "LACUNA TOTAL"
            dominios_vazios.append(f"{code}: {domain_id}")
        elif n_tot < 20:
            status = "RASO"
            dominios_rasos.append(f"{code}: {domain_id} ({n_tot}q)")
        elif n_tot < 50:
            status = "MODERADO"
        else:
            status = "BEM COBERTO"

        report_lines.append(f"\n  {code} · {domain_id}")
        report_lines.append(f"  VALIDADAS:{n_val} REVIEW:{n_rev} TOTAL:{n_tot} · {status}")

        cobertura_json[code] = {
            "domain_id": domain_id,
            "validadas": n_val,
            "legacy_review": n_rev,
            "total": n_tot,
            "status": status,
        }

    report_lines += [
        "",
        "=" * 70,
        "QUESTOES A DESCARTAR:",
        "=" * 70,
    ]
    for q in descartar:
        report_lines.append(
            f"  {q['_source_domain']}/{q['_source_file']} Q{q['num']} "
            f"[{q.get('tag','')}] — {q.get('_reason','')}"
        )

    report_lines += [
        "",
        "=" * 70,
        "RESUMO DE LACUNAS:",
        "=" * 70,
        f"DOMINIOS COM LACUNA TOTAL ({len(dominios_vazios)}):",
    ]
    for d in dominios_vazios:
        report_lines.append(f"  LACUNA: {d}")

    report_lines += [
        f"\nDOMINIOS RASOS ({len(dominios_rasos)}):",
    ]
    for d in dominios_rasos:
        report_lines.append(f"  RASO: {d}")

    # Salva relatorios
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    save_json(JSON_FILE, {
        "timestamp": TIMESTAMP,
        "total": len(all_questions),
        "validadas": len(validadas),
        "legacy_review": len(legacy_rev),
        "descartar": len(descartar),
        "cobertura": cobertura_json,
        "questoes_descartar": [
            {
                "source": f"{q['_source_domain']}/{q['_source_file']}",
                "num": q["num"],
                "tag": q.get("tag",""),
                "reason": q.get("_reason","")
            }
            for q in descartar
        ],
        "questoes_validadas": [
            {
                "source": f"{q['_source_domain']}/{q['_source_file']}",
                "num": q["num"],
                "tag": q.get("tag",""),
                "dest_code": q["_dest_domain_code"],
                "dest_id": q["_dest_domain_id"],
                "difficulty": q["_difficulty"],
            }
            for q in validadas + legacy_rev
        ]
    })

    # Resumo terminal
    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  Validadas      : {len(validadas)}")
    print(f"  Legacy Review  : {len(legacy_rev)}")
    print(f"  Descartar      : {len(descartar)}")
    print(f"  Lacunas totais : {len(dominios_vazios)} dominios")
    print(f"  Dominios rasos : {len(dominios_rasos)} dominios")
    print(f"  Relatorio      : {REPORT_FILE}")
    print(f"  JSON           : {JSON_FILE}")
    print("=" * 70)
    print()
    print("  PROXIMO PASSO:")
    print("  Revise o relatorio e execute o script de reposicionamento")

if __name__ == "__main__":
    main()
