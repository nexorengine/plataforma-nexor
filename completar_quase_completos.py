"""
NEXOR -- COMPLETAR QUASE COMPLETOS CFE v1
Completa automaticamente todos os quizzes EN com 40-49 questoes
nos dominios CFE novos. Usa a tag das questoes existentes como
contexto para gerar as faltantes com FractalLearning.

USO:
    python completar_quase_completos.py
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

def get_domain_context(domain_id, existing_tags):
    """Gera contexto do domínio baseado nas tags existentes."""
    tags_sample = list(existing_tags)[:10]
    return f"CFE 2026 domain: {domain_id.replace('_', ' ').title()}. Existing topics: {', '.join(tags_sample)}"

def generate_completion(client, domain_id, domain_name, existing_questions, n_needed, num_start):
    """Gera as questões faltantes para completar o quiz."""
    existing_tags = set(q.get("tag", "") for q in existing_questions)
    domain_ctx = get_domain_context(domain_id, existing_tags)

    # Determina distribuição de dificuldade das faltantes
    existing_easy = sum(1 for q in existing_questions if q.get("difficulty","STANDARD") == "EASY")
    existing_std  = sum(1 for q in existing_questions if q.get("difficulty","STANDARD") == "STANDARD")
    existing_hard = sum(1 for q in existing_questions if q.get("difficulty","STANDARD") == "HARD")
    total = len(existing_questions)

    # Meta: 20% Easy, 60% Standard, 20% Hard
    target_easy = max(0, round(50 * 0.20) - existing_easy)
    target_std  = max(0, round(50 * 0.60) - existing_std)
    target_hard = max(0, round(50 * 0.20) - existing_hard)

    # Distribui as n_needed questões proporcionalmente
    total_target = target_easy + target_std + target_hard
    if total_target == 0:
        # Gera tudo como STANDARD
        levels = ["STANDARD"] * n_needed
    else:
        levels = []
        if target_easy > 0:
            levels += ["EASY"] * min(target_easy, max(1, round(n_needed * target_easy / total_target)))
        if target_hard > 0:
            levels += ["HARD"] * min(target_hard, max(1, round(n_needed * target_hard / total_target)))
        # Preenche o resto com STANDARD
        while len(levels) < n_needed:
            levels.append("STANDARD")
        levels = levels[:n_needed]

    prompt = f"""You are an expert CFE (Certified Fraud Examiner) exam question writer.

DOMAIN: {domain_name} ({domain_id})
CONTEXT: {domain_ctx}

{METODO_NEXOR}

Generate exactly {n_needed} NEW questions to COMPLETE this quiz.
These questions must cover DIFFERENT topics than already covered.
Avoid repeating any of these existing tags: {', '.join(list(existing_tags)[:20])}

Difficulty distribution needed:
{', '.join(levels)}

Start numbering from num={num_start}.

For each question, difficulty levels:
- EASY: Bloom 1-2, direct definition or basic concept
- STANDARD: Bloom 3, application in professional scenario
- HARD: Bloom 4-5, complex analysis with multiple variables

US law scope only. No Brazilian law.

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
            if i < len(levels):
                q["difficulty"] = levels[i]
        return qs
    except Exception as e:
        print(f"\n    Erro: {e}")
        # Tenta individual
        results = []
        for i in range(n_needed):
            try:
                p2 = f"""Generate 1 CFE question for domain: {domain_name}.
Topic: new topic not in {list(existing_tags)[:5]}
Difficulty: {levels[i] if i < len(levels) else 'STANDARD'}
num={num_start+i}
Return ONLY JSON array with one object."""
                qs2 = call_api(client, p2)
                if qs2:
                    qs2[0]["num"] = num_start + i
                    results.append(qs2[0])
            except:
                pass
        return results

