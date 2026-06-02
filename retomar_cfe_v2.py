"""
NEXOR -- RETOMADA CFE v2
Completa arquivos incompletos baseado no estado atual.
Logica: le o EN como fonte da verdade, completa se necessario,
depois sincroniza PT e ES para o mesmo numero de questoes.

USO:
    python retomar_cfe_v2.py
"""

import json
import os
import anthropic
from pathlib import Path
from datetime import datetime
import shutil

OUTPUT_DIR = r"static\quizzes\cfe"
MODEL      = "claude-sonnet-4-5"
MAX_TOKENS = 8192
TIMESTAMP  = datetime.now().strftime("%Y%m%d_%H%M")

# Estado atual por arquivo EN (questoes atuais)
ARQUIVOS = {
    "law_cfe/quiz_003": {"en": 50, "pt": 33, "es": 31},
    "law_cfe/quiz_004": {"en": 31, "pt": 31, "es": 31},
    "law_cfe/quiz_005": {"en": 32, "pt": 32, "es": 32},
    "law_cfe/quiz_006": {"en": 32, "pt": 32, "es": 32},
    "prevention_deterrence/quiz_006": {"en": 43, "pt": 43, "es": 43},
}

TOPICOS_LAW = [
    "FCPA anti-bribery elements jurisdiction covered persons",
    "FCPA accounting provisions books records internal controls",
    "FCPA third party liability agent due diligence",
    "FCPA affirmative defenses local law promotional expenses",
    "SOX Section 302 CEO CFO certification liability",
    "SOX Section 404 ICFR management assessment auditor",
    "SOX Section 806 whistleblower employee protections",
    "RICO elements pattern racketeering predicate acts",
    "BSA currency transaction reports CTR 10000 threshold",
    "BSA suspicious activity reports SAR filing obligations",
    "AML Know Your Customer KYC Customer Due Diligence",
    "Dodd-Frank SEC whistleblower bounty program awards",
    "18 USC 1343 wire fraud elements interstate commerce",
    "18 USC 1956 money laundering concealment proceeds",
    "Computer Fraud Abuse Act unauthorized access elements",
    "Honest Services Fraud 18 USC 1346 bribery kickbacks",
    "False Claims Act qui tam relator bounty provisions",
    "Federal Sentencing Guidelines fraud offense levels",
    "PCAOB authority auditor independence public companies",
    "Corporate criminal liability respondeat superior doctrine",
]

TOPICOS_PREVENTION = [
    "Internal controls preventive detective corrective types",
    "Segregation of duties incompatible functions",
    "Anti-fraud program elements ACFE standards",
    "Whistleblower hotline anonymous reporting design",
    "Fraud risk assessment methodology frequency",
    "Data analytics continuous monitoring fraud detection",
    "Pre-employment background screening fraud prevention",
]

