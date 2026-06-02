#!/usr/bin/env python3
"""
Troca a tipografia do ARGO/AQUILES de Courier New para Inter
Execute em: C:\\NEXOR\\nexor_quiz\\
"""
import subprocess

# Le o arquivo via WSL
result = subprocess.run(
    ["wsl", "cat", "/home/dell/labs/openclaw/templates/index.html"],
    capture_output=True, text=True, encoding="utf-8"
)
c = result.stdout

if not c:
    print("ERRO - nao foi possivel ler o arquivo")
    exit()

original = c

# Adiciona Google Fonts Inter logo apos o <head>
google_fonts_link = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">'

if "fonts.googleapis.com" not in c:
    c = c.replace("<head>", f"<head>\n{google_fonts_link}")
    print("OK - Google Fonts Inter adicionado")
else:
    print("INFO - Google Fonts ja presente")

# Substitui todas as ocorrencias de Courier New
substituicoes = [
    ("font-family: 'Courier New', monospace", "font-family: 'Inter', sans-serif"),
    ('font-family: "Courier New", monospace', "font-family: 'Inter', sans-serif"),
    ("font-family:Courier New,monospace", "font-family:'Inter',sans-serif"),
    ("font-family: Courier New, monospace", "font-family: 'Inter', sans-serif"),
    ("font-family:Courier New, monospace", "font-family:'Inter',sans-serif"),
]

total = 0
for old, new in substituicoes:
    count = c.count(old)
    if count > 0:
        c = c.replace(old, new)
        total += count
        print(f"OK - {count}x '{old[:40]}' substituido")

if c != original:
    # Salva via WSL
    proc = subprocess.run(
        ["wsl", "bash", "-c", f"cat > /home/dell/labs/openclaw/templates/index.html"],
        input=c, text=True, encoding="utf-8"
    )
    if proc.returncode == 0:
        print(f"\nOK - Arquivo salvo! {total} substituicoes realizadas.")
        print("Reinicia o ARGO e verifica a nova tipografia.")
    else:
        print("ERRO ao salvar o arquivo")
else:
    print("Nenhuma substituicao realizada")
