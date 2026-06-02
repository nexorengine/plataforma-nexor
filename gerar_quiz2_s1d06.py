"""
NEXOR -- GERADOR QUIZ 2 S1D06 -- EN/PT/ES v1
Gera quiz_002 completo (50q x 3 idiomas) para
corruption_bribery (S1D06).

Quiz 2 é mais difícil que Quiz 1:
  5 Easy + 25 Standard + 20 Hard = 50q

USO:
    python gerar_quiz2_s1d06.py
"""

import json
import anthropic
from pathlib import Path
from datetime import datetime

QUIZZES_DIR = r"static\quizzes\cfe"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192

DOMAIN = {
    "domain_id":   "corruption_bribery",
    "domain_code": "S1D06",
    "domain_name": "S1D06 · Corruption, Bribery & Conflicts of Interest",
    "context": """CFE Exam 2026 S1D06 — Corruption, Bribery and Conflicts of Interest.
Advanced topics: complex kickback schemes in multinational corporations,
bid rigging in public procurement (complementary bidding, bid suppression, bid rotation),
conflicts of interest (undisclosed financial interests, nepotism, self-dealing),
illegal gratuities vs bribery distinctions, economic extortion,
FCPA anti-bribery provisions (third-party liability, books and records, affirmative defenses),
UK Bribery Act (corporate offense, adequate procedures defense),
OECD Anti-Bribery Convention, shell company structures in corruption,
whistleblower protections, corporate compliance programs,
internal investigation procedures for corruption cases,
asset recovery in corruption cases, parallel proceedings."""
}

