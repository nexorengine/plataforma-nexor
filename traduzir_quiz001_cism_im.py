"""
NEXOR -- TRADUTOR DE QUIZ v2
Traduz quiz_001_en.json para PT e ES via API Anthropic.
Blocos de 10 questoes com retry automatico e fallback questao a questao.
"""

import json
import anthropic
from pathlib import Path

SOURCE_FILE = r"static\quizzes\cism\incident_management\quiz_001_en.json"
OUTPUT_DIR  = r"static\quizzes\cism\incident_management"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
BLOCK_SIZE  = 10

LANG_CONFIG = {
    "pt": {
        "lang_name": "Portugues (Brasil)",
        "domain_name": "Gestao de Incidentes",
        "cert_name": "Certified Information Security Manager",
    },
    "es": {
        "lang_name": "Espanol (neutro, latinoamericano)",
        "domain_name": "Gestion de Incidentes",
        "cert_name": "Certified Information Security Manager",
    },
}

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def build_prompt(questions_block, lang_name):
    block_json = json.dumps(questions_block, ensure_ascii=False, indent=2)
    return f"""You are a professional certification exam translator specializing in information security.

Translate the following JSON array of exam questions from English to {lang_name}.

CRITICAL RULES:
1. Translate ONLY these fields: "text", "options", "justification_correct", "justification_wrong"
2. DO NOT translate or modify: "num", "tag", "correct"
3. Keep option prefixes exactly as-is: "A. ", "B. ", "C. ", "D. "
4. Maintain technical accuracy -- use standard {lang_name} terminology for CISM concepts
5. Keep the same JSON structure exactly
6. Return ONLY the JSON array -- no markdown, no explanation, no preamble

Input:
{block_json}"""

def translate_single(client, question, lang_name):
    prompt = build_prompt([question], lang_name)
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    return result[0] if isinstance(result, list) else result

def translate_block(client, questions, lang_name):
    prompt = build_prompt(questions, lang_name)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        print(f"\n    AVISO: erro no bloco ({e}). Fallback questao a questao...")
        results = []
        for q in questions:
            print(f"    Q{q['num']} ... ", end="", flush=True)
            translated = translate_single(client, q, lang_name)
            results.append(translated)
            print("OK")
        return results

def translate_quiz(client, source_data, lang_code, lang_cfg):
    questions = source_data["questions"]
    total = len(questions)
    translated_questions = []

    print(f"\n  [{lang_code.upper()}] Traduzindo {total} questoes em blocos de {BLOCK_SIZE}...")

    for start in range(0, total, BLOCK_SIZE):
        block = questions[start:start + BLOCK_SIZE]
        end = start + len(block)
        print(f"  Bloco {start+1}-{end} ... ", end="", flush=True)
        translated_block = translate_block(client, block, lang_cfg["lang_name"])
        translated_questions.extend(translated_block)
        print(f"OK ({len(translated_block)}q)")

    translated_data = {
        "cert_id":     source_data["cert_id"],
        "domain_id":   source_data["domain_id"],
        "quiz_num":    source_data["quiz_num"],
        "domain_name": lang_cfg["domain_name"],
        "cert_name":   lang_cfg["cert_name"],
        "lang":        lang_code,
        "questions":   translated_questions
    }
    return translated_data

def validate(original, translated):
    errors = []
    orig_q  = original["questions"]
    trans_q = translated["questions"]

    if len(orig_q) != len(trans_q):
        errors.append(f"Contagem diferente: original={len(orig_q)}, traduzido={len(trans_q)}")
        return errors

    for o, t in zip(orig_q, trans_q):
        if o["num"]     != t.get("num"):     errors.append(f"Q{o['num']}: num alterado")
        if o["tag"]     != t.get("tag"):     errors.append(f"Q{o['num']}: tag alterada")
        if o["correct"] != t.get("correct"): errors.append(f"Q{o['num']}: correct alterado")
        opts = t.get("options", [])
        if len(opts) != 4:
            errors.append(f"Q{o['num']}: {len(opts)} opcoes (esperado 4)")
        for j, opt in enumerate(opts):
            prefix = ["A. ", "B. ", "C. ", "D. "][j]
            if not opt.startswith(prefix):
                errors.append(f"Q{o['num']} opcao {j}: prefixo ausente")
    return errors

def main():
    print("=" * 70)
    print("  NEXOR -- TRADUTOR DE QUIZ v2")
    print("  CISM . incident_management . quiz_001")
    print("=" * 70)

    client = anthropic.Anthropic()
    source = load_json(SOURCE_FILE)
    print(f"\n  Fonte   : {SOURCE_FILE}")
    print(f"  Questoes: {len(source['questions'])}")

    for lang_code, lang_cfg in LANG_CONFIG.items():
        print(f"\n{'─'*70}")
        print(f"  IDIOMA: {lang_cfg['lang_name']}")
        print(f"{'─'*70}")

        translated = translate_quiz(client, source, lang_code, lang_cfg)
        errors = validate(source, translated)

        if errors:
            print(f"\n  ERROS ({len(errors)}):")
            for e in errors:
                print(f"    x {e}")
            print("  ARQUIVO NAO SALVO.")
            continue

        out_path = Path(OUTPUT_DIR) / f"quiz_001_{lang_code}.json"
        save_json(str(out_path), translated)
        print(f"\n  OK Salvo: {out_path}")
        print(f"  Questoes: {len(translated['questions'])} | Erros: 0")

    print("\n" + "=" * 70)
    print("  CONCLUIDO -- rode verificar_duplicatas.py a seguir")
    print("=" * 70)

if __name__ == "__main__":
    main()
