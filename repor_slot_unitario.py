"""
NEXOR — REPOSITOR DE SLOT UNITÁRIO v1
Gera N questões para um arquivo específico, exibe para aprovação
e só injeta após confirmação. Registra tópicos usados para
evitar reincidência em injeções futuras.

USO:
    python repor_slot_unitario.py

O script pergunta interativamente:
    - cert_id / domain_id / quiz_num / lang
    - quantos slots repor
    - tópicos a cobrir (dirigido)
    - tópicos bloqueados (já saturados)

SAÍDA:
    - Arquivo JSON atualizado (com backup .bak)
    - topicos_usados_{cert_id}_{domain_id}.json  ← memória permanente
    - reposicao_log_YYYYMMDD_HHMM.txt
"""

import os
import json
import shutil
import anthropic
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────
QUIZZES_DIR = "static/quizzes"
MODEL       = "claude-sonnet-4-5"
MAX_TOKENS  = 8192
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M")
LOG_FILE    = f"reposicao_log_{TIMESTAMP}.txt"

# Tópicos bloqueados globais (saturados nas duplicatas detectadas)
TOPICOS_BLOQUEADOS_GLOBAIS = {
    "cfe/law_cfe": [
        "FCPA facilitating payments",
        "FCPA safe harbor payments",
        "FCPA payments NOT prohibited",
        "FCPA payments explicitly permitted",
        "FCPA anti-bribery exemptions",
    ],
    "iso27001_li/annex_a_controls": [
        "cláusula 4.1 contexto da organização",
        "primary purpose of establishing an ISMS",
        "propósito principal del contexto de la organización cláusula 4.1",
        "propósito principal de identificar partes interesadas SGSI",
    ],
    "iso27001_li/performance_improvement": [
        "cláusula 9.1 monitoramento e medição propósito principal",
        "cláusula 9.2 frequência mínima auditorias internas",
        "clause 9.1 primary objective monitoring measurement ISMS",
        "cláusula 9.2.1 frecuencia mínima obligatoria auditorías",
    ],
    "iso27001_li/risk_management_li": [
        "asset identification primary objective ISO 27005",
        "vulnerability analysis propósito principal identificar",
    ],
    "cdpse/privacy_governance_cdpse": [
        "GDPR Article 35 DPIA mandatory processing",
        "Data Protection Impact Assessment triggers GDPR Art 35",
    ],
    "iso22301_li/bcms_fundamentals": [
        "diferença fundamental BCP vs BCMS ISO 22301",
        "diferencia fundamental Plan Continuidad Negocio vs Sistema Gestión",
    ],
}

