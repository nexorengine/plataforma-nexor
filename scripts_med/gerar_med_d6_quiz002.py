import anthropic
import json
import os
import random
from datetime import datetime

PRODUTO      = "med"
CERT_ID      = "med"
DOMAIN_ID    = "cirurgia_geral"
SUBDOMINIO   = "trato_digestivo_superior"
DOMAIN_NAME  = "D6 · Trato Digestivo Superior"
CERT_NAME    = "Residência Médica — Cirurgia Geral"
QUIZ_NUM     = 2
LANG         = "pt"
QUIZ001_PATH = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d6_001_pt.json"
OUTPUT_PATH  = r"C:\ARAGORN\aragorn_quiz\static\quizzes\med\cirurgia_geral\quiz_d6_002_pt.json"
LOG_PATH     = r"C:\ARAGORN\aragorn_quiz\scripts_med\log_d6_quiz002.txt"
MODEL        = "claude-haiku-4-5-20251001"

BLOCOS = [
    {"camada": "F1", "descricao": "Definição e terminologia clínica",       "difficulty": "EASY",     "n": 10, "tokens": 4000},
    {"camada": "F2", "descricao": "Diagnóstico diferencial e distinções",   "difficulty": "STANDARD", "n": 10, "tokens": 4000},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas",           "difficulty": "STANDARD", "n": 10, "tokens": 5600},
    {"camada": "F3", "descricao": "Cenários clínicos e condutas avançadas", "difficulty": "STANDARD", "n": 10, "tokens": 5600},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
    {"camada": "F4", "descricao": "Integração e julgamento clínico",        "difficulty": "HARD",     "n": 5,  "tokens": 3000},
]

TOPICOS = [
    "DRGE — diagnóstico, classificação de Los Angeles e tratamento",
    "Esôfago de Barrett — vigilância e risco de adenocarcinoma",
    "Úlcera péptica gástrica e duodenal — fisiopatologia e complicações",
    "Hemorragia digestiva alta — conduta e classificação de Forrest",
    "Câncer gástrico — classificação de Borrmann e estadiamento",
    "Câncer de esôfago — escamoso vs adenocarcinoma",
    "Síndrome de Zollinger-Ellison",
    "Acalasia e disfagia — diagnóstico diferencial"
]

METODO_NEXOR = """
MÉTODO NEXOR — APLICAR OBRIGATORIAMENTE:
STEM: cenário clínico realista + lead-in focado. Sem info irrelevante, sem negativo duplo.
OPÇÕES: 4 opções homogêneas (±20%). Correta NÃO é a mais longa. Distrátores plausíveis.
Sem absolutos (sempre/nunca), sem clang, sem "todas as anteriores".
EASY: Bloom 1-2. STANDARD: Bloom 3. HARD: Bloom 4-5.
justification_correct: princípio clínico/fisiopatológico (máx 30 palavras).
justification_wrong: por que cada distrator está errado (máx 20 palavras cada).
"""

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def shuffle_options(questoes):
    letras = ["A", "B", "C", "D"]
    for q in questoes:
        options = q.get("options", [])
        correct_idx = q.get("correct", 1) - 1
        if not options or correct_idx < 0 or correct_idx >= len(options):
            continue
        correct_text = options[correct_idx]
        textos = [opt[2:].strip() if len(opt) > 2 and opt[1] == "." else opt for opt in options]
        random.shuffle(textos)
        correct_limpo = correct_text[2:].strip() if len(correct_text) > 2 and correct_text[1] == "." else correct_text
        q["options"] = [f"{letras[i]}. {textos[i]}" for i in range(len(textos))]
        q["correct"] = textos.index(correct_limpo) + 1
    return questoes

def carregar_tags():
    try:
        with open(QUIZ001_PATH, encoding="utf-8") as f:
            data = json.load(f)
        tags = [q.get("tag","") for q in data.get("questions",[]) if q.get("tag")]
        log(f"  Tags quiz_001 carregadas: {len(tags)}")
        return tags
    except Exception as e:
        log(f"  AVISO: {e}")
        return []

