"""
gerar_flashcards_fractal.py — NEXOR FractalFlashcard Generator
Gera 48 flashcards por domínio (4 camadas × 12 cards) em PT/EN/ES.
Faz merge inteligente: preserva cards bons do banco anterior.

Uso:
    python gerar_flashcards_fractal.py                    # todos os 44 domínios
    python gerar_flashcards_fractal.py --domain accounting_concepts
    python gerar_flashcards_fractal.py --lang pt          # só português
    python gerar_flashcards_fractal.py --dry-run          # simula sem salvar

ATENÇÃO: Faz backup automático antes de sobrescrever qualquer arquivo.
"""

import json
import os
import re
import time
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
import anthropic

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(r"C:\ARAGORN\aragorn_quiz\static\flashcards\cfe")
BACKUP_DIR  = Path(r"C:\ARAGORN\aragorn_quiz\backup_flashcards_pre_fractal") / datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE    = Path(r"C:\ARAGORN\aragorn_quiz\fractal_flashcard_log.txt")

LANGS           = ["pt", "en", "es"]
CARDS_PER_LANG  = 48
CARDS_PER_LAYER = 12  # 4 camadas × 12 = 48
MODEL           = "claude-haiku-4-5-20251001"
MAX_TOKENS      = 8000
DELAY_BETWEEN   = 3   # segundos entre chamadas API

# Domínios que precisam regeneração (output da auditoria)
DOMAINS_TO_REGEN = [
    "accounting_concepts", "auditor_responsibilities", "bankruptcy_fraud",
    "cash_receipts_fraud", "collecting_evidence", "consumer_fraud",
    "corporate_governance", "covert_operations", "criminal_behavior",
    "criminal_prosecutions", "data_analysis_tools", "data_theft_ip",
    "emerging_fraud", "ethics_fraud_examiners", "evidence_principles",
    "expert_witness", "financial_institution_fraud", "financial_statement_fraud",
    "fraud_prevention_programs", "fraud_risk_assessment", "fraud_risk_management",
    "fraudulent_disbursements", "government_fraud", "healthcare_fraud",
    "identity_theft_cyberfraud", "individual_rights", "insurance_fraud",
    "international_fraud", "interview_techniques", "inventory_fraud",
    "investigation_planning", "law_cfe", "legal_issues_investigations",
    "legal_system_overview", "non_criminal_actions", "occupational_fraud",
    "payment_fraud", "prevention_deterrence", "procurement_contract_fraud",
    "report_writing", "securities_fraud", "sources_information",
    "tax_fraud", "tracing_assets",
]

LANG_NAMES = {"pt": "português", "en": "English", "es": "español"}

# ── FRACTAL LAYERS ────────────────────────────────────────────────────────────
LAYERS = {
    "F1": {
        "name": "Definição",
        "instruction": (
            "F1 — DEFINIÇÃO: Perguntas que testam conceitos puros, definições, "
            "terminologia e o significado exato de termos-chave do domínio. "
            "Formato: 'O que é X?', 'Como se define Y?', 'Qual o significado de Z?'"
        )
    },
    "F2": {
        "name": "Distinção",
        "instruction": (
            "F2 — DISTINÇÃO: Perguntas que comparam dois conceitos, diferenciam "
            "termos similares ou identificam qual conceito se aplica em dado contexto. "
            "Formato: 'Qual a diferença entre A e B?', 'Como distinguir X de Y?'"
        )
    },
    "F3": {
        "name": "Aplicação",
        "instruction": (
            "F3 — APLICAÇÃO: Perguntas práticas sobre como detectar, prevenir, "
            "investigar ou aplicar um conceito em situação real. "
            "Formato: 'Como detectar X?', 'Quais os red flags de Y?', 'Como se aplica Z?'"
        )
    },
    "F4": {
        "name": "Síntese",
        "instruction": (
            "F4 — SÍNTESE: Perguntas que integram múltiplos conceitos, exigem "
            "raciocínio sobre princípios subjacentes ou conexões entre temas. "
            "Formato: 'Por que X é importante para Y?', 'Como X e Y se relacionam?', "
            "'Qual o impacto de X sobre Z?'"
        )
    },
}

# ── HELPERS ──────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower().strip())

def md5(text: str) -> str:
    return hashlib.md5(normalize(text).encode()).hexdigest()

