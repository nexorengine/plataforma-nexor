import json

with open(r'C:\ARAGORN\aragorn_quiz\static\flashcards\med\cirurgia_geral\flashcards_pt.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {data['total']} cards\n")
for card in data['flashcards'][:8]:
    print(f"{card['id']} [{card['camada']}]")
    print(f"  F: {card['frente']}")
    print(f"  V: {card['verso']}")
    print()
