"""
gerar_quiz002_cfe.py — NEXOR FractalQuiz Generator
Gera quiz_002 para os 10 domínios CFE prioritários.
4 camadas × ~12 questões = 50 questões por domínio.
PT/EN/ES. Sem duplicar conteúdo do quiz_001.

Camadas FractalQuiz:
  F1 — Definição/Conceito (questões sobre o que é)
  F2 — Distinção/Comparação (A vs B, diferenças)
  F3 — Aplicação/Detecção (como identificar, red flags)
  F4 — Síntese/Análise (cenários complexos, julgamento)

Uso:
    python gerar_quiz002_cfe.py
    python gerar_quiz002_cfe.py --domain financial_statement_fraud
    python gerar_quiz002_cfe.py --dry-run
"""

import json
import os
import re
import time
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
import anthropic

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(r"C:\ARAGORN\aragorn_quiz\static\quizzes\cfe")
LOG_FILE   = Path(r"C:\ARAGORN\aragorn_quiz\fractal_quiz002_log.txt")
MODEL      = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8000
DELAY      = 4
LANGS      = ["pt", "en", "es"]
QUESTIONS_PER_LAYER = 12  # 4 × 12 = 48 + 2 = 50

# ── 10 DOMÍNIOS PRIORITÁRIOS ──────────────────────────────────────────────────
DOMAINS = [
    {"key": "financial_statement_fraud",  "code": "S1D02", "name": "Financial Statement Fraud"},
    {"key": "occupational_fraud",         "code": "S1D??", "name": "Occupational Fraud & Abuse"},
    {"key": "fraud_risk_assessment",      "code": "S3D??", "name": "Fraud Risk Assessment"},
    {"key": "fraudulent_disbursements",   "code": "S1D04", "name": "Asset Misappropriation — Disbursements"},
    {"key": "accounting_concepts",        "code": "S1D01", "name": "Accounting Concepts & Financial Analysis"},
    {"key": "interview_techniques",       "code": "S2D??", "name": "Interview Techniques"},
    {"key": "collecting_evidence",        "code": "S2D09", "name": "Collecting Evidence"},
    {"key": "tracing_assets",             "code": "S2D12", "name": "Tracing Illicit Transactions & Assets"},
    {"key": "fraud_prevention_programs",  "code": "S3D??", "name": "Fraud Prevention Programs"},
    {"key": "corporate_governance",       "code": "S3D??", "name": "Corporate Governance & Ethics"},
]

LAYERS = {
    "F1": {
        "name": "Definição",
        "en": "F1 — DEFINITION/CONCEPT: Questions testing precise knowledge of definitions, terminology, standards, and key concepts. Format: 'What is X?', 'Which of the following best defines Y?', 'According to the ACFE, Z is defined as...'",
        "pt": "F1 — DEFINIÇÃO/CONCEITO: Questões que testam conhecimento preciso de definições, terminologia, normas e conceitos-chave. Formato: 'O que é X?', 'Qual das alternativas melhor define Y?', 'De acordo com a ACFE, Z é definido como...'",
        "es": "F1 — DEFINICIÓN/CONCEPTO: Preguntas que prueban conocimiento preciso de definiciones, terminología, normas y conceptos clave. Formato: '¿Qué es X?', '¿Cuál de las siguientes opciones define mejor Y?'"
    },
    "F2": {
        "name": "Distinção",
        "en": "F2 — DISTINCTION/COMPARISON: Questions comparing two concepts, differentiating similar schemes, or identifying which concept applies in a given context. Format: 'What is the difference between A and B?', 'Which best distinguishes X from Y?'",
        "pt": "F2 — DISTINÇÃO/COMPARAÇÃO: Questões que comparam dois conceitos, diferenciam esquemas similares ou identificam qual conceito se aplica. Formato: 'Qual a diferença entre A e B?', 'O que melhor distingue X de Y?'",
        "es": "F2 — DISTINCIÓN/COMPARACIÓN: Preguntas que comparan dos conceptos, diferencian esquemas similares o identifican cuál concepto aplica. Formato: '¿Cuál es la diferencia entre A y B?'"
    },
    "F3": {
        "name": "Aplicação",
        "en": "F3 — APPLICATION/DETECTION: Practical questions about how to identify, detect, investigate, or prevent fraud. Scenario-based. Format: 'Which of the following is a red flag for X?', 'An examiner notices Y — what should they do?', 'Which control would best prevent Z?'",
        "pt": "F3 — APLICAÇÃO/DETECÇÃO: Questões práticas sobre como identificar, detectar, investigar ou prevenir fraude. Baseadas em cenários. Formato: 'Qual dos itens é um red flag de X?', 'Um examinador percebe Y — o que deve fazer?'",
        "es": "F3 — APLICACIÓN/DETECCIÓN: Preguntas prácticas sobre cómo identificar, detectar, investigar o prevenir fraude. Basadas en escenarios. Formato: '¿Cuál de los siguientes es una señal de alerta de X?'"
    },
    "F4": {
        "name": "Síntese",
        "en": "F4 — SYNTHESIS/ANALYSIS: Complex scenario questions requiring judgment, integration of multiple concepts, or evaluation of competing approaches. Format: 'In the following scenario, which conclusion is most supported?', 'Which combination of factors best explains...?'",
        "pt": "F4 — SÍNTESE/ANÁLISE: Questões complexas com cenários que exigem julgamento, integração de múltiplos conceitos ou avaliação de abordagens. Formato: 'No cenário apresentado, qual conclusão é mais fundamentada?'",
        "es": "F4 — SÍNTESIS/ANÁLISIS: Preguntas complejas con escenarios que requieren juicio, integración de múltiples conceptos. Formato: 'En el escenario presentado, ¿qué conclusión está mejor fundamentada?'"
    }
}

