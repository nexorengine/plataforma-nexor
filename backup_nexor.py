"""
backup_nexor.py
Backup completo do NEXOR/NEXOR Quiz Engine para D:\\NEXOR_BACKUP

Uso:
    cd C:\\NEXOR\\nexor_quiz
    python backup_nexor.py
"""

import shutil, os
from pathlib import Path
from datetime import datetime

ORIGEM  = Path(".")
DESTINO = Path("D:/NEXOR_BACKUP")

def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    dest  = DESTINO / f"backup_{stamp}"
    dest.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print(f"  BACKUP {stamp}")
    print("=" * 50)
    print(f"  Destino: {dest}")
    print()

    total_arq   = 0
    total_bytes = 0

    # 1. Quizzes
    src = ORIGEM / "static" / "quizzes"
    dst = dest / "static" / "quizzes"
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        arqs = [a for a in src.rglob("*") if a.is_file()]
        n = len(arqs)
        b = sum(a.stat().st_size for a in arqs)
        total_arq += n; total_bytes += b
        print(f"  OK - static/quizzes/ ({n} arquivos, {b/1024/1024:.1f} MB)")

    # 2. index.html
    for f in ["static/index.html", "static/index.html.backup"]:
        src = ORIGEM / f
        if src.exists():
            dst = dest / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            b = src.stat().st_size
            total_arq += 1; total_bytes += b
            print(f"  OK - {f} ({b/1024:.1f} KB)")

    # 3. Todos os .py da raiz
    scripts_dest = dest / "scripts"
    scripts_dest.mkdir(exist_ok=True)
    for s in sorted(ORIGEM.glob("*.py")):
        shutil.copy2(s, scripts_dest / s.name)
        b = s.stat().st_size
        total_arq += 1; total_bytes += b
    print(f"  OK - scripts Python ({len(list(ORIGEM.glob('*.py')))} arquivos)")

    # 4. server.py e backups
    for f in ["server.py", "server.py.backup", "server.py.backup2"]:
        src = ORIGEM / f
        if src.exists():
            shutil.copy2(src, dest / f)
            b = src.stat().st_size
            total_arq += 1; total_bytes += b
            print(f"  OK - {f} ({b/1024:.1f} KB)")

    # 5. Arquivos de configuracao e misc
    for f in ["requirements.txt", "README.md", "nexor_server.bat",
              "start.bat", "criar_atalhos.vbs", "nexor_quiz.ico",
              "nexor_server.ico"]:
        src = ORIGEM / f
        if src.exists():
            shutil.copy2(src, dest / f)
            b = src.stat().st_size
            total_arq += 1; total_bytes += b
            print(f"  OK - {f} ({b/1024:.1f} KB)")

    print()
    print("=" * 50)
    print(f"  BACKUP CONCLUIDO!")
    print(f"  Arquivos : {total_arq}")
    print(f"  Tamanho  : {total_bytes/1024/1024:.1f} MB")
    print(f"  Destino  : {dest}")
    print("=" * 50)

if __name__ == "__main__":
    main()