LANG_CONFIG = {
    "pt": "Portugues (Brasil)",
    "es": "Espanol (neutro latinoamericano)",
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup(path):
    bak = path + f".bak_{TIMESTAMP}"
    if not os.path.exists(bak):
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

def generate_en_questions(client, domain_id, n_needed, num_start, existing_tags):
    pool = TOPICOS_LAW if "law" in domain_id else TOPICOS_PREVENTION
    topicos = pool[:n_needed] if n_needed <= len(pool) else pool * 2
    topicos = topicos[:n_needed]
    topicos_str = "\n".join(f"  - {t}" for t in topicos)

    prompt = f"""Generate exactly {n_needed} CFE exam questions in English.
Domain: {domain_id}
US federal law and ACFE standards ONLY. No Brazilian law.

TOPICS:
{topicos_str}

Start from num={num_start}.

Return ONLY valid JSON array, no markdown:
[{{"num":{num_start},"text":"...","tag":"snake_case","options":["A. ...","B. ...","C. ...","D. ..."],"correct":0,"justification_correct":"...","justification_wrong":"..."}}]"""

    try:
        qs = call_api(client, prompt)
        for i, q in enumerate(qs):
            q["num"] = num_start + i
        return qs
    except Exception as e:
        print(f"\n    Erro bloco: {e}. Individual...")
        results = []
        for i, topico in enumerate(topicos):
            print(f"    Q{num_start+i}... ", end="", flush=True)
            try:
                p2 = f"""Generate 1 CFE exam question. Topic: {topico}
Domain: {domain_id}. US law only. num={num_start+i}.
Return ONLY JSON array with one object."""
                qs2 = call_api(client, p2)
                if isinstance(qs2, list) and qs2:
                    qs2[0]["num"] = num_start + i
                    results.append(qs2[0])
                    print("OK")
                else:
                    print("SKIP")
            except Exception as e2:
                print(f"FALHOU: {e2}")
        return results

def translate_questions(client, questions, lang_name):
    if not questions:
        return []
    translated = []
    block_size = 5  # blocos menores para evitar truncamento
    for i in range(0, len(questions), block_size):
        bloco = questions[i:i+block_size]
        block_json = json.dumps(bloco, ensure_ascii=False, indent=2)
        prompt = f"""Translate these CFE exam questions from English to {lang_name}.

RULES:
1. Translate ONLY: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT modify: "num", "tag", "correct"
3. Keep prefixes: "A. ", "B. ", "C. ", "D. "
4. Keep US law names in English: FCPA, SOX, RICO, BSA, AML, CFAA
5. Return ONLY the JSON array, no markdown

Input:
{block_json}"""
        try:
            result = call_api(client, prompt)
            translated.extend(result)
            print(f".", end="", flush=True)
        except Exception as e:
            print(f"\n    Erro traducao bloco {i}-{i+block_size}: {e}")
            translated.extend(bloco)  # fallback: mantém EN
    return translated

def process(client, base_key, state):
    parts     = base_key.split("/")
    domain_id = parts[0]
    quiz_base = parts[1]

    en_path = Path(OUTPUT_DIR) / domain_id / f"{quiz_base}_en.json"
    if not en_path.exists():
        print(f"  EN nao encontrado: {en_path}")
        return

    # FASE 1: Completa EN se necessario
    en_data = load_json(str(en_path))
    en_questions = en_data["questions"]
    en_count = len(en_questions)

    if en_count < 50:
        n_needed = 50 - en_count
        num_start = max(q["num"] for q in en_questions) + 1
        print(f"  EN: {en_count}q → gerando {n_needed}q...")
        backup(str(en_path))
        new_qs = generate_en_questions(client, domain_id, n_needed, num_start, 
                                        set(q.get("tag","") for q in en_questions))
        en_questions = en_questions + new_qs
        for i, q in enumerate(en_questions):
            q["num"] = i + 1
        en_data["questions"] = en_questions
        save_json(str(en_path), en_data)
        print(f"  EN salvo: {len(en_questions)}q")
    else:
        print(f"  EN: {en_count}q ✅")

    # FASE 2: Sincroniza PT e ES
    for lang_code, lang_name in LANG_CONFIG.items():
        lang_path = Path(OUTPUT_DIR) / domain_id / f"{quiz_base}_{lang_code}.json"
        if not lang_path.exists():
            print(f"  {lang_code.upper()}: arquivo nao encontrado")
            continue

        lang_data = load_json(str(lang_path))
        lang_questions = lang_data["questions"]
        lang_count = len(lang_questions)

        if lang_count >= 50:
            print(f"  {lang_code.upper()}: {lang_count}q ✅")
            continue

        # Identifica quais questoes EN nao tem traducao
        translated_nums = set(q["num"] for q in lang_questions)
        missing = [q for q in en_questions if q["num"] not in translated_nums]

        if not missing:
            print(f"  {lang_code.upper()}: sem questoes faltantes detectadas")
            continue

        print(f"  {lang_code.upper()}: {lang_count}q → traduzindo {len(missing)}q ", end="", flush=True)
        backup(str(lang_path))

        translated = translate_questions(client, missing, lang_name)
        print()

        all_lang = lang_questions + translated
        for i, q in enumerate(all_lang):
            q["num"] = i + 1

        lang_data["questions"] = all_lang
        save_json(str(lang_path), lang_data)
        print(f"  {lang_code.upper()} salvo: {len(all_lang)}q")

def main():
    print("=" * 70)
    print("  NEXOR -- RETOMADA CFE v2")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    for base_key, state in ARQUIVOS.items():
        print(f"\n{'─'*70}")
        print(f"  {base_key}")
        print(f"  EN:{state['en']} PT:{state['pt']} ES:{state['es']}")
        print(f"{'─'*70}")
        process(client, base_key, state)

    print("\n" + "=" * 70)
    print("  CONCLUIDO")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
