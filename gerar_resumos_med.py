#!/usr/bin/env python3
"""
Gerador de Resumos Analíticos — nexor_med
Uso: python gerar_resumos_med.py --materia CG --dominio D01 --quiz 001
     python gerar_resumos_med.py --materia PREV --dominio D01 --quiz 001

Saída: prototipo-med/content/resumos/{MATERIA}_{DOMINIO}_quiz_{QUIZ}_resumos.json

Modelo: claude-opus-4-8 (máxima qualidade para conteúdo médico)
"""

import anthropic
import json
import argparse
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-8"

OUTPUT_DIR = Path(__file__).parent / "prototipo-med" / "content" / "resumos"

# Mapa: prefixo da matéria → pasta dos JSONs de origem
FONTE_DIR = {
    "CG":   None,   # ainda não gerado — pasta a definir
    "GO":   None,
    "CM":   None,
    "PED":  None,
    "PREV": Path(__file__).parent,  # prev_d01_gen/ etc. ficam na raiz
}

# Fontes bibliográficas primárias por matéria (completar conforme necessário)
REFERENCIAS = {
    "PREV": [
        "Medronho RA et al. Epidemiologia. 2ª ed. São Paulo: Atheneu, 2009.",
        "Rouquayrol MZ, Gurgel M. Epidemiologia & Saúde. 7ª ed. Rio de Janeiro: MedBook, 2013.",
        "Brasil. Ministério da Saúde. Guia de Vigilância em Saúde. 5ª ed. Brasília: MS, 2022.",
        "OMS. Classificação Internacional de Doenças — CID-11. Genebra: OMS, 2022.",
        "Hulley SB et al. Delineando a Pesquisa Clínica. 4ª ed. Porto Alegre: Artmed, 2015.",
    ],
    "CG": [
        "Townsend CM Jr. et al. Sabiston Textbook of Surgery. 21ª ed. Elsevier, 2022.",
        "Brunicardi FC et al. Schwartz's Principles of Surgery. 11ª ed. McGraw-Hill, 2019.",
        "Associação Médica Brasileira. Diretrizes Clínicas na Saúde Suplementar. AMB, 2023.",
    ],
    "GO": [
        "Rezende J, Montenegro CAB. Obstetrícia Fundamental. 14ª ed. Rio de Janeiro: Guanabara Koogan, 2022.",
        "Berek JS. Berek & Novak's Gynecology. 16ª ed. Lippincott, 2019.",
        "Brasil. Ministério da Saúde. Manual de Atenção à Saúde da Mulher. Brasília: MS, 2022.",
    ],
    "CM": [
        "Goldman L, Schafer AI. Goldman-Cecil Medicine. 26ª ed. Elsevier, 2019.",
        "Harrison's Principles of Internal Medicine. 21ª ed. McGraw-Hill, 2022.",
        "Martins MA et al. Clínica Médica USP. 2ª ed. São Paulo: Manole, 2016.",
    ],
    "PED": [
        "Kliegman RM et al. Nelson Textbook of Pediatrics. 21ª ed. Elsevier, 2020.",
        "Brasil. Ministério da Saúde. Cadernos de Atenção Básica — Saúde da Criança. Brasília: MS, 2021.",
        "Sociedade Brasileira de Pediatria. Guias de Orientação SBP. Rio de Janeiro: SBP, 2023.",
    ],
}

SYSTEM_PROMPT = """Você é um especialista em medicina e educação médica, responsável por criar
resumos analíticos de alta qualidade para questões de residência médica.

Seu resumo deve:
1. Explicar por que a alternativa CORRETA é a resposta certa, com base fisiopatológica e clínica
2. Explicar por que cada alternativa ERRADA está incorreta, de forma precisa e educativa
3. Contextualizar o tema na prática clínica e nas provas de residência
4. Usar linguagem técnica precisa, em português brasileiro, sem simplificações excessivas
5. Ter entre 150 e 300 palavras no total
6. NÃO incluir seções de "macete", "dica rápida", "resumo" ou afins
7. NÃO usar bullet points ou listas — texto corrido em parágrafos
8. Sempre terminar indicando a referência bibliográfica mais adequada para aprofundamento

A resposta deve ser um JSON com exatamente esta estrutura:
{
  "texto": "texto corrido do resumo analítico...",
  "fonte": "Referência bibliográfica completa (Autor, Título, Edição, Editora, Ano, Capítulo/Página)"
}

Não inclua nada fora do JSON."""


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def localizar_json(materia: str, dominio: str, quiz: str) -> Path:
    """Encontra o arquivo JSON de questões para a matéria/domínio/quiz."""
    codigo = f"{materia}_{dominio}"
    quiz_padded = quiz.zfill(3)

    # Tenta pasta padrão: {materia_lower}_d{nn}_gen/
    numero = dominio.lstrip("D").lstrip("0") or "1"
    candidatas = [
        Path(__file__).parent / f"{materia.lower()}_d{numero.zfill(2)}_gen" / f"{codigo}_quiz_{quiz_padded}_pt.json",
        Path(__file__).parent / f"prev_d{numero.zfill(2)}_gen" / f"{codigo}_quiz_{quiz_padded}_pt.json",
        Path(__file__).parent / f"{codigo}_quiz_{quiz_padded}_pt.json",
    ]
    for c in candidatas:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"JSON de questões não encontrado para {codigo} quiz {quiz_padded}.\n"
        f"Tentativas: {[str(c) for c in candidatas]}"
    )


