"""
NEXOR -- COMPLETAR E TRADUZIR TODOS OS INCOMPLETOS CFE v1
Resolve dois problemas de uma vez:
1. Quizzes EN com menos de 50q → completa ate 50q
2. Quizzes sem PT ou ES → cria os idiomas faltantes

Aplica FractalLearning v1 em todas as gerações.

USO:
    python completar_e_traduzir_cfe.py
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
MÉTODO NEXOR DE FORMULAÇÃO — APLICAR:
- Cenário profissional no stem (Standard/Hard)
- Lead-in como pergunta completa
- 4 opções homogêneas em comprimento
- Correta não é a mais longa
- Sem absolutos, sem clang, sem convergência
- justification_correct: explica o princípio técnico
- justification_wrong: explica cada distrator
"""

LANG_CONFIG = {
    "pt": "Portugues (Brasil)",
    "es": "Espanol (neutro latinoamericano)",
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

def generate_questions(client, domain_id, domain_name, existing_tags, n_needed, num_start):
    """Gera n_needed questões novas para o domínio."""
    tags_str = ", ".join(list(existing_tags)[:15])
    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

DOMAIN: {domain_name} ({domain_id})
EXISTING TOPICS (avoid repeating): {tags_str}

{METODO_NEXOR}

Generate exactly {n_needed} NEW questions covering DIFFERENT topics.
Mix difficulty: ~20% EASY, ~60% STANDARD, ~20% HARD.
Start numbering from num={num_start}.
US law scope only. CFE 2026 exam content.

Return ONLY valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full question",
  "tag": "snake_case_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "STANDARD",
  "justification_correct": "Principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

    try:
        qs = call_api(client, prompt)
        for i, q in enumerate(qs):
            q["num"] = num_start + i
        return qs
    except Exception as e:
        print(f" ERRO:{e}", end="")
        # Individual fallback
        results = []
        for i in range(min(n_needed, 5)):  # max 5 individual
            try:
                p2 = f"Generate 1 CFE question for {domain_name}. New topic not in: {tags_str[:100]}. num={num_start+i}. Return ONLY JSON array."
                r = call_api(client, p2)
                if r: 
                    r[0]["num"] = num_start + i
                    results.append(r[0])
            except:
                pass
        return results

def translate_block(client, questions, lang_name):
    """Traduz em blocos de 5."""
    translated = []
    for i in range(0, len(questions), 5):
        bloco = questions[i:i+5]
        print(".", end="", flush=True)
        prompt = f"""Translate these CFE questions from English to {lang_name}.
Rules: translate text/options/justifications only.
Keep num/tag/correct/difficulty unchanged.
Keep legal terms in English (FCPA, SOX, RICO, etc).
Return ONLY JSON array, no markdown.
Input: {json.dumps(bloco, ensure_ascii=False)}"""
        try:
            result = call_api(client, prompt)
            # Garante campos intactos
            for j, q in enumerate(result):
                if j < len(bloco):
                    q["num"]       = bloco[j]["num"]
                    q["tag"]       = bloco[j]["tag"]
                    q["correct"]   = bloco[j]["correct"]
                    q["difficulty"]= bloco[j].get("difficulty","STANDARD")
            translated.extend(result)
        except Exception as e:
            print(f"ERR", end="")
            translated.extend(bloco)
    return translated

def process_quiz(client, domain_id, quiz_num):
    """Processa um quiz: completa EN se necessário e cria PT/ES se faltantes."""
    base      = Path(QUIZZES_DIR) / domain_id
    quiz_base = f"quiz_{quiz_num:03d}"
    en_path   = base / f"{quiz_base}_en.json"

    if not en_path.exists():
        return False

    data_en   = load_json(str(en_path))
    questions = data_en["questions"]
    current   = len(questions)
    domain_name = data_en.get("domain_name", domain_id.replace("_"," ").title())
    existing_tags = set(q.get("tag","") for q in questions)

    needs_completion = current < 50
    new_qs = []

    # PASSO 1: Completa EN se necessário
    if needs_completion:
        n_needed  = 50 - current
        num_start = max(q["num"] for q in questions) + 1 if questions else 1
        print(f"  +{n_needed}q EN ", end="", flush=True)

        new_qs = generate_questions(client, domain_id, domain_name, existing_tags, n_needed, num_start)

        if new_qs:
            all_qs = questions + new_qs
            for i, q in enumerate(all_qs):
                q["num"] = i + 1
            data_en["questions"] = all_qs
            save_json(str(en_path), data_en)
            questions = all_qs
            print(f"→ {len(questions)}q ✅", end="")
        else:
            print("→ FALHOU", end="")

    # PASSO 2: Cria/completa PT e ES
    for lang_code, lang_name in LANG_CONFIG.items():
        lang_path = base / f"{quiz_base}_{lang_code}.json"

        if not lang_path.exists():
            # Cria do zero — traduz tudo
            print(f" | {lang_code.upper()}(criar) ", end="", flush=True)
            translated = translate_block(client, questions, lang_name)
            for i, q in enumerate(translated):
                q["num"] = i + 1
            lang_data = dict(data_en)
            lang_data["lang"]      = lang_code
            lang_data["questions"] = translated
            save_json(str(lang_path), lang_data)
            print(f"→{len(translated)}q", end="")

        else:
            # Verifica se está incompleto
            lang_data = load_json(str(lang_path))
            lang_qs   = lang_data["questions"]
            lang_count = len(lang_qs)

            if lang_count < 50 and new_qs:
                # Traduz apenas as novas
                print(f" | {lang_code.upper()}(+{len(new_qs)}) ", end="", flush=True)
                translated_new = translate_block(client, new_qs, lang_name)
                all_lang = lang_qs + translated_new
                for i, q in enumerate(all_lang):
                    q["num"] = i + 1
                # Trim se passou de 50
                if len(all_lang) > 50:
                    all_lang = all_lang[:50]
                    for i, q in enumerate(all_lang):
                        q["num"] = i + 1
                lang_data["questions"] = all_lang
                save_json(str(lang_path), lang_data)
                print(f"→{len(all_lang)}q", end="")

            elif lang_count < 50 and not new_qs:
                # EN já estava completo mas lang incompleto — completa traduzindo EN
                missing = questions[lang_count:]
                if missing:
                    print(f" | {lang_code.upper()}(fill {len(missing)}) ", end="", flush=True)
                    translated_missing = translate_block(client, missing, lang_name)
                    all_lang = lang_qs + translated_missing
                    for i, q in enumerate(all_lang):
                        q["num"] = i + 1
                    if len(all_lang) > 50:
                        all_lang = all_lang[:50]
                        for i, q in enumerate(all_lang):
                            q["num"] = i + 1
                    lang_data["questions"] = all_lang
                    save_json(str(lang_path), lang_data)
                    print(f"→{len(all_lang)}q", end="")

    print()
    return True

def main():
    print("=" * 70)
    print("  NEXOR -- COMPLETAR E TRADUZIR TODOS OS INCOMPLETOS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    # Identifica todos os quizzes com problema
    targets = []
    base = Path(QUIZZES_DIR)

    for domain_dir in sorted(base.iterdir()):
        if not domain_dir.is_dir(): continue
        domain_id = domain_dir.name

        # Mapeia quizzes existentes
        quizzes = {}
        for f in domain_dir.glob("quiz_*.json"):
            if "bak" in f.name: continue
            parts = f.name.replace(".json","").split("_")
            if len(parts) < 3: continue
            num  = int(parts[1])
            lang = parts[2]
            if num not in quizzes: quizzes[num] = {}
            data = load_json(str(f))
            quizzes[num][lang] = len(data["questions"])

        for num, langs in sorted(quizzes.items()):
            en_count = langs.get("en", 0)
            pt_count = langs.get("pt", 0)
            es_count = langs.get("es", 0)
            has_problem = (
                en_count < 50 or
                pt_count < 50 or
                es_count < 50 or
                "pt" not in langs or
                "es" not in langs
            )
            if has_problem:
                targets.append((domain_id, num, en_count, pt_count, es_count))

    print(f"\n  Quizzes com problema: {len(targets)}")
    print()

    ok = 0
    for domain_id, quiz_num, en_q, pt_q, es_q in targets:
        status = f"EN:{en_q} PT:{pt_q} ES:{es_q}"
        print(f"  {domain_id}/quiz_{quiz_num:03d} [{status}]", end="")
        success = process_quiz(client, domain_id, quiz_num)
        if success: ok += 1

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(targets)} processados")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
