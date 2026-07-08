"""
gerar_flashcards_med.py -- NEXOR FractalFlashcard Generator (Medicina)
Gera 48 flashcards por dominio (F1/F2/F3/F4 x 12 cards) em PT-BR.
Metodologia FractalLearning: definicao -> distincao -> aplicacao -> sintese.

Uso:
    python gerar_flashcards_med.py --area gineco_obstetricia --dominio puerperio_aleitamento
    python gerar_flashcards_med.py --area clinica_medica --dominio pneumologia
    python gerar_flashcards_med.py --area pediatria --dominio neonatologia
    python gerar_flashcards_med.py --area medicina_preventiva --dominio epidemiologia_geral
"""

import json
import time
import argparse
from pathlib import Path
import anthropic

# -- CONFIG ------------------------------------------------------------------

MODEL      = "claude-opus-4-8"
MAX_TOKENS = 4000
DELAY      = 2   # segundos entre chamadas

REPO       = Path(r"C:\ARAGORN\aragorn_quiz")
OUTPUT_DIR = REPO / "flashcards" / "med"

# -- DOMINIOS ----------------------------------------------------------------

DOMINIOS = {
    "gineco_obstetricia": {
        "pre_natal":                  {"code": "GO_D01", "titulo": "Pré-natal"},
        "parto_normal":               {"code": "GO_D02", "titulo": "Parto Normal e Assistência ao Parto"},
        "puerperio_aleitamento":      {"code": "GO_D03", "titulo": "Puerpério e Aleitamento Materno"},
        "complicacoes_obstetricas":   {"code": "GO_D04", "titulo": "Complicações Obstétricas"},
        "ginecologia_geral":          {"code": "GO_D05", "titulo": "Ginecologia Geral"},
        "doencas_uterinas_anexiais":  {"code": "GO_D06", "titulo": "Doenças Uterinas e Anexiais"},
        "infeccoes_genitais_dsts":    {"code": "GO_D07", "titulo": "Infecções Genitais e DSTs"},
        "cancer_ginecologico":        {"code": "GO_D08", "titulo": "Câncer Ginecológico"},
        "uroginecologia_piso_pelvico":{"code": "GO_D09", "titulo": "Uroginecologia e Piso Pélvico"},
    },
    "clinica_medica": {
        "cardiologia":       {"code": "CM_D01", "titulo": "Cardiologia"},
        "pneumologia":       {"code": "CM_D02", "titulo": "Pneumologia"},
        "gastroenterologia": {"code": "CM_D03", "titulo": "Gastroenterologia"},
        "nefrologia":        {"code": "CM_D04", "titulo": "Nefrologia"},
        "endocrinologia":    {"code": "CM_D05", "titulo": "Endocrinologia"},
        "hematologia":       {"code": "CM_D06", "titulo": "Hematologia"},
        "reumatologia":      {"code": "CM_D07", "titulo": "Reumatologia"},
        "infectologia":      {"code": "CM_D08", "titulo": "Infectologia"},
        "neurologia":        {"code": "CM_D09", "titulo": "Neurologia"},
    },
    "pediatria": {
        "neonatologia":          {"code": "PED_D01", "titulo": "Neonatologia"},
        "puericultura":          {"code": "PED_D02", "titulo": "Puericultura e Desenvolvimento"},
        "pneumologia_ped":       {"code": "PED_D03", "titulo": "Pneumologia Pediátrica"},
        "gastro_ped":            {"code": "PED_D04", "titulo": "Gastroenterologia Pediátrica"},
        "infectologia_ped":      {"code": "PED_D05", "titulo": "Infectologia Pediátrica"},
        "cardio_ped":            {"code": "PED_D06", "titulo": "Cardiologia Pediátrica"},
        "endocrinologia_ped":    {"code": "PED_D07", "titulo": "Endocrinologia Pediátrica"},
        "hematologia_onco_ped":  {"code": "PED_D08", "titulo": "Hematologia e Oncologia Pediátrica"},
        "emergencias_ped":       {"code": "PED_D09", "titulo": "Emergências Pediátricas"},
    },
    "medicina_preventiva": {
        "epidemiologia_geral":        {"code": "PREV_D01", "titulo": "Epidemiologia Geral"},
        "vigilancia_epidemiologica":  {"code": "PREV_D02", "titulo": "Vigilância Epidemiológica"},
        "imunizacao_pni":             {"code": "PREV_D03", "titulo": "Imunização e PNI"},
        "bioestatistica":             {"code": "PREV_D04", "titulo": "Bioestatística"},
        "saude_familia_aps":          {"code": "PREV_D05", "titulo": "Saúde da Família e APS"},
        "politica_nacional_sus":      {"code": "PREV_D06", "titulo": "Política Nacional de Saúde e SUS"},
        "saude_ambiental_ocupacional":{"code": "PREV_D07", "titulo": "Saúde Ambiental e Ocupacional"},
        "dcnt_promocao_saude":        {"code": "PREV_D08", "titulo": "DCNT e Promoção da Saúde"},
        "bioetica_etica_medica":      {"code": "PREV_D09", "titulo": "Bioética e Ética Médica"},
    },
}

# -- FRACTAL LAYERS ----------------------------------------------------------

