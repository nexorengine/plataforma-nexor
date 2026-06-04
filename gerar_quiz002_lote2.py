"""
gerar_quiz002_lote2.py — NEXOR FractalQuiz · Lote 2 (13 domínios)

Uso:
    python gerar_quiz002_lote2.py
    python gerar_quiz002_lote2.py --dry-run
"""

import json, re, time, hashlib, argparse
from pathlib import Path
from datetime import datetime
import anthropic

BASE_DIR = Path(r"C:\ARAGORN\aragorn_quiz\static\quizzes\cfe")
LOG_FILE = Path(r"C:\ARAGORN\aragorn_quiz\quiz002_lote2_log.txt")
MODEL    = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8000
DELAY    = 4
LANGS    = ["pt", "en", "es"]

DOMAINS = [
    {"key": "inventory_fraud",          "name": "Asset Misappropriation — Inventory & Other Assets"},
    {"key": "international_fraud",      "name": "International & Cross-Border Fraud"},
    {"key": "financial_institution_fraud", "name": "Financial Institution Fraud & Money Laundering"},
    {"key": "tax_fraud",                "name": "Tax Fraud"},
    {"key": "consumer_fraud",           "name": "Consumer Fraud & Scams"},
    {"key": "covert_operations",        "name": "Covert Operations in Fraud Investigations"},
    {"key": "sources_information",      "name": "Sources of Information"},
    {"key": "auditor_responsibilities", "name": "Auditor Responsibilities in Fraud Detection"},
    {"key": "fraud_risk_management",    "name": "Fraud Risk Management"},
    {"key": "cash_receipts_fraud",      "name": "Asset Misappropriation — Cash Receipts"},
    {"key": "bankruptcy_fraud",         "name": "Bankruptcy Fraud"},
    {"key": "criminal_behavior",        "name": "Understanding Criminal Behavior"},
    {"key": "emerging_fraud",           "name": "Emerging Fraud & Technology"},
]

LAYERS = {
    "F1": {
        "pt": "F1 — DEFINIÇÃO: Questões sobre definições precisas, terminologia e conceitos-chave do domínio.",
        "en": "F1 — DEFINITION: Questions testing precise definitions, terminology, and key concepts.",
        "es": "F1 — DEFINICIÓN: Preguntas sobre definiciones precisas, terminología y conceptos clave.",
    },
    "F2": {
        "pt": "F2 — DISTINÇÃO: Questões comparando dois conceitos, diferenciando esquemas similares.",
        "en": "F2 — DISTINCTION: Questions comparing concepts, differentiating similar schemes.",
        "es": "F2 — DISTINCIÓN: Preguntas comparando conceptos, diferenciando esquemas similares.",
    },
    "F3": {
        "pt": "F3 — APLICAÇÃO: Questões práticas sobre como identificar, detectar ou prevenir fraude. Baseadas em cenários reais.",
        "en": "F3 — APPLICATION: Practical questions about identifying, detecting, or preventing fraud. Scenario-based.",
        "es": "F3 — APLICACIÓN: Preguntas prácticas sobre identificar, detectar o prevenir fraude. Basadas en escenarios.",
    },
    "F4": {
        "pt": "F4 — SÍNTESE: Questões complexas com cenários que exigem julgamento e integração de múltiplos conceitos.",
        "en": "F4 — SYNTHESIS: Complex scenario questions requiring judgment and integration of multiple concepts.",
        "es": "F4 — SÍNTESIS: Preguntas complejas con escenarios que requieren juicio e integración de conceptos.",
    },
}

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def md5(text):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()

def load_existing(domain_key, lang):
    path = BASE_DIR / domain_key / f"quiz_001_{lang}.json"
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [q.get("text", "") for q in data.get("questions", [])]
    except Exception:
        return []

def get_meta(domain_key):
    for lang in ["en", "pt", "es"]:
        path = BASE_DIR / domain_key / f"quiz_001_{lang}.json"
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    d = json.load(f)
                return {"cert_id": d.get("cert_id","cfe"), "domain_name": d.get("domain_name", domain_key), "cert_name": d.get("cert_name","Certified Fraud Examiner")}
            except Exception:
                pass
    return {"cert_id": "cfe", "domain_name": domain_key, "cert_name": "Certified Fraud Examiner"}