def translate_questions(client, questions, lang_name):
    """Traduz questões em blocos de 5."""
    translated = []
    for i in range(0, len(questions), 5):
        bloco = questions[i:i+5]
        print(".", end="", flush=True)
        prompt = f"""Translate these CFE questions from English to {lang_name}.
Rules: translate text/options/justifications only. Keep num/tag/correct/difficulty unchanged.
Keep legal terms in English. Return ONLY JSON array, no markdown.
Input: {json.dumps(bloco, ensure_ascii=False)}"""
        try:
            result = call_api(client, prompt)
            translated.extend(result)
        except:
            translated.extend(bloco)
    return translated

def process_domain(client, domain_id, quiz_fname):
    """Completa um quiz EN e sincroniza PT/ES."""
    en_path = Path(QUIZZES_DIR) / domain_id / quiz_fname

    data = load_json(str(en_path))
    questions = data["questions"]
    current_count = len(questions)
    n_needed = 50 - current_count
    num_start = max(q["num"] for q in questions) + 1
    domain_name = data.get("domain_name", domain_id)

    print(f"\n  {domain_id}/{quiz_fname}: {current_count}q → +{n_needed}q")

    # Gera em bloco
    new_qs = generate_completion(client, domain_id, domain_name, questions, n_needed, num_start)

    if not new_qs:
        print("  FALHOU — sem questões geradas")
        return False

    # Salva EN
    backup(str(en_path))
    all_qs = questions + new_qs
    for i, q in enumerate(all_qs):
        q["num"] = i + 1
    data["questions"] = all_qs
    save_json(str(en_path), data)
    print(f"  EN: {len(all_qs)}q ✅")

    # Sincroniza PT e ES
    for lang_code, lang_name in LANG_CONFIG.items():
        lang_fname = quiz_fname.replace("_en.json", f"_{lang_code}.json")
        lang_path  = Path(QUIZZES_DIR) / domain_id / lang_fname

        if not lang_path.exists():
            # Cria do zero traduzindo tudo
            print(f"  {lang_code.upper()} (criar) ", end="", flush=True)
            translated = translate_questions(client, all_qs, lang_name)
            for i, q in enumerate(translated):
                q["num"] = i + 1
            lang_data = dict(data)
            lang_data["lang"] = lang_code
            lang_data["questions"] = translated
            save_json(str(lang_path), lang_data)
            print(f"\n  {lang_code.upper()}: {len(translated)}q ✅")
        else:
            # Adiciona apenas as novas
            backup(str(lang_path))
            lang_data = load_json(str(lang_path))
            lang_qs   = lang_data["questions"]
            print(f"  {lang_code.upper()} (+{len(new_qs)}) ", end="", flush=True)
            translated_new = translate_questions(client, new_qs, lang_name)
            all_lang = lang_qs + translated_new
            for i, q in enumerate(all_lang):
                q["num"] = i + 1
            lang_data["questions"] = all_lang
            save_json(str(lang_path), lang_data)
            print(f"\n  {lang_code.upper()}: {len(all_lang)}q ✅")

    return True

def main():
    print("=" * 70)
    print("  NEXOR -- COMPLETAR QUASE COMPLETOS CFE v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    client = anthropic.Anthropic()

    # Identifica quizzes EN com 40-49q
    targets = []
    base = Path(QUIZZES_DIR)
    for domain_dir in sorted(base.iterdir()):
        if not domain_dir.is_dir(): continue
        for quiz_file in sorted(domain_dir.glob("quiz_*_en.json")):
            data = load_json(str(quiz_file))
            q = len(data["questions"])
            if 40 <= q < 50:
                targets.append((domain_dir.name, quiz_file.name, q))

    print(f"\n  Quizzes a completar: {len(targets)}")
    for d, f, q in targets:
        print(f"  · {d}/{f}: {q}q (+{50-q})")

    print()
    ok = 0
    for domain_id, quiz_fname, q in targets:
        success = process_domain(client, domain_id, quiz_fname)
        if success: ok += 1

    print("\n" + "=" * 70)
    print(f"  CONCLUIDO: {ok}/{len(targets)} completados")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
