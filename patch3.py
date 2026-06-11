with open('gerar_mini_apps_cfe.py', encoding='utf-8') as f:
    src = f.read()

src = src.replace('print(f"  OK \\u2192 {out_path} ({len(html):,} chars)")', 'print(f"  OK -> {out_path} ({len(html):,} chars)")')

with open('gerar_mini_apps_cfe.py', 'w', encoding='utf-8') as f:
    f.write(src)
print('PATCH OK')
