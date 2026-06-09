path = r'C:\ARAGORN\aragorn_quiz\scripts_med\gerar_nexor_med_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
old = "document.getElementById('fbw').textContent=q.justification_wrong||'';"
new = "const jw=q.justification_wrong;document.getElementById('fbw').textContent=jw?(typeof jw==='object'?Object.entries(jw).map(([k,v])=>k+': '+v).join(' | '):jw):'';"
content = content.replace(old, new)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK:', content.count('typeof jw'))