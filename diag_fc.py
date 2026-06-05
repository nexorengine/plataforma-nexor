import json, glob

for key in ['data_theft_ip', 'identity_theft_cyberfraud']:
    files = glob.glob(f'static/flashcards/cfe/{key}/*.json')
    print(f'\n=== {key} ({len(files)} arquivos) ===')
    for f in files:
        try:
            data = json.load(open(f, encoding='utf-8'))
            if isinstance(data, list):
                first = data[0] if data else {}
                print(f'  {f}: lista[{len(data)}], keys={list(first.keys())}')
            elif isinstance(data, dict):
                print(f'  {f}: dict, keys={list(data.keys())}')
        except Exception as e:
            print(f'  {f}: ERRO {e}')