def load_json(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_file(path: Path):
    if path.exists():
        rel = path.relative_to(BASE_DIR)
        dest = BACKUP_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

def get_good_cards(path: Path, lang: str) -> list:
    """Retorna cards sem duplicata do arquivo existente."""
    data = load_json(path)
    if not data:
        return []
    cards = data.get("cards", data) if isinstance(data, dict) else data
    if not isinstance(cards, list):
        return []

    seen_hashes = set()
    good = []
    for card in cards:
        front_val = card.get("front", {})
        front = front_val.get(lang, "") if isinstance(front_val, dict) else str(front_val)
        front = front.strip()
        if not front:
            continue
        h = md5(front)
        if h not in seen_hashes:
            seen_hashes.add(h)
            good.append(card)
    return good

def get_domain_meta(domain_dir: Path, lang: str) -> dict:
    """Lê metadados do arquivo existente."""
    for l in [lang, "pt", "en", "es"]:
        path = domain_dir / f"flashcards_{l}.json"
        data = load_json(path)
        if data and isinstance(data, dict):
            return {
                "cert_id":     data.get("cert_id", "cfe"),
                "domain_id":   data.get("domain_id", domain_dir.name),
                "domain_code": data.get("domain_code", ""),
                "domain_name": data.get("domain_name", domain_dir.name),
            }
    return {
        "cert_id":     "cfe",
        "domain_id":   domain_dir.name,
        "domain_code": "",
        "domain_name": domain_dir.name,
    }

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ── PROMPT ────────────────────────────────────────────────────────────────────

def build_prompt(domain_name: str, lang: str, layer_key: str, existing_fronts: list) -> str:
    layer = LAYERS[layer_key]
    existing_block = ""
    if existing_fronts:
        sample = existing_fronts[:20]
        existing_block = (
            "\n\nFRONTS JÁ EXISTENTES (NÃO REPITA estes temas nem perguntas similares):\n"
            + "\n".join(f"- {f}" for f in sample)
        )

    lang_instruction = {
        "pt": "Responda APENAS em português do Brasil.",
        "en": "Respond ONLY in English.",
        "es": "Responda ÚNICAMENTE en español.",
    }[lang]

    return f"""Você é um especialista em certificação CFE (Certified Fraud Examiner) da ACFE.

Gere exatamente 12 flashcards para o domínio: "{domain_name}"
Camada: {layer['name']} — {layer['instruction']}

{lang_instruction}

REGRAS OBRIGATÓRIAS:
1. Exatamente 12 cards, nem mais nem menos
2. Cada card deve ter um "front" (pergunta) e um "back" (resposta completa)
3. O "front" deve ser uma pergunta clara e específica
4. O "back" deve ter 2-4 frases: definição/resposta + contexto + exemplo prático quando relevante
5. ZERO repetição entre os 12 cards desta camada
6. Cada card deve cobrir um aspecto DIFERENTE do domínio
7. Nível de dificuldade compatível com o exame CFE{existing_block}

Responda SOMENTE com JSON válido, sem texto antes ou depois, sem markdown:
{{
  "cards": [
    {{
      "topic": "snake_case_topic_identifier",
      "front": "pergunta clara e específica?",
      "back": "resposta completa com contexto e exemplo quando relevante."
    }}
  ]
}}"""

# ── GERAÇÃO VIA API ───────────────────────────────────────────────────────────

def generate_layer(client, domain_name: str, lang: str, layer_key: str,
                   existing_fronts: list, retries: int = 3) -> list:
    prompt = build_prompt(domain_name, lang, layer_key, existing_fronts)

    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            # Remove markdown se presente
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            cards = data.get("cards", [])
            if len(cards) >= 10:  # tolerância mínima
                return cards[:12]
            log(f"    ⚠  {layer_key} retornou {len(cards)} cards — tentativa {attempt+1}")
        except json.JSONDecodeError as e:
            log(f"    ✗  JSON inválido {layer_key} tentativa {attempt+1}: {e}")
        except Exception as e:
            log(f"    ✗  Erro API {layer_key} tentativa {attempt+1}: {e}")
        time.sleep(2)

    return []

# ── GERAÇÃO POR DOMÍNIO/IDIOMA ────────────────────────────────────────────────

def generate_domain_lang(client, domain_dir: Path, lang: str,
                         dry_run: bool = False) -> bool:
    meta = get_domain_meta(domain_dir, lang)
    domain_name = meta["domain_name"]
    out_path = domain_dir / f"flashcards_{lang}.json"

    # Backup
    if not dry_run:
        backup_file(out_path)

    # Cards bons existentes (para evitar repetição no prompt)
    good_existing = get_good_cards(out_path, lang)
    existing_fronts = []
    for c in good_existing:
        fv = c.get("front", {})
        ft = fv.get(lang, "") if isinstance(fv, dict) else str(fv)
        if ft.strip():
            existing_fronts.append(ft.strip())

    log(f"  [{lang.upper()}] {domain_name} — {len(good_existing)} cards bons existentes")

    all_new_cards = []
    card_id = 1

    for layer_key in ["F1", "F2", "F3", "F4"]:
        log(f"    → Camada {layer_key} ({LAYERS[layer_key]['name']})...")
        if not dry_run:
            layer_cards = generate_layer(client, domain_name, lang, layer_key, existing_fronts)
        else:
            layer_cards = [{"topic": f"dry_run_{layer_key}_{i}", "front": f"Q{i}?", "back": f"R{i}."} for i in range(1, 13)]

        # Dedup interno da camada
        seen = set()
        clean = []
        for c in layer_cards:
            h = md5(c.get("front", ""))
            if h not in seen and c.get("front"):
                seen.add(h)
                clean.append(c)

        for c in clean:
            all_new_cards.append({
                "id":    card_id,
                "layer": layer_key,
                "topic": c.get("topic", f"{layer_key.lower()}_{card_id}"),
                "front": {lang: c.get("front", "")},
                "back":  {lang: c.get("back", "")},
            })
            # Adiciona ao contexto para próximas camadas
            existing_fronts.append(c.get("front", ""))
            card_id += 1

        log(f"    ✓  {layer_key}: {len(clean)} cards gerados")
        if not dry_run:
            time.sleep(DELAY_BETWEEN)

    if len(all_new_cards) < 40:
        log(f"  ⚠  Apenas {len(all_new_cards)} cards gerados para {domain_dir.name}/{lang} — pulando")
        return False

    output = {
        **meta,
        "lang":   lang,
        "total":  len(all_new_cards),
        "schema": "FractalFlashcard-v1",
        "layers": {"F1": "Definição", "F2": "Distinção", "F3": "Aplicação", "F4": "Síntese"},
        "cards":  all_new_cards,
    }

    if not dry_run:
        save_json(out_path, output)
        log(f"  ✅ Salvo: {out_path} ({len(all_new_cards)} cards)")
    else:
        log(f"  [DRY-RUN] Geraria {len(all_new_cards)} cards → {out_path}")

    return True

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain",  default=None, help="Domínio específico")
    parser.add_argument("--lang",    default=None, help="Idioma: pt/en/es")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem chamar API nem salvar")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    target_langs   = [args.lang] if args.lang else LANGS
    target_domains = [args.domain] if args.domain else DOMAINS_TO_REGEN

    log("=" * 72)
    log("NEXOR · FractalFlashcard Generator · CFE 2026")
    log(f"Domínios: {len(target_domains)} · Idiomas: {target_langs} · Dry-run: {args.dry_run}")
    log(f"Backup em: {BACKUP_DIR}")
    log("=" * 72)

    if not args.dry_run:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    total_domains = len(target_domains)
    ok_count  = 0
    err_count = 0

    for i, domain_name in enumerate(target_domains, 1):
        domain_dir = BASE_DIR / domain_name
        if not domain_dir.exists():
            log(f"[{i:02d}/{total_domains}] ⚠  Diretório não encontrado: {domain_name}")
            continue

        log(f"\n[{i:02d}/{total_domains}] DOMÍNIO: {domain_name}")

        for lang in target_langs:
            try:
                ok = generate_domain_lang(client, domain_dir, lang, dry_run=args.dry_run)
                if ok:
                    ok_count += 1
                else:
                    err_count += 1
            except Exception as e:
                log(f"  ✗  ERRO {lang}: {e}")
                err_count += 1

    log("\n" + "=" * 72)
    log(f"CONCLUÍDO — OK: {ok_count} · Erros: {err_count}")
    log(f"Log salvo em: {LOG_FILE}")
    log("=" * 72)

if __name__ == "__main__":
    main()