LANG_NAMES = {"pt": "português do Brasil", "en": "English", "es": "español"}

# ── HELPERS ──────────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def md5(text):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()

def load_quiz001_questions(domain_key, lang):
    """Carrega textos do quiz_001 para evitar duplicação."""
    path = BASE_DIR / domain_key / f"quiz_001_{lang}.json"
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return [q.get("text", "") for q in data.get("questions", [])]
    except Exception:
        return []

def get_domain_meta(domain_key):
    """Lê metadados do quiz_001 existente."""
    for lang in ["en", "pt", "es"]:
        path = BASE_DIR / domain_key / f"quiz_001_{lang}.json"
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                return {
                    "cert_id":     data.get("cert_id", "cfe"),
                    "domain_name": data.get("domain_name", domain_key),
                    "cert_name":   data.get("cert_name", "Certified Fraud Examiner"),
                }
            except Exception:
                pass
    return {
        "cert_id":     "cfe",
        "domain_name": domain_key,
        "cert_name":   "Certified Fraud Examiner",
    }

# ── PROMPT ────────────────────────────────────────────────────────────────────

def build_prompt(domain_name, lang, layer_key, existing_texts):
    layer = LAYERS[layer_key]
    lang_instruction = {
        "pt": "Responda APENAS em português do Brasil.",
        "en": "Respond ONLY in English.",
        "es": "Responda ÚNICAMENTE en español.",
    }[lang]
    layer_instruction = layer[lang]

    existing_block = ""
    if existing_texts:
        sample = existing_texts[:15]
        existing_block = (
            "\n\nQUESTÕES JÁ EXISTENTES (NÃO repita estes temas nem perguntas similares):\n"
            + "\n".join(f"- {t[:100]}" for t in sample if t)
        )

    return f"""Você é um especialista sênior em certificação CFE (Certified Fraud Examiner) da ACFE, nível avançado.

Domínio: "{domain_name}"
Camada: {layer_instruction}

{lang_instruction}

Gere exatamente 13 questões de múltipla escolha para o exame CFE.

REGRAS OBRIGATÓRIAS:
1. Exatamente 13 questões, cada uma com 4 alternativas (A, B, C, D)
2. Apenas UMA alternativa correta por questão
3. As alternativas incorretas devem ser plausíveis (não obviamente erradas)
4. Nível de dificuldade: intermediário-avançado (exame CFE real)
5. ZERO repetição entre as 13 questões desta camada
6. Cada questão deve cobrir um aspecto DIFERENTE do domínio
7. Inclua uma tag descritiva do subtópico para cada questão{existing_block}

Responda SOMENTE com JSON válido, sem texto antes ou depois, sem markdown:
{{
  "questions": [
    {{
      "text": "enunciado claro e específico da questão?",
      "options": ["A. opção A", "B. opção B", "C. opção C", "D. opção D"],
      "correct": 0,
      "tag": "subtopic — specific aspect"
    }}
  ]
}}

O campo "correct" é o índice (0-3) da opção correta."""

# ── GERAÇÃO VIA API ───────────────────────────────────────────────────────────

