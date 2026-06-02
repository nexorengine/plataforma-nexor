#!/usr/bin/env python3
# Troca modelo para Haiku - economia de tokens

from pathlib import Path

f = Path("server.py")
c = f.read_text(encoding="utf-8")

old = 'model="claude-sonnet-4-5"'
new = 'model="claude-haiku-4-5-20251001"'

count = c.count(old)
c = c.replace(old, new)
f.write_text(c, encoding="utf-8")
print(f"OK - {count} ocorrencia(s) trocada(s) para Haiku")
