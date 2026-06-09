import os, json

BASE_DIR = r"C:\ARAGORN\aragorn_quiz\flashcards\cfe"

LAYERS_PT = {"F1": "Definição", "F2": "Distinção", "F3": "Aplicação", "F4": "Síntese"}
LAYERS_EN = {"F1": "Definition", "F2": "Distinction", "F3": "Application", "F4": "Synthesis"}

def load_json_safe(path):
    # tenta UTF-8 primeiro, depois cp1252
    for enc in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
            data = json.loads(content)
            return data, enc
        except Exception:
            continue
    raise Exception(f"Nao foi possivel ler: {path}")

def save_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
            data, enc_used = load_json_safe(path)

            # corrige layers
            data["layers"] = LAYERS_PT if lang == "pt" else LAYERS_EN

            # corrige domain_name
            code = data.get("domain_code", "")
            did = data.get("domain_id", "")
            name_clean = did.replace("_", " ").title()
            if code:
                data["domain_name"] = f"{code} · {name_clean}"
            else:
                data["domain_name"] = name_clean

            save_json(path, data)
            print(f"  OK  {domain} [{lang}] enc={enc_used} -> {data['domain_name']}")
            fixed += 1
        except Exception as e:
            print(f"  ERRO {domain} [{lang}]: {e}")
            errors += 1

print(f"\nConcluido: {fixed} arquivos corrigidos, {errors} erros.")
