#!/usr/bin/env python3
# PATCH NEXOR - Adiciona suporte ao Espanhol (ES)
# Coloque este arquivo em C:\NEXOR\nexor_quiz\ e execute:
# python patch_nexor.py

import shutil
from pathlib import Path

SERVER = Path("server.py")
BACKUP = Path("server.py.backup2")

# Backup
shutil.copy(SERVER, BACKUP)
print(f"Backup criado: {BACKUP}")

content = SERVER.read_text(encoding="utf-8")

# PATCH 1: Adicionar "es" na lista de idiomas
old_langs = 'langs = ["pt", "en"] if bilingual else ["pt"]'
new_langs = 'langs = ["pt", "en", "es"] if bilingual else ["pt"]'

if old_langs in content:
    content = content.replace(old_langs, new_langs)
    print("PATCH 1 OK: idioma ES adicionado")
else:
    print("PATCH 1 ERRO: linha de langs nao encontrada")

# PATCH 2: Adicionar prompt em espanhol no make_prompt
old_end = '''    else:
        return f"""You are a senior certification examiner for {cert_name}.
Domain: {domain_context}

Generate exactly {count} multiple choice questions (Q{start} to Q{end}) for Quiz #{quiz_num}. Focus: {fase} topics.

Rules: senior certification level, exactly 4 options per question, technical justifications with normative references. ALL in ENGLISH.

Return ONLY valid JSON, no markdown. Justifications max 80 words:
{{"questions":[{{"num":{start},"text":"QUESTION","tag":"SUBTOPIC","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"correct justification.","justification_wrong":"wrong justification."}}]}}

Generate exactly {count} questions from {start} to {end}. correct = index 0-3."""'''

new_end = '''    elif lang == "en":
        return f"""You are a senior certification examiner for {cert_name}.
Domain: {domain_context}

Generate exactly {count} multiple choice questions (Q{start} to Q{end}) for Quiz #{quiz_num}. Focus: {fase} topics.

Rules: senior certification level, exactly 4 options per question, technical justifications with normative references. ALL in ENGLISH.

Return ONLY valid JSON, no markdown. Justifications max 80 words:
{{"questions":[{{"num":{start},"text":"QUESTION","tag":"SUBTOPIC","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"correct justification.","justification_wrong":"wrong justification."}}]}}

Generate exactly {count} questions from {start} to {end}. correct = index 0-3."""
    else:
        return f"""Usted es un examinador senior de certificacion profesional para {cert_name}.
Dominio: {domain_context}

Genere exactamente {count} preguntas de opcion multiple (P{start} a P{end}) para el Quiz #{quiz_num}. Enfoque: topicos {fase}.

Reglas: nivel senior de certificacion, exactamente 4 alternativas por pregunta, justificaciones tecnicas con referencias normativas precisas. TODO en ESPANOL TECNICO.

Retorne SOLO JSON valido, sin markdown. Justificaciones max 80 palabras:
{{"questions":[{{"num":{start},"text":"PREGUNTA","tag":"SUBTEMA","options":["A. op1","B. op2","C. op3","D. op4"],"correct":0,"justification_correct":"justificacion correcta.","justification_wrong":"justificacion incorrecta."}}]}}

Genere exactamente {count} preguntas de {start} a {end}. correct = indice 0-3."""'''

# PATCH 3: Adicionar "es" no has_lang e catalog
old_has_en = '"has_en": has_lang(cert["id"], dom["id"], n, "en")'
new_has_en = '"has_en": has_lang(cert["id"], dom["id"], n, "en"),\n                    "has_es": has_lang(cert["id"], dom["id"], n, "es")'

if old_end in content:
    content = content.replace(old_end, new_end)
    print("PATCH 2 OK: prompt ES adicionado")
else:
    print("PATCH 2 ERRO: bloco else nao encontrado - verificar manualmente")

if old_has_en in content:
    content = content.replace(old_has_en, new_has_en)
    print("PATCH 3 OK: has_es adicionado ao catalog")
else:
    print("PATCH 3 AVISO: has_en nao encontrado - nao critico")

SERVER.write_text(content, encoding="utf-8")
print("\nPATCH CONCLUIDO!")
print("Reinicie o servidor NEXOR para aplicar as mudancas.")
