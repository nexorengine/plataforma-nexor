import json
from pathlib import Path

fixes = {
    Path(r"quizzes\med\pediatria\puericultura\quiz_001_pt.json"): {
        "easy_add": ["Q01_09","Q01_21","Q01_38"],
        "hard_add": ["Q01_18","Q01_19","Q01_26"],
        "easy_remove": [],
        "hard_remove": []
    },
    Path(r"quizzes\med\pediatria\puericultura\quiz_002_pt.json"): {
        "easy_add": [],
        "hard_add": [],
        "easy_remove": ["Q02_02","Q02_33"],
        "hard_remove": ["Q02_09","Q02_26"]
    },
    Path(r"quizzes\med\pediatria\neonatologia\quiz_001_pt.json"): {
        "easy_add": ["Q01_11","Q01_22","Q01_46"],
        "hard_add": [],
        "easy_remove": [],
        "hard_remove": ["Q01_12","Q01_14","Q01_21","Q01_24","Q01_43"]
    },
    Path(r"quizzes\med\pediatria\neonatologia\quiz_002_pt.json"): {
        "easy_add": ["Q02_03","Q02_08","Q02_20","Q02_29","Q02_37","Q02_45","Q02_48"],
        "hard_add": [],
        "easy_remove": [],
        "hard_remove": ["Q02_04","Q02_07","Q02_11","Q02_13","Q02_17","Q02_19","Q02_23","Q02_30","Q02_33"]
    },
    Path(r"flashcards\med\pediatria\pneumologia_ped\flashcards_pt.json"): {
        "fix_front": {"F3_05": "Formula para peso esperado de 1 a 6 anos?"}
    },
    Path(r"quizzes\med\pediatria\pneumologia_ped\quiz_001_pt.json"): {
        "easy_add": ["Q01_02","Q01_03","Q01_04","Q01_10","Q01_25","Q01_34","Q01_42","Q01_46"],
        "hard_add": [],
        "easy_remove": [],
        "hard_remove": ["Q01_17","Q01_21","Q01_22","Q01_33","Q01_36"]
    },
    Path(r"quizzes\med\pediatria\pneumologia_ped\quiz_002_pt.json"): {
        "easy_add": ["Q02_02","Q02_03","Q02_06","Q02_21","Q02_29","Q02_30","Q02_38"],
        "hard_add": [],
        "easy_remove": [],
        "hard_remove": ["Q02_05","Q02_08","Q02_13","Q02_16","Q02_19","Q02_27","Q02_34","Q02_43"]
    },
}

for path, ops in fixes.items():
    if not path.exists():
        print(f"NAO ENCONTRADO: {path}")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))

    if "fix_front" in ops:
        for card in data.get("cards", []):
            if card["id"] in ops["fix_front"]:
                card["front"] = ops["fix_front"][card["id"]]
    else:
        for q in data.get("questions", []):
            if q["id"] in ops.get("easy_add", []):
                q["difficulty"] = "EASY"
            elif q["id"] in ops.get("hard_add", []):
                q["difficulty"] = "HARD"
            elif q["id"] in ops.get("easy_remove", []):
                q["difficulty"] = "STANDARD"
            elif q["id"] in ops.get("hard_remove", []):
                q["difficulty"] = "STANDARD"

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    dist = {}
    for item in data.get("questions", data.get("cards", [])):
        k = item.get("difficulty", item.get("layer","?"))
        dist[k] = dist.get(k, 0) + 1
    print(f"OK: {path.name} — {dist}")

print("PATCH CONCLUIDO")