def build_prompt(domain_name, lang, layer_key, existing):
    li = {"pt": "Responda APENAS em português do Brasil.", "en": "Respond ONLY in English.", "es": "Responda ÚNICAMENTE en español."}[lang]
    existing_block = ""
    if existing:
        existing_block = "\n\nNÃO repita estes temas (já cobertos no quiz anterior):\n" + "\n".join(f"- {t[:100]}" for t in existing[:15] if t)
    return f"""Especialista CFE (ACFE) nível avançado.

Domínio: "{domain_name}"
Camada: {LAYERS[layer_key][lang]}

{li}

Gere exatamente 13 questões de múltipla escolha CFE.

REGRAS:
1. Exatamente 13 questões com 4 alternativas (A, B, C, D)
2. Uma única alternativa correta
3. Alternativas incorretas plausíveis
4. Nível intermediário-avançado (exame CFE real)
5. Cada questão cobre aspecto DIFERENTE do domínio
6. Inclua tag do subtópico{existing_block}

Responda SOMENTE com JSON válido, sem markdown:
{{
  "questions": [
    {{
      "text": "enunciado da questão?",
      "options": ["A. opção", "B. opção", "C. opção", "D. opção"],
      "correct": 0,
      "tag": "subtopic"
    }}
  ]
}}"""

def generate_layer(client, domain_name, lang, layer_key, existing, retries=3):
    prompt = build_prompt(domain_name, lang, layer_key, existing)
    for attempt in range(retries):
        try:
            r = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, messages=[{"role":"user","content":prompt}])
            raw = re.sub(r"^```json\s*","",r.content[0].text.strip())
            raw = re.sub(r"\s*```$","",raw)
            data = json.loads(raw)
            qs = data.get("questions",[])
            if len(qs) >= 10:
                return qs[:13]
            log(f"    ⚠  {layer_key} retornou {len(qs)} — tentativa {attempt+1}")
        except Exception as e:
            log(f"    ✗  {layer_key} tentativa {attempt+1}: {e}")
        time.sleep(3)
    return []

def generate_domain_lang(client, domain, lang, dry_run=False):
    key  = domain["key"]
    name = domain["name"]
    out  = BASE_DIR / key / f"quiz_002_{lang}.json"

    if out.exists():
        log(f"  [{lang.upper()}] já existe — pulando")
        return True

    existing = load_existing(key, lang)
    log(f"  [{lang.upper()}] {name} — {len(existing)} questões quiz_001 carregadas")
    meta = get_meta(key)
    all_qs = []
    all_texts = list(existing)
    num = 1

    for lk in ["F1","F2","F3","F4"]:
        log(f"    → Camada {lk}...")
        if dry_run:
            layer_qs = [{"text":f"DRY {lk} Q{i}","options":["A","B","C","D"],"correct":0,"tag":"dry"} for i in range(13)]
        else:
            layer_qs = generate_layer(client, name, lang, lk, all_texts)

        seen = set()
        clean = []
        for q in layer_qs:
            h = md5(q.get("text",""))
            if h not in seen and q.get("text"):
                seen.add(h)
                clean.append(q)

        for q in clean:
            all_qs.append({"num":num,"text":q["text"],"options":q["options"],"correct":q["correct"],"tag":q.get("tag",lk),"layer":lk})
            all_texts.append(q["text"])
            num += 1

        log(f"    ✓  {lk}: {len(clean)} questões")
        if not dry_run:
            time.sleep(DELAY)

    if len(all_qs) < 40:
        log(f"  ⚠  Apenas {len(all_qs)} questões — pulando")
        return False

    output = {"cert_id":meta["cert_id"],"domain_id":key,"quiz_num":2,"domain_name":meta["domain_name"],"cert_name":meta["cert_name"],"lang":lang,"source":"fractal_quiz_v1","schema":"FractalQuiz-v1","layers":{"F1":"Definição","F2":"Distinção","F3":"Aplicação","F4":"Síntese"},"total":len(all_qs),"questions":all_qs}

    if not dry_run:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out,"w",encoding="utf-8") as f:
            json.dump(output,f,ensure_ascii=False,indent=2)
        log(f"  ✅ Salvo: {out} ({len(all_qs)} questões)")
    else:
        log(f"  [DRY] Geraria {len(all_qs)} questões → {out}")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    log("=" * 64)
    log(f"NEXOR · FractalQuiz · Lote 2 · 13 domínios · {'DRY-RUN' if args.dry_run else 'EXECUTANDO'}")
    log("=" * 64)

    ok = err = 0
    for i, domain in enumerate(DOMAINS, 1):
        log(f"\n[{i:02d}/13] {domain['key']}")
        for lang in LANGS:
            try:
                if generate_domain_lang(client, domain, lang, args.dry_run):
                    ok += 1
                else:
                    err += 1
            except Exception as e:
                log(f"  ✗ ERRO {lang}: {e}")
                err += 1

    log(f"\n{'='*64}")
    log(f"CONCLUÍDO — OK: {ok} · Erros: {err}")
    log("=" * 64)

if __name__ == "__main__":
    main()