def gerar_resumo(client: anthropic.Anthropic, questao: dict, materia: str) -> dict:
    """Chama a API e retorna {'texto': ..., 'fonte': ...}."""
    refs = "\n".join(f"- {r}" for r in REFERENCIAS.get(materia, []))
    user_msg = f"""Questão:
{questao['pergunta']}

Alternativas:
{chr(10).join(f"- {a}" for a in questao['alternativas'])}

Alternativa correta:
{questao['correct']}

Justificativa da correta (use como base, mas expanda):
{questao.get('justification_correct', '')}

Justificativa das erradas (use como base, mas expanda):
{questao.get('justification_wrong', '')}

Referências bibliográficas disponíveis para esta matéria:
{refs}

Gere o resumo analítico conforme as instruções do sistema."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = resp.content[0].text.strip()
    # Remove possível markdown code fence
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    return json.loads(raw)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Gerador de Resumos Analíticos nexor_med")
    parser.add_argument("--materia", required=True, help="Ex: PREV, CG, CM, GO, PED")
    parser.add_argument("--dominio", required=True, help="Ex: D01, D02")
    parser.add_argument("--quiz",    required=True, help="Ex: 001, 002")
    parser.add_argument("--delay",   type=float, default=1.0, help="Delay entre chamadas (s)")
    args = parser.parse_args()

    materia = args.materia.upper()
    dominio = args.dominio.upper()
    quiz    = args.quiz.zfill(3)

    print(f"\n{'='*60}")
    print(f"  nexor_med — Gerador de Resumos Analíticos")
    print(f"  Matéria: {materia}  Domínio: {dominio}  Quiz: {quiz}")
    print(f"  Modelo: {MODEL}")
    print(f"{'='*60}\n")

    # Localiza JSON de entrada
    json_path = localizar_json(materia, dominio, quiz)
    print(f"Fonte: {json_path}\n")

    with open(json_path, encoding="utf-8") as f:
        dados = json.load(f)

    questoes = dados.get("questoes", [])
    titulo   = dados.get("titulo", f"{materia}_{dominio}")
    total    = len(questoes)
    print(f"Domínio: {titulo} — {total} questões\n")

    client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saida_path = OUTPUT_DIR / f"{materia}_{dominio}_quiz_{quiz}_resumos.json"

    # Carrega progresso anterior se existir (permite retomar)
    if saida_path.exists():
        with open(saida_path, encoding="utf-8") as f:
            saida = json.load(f)
        print(f"Retomando — {len(saida['resumos'])} resumos já gerados.\n")
    else:
        saida = {
            "dominio": f"{materia}_{dominio}",
            "titulo":  titulo,
            "quiz":    quiz,
            "modelo":  MODEL,
            "resumos": []
        }

    ids_prontos = {r["id"] for r in saida["resumos"]}

    for i, q in enumerate(questoes, 1):
        qid = q.get("id", i)
        if qid in ids_prontos:
            print(f"  [{i:02d}/{total}] Q{qid} — já gerado, pulando.")
            continue

        print(f"  [{i:02d}/{total}] Q{qid} — gerando...", end=" ", flush=True)
        try:
            resumo = gerar_resumo(client, q, materia)
            saida["resumos"].append({
                "id":     qid,
                "texto":  resumo["texto"],
                "fonte":  resumo["fonte"],
            })
            # Salva após cada questão (seguro contra interrupções)
            with open(saida_path, "w", encoding="utf-8") as f:
                json.dump(saida, f, ensure_ascii=False, indent=2)
            print(f"OK")
        except Exception as e:
            print(f"ERRO: {e}")

        if i < total:
            time.sleep(args.delay)

    print(f"\nConcluído! {len(saida['resumos'])}/{total} resumos.")
    print(f"Arquivo: {saida_path}\n")


if __name__ == "__main__":
    main()
