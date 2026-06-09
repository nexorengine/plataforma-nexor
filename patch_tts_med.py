import os

path = r'C:\ARAGORN\aragorn_quiz\scripts_med\gerar_nexor_med_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adiciona variavel TTS e funcoes no bloco JS (antes do fechamento do script)
tts_js = """
var _ttsOn=false,_ttsBtn=null;
function ttsStop(){if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}_ttsBtn=null;}
function ttsTxt(txt,btn){if(_ttsOn){ttsStop();return;}if(!window.speechSynthesis||!txt)return;try{_ttsOn=true;_ttsBtn=btn||null;if(btn){btn.innerHTML='&#9209;';btn.classList.add('playing');}var u=new SpeechSynthesisUtterance(txt);u.lang='pt-BR';u.onend=u.onerror=function(){ttsStop();};window.speechSynthesis.speak(u);}catch(e){ttsStop();}}
function ttsQ(btn){var qq=document.getElementById('qq');var qo=document.getElementById('qo');if(!qq)return;var txt=qq.textContent+'. '+Array.from(qo.querySelectorAll('.opt-text')).map(function(o){return o.textContent;}).join('. ');ttsTxt(txt,btn);}
function ttsFc(btn){var front=document.getElementById('fc-front-text');var back=document.getElementById('fc-back-text');var txt=(front&&back)?front.textContent+'. '+back.textContent:(front?front.textContent:'');ttsTxt(txt,btn);}
"""

# 2. Injeta TTS JS antes do fechamento </script>
old_script_end = '</script>\n</body>'
new_script_end = tts_js + '\n</script>\n</body>'
content = content.replace(old_script_end, new_script_end)

# 3. Adiciona botao TTS na pergunta do quiz
old_qq = '<div class="quiz-q" id="qq"></div>'
new_qq = '<div style="display:flex;align-items:center;gap:6px;"><div class="quiz-q" id="qq" style="flex:1"></div><button class="tts-btn" onclick="ttsQ(this)" title="Ouvir pergunta">&#128266;</button></div>'
content = content.replace(old_qq, new_qq)

# 4. Adiciona botao TTS no feedback correto
old_fbc = '<div class="fb-correct" id="fbc"></div>'
new_fbc = '<div style="display:flex;align-items:center;gap:6px;"><div class="fb-correct" id="fbc" style="flex:1"></div><button class="tts-btn" onclick="ttsTxt(document.getElementById(\'fbc\').textContent,this)" title="Ouvir justificativa">&#128266;</button></div>'
content = content.replace(old_fbc, new_fbc)

# 5. Adiciona botao TTS no feedback errado
old_fbw = '<div class="fb-wrong" id="fbw"></div>'
new_fbw = '<div style="display:flex;align-items:center;gap:6px;"><div class="fb-wrong" id="fbw" style="flex:1"></div><button class="tts-btn" onclick="ttsTxt(document.getElementById(\'fbw\').textContent,this)" title="Ouvir distractors">&#128266;</button></div>'
content = content.replace(old_fbw, new_fbw)

# 6. Adiciona CSS do botao TTS
old_css_end = ':root{--accent:#8b1a1a;--accent2:#8b1a1add;}'
new_css = '.tts-btn{background:transparent;border:none;font-size:14px;padding:4px 6px;color:#d4a017;opacity:.7;flex-shrink:0;touch-action:manipulation;min-width:28px;min-height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;}.tts-btn.playing{opacity:1;color:#c0392b;}\n'
content = content.replace(old_css_end, new_css + old_css_end)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# Verifica substituicoes
print('ttsStop:', content.count('ttsStop'))
print('tts-btn CSS:', content.count('tts-btn'))
print('ttsQ:', content.count('ttsQ'))
print('OK')