import anthropic, json, os

client = anthropic.Anthropic()

QUESTOES = [
    {
        "arquivo": "C:/ARAGORN/plataforma-nexor/content/resumos/cirurgia_geral/trauma_urgencia/quiz_001_resumos.json",
        "num": 12,
        "questao": "Mulher, 28 anos, ferimento penetrante em tórax anterior direito (5 cm abaixo do mamilho). Hemodinamicamente estável, sem dispneia. Qual investigação é mais sensível para descartar lesão cardíaca neste cenário?",
        "opcoes": "A) Radiografia de tórax simples | B) Tomografia computadorizada com contraste | C) Observação clínica por 24 horas | D) Ecocardiografia/ultrassom pericárdico (POCUS)",
        "correta": "D",
        "exp": "POCUS detecta fluido pericárdico com alta sensibilidade (92-100%) em ferimentos penetrantes. Realizado à beira do leito, orientado à decisão."
    },
    {
        "arquivo": "C:/ARAGORN/plataforma-nexor/content/resumos/medicina_preventiva/vigilancia_epidemiologica/quiz_001_resumos.json",
        "num": 12,
        "questao": "Município com cobertura vacinal de poliomielite caída para 68% nos últimos dois anos notifica um caso de paralisia flácida aguda confirmado como poliovírus vacinal derivado tipo 2 (VDPV2). O comitê técnico decide iniciar campanha de vacinação em massa com VOP bivalente. Por que a queda da cobertura vacinal abaixo do limiar crítico favorece especificamente a emergência de VDPV circulante?",
        "opcoes": "A) Cobertura insuficiente aumenta a proporção de suscetíveis, permitindo que o vírus vacinal atenuado circule em comunidade e acumule mutações de reversão de neurovirulência ao longo de múltiplas replicações | B) A queda da cobertura reduz a imunidade de mucosa intestinal em vacinados, impedindo que a VOP induza resposta secretória de IgA eficaz | C) Coberturas abaixo de 70% permitem recombinação entre poliovírus selvagem e vacinal no intestino de crianças vacinadas, gerando VDPV independentemente da circulação comunitária | D) A VOP perde estabilidade genética quando administrada em populações com baixa cobertura porque há menor competição viral no ambiente intestinal dos vacinados",
        "correta": "A",
        "exp": "O VDPV circulante emerge quando o poliovírus vacinal atenuado se propaga em cadeia entre indivíduos suscetíveis, pois cada ciclo replicativo em novo hospedeiro seleciona reversões nas posições críticas de atenuação. Coberturas abaixo do limiar de imunidade de rebanho (~80-85% para poliomielite) mantêm massa suscetível suficiente para sustentar essa circulação prolongada."
    },
    {
        "arquivo": "C:/ARAGORN/plataforma-nexor/content/resumos/medicina_preventiva/vigilancia_epidemiologica/quiz_002_resumos.json",
        "num": 41,
        "questao": "Secretaria estadual de saúde investiga surto de coqueluche em município com cobertura vacinal de DTP/DTPa historicamente superior a 95%. Em 14 semanas, confirmam-se 43 casos: 61% em lactentes menores de 6 meses, 28% em adolescentes de 11-14 anos e 11% em adultos com esquema primário completo. A investigação genômica identifica circulação de Bordetella pertussis com mutação no gene codificador do antígeno ptxP3, associada à maior produção de toxina pertussis e à evasão da imunidade induzida pela vacina acelular. Qual é a principal limitação estrutural do programa de imunização evidenciada por este surto e a intervenção mais adequada para redução da mortalidade no grupo de maior risco?",
        "opcoes": "A) Falha primária vacinal por cobertura insuficiente em adolescentes; solução: reforço de DTPa em adolescentes de 11-14 anos como estratégia de cocoon | B) Waning immunity da vacina acelular em adolescentes e adultos com perda de proteção 5-7 anos após a última dose, criando reservatório de transmissão para lactentes vulneráveis; solução prioritária: vacinação de gestantes com dTpa no terceiro trimestre para transferência de anticorpos maternos | C) Escape imunológico por variante ptxP3 tornando a vacina ineficaz em todas as faixas etárias; solução: suspensão do esquema atual | D) Subnotificação laboratorial mascarando casos em adultos imunocompetentes",
        "correta": "B",
        "exp": "A vacina acelular induz imunidade humoral robusta inicialmente, porém com declínio em 4-7 anos. Adolescentes e adultos tornam-se reservatórios transmitindo aos lactentes menores de 6 meses. A vacinação de gestantes com dTpa entre 27-36 semanas gera anticorpos IgG que cruzam a placenta, conferindo proteção passiva ao recém-nascido."
    }
]

PROMPT_TEMPLATE = """Você é um professor de medicina de residência médica experiente. Escreva um resumo analítico CONCISO (entre 80 e 130 palavras) explicando o conceito médico central desta questão. O resumo deve:
- Explicar POR QUE a alternativa correta está certa
- Citar o dado clínico-chave ou mecanismo fisiopatológico central
- Ser direto, denso e útil para revisão de residência
- NÃO repetir o enunciado integralmente

QUESTÃO: {questao}
OPÇÕES: {opcoes}
CORRETA: {correta}
GABARITO: {exp}

Responda em JSON com exatamente dois campos: texto e fonte. Apenas o JSON, sem mais nada."""

for q in QUESTOES:
    print(f"\nGerando: {q['arquivo']} num:{q['num']}")
    prompt = PROMPT_TEMPLATE.format(**q)
    msg = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    text = msg.content[0].text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    novo = json.loads(text[start:end])
    print(f"  texto ({len(novo['texto'].split())} palavras): {novo['texto'][:100]}...")
    print(f"  fonte: {novo['fonte'][:80]}")

    # Atualiza o arquivo
    with open(q["arquivo"], encoding="utf-8") as f:
        dados = json.load(f)
    for r in dados["resumos"]:
        if r["num"] == q["num"]:
            r["texto"] = novo["texto"]
            r["fonte"] = novo["fonte"]
            break
    with open(q["arquivo"], "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  -> SALVO")

print("\nConcluído.")
