# NEXOR QUIZ ENGINE v3.0
## Sistema de Preparação para Certificações

---

### INSTALAÇÃO — PRIMEIRA VEZ

1. Instale Python 3.10+ em https://www.python.org/downloads/
   - Marque "Add Python to PATH" durante a instalação

2. Copie a pasta `nexor_quiz` para onde preferir (ex: `C:\NEXOR\`)

3. Configure sua API Key da Anthropic:
   - Crie a variável de ambiente `ANTHROPIC_API_KEY` no Windows
   - Ou deixe o start.bat pedir na primeira execução

---

### USO DIÁRIO

**Duplo clique em `start.bat`**

O sistema abre automaticamente no navegador em http://localhost:8765

---

### ESTRUTURA

```
nexor_quiz/
├── start.bat          ← EXECUTAR ESTE
├── server.py          ← Backend FastAPI
├── requirements.txt
└── static/
    ├── index.html     ← Interface
    └── quizzes/       ← Quizzes salvos (JSON)
        ├── cfe/
        │   ├── fraud_investigation/
        │   │   ├── quiz_001.json
        │   │   └── quiz_002.json
        │   └── ...
        └── iso27001_li/
            └── ...
```

---

### CERTIFICAÇÕES INCLUÍDAS

| Certificação | Domínios | Timer |
|---|---|---|
| CFE / ACFE | 4 | Proporcional (500 q / 150 min) |
| ISO 27001 Lead Implementer | 5 | Proporcional (100 q / 180 min) |
| ISO 27001 Lead Auditor | 4 | Proporcional (100 q / 180 min) |

---

### COMO FUNCIONA

- Cada quiz tem **50 questões** geradas por IA no padrão da prova real
- O quiz é **salvo em disco** após geração — não precisa gerar de novo
- Repita o mesmo quiz quantas vezes quiser
- Timer proporcional ao tempo real da prova original
- Aprovação: 70% (padrão PECB/ACFE)
- Feedback técnico denso com referências normativas em cada questão

---

### ADICIONAR NOVA CERTIFICAÇÃO

Edite `server.py` e adicione uma entrada no dicionário `CATALOG` seguindo o padrão existente.

---

### SUPORTE

NEXOR — Sistema de Inteligência Investigativa e Segurança da Informação
