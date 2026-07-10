"""
Expande os resumos analíticos abaixo de 600 caracteres para a faixa 600–900 chars.
Usa claude-opus-4-8 para máxima qualidade clínica.
"""

import anthropic
import json
import os

client = anthropic.Anthropic()

SYSTEM = """Você é um professor de medicina de alto nível especializado em preparação para Residência Médica brasileira.

Recebe uma questão de múltipla escolha e um resumo analítico existente (porém incompleto).

Sua tarefa é reescrever o resumo com EXATAMENTE entre 600 e 900 caracteres (conte os caracteres — não palavras).
Isso equivale a aproximadamente 3 a 5 frases densas. Não ultrapasse 900 caracteres em hipótese alguma.

O resumo deve conter:
1. O raciocínio que justifica a alternativa correta
2. Por que as alternativas incorretas estão erradas
3. Uma referência clínica citada (ex: "Conforme o Harrison..." ou "Segundo o MS Brasil...")

Escreva de forma compacta e direta. Cada palavra deve ter peso clínico.
Retorne APENAS o texto do resumo, sem cabeçalho, sem marcadores, sem markdown."""


CASOS = [
    {
        "arquivo": r"C:\NEXOR_MED\plataforma-nexor\content\resumos\medicina_preventiva\dcnt_promocao_saude\quiz_001_resumos.json",
        "num": 25,
        "questao": "Pesquisador avalia o impacto de uma intervenção anti-tabagismo em uma coorte de 10.000 adultos fumantes. Após 5 anos, a incidência de infarto agudo do miocárdio (IAM) no grupo intervenção (cessação tabágica confirmada) foi de 1,2%, versus 3,6% no grupo controle (fumantes contínuos). Qual é a redução do risco relativo (RRR) e o número necessário para tratar (NNT) calculados corretamente?",
        "opts": [
            "A) RRR = 67% e NNT = 42",
            "B) RRR = 67% e NNT = 24",
            "C) RRR = 33% e NNT = 42",
            "D) RRR = 2,4% e NNT = 42"
        ],
        "correta": "A"
    },
    {
        "arquivo": r"C:\NEXOR_MED\plataforma-nexor\content\resumos\medicina_preventiva\vigilancia_epidemiologica\quiz_002_resumos.json",
        "num": 41,
        "questao": "Secretaria estadual de saúde investiga surto de coqueluche em município com cobertura vacinal de DTP/DTPa historicamente superior a 95%. Em 14 semanas, confirmam-se 43 casos: 61% em lactentes menores de 6 meses, 28% em adolescentes de 11-14 anos e 11% em adultos com esquema primário completo. A investigação genômica identifica circulação de Bordetella pertussis com mutação no gene ptxP3. Qual é a principal limitação estrutural do programa de imunização e a intervenção mais adequada para redução da mortalidade?",
        "opts": [
            "A) Falha primária vacinal por cobertura insuficiente em adolescentes; reforço de DTPa em adolescentes.",
            "B) Waning immunity da vacina acelular em adolescentes/adultos criando reservatório para lactentes; vacinação de gestantes com dTpa no 3º trimestre.",
            "C) Escape imunológico por variante ptxP3 tornando a vacina ineficaz em todas as faixas; suspensão do esquema atual.",
            "D) Subnotificação laboratorial mascarando casos em adultos; ampliar PCR para Bordetella pertussis."
        ],
        "correta": "B"
    }
]


def montar_prompt(caso, resumo_atual=""):
    opts_str = "\n".join(caso["opts"])
    base = f"""QUESTÃO:
{caso["questao"]}

ALTERNATIVAS:
{opts_str}

ALTERNATIVA CORRETA: {caso["correta"]}
"""
    if resumo_atual:
        base += f"\nRESUMO ATUAL (incompleto, use como base):\n{resumo_atual}\n"
    base += "\nEscreva o resumo analítico (ENTRE 600 E 900 CARACTERES — obrigatório):"
    return base


def expandir_resumo(caso, resumo_atual=""):
    print(f"\n> Processando: {os.path.basename(caso['arquivo'])} questao #{caso['num']}")

    for tentativa in range(1, 4):
        resposta = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=400,
            system=SYSTEM,
            messages=[{"role": "user", "content": montar_prompt(caso, resumo_atual)}]
        )

        texto = resposta.content[0].text.strip()
        chars = len(texto)
        print(f"  Tentativa {tentativa}: {chars} chars", end="")

        if 600 <= chars <= 900:
            print(" [OK]")
            return texto
        elif chars > 900:
            print(" [ACIMA — reduzindo na proxima tentativa]")
            # Passa o texto longo como base para cortar
            resumo_atual = texto
        else:
            print(" [ABAIXO — expandindo na proxima tentativa]")

    print(f"  [AVISO] Nao atingiu a faixa em 3 tentativas. Usando ultimo resultado ({chars} chars).")
    return texto


def salvar(caso, novo_texto):
    caminho = caso["arquivo"]
    with open(caminho, encoding="utf-8-sig") as f:
        data = json.load(f)

    idx = next(i for i, r in enumerate(data["resumos"]) if r["num"] == caso["num"])
    texto_antigo = data["resumos"][idx]["texto"]

    data["resumos"][idx]["texto"] = novo_texto

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Salvo  : {caminho}")
    print(f"  Antes  : {len(texto_antigo)} chars")
    print(f"  Depois : {len(novo_texto)} chars")


if __name__ == "__main__":
    print("=== Retrofit: expandir resumos abaixo de 600 chars ===")
    print(f"Modelo: claude-opus-4-8 · Casos: {len(CASOS)}\n")

    for caso in CASOS:
        # Carrega o resumo atual para usar como base
        with open(caso["arquivo"], encoding="utf-8-sig") as f:
            data = json.load(f)
        idx = next(i for i, r in enumerate(data["resumos"]) if r["num"] == caso["num"])
        resumo_atual = data["resumos"][idx]["texto"]

        novo_texto = expandir_resumo(caso, resumo_atual)
        salvar(caso, novo_texto)

    print("\nConcluido. Verificar resultados antes de commitar.")
