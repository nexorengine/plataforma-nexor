"""
scan_nexor.py
Mapeia todas as ocorrencias de NEXOR no projeto, classificando por risco.

Uso:
    cd C:\\NEXOR\\nexor_quiz
    python scan_nexor.py
"""

import os, re
from pathlib import Path
from datetime import datetime

RAIZ    = Path(".")
REPORT  = f"scan_nexor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
BUSCA   = re.compile(r'nexor', re.IGNORECASE)

# Extensoes a escanear
EXTS = {".py", ".json", ".html", ".bat", ".vbs", ".txt", ".md", ".ini",
        ".cfg", ".env", ".js", ".css", ".bat", ".sh", ".backup"}

# Pastas a ignorar
IGNORAR = {"__pycache__", ".git", "node_modules", "NEXOR_BACKUP"}

# Classificacao de risco por tipo de ocorrencia
def classificar(arq, linha, texto):
    arq_s = str(arq).lower()
    txt_l = texto.strip().lower()

    # Caminho de pasta/arquivo
    if arq_s.endswith((".bat", ".vbs", ".sh")):
        return "MEDIO", "Script de inicializacao — ajustar caminho"
    if "c:\\nexor" in txt_l or "c:/nexor" in txt_l:
        return "MEDIO", "Caminho hardcoded — ajustar se pasta for renomeada"
    # JSON de quiz — conteudo das questoes
    if arq_s.endswith(".json") and "quizzes" in arq_s:
        return "BAIXO", "Conteudo de quiz — improvavel ter NEXOR aqui"
    # HTML frontend
    if arq_s.endswith(".html"):
        return "BAIXO", "Display na UI — seguro renomear"
    # Python — print/comentario/string display
    if arq_s.endswith(".py"):
        if txt_l.strip().startswith("#"):
            return "BAIXO", "Comentario Python — seguro renomear"
        if "print" in txt_l or '"""' in txt_l or "'''" in txt_l:
            return "BAIXO", "String de display — seguro renomear"
        if "path" in txt_l or "dir" in txt_l or "backup" in txt_l:
            return "MEDIO", "Caminho ou diretorio — verificar antes"
        return "BAIXO", "String Python — provavelmente seguro"
    return "BAIXO", "Verificar manualmente"

linhas_rep = []
def L(t=""): linhas_rep.append(t)
def S(): L("=" * 70)
def H(t): S(); L(f"  {t}"); S()

S()
L(f"  NEXOR — SCAN DE OCORRENCIAS 'NEXOR'")
L(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
S(); L()

resultados = []  # (risco, arq, linha_num, texto)

for arq in sorted(RAIZ.rglob("*")):
    # Ignora pastas bloqueadas
    if any(ig in arq.parts for ig in IGNORAR):
        continue
    # Ignora diretorios
    if arq.is_dir():
        continue
    # Checa nome do arquivo
    if BUSCA.search(arq.name):
        risco, motivo = "MEDIO", "Nome do arquivo contem NEXOR"
        resultados.append((risco, arq, 0, f"[NOME DO ARQUIVO] {arq.name}", motivo))
    # Checa extensao
    if arq.suffix.lower() not in EXTS:
        continue
    # Le conteudo
    try:
        texto = arq.read_text(encoding="utf-8", errors="ignore")
    except:
        continue
    for i, linha in enumerate(texto.splitlines(), 1):
        if BUSCA.search(linha):
            risco, motivo = classificar(arq, i, linha)
            resultados.append((risco, arq, i, linha.strip(), motivo))

# Agrupa por risco
medio  = [r for r in resultados if r[0] == "MEDIO"]
baixo  = [r for r in resultados if r[0] == "BAIXO"]

H(f"RISCO MEDIO — verificar antes de renomear ({len(medio)} ocorrencias)")
arq_atual = None
for risco, arq, lnum, texto, motivo in medio:
    if arq != arq_atual:
        L(f"\n  ARQUIVO: {arq}")
        arq_atual = arq
    if lnum == 0:
        L(f"    [NOME]  {motivo}")
    else:
        L(f"    L{lnum:04d} [{motivo}]")
        L(f"           {texto[:100]}")

L()
H(f"RISCO BAIXO — seguro renomear ({len(baixo)} ocorrencias)")
arq_atual = None
for risco, arq, lnum, texto, motivo in baixo:
    if arq != arq_atual:
        L(f"\n  ARQUIVO: {arq}")
        arq_atual = arq
    if lnum == 0:
        L(f"    [NOME]  {motivo}")
    else:
        L(f"    L{lnum:04d} [{motivo}]")
        L(f"           {texto[:100]}")

L()
S()
L(f"  RESUMO")
S()
L(f"  Ocorrencias MEDIO : {len(medio)}")
L(f"  Ocorrencias BAIXO : {len(baixo)}")
L(f"  TOTAL             : {len(resultados)}")
L()

# Lista arquivos unicos com risco medio
arqs_medio = sorted(set(str(r[1]) for r in medio))
if arqs_medio:
    L(f"  Arquivos com risco MEDIO ({len(arqs_medio)}):")
    for a in arqs_medio:
        L(f"    {a}")
L()
S()
L(f"  Relatorio: {REPORT}")
S()

Path(REPORT).write_text("\n".join(linhas_rep), encoding="utf-8")
print("\n".join(linhas_rep))
