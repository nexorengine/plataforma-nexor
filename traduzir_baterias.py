#!/usr/bin/env python3
"""
NEXOR - TRADUTOR DE BATERIAS v2
Traduz quizzes PT para EN e ES em batches de 10.
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")
BATCH_SIZE = 10

def extract_questions(raw):
    txt = re.sub(r'```json\s*','',raw.strip())
    txt = re.sub(r'```\s*','',txt).strip()
    try:
        d = json.loads(txt)
        if "questions" in d: return d["questions"]
        if isinstance(d, list): return d
    except: pass
    match = re.search(r'\[.*\]', txt, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except: pass
    return None

def traduz_batch(questions, lang, cert_name, domain_name):
    if lang == "en":
        lang_label = "American English"
        lang_instr = "ALL text in fluent technical American English"
    else:
        lang_label = "Spanish"
        lang_instr = "TODO en español técnico latinoamericano fluido"

    q_min = []
    for q in questions:
        q_min.append({
            "num": q.get("num"),
            "text": q.get("text",""),
            "tag": q.get("tag",""),
            "options": q.get("options",[]),
            "correct": q.get("correct",0),
            "justification_correct": q.get("justification_correct","")[:300],
            "justification_wrong": q.get("justification_wrong","")[:200]
        })

    prompt = f"""Translate these {len(questions)} exam questions for {cert_name} ({domain_name}) from Brazilian Portuguese to {lang_label}.

Rules:
- {lang_instr}
- Keep technical terminology accurate for the certification
- Keep same correct answer index (do NOT change the "correct" field)
- Keep same question numbers
- Translate tag field too
- Translate options including letter prefix (A. B. C. D.)
- Return ONLY valid JSON, no markdown, no explanation

Input:
{json.dumps(q_min, ensure_ascii=False)}

Return format: {{"questions": [array of translated questions with same structure]}}"""

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[{"role":"user","content":prompt}]
        )
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        return extract_questions(raw)
    except Exception as e:
        print(f"ERRO API: {e}")
        return None

def traduz_quiz(path_pt, lang):
    path_out = Path(str(path_pt).replace("_pt.json", f"_{lang}.json"))
    if path_out.exists():
        return "ja_existe"

    data = json.loads(path_pt.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    cert_name = data.get("cert_name", "")
    domain_name = data.get("domain_name", "")
    if not questions: return "vazio"

    todas = []
    n_batches = (len(questions) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i:i+BATCH_SIZE]
        batch_num = i//BATCH_SIZE + 1
        print(f"    Batch {batch_num}/{n_batches}...", end=" ", flush=True)

        result = traduz_batch(batch, lang, cert_name, domain_name)

        if result and len(result) == len(batch):
            todas.extend(result)
            print("OK")
        else:
            time.sleep(2)
            print("retentando...", end=" ", flush=True)
            result = traduz_batch(batch, lang, cert_name, domain_name)
            if result and len(result) > 0:
                todas.extend(result)
                print(f"OK ({len(result)})")
            else:
                print("FALHOU")
                return "erro"
        time.sleep(0.5)

    data_out = dict(data)
    data_out["lang"] = lang
    data_out["questions"] = todas
    path_out.write_text(json.dumps(data_out, ensure_ascii=False, indent=2), encoding="utf-8")
    return "ok"

# ── EXECUTA ───────────────────────────────────────────────────────────────────
print("=" * 65)
print("  NEXOR — TRADUTOR v2 (batches de 10)")
print("=" * 65)

quizzes_pt = sorted(QUIZ_DIR.rglob("quiz_*_pt.json"))
print(f"  Quizzes PT: {len(quizzes_pt)}")

stats = {"en":{"ok":0,"ja":0,"erro":0}, "es":{"ok":0,"ja":0,"erro":0}}

for path_pt in quizzes_pt:
    data = json.loads(path_pt.read_text(encoding="utf-8"))
    cert = data.get("cert_id","?")
    domain = data.get("domain_id","?")
    qnum = data.get("quiz_num","?")
    label = f"{cert}/{domain}/quiz_{qnum:03d}"
    print(f"\n📁 {label}")

    for lang in ["en","es"]:
        path_out = Path(str(path_pt).replace("_pt.json",f"_{lang}.json"))
        if path_out.exists():
            print(f"  [{lang.upper()}] Ja existe")
            stats[lang]["ja"] += 1
            continue
        print(f"  [{lang.upper()}] Traduzindo...")
        r = traduz_quiz(path_pt, lang)
        if r == "ok":
            stats[lang]["ok"] += 1
            print(f"  [{lang.upper()}] Salvo")
        elif r == "ja_existe":
            stats[lang]["ja"] += 1
        else:
            stats[lang]["erro"] += 1
            print(f"  [{lang.upper()}] Erro")
        time.sleep(0.3)

print(f"\n{'='*65}")
print(f"  TRADUCAO CONCLUIDA!")
print(f"  EN — OK:{stats['en']['ok']} Ja:{stats['en']['ja']} Erro:{stats['en']['erro']}")
print(f"  ES — OK:{stats['es']['ok']} Ja:{stats['es']['ja']} Erro:{stats['es']['erro']}")
print(f"{'='*65}")
