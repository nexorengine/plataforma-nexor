import copy, sys

with open('gerar_mini_apps_cfe.py', encoding='utf-8') as f:
    src = f.read()

marker = 'if __name__ == "__main__":'
idx = src.index(marker)

novo = '''if __name__ == "__main__":
    import sys, copy as _cp
    lote_num = None
    if "--lote" in sys.argv:
        i = sys.argv.index("--lote")
        lote_num = int(sys.argv[i + 1])
    todos = _cp.deepcopy(DOMAINS)
    LOTE_SIZE = 10
    if lote_num is not None:
        inicio = (lote_num - 1) * LOTE_SIZE
        fim = inicio + LOTE_SIZE
        subset = todos[inicio:fim]
    else:
        subset = todos
    del DOMAINS[:]
    DOMAINS.extend(subset)
    main()
'''

src = src[:idx] + novo
with open('gerar_mini_apps_cfe.py', 'w', encoding='utf-8') as f:
    f.write(src)
print('PATCH OK')