# Tópicos recomendados por domínio (evitar os bloqueados)
TOPICOS_RECOMENDADOS = {
    "cfe/law_cfe": [
        "SOX §302 CEO/CFO certification requirements",
        "SOX §404 internal controls over financial reporting",
        "SOX §906 criminal penalties for false certifications",
        "RICO statute elements and civil/criminal application",
        "Bank Secrecy Act / AML suspicious activity reports",
        "Dodd-Frank whistleblower protections and awards",
        "18 U.S.C. §1343 wire fraud elements",
        "18 U.S.C. §1956 money laundering",
        "Computer Fraud and Abuse Act (CFAA)",
        "FCPA accounting provisions (books and records)",
        "PCAOB inspection authority and auditor independence",
        "Honest Services Fraud 18 U.S.C. §1346",
    ],
    "iso27001_li/annex_a_controls": [
        "A.5.1 políticas de segurança da informação",
        "A.6.1 triagem de candidatos (pessoas)",
        "A.6.3 conscientização e treinamento em SI",
        "A.7.1 perímetros de segurança física",
        "A.7.4 monitoramento de segurança física",
        "A.8.2 direitos de acesso privilegiado",
        "A.8.7 proteção contra malware",
        "A.8.23 filtragem de web",
        "A.8.28 codificação segura (secure coding)",
        "A.5.23 segurança para uso de serviços em nuvem",
        "A.8.16 monitoramento de atividades",
        "A.5.30 preparação de TIC para continuidade de negócios",
    ],
    "iso27001_li/performance_improvement": [
        "cláusula 9.3 revisão pela direção — entradas obrigatórias",
        "cláusula 9.3 revisão pela direção — saídas esperadas",
        "cláusula 10.1 não conformidade e ação corretiva",
        "cláusula 10.2 melhoria contínua do SGSI",
        "critérios de seleção e competência de auditores internos",
        "KPIs e métricas de desempenho do SGSI",
        "programa de auditoria interna — planejamento e escopo",
        "evidências de conformidade — retenção de informação documentada",
    ],
    "iso27001_li/risk_management_li": [
        "ISO 27005:2022 risk treatment options — aceitar/mitigar/transferir/evitar",
        "critérios de aceitação de risco e apetite de risco",
        "plano de tratamento de risco (RTP) — conteúdo obrigatório",
        "risco residual — aprovação pela direção",
        "comunicação e consulta no processo de gestão de riscos",
        "monitoramento e revisão contínua dos riscos",
    ],
    "cdpse/privacy_governance_cdpse": [
        "GDPR Art.37 DPO designation mandatory criteria",
        "GDPR Art.44 international data transfers mechanisms",
        "GDPR Art.25 Privacy by Design and by Default",
        "GDPR Art.30 records of processing activities",
        "GDPR Art.33 breach notification to supervisory authority",
        "GDPR Art.17 right to erasure conditions",
        "CCPA consumer rights and business obligations",
    ],
    "iso22301_li/bcms_fundamentals": [
        "ISO 22301 cláusula 8.2 Business Impact Analysis (BIA)",
        "ISO 22301 RTO e RPO — definição e aplicação",
        "ISO 22301 cláusula 8.4 planos de continuidade — conteúdo",
        "ISO 22301 cláusula 8.5 exercícios e testes do BCMS",
        "ISO 22301 cláusula 5 liderança e política de continuidade",
        "ISO 22301 cláusula 6.1 ações para tratar riscos e oportunidades",
    ],
}

# ─────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup(path):
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

def topicos_file(cert_id, domain_id):
    return f"topicos_usados_{cert_id}_{domain_id}.json"