def gerar_bloco(client, bloco, topicos, tags_usadas, q_start):
    camada = bloco["camada"]; descricao = bloco["descricao"]
    difficulty = bloco["difficulty"]; n = bloco["n"]; tokens = bloco["tokens"]

    restricao = ""
    if tags_usadas:
        restricao = f"\nTAGS JÁ USADAS — NÃO REPITA:\n{', '.join(tags_usadas[:25])}\nCubra ângulos DIFERENTES.\n"

    system = f"""Você é um gerador expert de questões de múltipla escolha para provas de residência médica no Brasil.
Referência: Sabiston 2019. Nível: ACM/SC.
{METODO_NEXOR}
Responda SOMENTE com JSON válido, sem markdown, sem backticks."""

    prompt = f"""Gere exatamente {n} questões nível {difficulty} ({camada} — {descricao}) sobre Trato Digestivo Superior em Cirurgia Geral.
Tópicos: {', '.join(topicos)}
{restricao}
JSON:
{{"questoes":[{{"num":{q_start},"text":"enunciado","tag":"snake_case","camada":"{camada}","options":["A. texto","B. texto","C. texto","D. texto"],"correct":1,"difficulty":"{difficulty}","justification_correct":"princípio em 30 palavras","justification_wrong":"A: motivo; B: motivo; C: motivo"}}]}}

IDs começando em num={q_start}. correct=1-4. Opções homogêneas. Correta não é a mais longa."""

    for tentativa in range(1, 4):
        try:
            response = client.messages.create(model=MODEL, max_tokens=tokens, system=system,
                messages=[{"role": "user", "content": prompt}])
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
            data = json.loads(raw.strip())
            return data["questoes"]
        except json.JSONDecodeError as e:
            log(f"  Tentativa {tentativa} falhou: {e}")
            if tentativa == 3: raise
            tokens = int(tokens * 1.4)
            log(f"  Retentando com {tokens} tokens...")

def main():
    log("=" * 60)
    log(f"NEXOR MED — Quiz {QUIZ_NUM:03d} — {DOMAIN_NAME} — PT")
    log(f"Padrão: 20% EASY + 60% STANDARD + 20% HARD | Shuffle: ON")
    log(f"Zero repeat de temas do quiz_001")
    log("=" * 60)

    client = anthropic.Anthropic()
    log("Carregando tags do quiz_001...")
    tags_usadas = carregar_tags()

    todas = []
    q_start = 1

    for i, bloco in enumerate(BLOCOS):
        label = f"{bloco['camada']}/{bloco['difficulty']} ({bloco['n']}q)"
        log(f"Gerando bloco {i+1}/{len(BLOCOS)}: {label}...")
        questoes = gerar_bloco(client, bloco, TOPICOS, tags_usadas, q_start)
        novas = [q.get("tag","") for q in questoes if q.get("tag")]
        tags_usadas.extend(novas)
        todas.extend(questoes)
        q_start += bloco["n"]
        log(f"  OK: {len(questoes)} questões")

    log("Aplicando shuffle...")
    random.seed(None)
    todas = shuffle_options(todas)
    dist = {}
    for q in todas:
        l = ["A","B","C","D"][q.get("correct",1)-1]
        dist[l] = dist.get(l, 0) + 1
    log(f"  Distribuição: {dict(sorted(dist.items()))}")

    log(f"\nAUDITORIA:")
    log(f"  Total: {len(todas)}")
    easy = sum(1 for q in todas if q.get("difficulty") == "EASY")
    std  = sum(1 for q in todas if q.get("difficulty") == "STANDARD")
    hard = sum(1 for q in todas if q.get("difficulty") == "HARD")
    log(f"  EASY: {easy} | STANDARD: {std} | HARD: {hard}")
    alertas = sum(1 for q in todas if len(q.get("options",[])) != 4 or q.get("correct") not in [1,2,3,4])
    log("  Todas dentro do padrão NEXOR." if not alertas else f"  Alertas: {alertas}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"cert_id": CERT_ID, "domain_id": DOMAIN_ID,
                   "subdominio": SUBDOMINIO, "quiz_num": QUIZ_NUM,
                   "domain_name": DOMAIN_NAME, "cert_name": CERT_NAME,
                   "lang": LANG, "total": len(todas), "questions": todas},
                  f, ensure_ascii=False, indent=2)

    log(f"\nSalvo em: {OUTPUT_PATH}")
    log("CONCLUÍDO.")

if __name__ == "__main__":
    main()
