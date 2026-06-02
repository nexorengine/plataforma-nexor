f = open('static/index.html', encoding='utf-8')
html = f.read()
f.close()

old = (
    'const preferred=voices.find(v=>v.lang==="en-US"&&v.name.includes("Google"))'
    '||voices.find(v=>v.lang==="en-US")||voices[0];'
    ' if(preferred)utt.voice=preferred;'
)

new = (
    'const preferred='
    'voices.find(v=>v.lang===lang&&v.name.includes("Google"))'
    '||voices.find(v=>v.lang===lang)'
    '||voices.find(v=>v.lang.startsWith(lang.split("-")[0]))'
    '||voices[0];'
    ' if(preferred)utt.voice=preferred;'
    ' utt.lang=lang;'
)

if old in html:
    html = html.replace(old, new)
    open('static/index.html', 'w', encoding='utf-8').write(html)
    print('OK — deteccao de idioma corrigida')
else:
    print('ERRO — trecho nao encontrado')
    # Mostra o trecho atual para diagnostico
    idx = html.find('const preferred=')
    if idx >= 0:
        print('Trecho atual encontrado:')
        print(repr(html[idx:idx+200]))