METODO = """
NEXOR METHOD v2 — QUIZ 2 (ADVANCED):
- More complex scenarios than Quiz 1
- Multi-variable situations requiring analysis
- Competing considerations or ambiguous facts
- Professional judgment required
- Correct answer is NOT the longest
- Genuinely plausible distractors
- No "all of the above" / "none of the above"
- justification_correct: explains the PRINCIPLE with depth
- justification_wrong: explains each distractor specifically
- US law scope only (FCPA, UK Bribery Act where relevant)
"""

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def call_api(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def get_existing_tags():
    path = Path(QUIZZES_DIR) / "corruption_bribery" / "quiz_001_en.json"
    if not path.exists():
        return set()
    data = load_json(str(path))
    return set(q.get("tag","") for q in data["questions"])

def generate_block(client, level, num_start, used_tags):
    tags_str = ", ".join(list(used_tags)[:20]) if used_tags else "none"

    if level == "EASY":
        diff_desc = "EASY (Bloom 1-2): Direct definition or basic concept. Simple stem."
    elif level == "STANDARD":
        diff_desc = "STANDARD (Bloom 3-4): Complex professional scenario requiring application and analysis."
    else:
        diff_desc = "HARD (Bloom 4-5): Multi-variable scenario with competing considerations, ambiguous facts, or nuanced legal distinctions requiring expert judgment."

    prompt = f"""You are an expert CFE exam question writer creating ADVANCED Quiz 2 questions.

DOMAIN: {DOMAIN['domain_name']}
CONTEXT: {DOMAIN['context']}

{METODO}

DIFFICULTY: {level}
{diff_desc}

Generate exactly 10 questions.
Start numbering from num={num_start}.
Cover DIFFERENT topics — avoid repeating: {tags_str}
These must be MORE CHALLENGING than Quiz 1 questions.

Return ONLY valid JSON array, no markdown:
[{{
  "num": {num_start},
  "text": "Full question text",
  "tag": "snake_case_topic_tag",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": 0,
  "difficulty": "{level}",
  "justification_correct": "Detailed principle explanation",
  "justification_wrong": "Why each distractor is wrong"
}}]"""

    qs = call_api(client, prompt)
    for i, q in enumerate(qs):
        q["num"] = num_start + i
        q["difficulty"] = level
    return qs

def translate_block(client, questions, lang_name):
    prompt = f"""Translate these CFE exam questions from English to {lang_name}.

STRICT RULES:
1. Translate ONLY: text, options, justification_correct, justification_wrong
2. DO NOT modify: num, tag, correct, difficulty
3. Keep prefixes exactly: "A. ", "B. ", "C. ", "D. "
4. Keep ALL legal terms in English:
   FCPA, SOX, RICO, BSA, SAR, CTR, SEC, ACFE, CFE,
   GAAP, IFRS, MLAT, FBAR, FATCA, FinCEN, FATF, DPA, NPA
5. Return ONLY valid JSON array, no markdown

Input:
{json.dumps(questions, ensure_ascii=False, indent=2)}"""

    result = call_api(client, prompt)
    for i, q in enumerate(result):
        if i < len(questions):
            q["num"]        = questions[i]["num"]
            q["tag"]        = questions[i]["tag"]
            q["correct"]    = questions[i]["correct"]
            q["difficulty"] = questions[i]["difficulty"]
    return result

def main():
    print("=" * 70)
    print("  NEXOR -- GERADOR QUIZ 2 S1D06 -- EN/PT/ES v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  5 Easy + 25 Standard + 20 Hard = 50q")
    print("=" * 70)

    client = anthropic.Anthropic()
    used_tags = get_existing_tags()
    print(f"\n  Tags do Quiz 1 carregadas: {len(used_tags)}")

    all_en = []

    # Blocos: 5 Easy (1 bloco de 5 + 1 de 5 standard para completar)
    # Simplificado: 1 bloco Easy(10) + 2 blocos Standard(10) + 1 bloco Standard(5)+Hard(5) + 2 blocos Hard(10)
    # Ajustado para blocos de 10:
    blocks = [
        ("EASY",     1,  "Q01-Q10", 10),
        ("STANDARD", 11, "Q11-Q20", 10),
        ("STANDARD", 21, "Q21-Q30", 10),
        ("HARD",     31, "Q31-Q40", 10),
        ("HARD",     41, "Q41-Q50", 10),
    ]

    print(f"\n  GERANDO EN:")
    for level, num_start, label, size in blocks:
        print(f"  Bloco {label} · {level}... ", end="", flush=True)
        try:
            qs = generate_block(client, level, num_start, used_tags)
            all_en.extend(qs)
            for q in qs: used_tags.add(q.get("tag",""))
            print(f"OK ({len(qs)}q)")
        except Exception as e:
            print(f"ERRO: {e}")
            return

    if len(all_en) < 45:
        print(f"  INSUFICIENTE: {len(all_en)}q")
        return

    for i, q in enumerate(all_en): q["num"] = i + 1

    # Salva EN
    en_path = Path(QUIZZES_DIR) / "corruption_bribery" / "quiz_002_en.json"
    save_json(str(en_path), {
        "cert_id": "cfe", "domain_id": "corruption_bribery",
        "domain_code": "S1D06", "quiz_num": 2,
        "domain_name": DOMAIN["domain_name"],
        "cert_name": "Certified Fraud Examiner",
        "lang": "en", "questions": all_en
    })
    print(f"  EN: {len(all_en)}q salvo ✅")

    # Traduz PT e ES
    for lang_code, lang_name in [("pt","Portugues (Brasil)"), ("es","Espanol neutro latinoamericano")]:
        print(f"\n  Traduzindo {lang_code.upper()}...")
        translated = []
        for i in range(0, len(all_en), 10):
            bloco = all_en[i:i+10]
            start = i+1; end = min(i+10, len(all_en))
            print(f"  Q{start}-Q{end}... ", end="", flush=True)
            try:
                t = translate_block(client, bloco, lang_name)
                translated.extend(t)
                print(f"OK")
            except Exception as e:
                print(f"ERRO: {e}")
                translated.extend(bloco)

        for i, q in enumerate(translated): q["num"] = i + 1

        lang_path = Path(QUIZZES_DIR) / "corruption_bribery" / f"quiz_002_{lang_code}.json"
        save_json(str(lang_path), {
            "cert_id": "cfe", "domain_id": "corruption_bribery",
            "domain_code": "S1D06", "quiz_num": 2,
            "domain_name": DOMAIN["domain_name"],
            "cert_name": "Certified Fraud Examiner",
            "lang": lang_code, "questions": translated
        })
        print(f"  {lang_code.upper()}: {len(translated)}q salvo ✅")

    print("\n" + "=" * 70)
    print("  CONCLUIDO — Quiz 2 S1D06 trilíngue pronto")
    print("  EN + PT + ES · 50q cada")
    print("  Rode: python verificar_duplicatas.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
