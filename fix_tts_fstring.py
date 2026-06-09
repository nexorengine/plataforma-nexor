path = r'C:\ARAGORN\aragorn_quiz\scripts_med\gerar_nexor_med_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Escapa as chaves do bloco TTS dentro do f-string
old = """var _ttsOn=false,_ttsBtn=null;
function ttsStop(){if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}_ttsBtn=null;}
function ttsTxt(txt,btn){if(_ttsOn){ttsStop();return;}if(!window.speechSynthesis||!txt)return;try{_ttsOn=true;_ttsBtn=btn||null;if(btn){btn.innerHTML='&#9209;';btn.classList.add('playing');}var u=new SpeechSynthesisUtterance(txt);u.lang='pt-BR';u.onend=u.onerror=function(){ttsStop();};window.speechSynthesis.speak(u);}catch(e){ttsStop();}}
function ttsQ(btn){var qq=document.getElementById('qq');var qo=document.getElementById('qo');if(!qq)return;var txt=qq.textContent+'. '+Array.from(qo.querySelectorAll('.opt-text')).map(function(o){return o.textContent;}).join('. ');ttsTxt(txt,btn);}
function ttsFc(btn){var front=document.getElementById('fc-front-text');var back=document.getElementById('fc-back-text');var txt=(front&&back)?front.textContent+'. '+back.textContent:(front?front.textContent:'');ttsTxt(txt,btn);}"""

new = """var _ttsOn=false,_ttsBtn=null;
function ttsStop(){{if(window.speechSynthesis)window.speechSynthesis.cancel();_ttsOn=false;if(_ttsBtn){{_ttsBtn.innerHTML='&#128266;';_ttsBtn.classList.remove('playing');}}_ttsBtn=null;}}
function ttsTxt(txt,btn){{if(_ttsOn){{ttsStop();return;}}if(!window.speechSynthesis||!txt)return;try{{_ttsOn=true;_ttsBtn=btn||null;if(btn){{btn.innerHTML='&#9209;';btn.classList.add('playing');}}var u=new SpeechSynthesisUtterance(txt);u.lang='pt-BR';u.onend=u.onerror=function(){{ttsStop();}};window.speechSynthesis.speak(u);}}catch(e){{ttsStop();}}}}
function ttsQ(btn){{var qq=document.getElementById('qq');var qo=document.getElementById('qo');if(!qq)return;var txt=qq.textContent+'. '+Array.from(qo.querySelectorAll('.opt-text')).map(function(o){{return o.textContent;}}).join('. ');ttsTxt(txt,btn);}}
function ttsFc(btn){{var front=document.getElementById('fc-front-text');var back=document.getElementById('fc-back-text');var txt=(front&&back)?front.textContent+'. '+back.textContent:(front?front.textContent:'');ttsTxt(txt,btn);}}"""

content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('OK:', content.count('ttsStop'))