def generate_layer(client, domain_name, lang, layer_key, existing_texts, retries=3):
    prompt = build_prompt(domain_name, lang, layer_key, existing_texts)
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            questions = data.get("questions", [])
            if len(questions) >= 10:
                return questions[:13]
            log(f"    ⚠  {layer_key} retornou {len(questions)} questões — tentativa {attempt+1}")
        except json.JSONDecodeError as e:
            log(f"    ✗  JSON inválido {layer_key} tentativa {attempt+1}: {e}")
        except Exception as e:
            log(f"    ✗  Erro API {layer_key} tentativa {attempt+1}: {e}")
        time.sleep(3)
    return []

# ── GERAÇÃO POR DOMÍNIO/IDIOMA ────────────────────────────────────────────────

def generate_domain_lang(client, domain, lang, dry_run=False):
    domain_key  = domain["key"]
    domain_name = domain["name"]
    out_path    = BASE_DIR / domain_key / f"quiz_002_{lang}.json"

    if out_path.exists():
        log(f"  [{lang.upper()}] quiz_002 já existe — pulando")
        return True

    # Carrega quiz_001 para evitar duplicação
    existing = load_quiz001_questions(domain_key, lang)
    log(f"  [{lang.upper()}] {domain_name} — {len(existing)} questões do quiz_001 carregadas")

    meta = get_domain_meta(domain_key)
    all_questions = []
    q_num = 1
    all_texts = list(existing)  # acumula para evitar duplicação entre camadas

    for layer_key in ["F1", "F2", "F3", "F4"]:
        log(f"    → Camada {layer_key} ({LAYERS[layer_key]['name']})...")
        if dry_run:
            layer_qs = [{"text": f"DRY {layer_key} Q{i}", "options": ["A","B","C","D"], "correct": 0, "tag": "dry"} for i in range(1, 14)]
        else:
            layer_qs = generate_layer(client, domain_name, lang, layer_key, all_texts)

        # Dedup interno
        seen = set()
        clean = []
        for q in layer_qs:
            h = md5(q.get("text", ""))
            if h not in seen and q.get("text"):
                seen.add(h)
                clean.append(q)

        for q in clean:
            all_questions.append({
                "num":     q_num,
                "text":    q.get("text", ""),
                "options": q.get("options", []),
                "correct": q.get("correct", 0),
                "tag":     q.get("tag", f"{layer_key} — {LAYERS[layer_key]['name']}"),
                "layer":   layer_key,
            })
            all_texts.append(q.get("text", ""))
            q_num += 1

        log(f"    ✓  {layer_key}: {len(clean)} questões")
        if not dry_run:
            time.sleep(DELAY)

    if len(all_questions) < 40:
        log(f"  ⚠  Apenas {len(all_questions)} questões — pulando {domain_key}/{lang}")
        return False

    output = {
        "cert_id":     meta["cert_id"],
        "domain_id":   domain_key,
        "quiz_num":    2,
        "domain_name": meta["domain_name"],
        "cert_name":   meta["cert_name"],
        "lang":        lang,
        "source":      "fractal_quiz_v1",
        "schema":      "FractalQuiz-v1",
        "layers":      {"F1": "Definição", "F2": "Distinção", "F3": "Aplicação", "F4": "Síntese"},
        "total":       len(all_questions),
        "questions":   all_questions,
    }

    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        log(f"  ✅ Salvo: {out_path} ({len(all_questions)} questões)")
    else:
        log(f"  [DRY-RUN] Geraria {len(all_questions)} questões → {out_path}")

    return True

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain",  default=None)
    parser.add_argument("--lang",    default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    target_domains = [d for d in DOMAINS if d["key"] == args.domain] if args.domain else DOMAINS
    target_langs   = [args.lang] if args.lang else LANGS

    log("=" * 68)
    log("NEXOR · FractalQuiz Generator · quiz_002 · CFE 2026")
    log(f"Domínios: {len(target_domains)} · Idiomas: {target_langs} · Dry-run: {args.dry_run}")
    log("=" * 68)

    ok = err = 0
    for i, domain in enumerate(target_domains, 1):
        log(f"\n[{i:02d}/{len(target_domains)}] {domain['key']}")
        for lang in target_langs:
            try:
                result = generate_domain_lang(client, domain, lang, dry_run=args.dry_run)
                if result:
                    ok += 1
                else:
                    err += 1
            except Exception as e:
                log(f"  ✗ ERRO {lang}: {e}")
                err += 1

    log("\n" + "=" * 68)
    log(f"CONCLUÍDO — OK: {ok} · Erros: {err}")
    log(f"Log: {LOG_FILE}")
    log("=" * 68)

if __name__ == "__main__":
    main()
