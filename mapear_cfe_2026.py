"""
NEXOR -- MAPEADOR CFE 2026 v1
Mapeia todas as questoes CFE existentes para a nova estrutura
de 3 secoes e 45 dominios valida a partir de 02/06/2026.
Usa a tag de cada questao como ancora de classificacao via API.
Gera relatorio de cobertura por dominio.

USO:
    python mapear_cfe_2026.py
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
REPORT_FILE = f"mapeamento_cfe_2026_{TIMESTAMP}.txt"
JSON_FILE   = f"cobertura_cfe_2026_{TIMESTAMP}.json"

# Nova estrutura CFE 2026 -- 3 secoes, 45 dominios
ESTRUTURA_2026 = {
    "S1": {
        "nome": "Fraud Schemes and Financial Crimes",
        "dominios": {
            "S1D01": "Accounting Concepts and Financial Statement Analysis",
            "S1D02": "Financial Statement Fraud",
            "S1D03": "Asset Misappropriation — Cash Receipts",
            "S1D04": "Asset Misappropriation — Fraudulent Disbursements",
            "S1D05": "Asset Misappropriation — Inventory and Other Assets",
            "S1D06": "Corruption, Bribery, and Conflicts of Interest",
            "S1D07": "Theft of Data and Intellectual Property",
            "S1D08": "Identity Theft and Cyberfraud",
            "S1D09": "Financial Institution Fraud and Money Laundering",
            "S1D10": "Securities and Investment Fraud",
            "S1D11": "Payment Fraud",
            "S1D12": "Insurance Fraud",
            "S1D13": "Consumer Fraud and Scams",
            "S1D14": "Bankruptcy Fraud",
            "S1D15": "Tax Fraud",
            "S1D16": "Health Care Fraud",
            "S1D17": "Government and Public Sector Fraud",
            "S1D18": "Procurement and Contract Fraud",
            "S1D19": "International and Cross-Border Fraud",
            "S1D20": "Emerging Fraud Schemes and Technology",
        }
    },
    "S2": {
        "nome": "Fraud Investigations and Legal Issues",
        "dominios": {
            "S2D01": "Planning and Conducting a Fraud Examination",
            "S2D02": "Legal Issues in Conducting Investigations",
            "S2D03": "The Law Related to Fraud",
            "S2D04": "Overview of the Legal System",
            "S2D05": "Criminal Prosecutions",
            "S2D06": "Non-Criminal Actions (Civil and Administrative)",
            "S2D07": "Individual Rights During Examinations",
            "S2D08": "Basic Principles of Evidence",
            "S2D09": "Collecting Evidence",
            "S2D10": "Sources of Information",
            "S2D11": "Data Analysis and Reporting Tools",
            "S2D12": "Tracing Illicit Transactions and Assets",
            "S2D13": "Interview Theory and Application",
            "S2D14": "Covert Operations",
            "S2D15": "Report Writing",
            "S2D16": "Testifying as an Expert Witness",
        }
    },
    "S3": {
        "nome": "Fraud Prevention and Deterrence",
        "dominios": {
            "S3D01": "Understanding Criminal Behavior and White-Collar Crime",
            "S3D02": "Occupational Fraud",
            "S3D03": "Corporate Governance",
            "S3D04": "Management's and Auditors' Responsibilities",
            "S3D05": "Fraud Risk Assessment",
            "S3D06": "Internal Controls and Anti-Fraud Programs",
            "S3D07": "Fraud Prevention Programs",
            "S3D08": "Fraud Risk Management",
            "S3D09": "Ethics for Fraud Examiners",
        }
    }
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def build_classification_prompt(tags_batch):
    """Prompt para classificar um lote de tags nos 45 dominios."""
    dominios_str = ""
    for sec_id, sec in ESTRUTURA_2026.items():
        dominios_str += f"\n{sec_id}: {sec['nome']}\n"
        for dom_id, dom_nome in sec["dominios"].items():
            dominios_str += f"  {dom_id}: {dom_nome}\n"

    tags_str = json.dumps(tags_batch, ensure_ascii=False, indent=2)

    return f"""You are an expert CFE (Certified Fraud Examiner) exam content classifier.

Classify each question tag below into the correct domain of the new CFE Exam 2026 structure.

NEW CFE EXAM 2026 STRUCTURE:
{dominios_str}

Tags to classify (format: "tag": "domain_code"):
{tags_str}

RULES:
- Use ONLY the domain codes shown above (S1D01 through S3D09)
- If a tag could fit multiple domains, choose the PRIMARY one
- If a tag is unclear, use your best judgment based on CFE content
- Return ONLY a valid JSON object mapping each tag to its domain code

Example output format:
{{"fcpa_anti_bribery_elements": "S2D03", "cash_skimming_detection": "S1D03"}}

