import json

for key in ['data_theft_ip', 'identity_theft_cyberfraud']:
    print(f'\n=== {key} ===')
    for lang in ['en', 'pt', 'es']:
        f = f'static/flashcards/cfe/{key}/flashcards_{lang}.json'
        data = json.load(open(f, encoding='utf-8'))
        cards = data.get('cards', [])
        print(f'  {lang}: {len(cards)} cards')
        for i, c in enumerate(cards):
            if 'front' not in c:
                print(f'    FALTA front: card[{i}] keys={list(c.keys())}')
            elif 'back' not in c:
                print(f'    FALTA back: card[{i}] keys={list(c.keys())}')
            elif not isinstance(c['front'], dict):
                print(f'    front nao eh dict: card[{i}] front={repr(c["front"])[:80]}')
