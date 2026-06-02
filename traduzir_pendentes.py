#!/usr/bin/env python3
"""
NEXOR - TRADUTOR ESPECIFICO
Traduz os 12 quizzes que falharam, com batches de 5.
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import os, json, re, time
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
QUIZ_DIR = Path("static/quizzes")
BATCH_SIZE = 5

ALVOS = [
    "cfe/financial_transactions/quiz_002_pt.json",
    "cfe/financial_transactions/quiz_003_pt.json",
    "cfe/financial_transactions/quiz_004_pt.json",
    "cfe/financial_transactions/quiz_005_pt.json",
    "cfe/financial_transactions/quiz_006_pt.json",
    "cfe/fraud_investigation/quiz_003_pt.json",
    "cfe/fraud_investigation/quiz_004_pt.json",
    "cfe/law_cfe/quiz_002_pt.json",
    "cfe/prevention_deterrence/quiz_002_pt.json",
    "cism/info_security_governance/quiz_002_pt.json",
    "iso27001_li/fundamentals_isms/quiz_004_pt.json",
    "iso27001_li/planning_implementation/quiz_004_pt.json",
]

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
    lang_label = "American English" if lang == "en" else "Latin American Spanish"
    lang_instr = "ALL in fluent technical English" if lang == "en" else "TODO en español técnico"

    q_min = []
    for q in questions:
        q_min.append({
            "num": q.get("num"),
            "text": q.get("text","")[:400],
            "tag": q.get("tag",""),
            "options": [o[:150] for o in q.get("options",[])],
            "correct": q.get("correct",0),
            "justification_correct": q.get("justification_correct","")[:200],
            "justification_wrong": q.get("justification_wrong","")[:150]
        })

    prompt = f"""Translate {len(questions)} exam questions for {cert_name} from Portuguese to {lang_label}.
{lang_instr}. Keep correct index unchanged. Keep question numbers. Translate tags and options (keep A. B. C. D. prefix).
Return ONLY JSON: {{"questions":[...]}}

{json.dumps(q_min, ensure_ascii=False)}"""

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2500,
            messages=[{"role":"user","content":prompt}]
        )
        raw = "".join(b.text for b in msg.content if hasattr(b,"text"))
        return extract_questions(raw)
    except Exception as e:
        print(f"ERRO: {e}")
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
        bn = i//BATCH_SIZE + 1
        print(f"    B{bn}/{n_batches}...", end=" ", flush=True)

        result = traduz_batch(batch, lang, cert_name, domain_name)

        if result and len(result) >= len(batch) - 1:
            todas.extend(result[:len(batch)])
            print("OK")
        else:
            time.sleep(3)
            print("retry...", end=" ", flush=True)
            result = traduz_batch(batch, lang, cert_name, domain_name)
            if result and len(result) > 0:
                todas.extend(result[:len(batch)])
                print(f"OK({len(result)})")
            else:
                print("FALHOU")
                return "erro"
        time.sleep(1)

    # Garante numeracao correta
    for i, q in enumerate(todas):
        if "num" not in q or not q["num"]:
            q["num"] = questions[i].get("num", i+1) if i < len(questions) else i+1

    data_out = dict(data)
    data_out["lang"] = lang
    data_out["questions"] = todas
    path_out.write_text(json.dumps(data_out, ensure_ascii=False, indent=2), encoding="utf-8")
    return "ok"

# ── EXECUTA ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("  TRADUTOR ESPECIFICO — 12 quizzes pendentes")
print("=" * 60)

ok_en = ok_es = erro_en = erro_es = 0

for alvo in ALVOS:
    path_pt = QUIZ_DIR / alvo
    if not path_pt.exists():
        print(f"\nNAO ENCONTRADO: {alvo}")
        continue

    data = json.loads(path_pt.read_text(encoding="utf-8"))
    label = f"{data.get('cert_id','?')}/{data.get('domain_id','?')}/quiz_{data.get('quiz_num','?'):03d}"
    print(f"\n📁 {label}")

    for lang in ["en","es"]:
        path_out = Path(str(path_pt).replace("_pt.json",f"_{lang}.json"))
        if path_out.exists():
            print(f"  [{lang.upper()}] Ja existe")
            continue
        print(f"  [{lang.upper()}] Traduzindo (batches de {BATCH_SIZE})...")
        r = traduz_quiz(path_pt, lang)
        if r == "ok":
            if lang=="en": ok_en+=1
            else: ok_es+=1
            print(f"  [{lang.upper()}] Salvo")
        else:
            if lang=="en": erro_en+=1
            else: erro_es+=1
            print(f"  [{lang.upper()}] Erro: {r}")
        time.sleep(0.5)

print(f"\n{'='*60}")
print(f"  CONCLUIDO!")
print(f"  EN — OK:{ok_en} Erro:{erro_en}")
print(f"  ES — OK:{ok_es} Erro:{erro_es}")
print(f"{'='*60}")