def load_topicos_usados(cert_id, domain_id):
    fpath = topicos_file(cert_id, domain_id)
    if os.path.exists(fpath):
        with open(fpath, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_topicos_usados(cert_id, domain_id, data):
    fpath = topicos_file(cert_id, domain_id)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_num(questions):
    if not questions:
        return 1
    return max(q.get("num", 0) for q in questions) + 1

def separador(char="─", n=70):
    print(char * n)

# ─────────────────────────────────────────────────────────────
# PROMPT DE GERAÇÃO
# ─────────────────────────────────────────────────────────────

LANG_NAMES = {"pt": "Português (Brasil)", "en": "English", "es": "Español"}

def build_prompt(cert_id, domain_id, lang, n_slots, topicos_alvo,
                 topicos_bloqueados, topicos_ja_usados, existing_questions):
    """Monta o prompt cirúrgico para geração de N questões."""

    lang_name = LANG_NAMES.get(lang, lang)
    domain_key = f"{cert_id}/{domain_id}"

    # Extrai textos das questões existentes para contexto anti-duplicata
    existing_texts = []
    for q in existing_questions[-20:]:  # últimas 20 para contexto
        text = q.get("text", "")[:80]
        existing_texts.append(f"  - {text}")
    existing_sample = "\n".join(existing_texts) if existing_texts else "  (nenhuma)"

    bloqueados_str = "\n".join(f"  ❌ {t}" for t in topicos_bloqueados)
    alvo_str       = "\n".join(f"  ✅ {t}" for t in topicos_alvo)
    usados_str     = "\n".join(f"  ⚠️  {t}" for t in topicos_ja_usados) if topicos_ja_usados else "  (nenhum ainda)"

    prompt = f"""You are an expert certification exam question writer for {cert_id.upper()} — {domain_id}.

TASK: Generate exactly {n_slots} unique exam question(s) in {lang_name}.

CERTIFICATION: {cert_id.upper()}
DOMAIN: {domain_id}
LANGUAGE: {lang_name}
QUESTIONS TO GENERATE: {n_slots}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOPICS TO COVER (choose from these):
{alvo_str}

BLOCKED TOPICS — DO NOT USE (already saturated):
{bloqueados_str}

TOPICS ALREADY USED IN THIS DOMAIN (avoid repetition):
{usados_str}

SAMPLE OF EXISTING QUESTIONS IN THIS FILE (do NOT repeat):
{existing_sample}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUALITY REQUIREMENTS:
- Each question must cover a DIFFERENT topic from the list above
- No question may resemble any existing question shown above
- All 4 options must be plausible and distinct
- Correct answer must be unambiguous and defensible
- Justifications must be technical and specific (not generic)
- Difficulty level: professional certification exam (advanced)

OUTPUT FORMAT — respond ONLY with valid JSON, no markdown, no explanation:

[
  {{
    "text": "Full question text in {lang_name}",
    "tag": "topic_tag_in_english_snake_case",
    "options": [
      "A. First option",
      "B. Second option",
      "C. Third option",
      "D. Fourth option"
    ],
    "correct": 0,
    "justification_correct": "Detailed explanation of why this answer is correct",
    "justification_wrong": "Brief explanation of why the other options are incorrect"
  }}
]

CRITICAL: Return ONLY the JSON array. No preamble. No markdown fences. No explanation."""

    return prompt

# ─────────────────────────────────────────────────────────────
# GERAÇÃO VIA API
# ─────────────────────────────────────────────────────────────

def gerar_questoes(prompt):
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    # Remove fences se o modelo insistir
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# ─────────────────────────────────────────────────────────────
# EXIBIÇÃO PARA APROVAÇÃO
# ─────────────────────────────────────────────────────────────

def exibir_questao(idx, q):
    separador()
    print(f"  QUESTÃO {idx+1}")
    separador()
    print(f"  TAG    : {q.get('tag','')}")
    print(f"  TEXTO  : {q.get('text','')}")
    print()
    options = q.get("options", [])
    correct = q.get("correct", 0)
    for i, opt in enumerate(options):
        marker = "✅" if i == correct else "  "
        print(f"  {marker} {opt}")
    print()
    print(f"  JUSTIF. CORRETA : {q.get('justification_correct','')}")
    print(f"  JUSTIF. ERRADA  : {q.get('justification_wrong','')}")
    separador()

def aprovar_questao(idx, q):
    while True:
        resp = input(f"  Aprovar questão {idx+1}? [s=sim / n=não / r=regenerar] → ").strip().lower()
        if resp in ("s", "n", "r"):
            return resp
        print("  Digite s, n ou r.")

# ─────────────────────────────────────────────────────────────
# INJEÇÃO NO JSON
# ─────────────────────────────────────────────────────────────

def injetar_questao(filepath, questao, num):
    data = load_json(filepath)
    questao["num"] = num
    data["questions"].append(questao)
    save_json(filepath, data)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 70)
    print("  NEXOR — REPOSITOR DE SLOT UNITÁRIO v1")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    print()

    # ── Coleta de parâmetros ──────────────────────────────────
    cert_id   = input("  cert_id   (ex: cfe, iso27001_li, cdpse): ").strip().lower()
    domain_id = input("  domain_id (ex: law_cfe, annex_a_controls): ").strip().lower()
    quiz_num  = int(input("  quiz_num  (ex: 3 para quiz_003): ").strip())
    lang      = input("  lang      (pt / en / es): ").strip().lower()
    n_slots   = int(input("  slots a repor (ex: 2): ").strip())

    domain_key = f"{cert_id}/{domain_id}"
    fpath = os.path.join(
        QUIZZES_DIR, cert_id, domain_id,
        f"quiz_{quiz_num:03d}_{lang}.json"
    )

    if not os.path.exists(fpath):
        print(f"\n  ERRO: Arquivo não encontrado: {fpath}")
        return

    # ── Tópicos ──────────────────────────────────────────────
    bloqueados_globais = TOPICOS_BLOQUEADOS_GLOBAIS.get(domain_key, [])

    print(f"\n  Tópicos recomendados para {domain_key}:")
    recomendados = TOPICOS_RECOMENDADOS.get(domain_key, [])
    for i, t in enumerate(recomendados):
        print(f"    [{i+1}] {t}")

    print()
    print("  Digite os números dos tópicos alvo (ex: 1,3,5)")
    print("  ou deixe em branco para usar todos os recomendados:")
    sel = input("  → ").strip()

    if sel:
        indices = [int(x.strip()) - 1 for x in sel.split(",") if x.strip().isdigit()]
        topicos_alvo = [recomendados[i] for i in indices if 0 <= i < len(recomendados)]
    else:
        topicos_alvo = recomendados

    # ── Memória de tópicos já usados ─────────────────────────
    topicos_usados_db = load_topicos_usados(cert_id, domain_id)
    topicos_ja_usados = list(topicos_usados_db.get("usados", []))

    # ── Carrega arquivo alvo ──────────────────────────────────
    data = load_json(fpath)
    existing_questions = data.get("questions", [])
    total_atual = len(existing_questions)
    backup(fpath)

    print(f"\n  Arquivo  : {fpath}")
    print(f"  Questões : {total_atual}/50  →  slots livres: {50 - total_atual}")
    print(f"  Gerando  : {n_slots} questão(ões)")
    separador()

    # ── Loop de geração por slot ──────────────────────────────
    log_lines     = [f"NEXOR — REPOSIÇÃO — {TIMESTAMP}", f"Arquivo: {fpath}", ""]
    injetadas     = 0
    regeneracoes  = 0

    for slot in range(n_slots):
        print(f"\n  ── SLOT {slot + 1}/{n_slots} ──────────────────────────────")
        print("  Chamando API...")

        aprovado = False
        tentativas = 0

        while not aprovado:
            tentativas += 1
            if tentativas > 3:
                print("  AVISO: 3 tentativas sem aprovação. Pulando slot.")
                log_lines.append(f"  SLOT {slot+1}: PULADO após 3 tentativas")
                break

            try:
                prompt = build_prompt(
                    cert_id, domain_id, lang, 1,
                    topicos_alvo, bloqueados_globais,
                    topicos_ja_usados, existing_questions
                )
                questoes = gerar_questoes(prompt)
                q = questoes[0] if questoes else None

                if not q:
                    print("  ERRO: API retornou lista vazia. Tentando novamente...")
                    continue

                exibir_questao(slot, q)
                resp = aprovar_questao(slot, q)

                if resp == "s":
                    num = get_next_num(data["questions"])
                    injetar_questao(fpath, q, num)
                    data = load_json(fpath)  # recarrega após injeção
                    existing_questions = data["questions"]

                    tag = q.get("tag", "sem_tag")
                    topicos_ja_usados.append(tag)
                    log_lines.append(f"  SLOT {slot+1}: INJETADA — Q{num} — tag: {tag}")
                    print(f"\n  ✅ Questão {num} injetada em {os.path.basename(fpath)}")
                    injetadas += 1
                    aprovado = True

                elif resp == "n":
                    print("  ❌ Questão rejeitada. Slot não preenchido.")
                    log_lines.append(f"  SLOT {slot+1}: REJEITADA pelo usuário")
                    aprovado = True  # sai do loop sem injetar

                elif resp == "r":
                    print("  🔄 Regenerando...")
                    regeneracoes += 1

            except json.JSONDecodeError as e:
                print(f"  ERRO JSON: {e}. Tentando novamente...")
            except Exception as e:
                print(f"  ERRO API: {e}")
                break

    # ── Salva memória de tópicos ──────────────────────────────
    topicos_usados_db["usados"] = list(set(topicos_ja_usados))
    save_topicos_usados(cert_id, domain_id, topicos_usados_db)

    # ── Salva log ─────────────────────────────────────────────
    log_lines += [
        "",
        f"Injetadas    : {injetadas}",
        f"Rejeitadas   : {n_slots - injetadas - regeneracoes}",
        f"Regenerações : {regeneracoes}",
        f"Total no arquivo após: {len(data['questions'])}/50",
    ]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n\n")

    # ── Resumo final ──────────────────────────────────────────
    print()
    separador("=")
    print(f"  CONCLUÍDO")
    print(f"  Injetadas       : {injetadas}/{n_slots}")
    print(f"  Regenerações    : {regeneracoes}")
    print(f"  Total no arquivo: {len(data['questions'])}/50")
    print(f"  Log             : {LOG_FILE}")
    print(f"  Memória tópicos : {topicos_file(cert_id, domain_id)}")
    separador("=")
    print()
    print("  PRÓXIMO PASSO:")
    print("  python verificar_duplicatas.py  ← validar após cada injeção")
    separador("=")


if __name__ == "__main__":
    main()
