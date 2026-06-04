"""
gerar_s1d06.py — Gera mini-app corruption_bribery (S1D06)
Copia o gerar_mini_apps_cfe.py e adiciona S1D06 na lista,
depois gera apenas esse domínio.
"""
import json, base64, os, re
from pathlib import Path

# Lê o gerador original
src = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe.py")
content = src.read_text(encoding="utf-8")

# Adiciona S1D06 na lista DOMAINS
old = '{"id":"s1d07"'
new = '{"id":"s1d06","key":"corruption_bribery","code":"S1D06","name":"Corruption & Bribery Schemes","section":1,"badge_name":"Corruption Specialist"},\n    {"id":"s1d07"'

if old not in content:
    print("ERRO: padrão não encontrado no gerador")
    exit(1)

content = content.replace(old, new)

# Salva versão modificada
dest = Path(r"C:\ARAGORN\aragorn_quiz\gerar_mini_apps_cfe_s1d06.py")
dest.write_text(content, encoding="utf-8")
print(f"Script gerado: {dest}")
print("Agora rode: python gerar_mini_apps_cfe_s1d06.py")
