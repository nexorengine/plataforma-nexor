import json

for key in ['data_theft_ip', 'identity_theft_cyberfraud']:
    f = f'static/flashcards/cfe/{key}/flashcards_en.json'
    data = json.load(open(f, encoding='utf-8'))
    cards = data.get('cards', [])
    print(f'\n=== {key} — total cards: {len(cards)} ===')
    if cards:
        c = cards[0]
        print(f'  keys do card[0]: {list(c.keys())}')
        print(f'  front type: {type(c.get("front"))}')
        print(f'  front value: {repr(c.get("front"))[:120]}')
        print(f'  back type:   {type(c.get("back"))}')
        print(f'  back value:  {repr(c.get("back"))[:120]}')
    # Compara com um domínio que funciona
    
f2 = 'static/flashcards/cfe/tax_fraud/flashcards_en.json'
data2 = json.load(open(f2, encoding='utf-8'))
cards2 = data2.get('cards', [])
print(f'\n=== tax_fraud (referência OK) — total cards: {len(cards2)} ===')
if cards2:
    c2 = cards2[0]
    print(f'  keys do card[0]: {list(c2.keys())}')
    print(f'  front type: {type(c2.get("front"))}')
    print(f'  front value: {repr(c2.get("front"))[:120]}')
