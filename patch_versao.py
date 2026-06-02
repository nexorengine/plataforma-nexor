#!/usr/bin/env python3
# PATCH - Adiciona version e last_updated no catálogo
# Execute em: C:\NEXOR\nexor_quiz\

from pathlib import Path

f = Path("server.py")
c = f.read_text(encoding="utf-8")

# Mapeamento de versões e datas por certificação
versions = {
    '"id": "cissp"':          '"version": "CISSP 2024", "last_updated": "2024-04",',
    '"id": "cism"':           '"version": "CISM 2022", "last_updated": "2022-06",',
    '"id": "cciso"':          '"version": "CCISO v3", "last_updated": "2023-01",',
    '"id": "cisa"':           '"version": "CISA 2024", "last_updated": "2024-01",',
    '"id": "iso27001_la"':    '"version": "ISO 27001:2022", "last_updated": "2022-10",',
    '"id": "iso27001_li"':    '"version": "ISO 27001:2022", "last_updated": "2022-10",',
    '"id": "iso27701_li"':    '"version": "ISO 27701:2019", "last_updated": "2019-08",',
    '"id": "iso22301_li"':    '"version": "ISO 22301:2019", "last_updated": "2019-10",',
    '"id": "itil4"':          '"version": "ITIL 4 2023", "last_updated": "2023-03",',
    '"id": "crisc"':          '"version": "CRISC 2023", "last_updated": "2023-06",',
    '"id": "iso27005"':       '"version": "ISO 27005:2022", "last_updated": "2022-10",',
    '"id": "cobit"':          '"version": "COBIT 2019", "last_updated": "2019-11",',
    '"id": "cippe"':          '"version": "CIPP/E 2024", "last_updated": "2024-01",',
    '"id": "cipm"':           '"version": "CIPM 2024", "last_updated": "2024-01",',
    '"id": "cdpse"':          '"version": "CDPSE 2023", "last_updated": "2023-06",',
    '"id": "grcp"':           '"version": "GRCP 2023", "last_updated": "2023-01",',
    '"id": "cfe"':            '"version": "CFE 2024", "last_updated": "2024-01",',
    '"id": "chfi"':           '"version": "CHFI v11", "last_updated": "2023-06",',
    '"id": "gcfa"':           '"version": "GCFA 2024", "last_updated": "2024-01",',
    '"id": "security_plus"':  '"version": "Security+ SY0-701", "last_updated": "2023-11",',
}

count = 0
for id_str, version_str in versions.items():
    # Adiciona version logo após o id, se ainda não existir
    old = id_str + ', "name":'
    new = id_str + ', ' + version_str + ' "name":'
    if old in c and version_str not in c:
        c = c.replace(old, new)
        count += 1

f.write_text(c, encoding="utf-8")
print(f"OK - {count} certificações atualizadas com version e last_updated")

# Agora atualiza o endpoint /api/catalog para expor esses campos
f2 = Path("server.py")
c2 = f2.read_text(encoding="utf-8")

old_catalog = '''        result.append({
            "id": cert["id"],
            "name": cert["name"],
            "icon": cert["icon"],
            "color": cert["color"],
            "exam_minutes": cert["exam_minutes"],
            "exam_questions": cert["exam_questions"],
            "bilingual": cert.get("bilingual", True),
            "domains": domains_info
        })'''

new_catalog = '''        result.append({
            "id": cert["id"],
            "name": cert["name"],
            "icon": cert["icon"],
            "color": cert["color"],
            "exam_minutes": cert["exam_minutes"],
            "exam_questions": cert["exam_questions"],
            "bilingual": cert.get("bilingual", True),
            "version": cert.get("version", ""),
            "last_updated": cert.get("last_updated", ""),
            "domains": domains_info
        })'''

if old_catalog in c2:
    c2 = c2.replace(old_catalog, new_catalog)
    f2.write_text(c2, encoding="utf-8")
    print("OK - endpoint /api/catalog expõe version e last_updated")
else:
    print("AVISO - bloco catalog não encontrado, verificar manualmente")

print("\nPATCH VERSÃO CONCLUÍDO!")
print("Reinicie o servidor e faça Ctrl+Shift+R no navegador.")
