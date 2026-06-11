with open('gerar_mini_apps_cfe.py', encoding='utf-8') as f:
    src = f.read()

old = '        badge_path = badges_dir / badge_fname'
new = '        badge_b64 = ""\n        badge_path = badges_dir / badge_fname'

if old in src:
    src = src.replace(old, new, 1)
    with open('gerar_mini_apps_cfe.py', 'w', encoding='utf-8') as f:
        f.write(src)
    print('PATCH OK')
else:
    print('PATCH FALHOU')
