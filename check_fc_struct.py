import json
from pathlib import Path

for dom in ['data_theft_ip', 'identity_theft_cyberfraud']:
    for lang in ['en', 'pt', 'es']:
        p = Path(f'static/flashcards/cfe/{dom}/flashcards_{lang}.json')
        d = json.load(open(p, encoding='utf-8'))
        card = d['cards'][0]
        print(f"{dom}/{lang}: keys={list(card.keys())} front={type(card.get('front')).__name__}")
        if isinstance(card.get('front'), dict):
            print(f"  front keys: {list(card['front'].keys())}")
        else:
            print(f"  front value: {repr(card.get('front'))[:80]}")