Return ONLY the JSON object, no markdown, no explanation."""

def classify_tags_batch(client, tags_batch):
    """Classifica um lote de tags via API."""
    prompt = build_classification_prompt(tags_batch)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"\n    Erro API: {e}")
        return {}

def collect_cfe_questions():
    """Coleta todas as questoes EN do CFE."""
    questions_by_tag = defaultdict(list)  # tag -> [{"file", "num"}]
    all_questions = []

    base = Path(QUIZZES_DIR)
    for domain_dir in sorted(base.iterdir()):
        if not domain_dir.is_dir():
            continue
        domain_id = domain_dir.name

        for quiz_file in sorted(domain_dir.glob("quiz_*_en.json")):
            try:
                data = load_json(str(quiz_file))
                for q in data.get("questions", []):
                    tag = q.get("tag", "unknown").strip()
                    info = {
                        "domain": domain_id,
                        "file": quiz_file.name,
                        "num": q.get("num"),
                        "tag": tag,
                        "text_preview": q.get("text", "")[:60]
                    }
                    questions_by_tag[tag].append(info)
                    all_questions.append(info)
            except Exception as e:
                print(f"  Erro ao ler {quiz_file}: {e}")

    return all_questions, questions_by_tag

def main():
    print("=" * 70)
    print("  NEXOR -- MAPEADOR CFE 2026 v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    # 1. Coleta questoes
    print("\n  Coletando questoes CFE...")
    all_questions, questions_by_tag = collect_cfe_questions()
    unique_tags = list(questions_by_tag.keys())

    print(f"  Total questoes EN : {len(all_questions)}")
    print(f"  Tags unicas       : {len(unique_tags)}")

    # 2. Classifica tags em lotes de 30
    print(f"\n  Classificando {len(unique_tags)} tags em lotes de 30...")
    tag_to_domain = {}
    batch_size = 30

    for i in range(0, len(unique_tags), batch_size):
        batch = unique_tags[i:i+batch_size]
        end = min(i+batch_size, len(unique_tags))
        print(f"  Tags {i+1}-{end}... ", end="", flush=True)
        result = classify_tags_batch(client, batch)
        tag_to_domain.update(result)
        print(f"OK ({len(result)} classificadas)")

    # 3. Compila cobertura por dominio
    cobertura = defaultdict(list)
    nao_classificadas = []

    for tag, infos in questions_by_tag.items():
        domain_code = tag_to_domain.get(tag, "UNKNOWN")
        if domain_code == "UNKNOWN" or domain_code not in [
            d for sec in ESTRUTURA_2026.values() for d in sec["dominios"]
        ]:
            nao_classificadas.extend(infos)
        else:
            cobertura[domain_code].extend(infos)

    # 4. Gera relatorio
    report_lines = [
        f"NEXOR -- MAPEAMENTO CFE 2026 -- {TIMESTAMP}",
        f"Total questoes EN analisadas: {len(all_questions)}",
        f"Tags unicas classificadas: {len(unique_tags)}",
        "=" * 70,
        "",
    ]

    cobertura_json = {}
    total_com_cobertura = 0
    dominios_zerados = []
    dominios_rasos = []

    for sec_id, sec_data in ESTRUTURA_2026.items():
        report_lines.append(f"\n{'─'*70}")
        report_lines.append(f"SECAO {sec_id}: {sec_data['nome']}")
        report_lines.append(f"{'─'*70}")

        sec_total = 0
        for dom_id, dom_nome in sec_data["dominios"].items():
            qs = cobertura.get(dom_id, [])
            n = len(qs)
            sec_total += n
            total_com_cobertura += n

            # Status
            if n == 0:
                status = "❌ LACUNA TOTAL"
                dominios_zerados.append(f"{dom_id}: {dom_nome}")
            elif n < 20:
                status = f"⚠️  RASO"
                dominios_rasos.append(f"{dom_id}: {dom_nome} ({n}q)")
            elif n < 50:
                status = "🔶 MODERADO"
            else:
                status = "✅ BEM COBERTO"

            report_lines.append(f"  {dom_id} · {dom_nome}")
            report_lines.append(f"         {n} questoes · {status}")

            # Tags encontradas
            tags_neste_dom = list(set(q["tag"] for q in qs))[:5]
            if tags_neste_dom:
                report_lines.append(f"         Tags: {', '.join(tags_neste_dom[:3])}...")

            cobertura_json[dom_id] = {
                "nome": dom_nome,
                "secao": sec_id,
                "total_questoes": n,
                "status": status.replace("❌ ", "").replace("⚠️  ", "").replace("🔶 ", "").replace("✅ ", ""),
                "tags": list(set(q["tag"] for q in qs)),
                "arquivos": list(set(q["domain"] + "/" + q["file"] for q in qs)),
            }

        report_lines.append(f"\n  SUBTOTAL SECAO {sec_id}: {sec_total} questoes")

    # Resumo executivo
    report_lines += [
        "",
        "=" * 70,
        "RESUMO EXECUTIVO",
        "=" * 70,
        f"Total questoes mapeadas : {total_com_cobertura}",
        f"Nao classificadas       : {len(nao_classificadas)}",
        "",
        f"DOMINIOS COM LACUNA TOTAL ({len(dominios_zerados)}):",
    ]
    for d in dominios_zerados:
        report_lines.append(f"  ❌ {d}")

    report_lines += [
        "",
        f"DOMINIOS RASOS - menos de 20q ({len(dominios_rasos)}):",
    ]
    for d in dominios_rasos:
        report_lines.append(f"  ⚠️  {d}")

    report_lines += [
        "",
        "PRIORIDADE DE GERACAO (lacunas primeiro, rasos depois)",
        "Use este relatorio para guiar o FractalLearning.",
    ]

    # Salva relatorio texto
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    # Salva JSON de cobertura
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(cobertura_json, f, ensure_ascii=False, indent=2)

    # Resumo no terminal
    print("\n" + "=" * 70)
    print(f"  CONCLUIDO")
    print(f"  Questoes mapeadas    : {total_com_cobertura}")
    print(f"  Nao classificadas    : {len(nao_classificadas)}")
    print(f"  Lacunas totais       : {len(dominios_zerados)} dominios")
    print(f"  Dominios rasos       : {len(dominios_rasos)} dominios")
    print(f"  Relatorio            : {REPORT_FILE}")
    print(f"  JSON de cobertura    : {JSON_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
