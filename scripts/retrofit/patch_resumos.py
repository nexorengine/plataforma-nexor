import json

updates = [
    {
        "arquivo": "content/resumos/cirurgia_geral/trauma_urgencia/quiz_001_resumos.json",
        "num": 12,
        "texto": "Ferimentos penetrantes na zona precordial (entre mamilos, abaixo das clavículas) exigem rastreio obrigatório de tamponamento cardíaco. O POCUS com janela subxifoide detecta derrame pericárdico com sensibilidade de 92-100%, superando a radiografia de tórax (que detecta apenas derrames volumosos) e a TC (que consome tempo crítico). Em paciente hemodinamicamente estável, o POCUS é o exame inicial de escolha: rápido, não invasivo e disponível à beira do leito. Tamponamento oculto pode evoluir para choque obstrutivo súbito; o diagnóstico precoce permite pericardiocentese ou janela pericárdica a tempo.",
        "fonte": "Moore EE et al. Trauma. 9ª ed. McGraw-Hill, 2021. Cap. 26 — Trauma cardíaco."
    },
    {
        "arquivo": "content/resumos/medicina_preventiva/vigilancia_epidemiologica/quiz_001_resumos.json",
        "num": 12,
        "texto": "O poliovírus vacinal derivado circulante (cVDPV) emerge quando a VOP se propaga em cadeia entre suscetíveis, acumulando mutações de reversão de neurovirulência a cada ciclo replicativo. Esse processo exige circulação comunitária prolongada, possível apenas quando a cobertura cai abaixo do limiar de imunidade de rebanho (80-85%). Com 68% de cobertura, a massa suscetível sustenta transmissão suficiente para selecionar cVDPV2. As demais alternativas descrevem mecanismos incorretos: IgA secretória, recombinação com vírus selvagem e competição viral intestinal não explicam a emergência de cVDPV em contexto de baixa cobertura vacinal.",
        "fonte": "Brasil. Ministério da Saúde. Guia de Vigilância em Saúde. 5ª ed. Brasília: MS, 2022. Cap. Poliomielite."
    },
    {
        "arquivo": "content/resumos/medicina_preventiva/vigilancia_epidemiologica/quiz_002_resumos.json",
        "num": 41,
        "texto": "A vacina acelular (DTPa) induz imunidade humoral robusta, mas com declínio significativo em 4-7 anos. Adolescentes e adultos com waning immunity tornam-se reservatório silencioso, transmitindo aos lactentes menores de 6 meses — grupo com maior mortalidade por coqueluche. A mutação ptxP3 da Bordetella agrava o escape vacinal. A estratégia de maior impacto na mortalidade infantil é a vacinação de gestantes com dTpa entre 27-36 semanas: os anticorpos IgG maternos cruzam a placenta, conferindo proteção passiva ao recém-nascido antes do início do esquema primário, conforme recomendação OMS/SAGE.",
        "fonte": "Brasil. Ministério da Saúde. Programa Nacional de Imunizações. Nota Técnica dTpa gestante. Brasília: MS, 2023."
    }
]

for u in updates:
    with open(u["arquivo"], encoding="utf-8") as f:
        dados = json.load(f)
    for r in dados["resumos"]:
        if r["num"] == u["num"]:
            r["texto"] = u["texto"]
            r["fonte"] = u["fonte"]
            print("  {} num:{} -> {} palavras OK".format(
                u["arquivo"].split("/")[-1], u["num"], len(u["texto"].split())))
            break
    with open(u["arquivo"], "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

print("\nConcluido.")