LAYERS = {
    "F1": (
        "F1 — DEFINIÇÃO: Gere 12 flashcards que testem conceitos puros, definições, "
        "terminologia e significado exato de termos-chave do domínio. "
        "Exemplos de frente: 'Defina X', 'O que é Y?', 'Qual o critério diagnóstico de Z?', "
        "'Qual o valor de referência de W?'. "
        "Respostas objetivas, diretas, com números e critérios quando aplicável."
    ),
    "F2": (
        "F2 — DISTINÇÃO: Gere 12 flashcards que comparem dois conceitos, diferenciem "
        "entidades similares ou identifiquem qual se aplica em dado contexto. "
        "Exemplos de frente: 'Qual a diferença entre A e B?', 'Como distinguir X de Y?', "
        "'Quando usar A vs B?'. "
        "Respostas com diferenciação clara, tabela mental ou regra mnemônica."
    ),
    "F3": (
        "F3 — APLICAÇÃO: Gere 12 flashcards práticos sobre como diagnosticar, tratar, "
        "prevenir ou conduzir casos clínicos reais. "
        "Exemplos de frente: 'Qual a conduta inicial em X?', 'Como tratar Y?', "
        "'Quais os red flags de Z?', 'Qual o exame de escolha para W?'. "
        "Respostas com protocolo prático, dose quando relevante, fluxo de decisão."
    ),
    "F4": (
        "F4 — SÍNTESE: Gere 12 flashcards integrando múltiplos conceitos, exigindo "
        "raciocínio clínico de alto nível, fisiopatologia ou conexões entre temas. "
        "Exemplos de frente: 'Por que X causa Y?', 'Como X e Y se relacionam na fisiopatologia?', "
        "'Qual o mecanismo de ação de Z?', 'Integre A, B e C no diagnóstico diferencial de W'. "
        "Respostas ricas, com mecanismo, implicação clínica e conexão entre conceitos."
    ),
}

# -- PROMPT ------------------------------------------------------------------

SYSTEM = (
    "Você é um especialista em medicina e educação médica para residência médica brasileira. "
    "Seu papel é criar flashcards de alta qualidade para o estudo de medicina, "
    "seguindo a metodologia FractalLearning com 4 camadas cognitivas progressivas. "
    "Os flashcards devem ser precisos, objetivos e alinhados com o que cai nas provas de residência médica no Brasil."
)

def build_prompt(area: str, dominio_info: dict, layer: str, layer_instruction: str) -> str:
    return f"""Você está gerando flashcards para o domínio: **{dominio_info['titulo']}** ({dominio_info['code']})
Especialidade: {area.replace('_', ' ').title()}
Camada: {layer}

{layer_instruction}

FORMATO DE RESPOSTA (JSON puro, sem markdown):
{{
  "cards": [
    {{"layer": "{layer}", "front": "pergunta objetiva e clara", "back": "resposta precisa e direta"}},
    ...
  ]
}}

Gere exatamente 12 cards. Todos em português brasileiro. Foque em conteúdo cobrado nas provas de residência médica.
Não repita conceitos entre os cards. Varie os temas dentro do domínio.
Responda APENAS com o JSON, sem texto adicional."""

# -- GERADOR -----------------------------------------------------------------

def gerar_layer(client, area, dominio_info, layer, instruction, code):
    prompt = build_prompt(area, dominio_info, layer, instruction)
    for tentativa in range(3):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            texto = resp.content[0].text.strip()
            # limpa markdown se necessario
            if texto.startswith("```"):
                texto = texto.split("```")[1]
                if texto.startswith("json"):
                    texto = texto[4:]
            data = json.loads(texto)
            cards = data.get("cards", [])
            # garante layer e adiciona id
            for i, c in enumerate(cards, 1):
                c["layer"] = layer
                c["id"] = f"{code}_{layer}_{i:03d}"
            return cards
        except Exception as e:
            print(f"    tentativa {tentativa+1} falhou: {e}")
            time.sleep(5)
    return []

# -- MAIN --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--area", required=True,
        help="gineco_obstetricia | clinica_medica | pediatria | medicina_preventiva")
    parser.add_argument("--dominio", required=True,
        help="Ex: puerperio_aleitamento, pneumologia, neonatologia")
    parser.add_argument("--delay", type=float, default=DELAY)
    args = parser.parse_args()

    area    = args.area.lower()
    dominio = args.dominio.lower()

    if area not in DOMINIOS:
        print(f"Area invalida: {area}"); return
    if dominio not in DOMINIOS[area]:
        print(f"Dominio invalido: {dominio}"); return

    dominio_info = DOMINIOS[area][dominio]
    code = dominio_info["code"]

    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY") or \
        __import__("subprocess").check_output(
            ["powershell", "-Command",
             "[System.Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')"],
            text=True).strip()
    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n{'='*60}")
    print(f"  FractalFlashcard Generator — NEXOR med")
    print(f"  Area:    {area}")
    print(f"  Dominio: {dominio_info['titulo']} ({code})")
    print(f"  Modelo:  {MODEL}")
    print(f"{'='*60}\n")

    todos_cards = []
    for layer, instruction in LAYERS.items():
        print(f"  [{layer}] gerando 12 cards...", end=" ", flush=True)
        cards = gerar_layer(client, area, dominio_info, layer, instruction, code)
        print(f"OK ({len(cards)} cards)")
        todos_cards.extend(cards)
        time.sleep(args.delay)

    out = {
        "especialidade": area,
        "dominio": code,
        "titulo": dominio_info["titulo"],
        "versao": "1.0",
        "total_cards": len(todos_cards),
        "cards": todos_cards
    }

    dest = OUTPUT_DIR / area / dominio / "flashcards_pt.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nConcluido! {len(todos_cards)}/48 cards gerados.")
    print(f"Arquivo: {dest}\n")

if __name__ == "__main__":
    main()
