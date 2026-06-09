import os, json

BASE_DIR = r"C:\ARAGORN\aragorn_quiz\flashcards\cfe"

LAYERS_PT = {"F1": "Definição", "F2": "Distinção", "F3": "Aplicação", "F4": "Síntese"}
LAYERS_EN = {"F1": "Definition", "F2": "Distinction", "F3": "Application", "F4": "Synthesis"}

def fix_domain_name(name):
    # remove codigo do prefixo se corrompido, reescreve limpo
    # ex: "S3D02 Â· Occupational Fraud" -> pega so a parte legivel apos o separador
    if "·" in name:
        return name  # ja ok
    parts = name.split(" ", 1)
    if len(parts) == 2:
        # tenta extrair codigo + nome limpo
        return name  # deixa como esta, sera substituido abaixo
    return name

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# mapa de domain_id -> domain_code + domain_name limpo
# extraido dos proprios arquivos (domain_code esta correto nos JSONs)
fixed = 0
errors = 0

domains = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])

for domain in domains:
    domain_path = os.path.join(BASE_DIR, domain)
    for lang in ["pt", "en"]:
        path = os.path.join(domain_path, f"flashcards_{lang}.json")
        if not os.path.exists(path):
            continue
        try:
            data = load_json(path)

            # corrige layers
            data["layers"] = LAYERS_PT if lang == "pt" else LAYERS_EN

            # corrige domain_name: remove mojibake, reconstroi do domain_code + domain_id
            code = data.get("domain_code", "")
            did = data.get("domain_id", "")
            name_clean = did.replace("_", " ").title()
            if code:
                data["domain_name"] = f"{code} · {name_clean}"
            else:
                data["domain_name"] = name_clean

            save_json(path, data)
            print(f"  OK  {domain} [{lang}] -> {data['domain_name']}")
            fixed += 1
        except Exception as e:
            print(f"  ERRO {domain} [{lang}]: {e}")
            errors += 1

print(f"\nConcluido: {fixed} arquivos corrigidos, {errors} erros.")
