f = open('static/index.html', encoding='utf-8')
html = f.read()
f.close()

old = 'const utt = new SpeechSynthesisUtterance(text);'

new = (
    'const utt = new SpeechSynthesisUtterance(text);'
    ' utt.rate=0.87; utt.pitch=1.08; utt.volume=1.0;'
    ' const voices=window.speechSynthesis.getVoices();'
    ' const preferred=voices.find(v=>v.lang==="en-US"&&v.name.includes("Google"))'
    '||voices.find(v=>v.lang==="en-US")||voices[0];'
    ' if(preferred)utt.voice=preferred;'
)

if old in html:
    html = html.replace(old, new)
    open('static/index.html', 'w', encoding='utf-8').write(html)
    print('OK — TTS corrigido')
else:
    print('ERRO — trecho nao encontrado')
