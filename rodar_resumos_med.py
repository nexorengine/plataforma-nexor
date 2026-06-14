#!/usr/bin/env python3
"""
Orquestrador de Resumos Analíticos — nexor_med
Roda gerar_resumos_med.py domínio a domínio, pausando para confirmação entre cada um.

Uso: python rodar_resumos_med.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "gerar_resumos_med.py"
PYTHON = sys.executable

# Sequência completa: CG → GO → CM → PED → PREV
# Cada entrada: (label, args_do_script)
SEQUENCIA = [
    # ── CIRURGIA GERAL ──────────────────────────────────────────────────────
    ("CG D1 · Abdome Agudo               — quiz 001", ["--area","cirurgia_geral","--cg-dominio","1","--quiz","001"]),
    ("CG D1 · Abdome Agudo               — quiz 002", ["--area","cirurgia_geral","--cg-dominio","1","--quiz","002"]),
    ("CG D2 · Hepatobiliar e Pâncreas    — quiz 001", ["--area","cirurgia_geral","--cg-dominio","2","--quiz","001"]),
    ("CG D2 · Hepatobiliar e Pâncreas    — quiz 002", ["--area","cirurgia_geral","--cg-dominio","2","--quiz","002"]),
    ("CG D3 · Trauma e Urgência          — quiz 001", ["--area","cirurgia_geral","--cg-dominio","3","--quiz","001"]),
    ("CG D3 · Trauma e Urgência          — quiz 002", ["--area","cirurgia_geral","--cg-dominio","3","--quiz","002"]),
    ("CG D4 · Parede Abdominal e Hérnias — quiz 001", ["--area","cirurgia_geral","--cg-dominio","4","--quiz","001"]),
    ("CG D4 · Parede Abdominal e Hérnias — quiz 002", ["--area","cirurgia_geral","--cg-dominio","4","--quiz","002"]),
    ("CG D5 · Esôfago e Estômago         — quiz 001", ["--area","cirurgia_geral","--cg-dominio","5","--quiz","001"]),
    ("CG D5 · Esôfago e Estômago         — quiz 002", ["--area","cirurgia_geral","--cg-dominio","5","--quiz","002"]),
    ("CG D6 · Intestino Delgado e Cólon  — quiz 001", ["--area","cirurgia_geral","--cg-dominio","6","--quiz","001"]),
    ("CG D6 · Intestino Delgado e Cólon  — quiz 002", ["--area","cirurgia_geral","--cg-dominio","6","--quiz","002"]),
    ("CG D7 · Doenças Anorretais         — quiz 001", ["--area","cirurgia_geral","--cg-dominio","7","--quiz","001"]),
    ("CG D7 · Doenças Anorretais         — quiz 002", ["--area","cirurgia_geral","--cg-dominio","7","--quiz","002"]),
    ("CG D8 · Oncologia Cirúrgica        — quiz 001", ["--area","cirurgia_geral","--cg-dominio","8","--quiz","001"]),
    ("CG D8 · Oncologia Cirúrgica        — quiz 002", ["--area","cirurgia_geral","--cg-dominio","8","--quiz","002"]),
    ("CG D9 · Cirurgia Minimamente Inv.  — quiz 001", ["--area","cirurgia_geral","--cg-dominio","9","--quiz","001"]),
    ("CG D9 · Cirurgia Minimamente Inv.  — quiz 002", ["--area","cirurgia_geral","--cg-dominio","9","--quiz","002"]),

    # ── GINECOLOGIA & OBSTETRÍCIA ────────────────────────────────────────────
    ("GO · Pré-Natal                     — quiz 001", ["--area","gineco_obstetricia","--dominio","pre_natal","--quiz","001"]),
    ("GO · Pré-Natal                     — quiz 002", ["--area","gineco_obstetricia","--dominio","pre_natal","--quiz","002"]),
    ("GO · Parto Normal                  — quiz 001", ["--area","gineco_obstetricia","--dominio","parto_normal","--quiz","001"]),
    ("GO · Parto Normal                  — quiz 002", ["--area","gineco_obstetricia","--dominio","parto_normal","--quiz","002"]),
    ("GO · Complicações Obstétricas      — quiz 001", ["--area","gineco_obstetricia","--dominio","complicacoes_obstetricas","--quiz","001"]),
    ("GO · Complicações Obstétricas      — quiz 002", ["--area","gineco_obstetricia","--dominio","complicacoes_obstetricas","--quiz","002"]),
    ("GO · Puerpério e Aleitamento       — quiz 001", ["--area","gineco_obstetricia","--dominio","puerperio_aleitamento","--quiz","001"]),
    ("GO · Puerpério e Aleitamento       — quiz 002", ["--area","gineco_obstetricia","--dominio","puerperio_aleitamento","--quiz","002"]),
    ("GO · Ginecologia Geral             — quiz 001", ["--area","gineco_obstetricia","--dominio","ginecologia_geral","--quiz","001"]),
    ("GO · Ginecologia Geral             — quiz 002", ["--area","gineco_obstetricia","--dominio","ginecologia_geral","--quiz","002"]),
    ("GO · Infecções Genitais e DSTs     — quiz 001", ["--area","gineco_obstetricia","--dominio","infeccoes_genitais_dsts","--quiz","001"]),
    ("GO · Infecções Genitais e DSTs     — quiz 002", ["--area","gineco_obstetricia","--dominio","infeccoes_genitais_dsts","--quiz","002"]),
    ("GO · Doenças Uterinas e Anexiais   — quiz 001", ["--area","gineco_obstetricia","--dominio","doencas_uterinas_anexiais","--quiz","001"]),
    ("GO · Doenças Uterinas e Anexiais   — quiz 002", ["--area","gineco_obstetricia","--dominio","doencas_uterinas_anexiais","--quiz","002"]),
    ("GO · Câncer Ginecológico           — quiz 001", ["--area","gineco_obstetricia","--dominio","cancer_ginecologico","--quiz","001"]),
    ("GO · Câncer Ginecológico           — quiz 002", ["--area","gineco_obstetricia","--dominio","cancer_ginecologico","--quiz","002"]),
    ("GO · Uroginecologia e Piso Pélvico — quiz 001", ["--area","gineco_obstetricia","--dominio","uroginecologia_piso_pelvico","--quiz","001"]),
    ("GO · Uroginecologia e Piso Pélvico — quiz 002", ["--area","gineco_obstetricia","--dominio","uroginecologia_piso_pelvico","--quiz","002"]),

    # ── CLÍNICA MÉDICA ───────────────────────────────────────────────────────
    ("CM · Cardiologia                   — quiz 001", ["--area","clinica_medica","--dominio","cardiologia","--quiz","001"]),
    ("CM · Cardiologia                   — quiz 002", ["--area","clinica_medica","--dominio","cardiologia","--quiz","002"]),
    ("CM · Pneumologia                   — quiz 001", ["--area","clinica_medica","--dominio","pneumologia","--quiz","001"]),
    ("CM · Pneumologia                   — quiz 002", ["--area","clinica_medica","--dominio","pneumologia","--quiz","002"]),
    ("CM · Gastroenterologia             — quiz 001", ["--area","clinica_medica","--dominio","gastroenterologia","--quiz","001"]),
    ("CM · Gastroenterologia             — quiz 002", ["--area","clinica_medica","--dominio","gastroenterologia","--quiz","002"]),
    ("CM · Nefrologia                    — quiz 001", ["--area","clinica_medica","--dominio","nefrologia","--quiz","001"]),
    ("CM · Nefrologia                    — quiz 002", ["--area","clinica_medica","--dominio","nefrologia","--quiz","002"]),
    ("CM · Endocrinologia                — quiz 001", ["--area","clinica_medica","--dominio","endocrinologia","--quiz","001"]),
    ("CM · Endocrinologia                — quiz 002", ["--area","clinica_medica","--dominio","endocrinologia","--quiz","002"]),
    ("CM · Hematologia                   — quiz 001", ["--area","clinica_medica","--dominio","hematologia","--quiz","001"]),
    ("CM · Hematologia                   — quiz 002", ["--area","clinica_medica","--dominio","hematologia","--quiz","002"]),
    ("CM · Reumatologia                  — quiz 001", ["--area","clinica_medica","--dominio","reumatologia","--quiz","001"]),
    ("CM · Reumatologia                  — quiz 002", ["--area","clinica_medica","--dominio","reumatologia","--quiz","002"]),
    ("CM · Infectologia                  — quiz 001", ["--area","clinica_medica","--dominio","infectologia","--quiz","001"]),
    ("CM · Infectologia                  — quiz 002", ["--area","clinica_medica","--dominio","infectologia","--quiz","002"]),
    ("CM · Neurologia                    — quiz 001", ["--area","clinica_medica","--dominio","neurologia","--quiz","001"]),
    ("CM · Neurologia                    — quiz 002", ["--area","clinica_medica","--dominio","neurologia","--quiz","002"]),

    # ── PEDIATRIA ────────────────────────────────────────────────────────────
    ("PED · Neonatologia                 — quiz 001", ["--area","pediatria","--dominio","neonatologia","--quiz","001"]),
    ("PED · Neonatologia                 — quiz 002", ["--area","pediatria","--dominio","neonatologia","--quiz","002"]),
    ("PED · Puericultura                 — quiz 001", ["--area","pediatria","--dominio","puericultura","--quiz","001"]),
    ("PED · Puericultura                 — quiz 002", ["--area","pediatria","--dominio","puericultura","--quiz","002"]),
    ("PED · Pneumologia Pediátrica       — quiz 001", ["--area","pediatria","--dominio","pneumologia_ped","--quiz","001"]),
    ("PED · Pneumologia Pediátrica       — quiz 002", ["--area","pediatria","--dominio","pneumologia_ped","--quiz","002"]),
    ("PED · Cardiologia Pediátrica       — quiz 001", ["--area","pediatria","--dominio","cardio_ped","--quiz","001"]),
    ("PED · Cardiologia Pediátrica       — quiz 002", ["--area","pediatria","--dominio","cardio_ped","--quiz","002"]),
    ("PED · Gastroenterologia Pediátrica — quiz 001", ["--area","pediatria","--dominio","gastro_ped","--quiz","001"]),
    ("PED · Gastroenterologia Pediátrica — quiz 002", ["--area","pediatria","--dominio","gastro_ped","--quiz","002"]),
    ("PED · Infectologia Pediátrica      — quiz 001", ["--area","pediatria","--dominio","infectologia_ped","--quiz","001"]),
    ("PED · Infectologia Pediátrica      — quiz 002", ["--area","pediatria","--dominio","infectologia_ped","--quiz","002"]),
    ("PED · Endocrinologia Pediátrica    — quiz 001", ["--area","pediatria","--dominio","endocrinologia_ped","--quiz","001"]),
    ("PED · Endocrinologia Pediátrica    — quiz 002", ["--area","pediatria","--dominio","endocrinologia_ped","--quiz","002"]),
    ("PED · Hematologia e Oncologia Ped  — quiz 001", ["--area","pediatria","--dominio","hematologia_onco_ped","--quiz","001"]),
    ("PED · Hematologia e Oncologia Ped  — quiz 002", ["--area","pediatria","--dominio","hematologia_onco_ped","--quiz","002"]),
    ("PED · Emergências Pediátricas      — quiz 001", ["--area","pediatria","--dominio","emergencias_ped","--quiz","001"]),
    ("PED · Emergências Pediátricas      — quiz 002", ["--area","pediatria","--dominio","emergencias_ped","--quiz","002"]),

    # ── MEDICINA PREVENTIVA ──────────────────────────────────────────────────
    ("PREV · Epidemiologia Geral         — quiz 001", ["--area","medicina_preventiva","--dominio","epidemiologia_geral","--quiz","001"]),
    ("PREV · Epidemiologia Geral         — quiz 002", ["--area","medicina_preventiva","--dominio","epidemiologia_geral","--quiz","002"]),
    ("PREV · Vigilância Epidemiológica   — quiz 001", ["--area","medicina_preventiva","--dominio","vigilancia_epidemiologica","--quiz","001"]),
    ("PREV · Vigilância Epidemiológica   — quiz 002", ["--area","medicina_preventiva","--dominio","vigilancia_epidemiologica","--quiz","002"]),
    ("PREV · Imunização e PNI            — quiz 001", ["--area","medicina_preventiva","--dominio","imunizacao_pni","--quiz","001"]),
    ("PREV · Imunização e PNI            — quiz 002", ["--area","medicina_preventiva","--dominio","imunizacao_pni","--quiz","002"]),
    ("PREV · Bioestatística              — quiz 001", ["--area","medicina_preventiva","--dominio","bioestatistica","--quiz","001"]),
    ("PREV · Bioestatística              — quiz 002", ["--area","medicina_preventiva","--dominio","bioestatistica","--quiz","002"]),
    ("PREV · Saúde da Família e APS      — quiz 001", ["--area","medicina_preventiva","--dominio","saude_familia_aps","--quiz","001"]),
    ("PREV · Saúde da Família e APS      — quiz 002", ["--area","medicina_preventiva","--dominio","saude_familia_aps","--quiz","002"]),
    ("PREV · Política Nacional e SUS     — quiz 001", ["--area","medicina_preventiva","--dominio","politica_nacional_sus","--quiz","001"]),
    ("PREV · Política Nacional e SUS     — quiz 002", ["--area","medicina_preventiva","--dominio","politica_nacional_sus","--quiz","002"]),
    ("PREV · Saúde Ambiental e Ocup.     — quiz 001", ["--area","medicina_preventiva","--dominio","saude_ambiental_ocupacional","--quiz","001"]),
    ("PREV · Saúde Ambiental e Ocup.     — quiz 002", ["--area","medicina_preventiva","--dominio","saude_ambiental_ocupacional","--quiz","002"]),
    ("PREV · DCNT e Promoção da Saúde    — quiz 001", ["--area","medicina_preventiva","--dominio","dcnt_promocao_saude","--quiz","001"]),
    ("PREV · DCNT e Promoção da Saúde    — quiz 002", ["--area","medicina_preventiva","--dominio","dcnt_promocao_saude","--quiz","002"]),
    ("PREV · Bioética e Ética Médica     — quiz 001", ["--area","medicina_preventiva","--dominio","bioetica_etica_medica","--quiz","001"]),
    ("PREV · Bioética e Ética Médica     — quiz 002", ["--area","medicina_preventiva","--dominio","bioetica_etica_medica","--quiz","002"]),
]

TOTAL = len(SEQUENCIA)

def separador(label, idx):
    print(f"\n{'─'*64}")
    print(f"  [{idx:02d}/{TOTAL}]  {label}")
    print(f"{'─'*64}")

def perguntar(proximo_label, idx):
    print(f"\n  Próximo: [{idx+1:02d}/{TOTAL}]  {proximo_label}")
    while True:
        resp = input("  Continuar? (s = sim / n = parar agora): ").strip().lower()
        if resp in ("s", "sim", "y", "yes", ""):
            return True
        if resp in ("n", "nao", "não", "no"):
            return False

def main():
    print(f"\n{'='*64}")
    print(f"  nexor_med — Orquestrador de Resumos Analíticos")
    print(f"  Total de lotes: {TOTAL}")
    print(f"{'='*64}")
    print(f"\n  Pressione ENTER para iniciar o primeiro domínio.")
    input("  >> ")

    for i, (label, args) in enumerate(SEQUENCIA, 1):
        separador(label, i)
        cmd = [PYTHON, str(SCRIPT)] + args
        result = subprocess.run(cmd, cwd=str(SCRIPT.parent))

        if result.returncode != 0:
            print(f"\n  AVISO: o script retornou código {result.returncode}.")

        if i < TOTAL:
            proxima_label = SEQUENCIA[i][0]
            if not perguntar(proxima_label, i):
                print(f"\n  Interrompido após [{i:02d}/{TOTAL}] {label}")
                print(f"  Para retomar, rode novamente — o progresso está salvo.\n")
                break
        else:
            print(f"\n{'='*64}")
            print(f"  TODOS OS {TOTAL} DOMÍNIOS CONCLUÍDOS!")
            print(f"  Resumos em: prototipo-med/content/resumos/")
            print(f"{'='*64}\n")


if __name__ == "__main__":
    main()
