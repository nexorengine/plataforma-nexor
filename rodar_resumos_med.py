"""
rodar_resumos_med.py -- Orquestrador automatico de Resumos Analiticos
Roda gerar_resumos_med.py para todos os 90 arquivos (5 areas x 9 dominios x 2 quizzes).
Pula automaticamente os que ja tem 50 resumos. Retoma os incompletos.

Uso:
    python rodar_resumos_med.py           # tudo
    python rodar_resumos_med.py --area go # so GO
    python rodar_resumos_med.py --status  # so mostra o que falta, sem rodar
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path

SCRIPT     = Path(__file__).parent / "gerar_resumos_med.py"
PYTHON     = sys.executable
RESUMOS    = Path(__file__).parent / "prototipo-med" / "content" / "resumos"
META_TOTAL = 50

FILA = [
    ("cirurgia_geral", None, 1, "001", "CG D1 Abdome Agudo q001"),
    ("cirurgia_geral", None, 1, "002", "CG D1 Abdome Agudo q002"),
    ("cirurgia_geral", None, 2, "001", "CG D2 Hepatobiliar q001"),
    ("cirurgia_geral", None, 2, "002", "CG D2 Hepatobiliar q002"),
    ("cirurgia_geral", None, 3, "001", "CG D3 Trauma q001"),
    ("cirurgia_geral", None, 3, "002", "CG D3 Trauma q002"),
    ("cirurgia_geral", None, 4, "001", "CG D4 Perioperatorio q001"),
    ("cirurgia_geral", None, 4, "002", "CG D4 Perioperatorio q002"),
    ("cirurgia_geral", None, 5, "001", "CG D5 Hernias q001"),
    ("cirurgia_geral", None, 5, "002", "CG D5 Hernias q002"),
    ("cirurgia_geral", None, 6, "001", "CG D6 TGI Superior q001"),
    ("cirurgia_geral", None, 6, "002", "CG D6 TGI Superior q002"),
    ("cirurgia_geral", None, 7, "001", "CG D7 TGI Inferior q001"),
    ("cirurgia_geral", None, 7, "002", "CG D7 TGI Inferior q002"),
    ("cirurgia_geral", None, 8, "001", "CG D8 Cirurgia Vascular q001"),
    ("cirurgia_geral", None, 8, "002", "CG D8 Cirurgia Vascular q002"),
    ("cirurgia_geral", None, 9, "001", "CG D9 Queimaduras q001"),
    ("cirurgia_geral", None, 9, "002", "CG D9 Queimaduras q002"),
    ("gineco_obstetricia", "pre_natal",                   None, "001", "GO pre_natal q001"),
    ("gineco_obstetricia", "pre_natal",                   None, "002", "GO pre_natal q002"),
    ("gineco_obstetricia", "parto_normal",                None, "001", "GO parto_normal q001"),
    ("gineco_obstetricia", "parto_normal",                None, "002", "GO parto_normal q002"),
    ("gineco_obstetricia", "puerperio_aleitamento",       None, "001", "GO puerperio q001"),
    ("gineco_obstetricia", "puerperio_aleitamento",       None, "002", "GO puerperio q002"),
    ("gineco_obstetricia", "complicacoes_obstetricas",    None, "001", "GO complicacoes q001"),
    ("gineco_obstetricia", "complicacoes_obstetricas",    None, "002", "GO complicacoes q002"),
    ("gineco_obstetricia", "ginecologia_geral",           None, "001", "GO ginecologia q001"),
    ("gineco_obstetricia", "ginecologia_geral",           None, "002", "GO ginecologia q002"),
    ("gineco_obstetricia", "doencas_uterinas_anexiais",   None, "001", "GO doencas_uterinas q001"),
    ("gineco_obstetricia", "doencas_uterinas_anexiais",   None, "002", "GO doencas_uterinas q002"),
    ("gineco_obstetricia", "infeccoes_genitais_dsts",     None, "001", "GO infeccoes q001"),
    ("gineco_obstetricia", "infeccoes_genitais_dsts",     None, "002", "GO infeccoes q002"),
    ("gineco_obstetricia", "cancer_ginecologico",         None, "001", "GO cancer q001"),
    ("gineco_obstetricia", "cancer_ginecologico",         None, "002", "GO cancer q002"),
    ("gineco_obstetricia", "uroginecologia_piso_pelvico", None, "001", "GO uroginecologia q001"),
    ("gineco_obstetricia", "uroginecologia_piso_pelvico", None, "002", "GO uroginecologia q002"),
    ("clinica_medica", "cardiologia",       None, "001", "CM cardiologia q001"),
    ("clinica_medica", "cardiologia",       None, "002", "CM cardiologia q002"),
    ("clinica_medica", "pneumologia",       None, "001", "CM pneumologia q001"),
    ("clinica_medica", "pneumologia",       None, "002", "CM pneumologia q002"),
    ("clinica_medica", "gastroenterologia", None, "001", "CM gastroenterologia q001"),
    ("clinica_medica", "gastroenterologia", None, "002", "CM gastroenterologia q002"),
    ("clinica_medica", "nefrologia",        None, "001", "CM nefrologia q001"),
    ("clinica_medica", "nefrologia",        None, "002", "CM nefrologia q002"),
    ("clinica_medica", "endocrinologia",    None, "001", "CM endocrinologia q001"),
    ("clinica_medica", "endocrinologia",    None, "002", "CM endocrinologia q002"),
    ("clinica_medica", "hematologia",       None, "001", "CM hematologia q001"),
    ("clinica_medica", "hematologia",       None, "002", "CM hematologia q002"),
    ("clinica_medica", "reumatologia",      None, "001", "CM reumatologia q001"),
    ("clinica_medica", "reumatologia",      None, "002", "CM reumatologia q002"),
    ("clinica_medica", "infectologia",      None, "001", "CM infectologia q001"),
    ("clinica_medica", "infectologia",      None, "002", "CM infectologia q002"),
    ("clinica_medica", "neurologia",        None, "001", "CM neurologia q001"),
    ("clinica_medica", "neurologia",        None, "002", "CM neurologia q002"),
    ("pediatria", "neonatologia",          None, "001", "PED neonatologia q001"),
    ("pediatria", "neonatologia",          None, "002", "PED neonatologia q002"),
    ("pediatria", "puericultura",          None, "001", "PED puericultura q001"),
    ("pediatria", "puericultura",          None, "002", "PED puericultura q002"),
    ("pediatria", "pneumologia_ped",       None, "001", "PED pneumologia q001"),
    ("pediatria", "pneumologia_ped",       None, "002", "PED pneumologia q002"),
    ("pediatria", "gastro_ped",            None, "001", "PED gastro q001"),
    ("pediatria", "gastro_ped",            None, "002", "PED gastro q002"),
    ("pediatria", "infectologia_ped",      None, "001", "PED infectologia q001"),
    ("pediatria", "infectologia_ped",      None, "002", "PED infectologia q002"),
    ("pediatria", "cardio_ped",            None, "001", "PED cardio q001"),
    ("pediatria", "cardio_ped",            None, "002", "PED cardio q002"),
    ("pediatria", "endocrinologia_ped",    None, "001", "PED endocrinologia q001"),
    ("pediatria", "endocrinologia_ped",    None, "002", "PED endocrinologia q002"),
    ("pediatria", "hematologia_onco_ped",  None, "001", "PED hematologia q001"),
    ("pediatria", "hematologia_onco_ped",  None, "002", "PED hematologia q002"),
    ("pediatria", "emergencias_ped",       None, "001", "PED emergencias q001"),
    ("pediatria", "emergencias_ped",       None, "002", "PED emergencias q002"),
    ("medicina_preventiva", "epidemiologia_geral",         None, "001", "PREV epidemiologia q001"),
    ("medicina_preventiva", "epidemiologia_geral",         None, "002", "PREV epidemiologia q002"),
    ("medicina_preventiva", "vigilancia_epidemiologica",   None, "001", "PREV vigilancia q001"),
    ("medicina_preventiva", "vigilancia_epidemiologica",   None, "002", "PREV vigilancia q002"),
    ("medicina_preventiva", "imunizacao_pni",              None, "001", "PREV imunizacao q001"),
    ("medicina_preventiva", "imunizacao_pni",              None, "002", "PREV imunizacao q002"),
    ("medicina_preventiva", "bioestatistica",              None, "001", "PREV bioestatistica q001"),
    ("medicina_preventiva", "bioestatistica",              None, "002", "PREV bioestatistica q002"),
    ("medicina_preventiva", "saude_familia_aps",           None, "001", "PREV saude_familia q001"),
    ("medicina_preventiva", "saude_familia_aps",           None, "002", "PREV saude_familia q002"),
    ("medicina_preventiva", "politica_nacional_sus",       None, "001", "PREV politica_sus q001"),
    ("medicina_preventiva", "politica_nacional_sus",       None, "002", "PREV politica_sus q002"),
    ("medicina_preventiva", "saude_ambiental_ocupacional", None, "001", "PREV saude_ambiental q001"),
    ("medicina_preventiva", "saude_ambiental_ocupacional", None, "002", "PREV saude_ambiental q002"),
    ("medicina_preventiva", "dcnt_promocao_saude",         None, "001", "PREV dcnt q001"),
    ("medicina_preventiva", "dcnt_promocao_saude",         None, "002", "PREV dcnt q002"),
    ("medicina_preventiva", "bioetica_etica_medica",       None, "001", "PREV bioetica q001"),
    ("medicina_preventiva", "bioetica_etica_medica",       None, "002", "PREV bioetica q002"),
]

CG_SLUGS = {
    1: "abdome_agudo", 2: "hepatobiliar_pancreas", 3: "trauma_urgencia",
    4: "perioperatorio", 5: "hernias_parede_abdominal", 6: "trato_digestivo_superior",
    7: "trato_digestivo_inferior_coloproctologia", 8: "cirurgia_vascular", 9: "queimaduras",
}

def slug_de(area, dominio, cg_idx):
    return CG_SLUGS.get(cg_idx, f"d{cg_idx}") if area == "cirurgia_geral" else dominio

def count_resumos(area, slug, quiz):
    path = RESUMOS / area / slug / f"quiz_{quiz}_resumos.json"
    if not path.exists():
        return 0
    try:
        return len(json.loads(path.read_text(encoding="utf-8")).get("resumos", []))
    except:
        return 0

def rodar(area, dominio, cg_idx, quiz):
    cmd = [PYTHON, str(SCRIPT), "--area", area, "--quiz", quiz]
    cmd += ["--cg-dominio", str(cg_idx)] if area == "cirurgia_geral" else ["--dominio", dominio]
    return subprocess.run(cmd, cwd=str(SCRIPT.parent)).returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--area", default="all", help="all | cg | go | cm | ped | prev")
    parser.add_argument("--status", action="store_true", help="So mostra status, nao roda")
    args = parser.parse_args()

    mapa = {"cg":"cirurgia_geral","go":"gineco_obstetricia",
            "cm":"clinica_medica","ped":"pediatria","prev":"medicina_preventiva"}
    area_filtro = mapa.get(args.area.lower())
    fila = [(a,d,ci,q,l) for a,d,ci,q,l in FILA
            if args.area.lower() == "all" or a == area_filtro]

    counts = [(count_resumos(a, slug_de(a,d,ci), q), l) for a,d,ci,q,l in fila]
    completos = sum(1 for n,_ in counts if n >= META_TOTAL)

    print(f"\n{'='*60}")
    print(f"  nexor_med -- Resumos Analiticos (Opus)")
    print(f"  Total: {len(fila)} | Completos: {completos} | Pendentes: {len(fila)-completos}")
    print(f"{'='*60}\n")

    if args.status:
        for (a,d,ci,q,label),(n,_) in zip(fila, counts):
            print(f"  {'OK' if n>=META_TOTAL else f'{n:2d}/50':>5}  {label}")
        return

    rodados = erros = 0
    for i, (a,d,ci,q,label) in enumerate(fila, 1):
        slug = slug_de(a,d,ci)
        n = count_resumos(a, slug, q)
        if n >= META_TOTAL:
            print(f"  [{i:02d}/{len(fila)}] SKIP  {label}")
            continue
        sufixo = f" (retomando {n}/50)" if n > 0 else ""
        print(f"\n  [{i:02d}/{len(fila)}] START {label}{sufixo}")
        rc = rodar(a, d, ci, q)
        if rc != 0:
            print(f"  ERRO exit={rc}")
            erros += 1
        else:
            rodados += 1

    print(f"\n{'='*60}")
    print(f"  Pronto! Rodados: {rodados} | Erros: {erros} | Ja prontos: {completos}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
