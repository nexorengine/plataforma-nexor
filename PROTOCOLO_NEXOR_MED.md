# PROTOCOLO NEXOR MED — Geração de Conteúdo via API
**Documento de continuidade — leia isto no início de qualquer sessão antes de executar qualquer ação.**

Última atualização: 13/06/2026

---

## 1. CONTEXTO DO PROJETO

NEXOR é uma plataforma de certificação e preparação para residência médica
(ENARE/AMRIGS/ACM-SC), fundada por Alexandre Andrade (Agente da Polícia
Federal — NUNCA chamar de "Delegado"). A vertical NEXOR MED produz conteúdo
de estudo (flashcards + quizzes) para as principais áreas médicas avaliadas
em concursos de residência no Brasil.

### O que é FractalLearning™ / FractalFlashcard v1
Metodologia proprietária de flashcards em 4 camadas progressivas por domínio
de conhecimento:

- **F1** — Definição pura, sem exemplos. `front` ≤ 15 palavras, `back` ≤ 25
  palavras.
- **F2** — Distinções / diferenciação entre conceitos relacionados.
- **F3** — Caso clínico + conduta (aplicação prática).
- **F4** — Síntese multi-conceito / fisiopatologia encadeada (integração).

Cada domínio tem **48 flashcards** = 4 camadas × 12 cards.

Regra de calibração (definida pelo filho de Alexandre, estudante de
medicina, validador beta): sem exemplos no F1, limites de palavras
estritos — testados e aprovados como padrão da plataforma inteira.

### Estrutura geral
Cada domínio médico = 1 conjunto de 3 arquivos:
- `{CODIGO}_flashcards_pt.json` — 48 cards
- `{CODIGO}_quiz_001_pt.json` — 50 questões (10 EASY + 20 STANDARD + 20 HARD)
- `{CODIGO}_quiz_002_pt.json` — 50 questões (mesma distribuição, SEM
  repetição de casos/temas do quiz_001)

---

## 2. STATUS ATUAL DO ROADMAP (verificar sempre via git, não confiar em handoff)

| Área | Domínios | Status |
|---|---|---|
| Cirurgia Geral | 9 | ✅ 9/9 completo |
| Clínica Médica (CM) | 9 (Cardiologia, Pneumologia, Gastro/Hepato, Nefrologia, Endocrino, Hematologia, Reumatologia, Infectologia, Neurologia) | ✅ 9/9 completo |
| Pediatria (PED) | 9 (Puericultura, Neonatologia, Pneumo, Gastro, Cardio, Endocrino, Hemato/Onco, Infecto, Emergências) | ✅ 9/9 completo |
| Gineco-Obstetrícia (GO) | 9 | ✅ 9/9 completo |
| Medicina Preventiva e Social (PREV) | 9 | 🟡 4/9 — D01-D04 completos, **D05-D09 pendentes** |

### PREV — domínios definidos
1. ✅ PREV_D01 Epidemiologia Geral
2. ✅ PREV_D02 Vigilância Epidemiológica e Doenças de Notificação
3. ✅ PREV_D03 Imunização e Programa Nacional de Imunizações (PNI)
4. ✅ PREV_D04 Bioestatística Aplicada à Saúde
5. ⬜ PREV_D05 Saúde da Família e Atenção Primária (SUS/ESF)
6. ⬜ PREV_D06 Política Nacional de Saúde / Legislação do SUS
7. ⬜ PREV_D07 Saúde Ambiental e Ocupacional
8. ⬜ PREV_D08 Doenças Crônicas Não Transmissíveis e Promoção da Saúde
9. ⬜ PREV_D09 Bioética e Ética Médica

**SEMPRE confirme o status real rodando:**
```powershell
cd C:\ARAGORN\aragorn_quiz
git log --oneline -- flashcards/med/medicina_preventiva
```
Handoffs escritos podem estar desatualizados. O git log é a fonte da
verdade.

---

## 3. SCHEMA DOS ARQUIVOS

### ⚠️ ATENÇÃO: existem DOIS schemas no repo (legado vs atual)

**Schema ATUAL (usado por gerar_dominio.py, domínios CM_DXX e PREV_DXX):**

Flashcards:
```json
{"dominio":"CM_D01","titulo":"...","especialidade":"Clinica Medica",
 "total_cards":48,"cards":[{"layer":"F1-F4","front":"...","back":"..."}]}
```

Quiz:
```json
{"dominio":"CM_D01","titulo":"...","quiz":"001","total_questoes":50,
 "questoes":[{"id":N,"nivel":"EASY/STANDARD/HARD","pergunta":"...",
 "alternativas":[4 opções],"correct":"...",
 "justification_correct":"...","justification_wrong":"..."}]}
```

**Schema LEGADO (Pediatria, GO — gerado em sessões anteriores ao
gerar_dominio.py):**

Flashcards:
```json
{"domain":"PED_D01","domain_name":"...","total":48 ou null,
 "cards":[{"id":"F1_01","layer":"F1","front":"...","back":"..."}]}
```

Quiz:
```json
{"domain":"PED_D01","domain_name":"...","quiz_number":1,
 "total":50 ou null,
 "questions":[{"id":"Q01_01","question":"...","options":{"A":..,"B":..,
 "C":..,"D":..},"correct":"A/B/C/D","difficulty":"EASY/STANDARD/HARD",
 "justification_correct":"...","justification_wrong":"..."}]}
```

**Não tente "corrigir" o schema legado — ambos são válidos e o
total/total_cards = null não é bug, é só metadado opcional não
preenchido. Validação deve checar AMBOS os schemas.**

Para novos domínios (PREV_D05+), seguir o schema ATUAL (compatível com
gerar_dominio.py).

---

## 4. SCRIPT DE GERAÇÃO — gerar_dominio.py

### Localização
Cópia funcional sempre na última pasta `prev_dXX_gen` ou `cm_dXX_gen`
gerada. Para novo domínio, copiar de uma pasta recente:
```powershell
cd C:\ARAGORN\aragorn_quiz
New-Item -ItemType Directory -Force -Path "prev_d05_gen"
Copy-Item -Force ".\prev_d04_gen\gerar_dominio.py" -Destination ".\prev_d05_gen\"
cd prev_d05_gen
python gerar_dominio.py PREV_D05 "Saude da Familia e Atencao Primaria" "Medicina Preventiva e Social"
```

### Características
- 10 chamadas de API (Claude Sonnet 4.6, model="claude-sonnet-4-6"):
  F1, F2, F3, F4 (12 cards cada) + quiz_001 e quiz_002 em lotes de 10
  (EASY 1x10, STANDARD 2x10, HARD 2x10).
- MAX_TOKENS_QUIZ=16000, timeout 300s, retry 3x (15s/30s/45s).
- **CHECKPOINT incremental**: salva `{CODIGO}_quiz_00X.partial.json`
  após cada lote. Se o script cair (timeout ou JSONDecodeError), rodar
  o MESMO comando de novo retoma do ponto certo.
- **RESUME de arquivos finais**: se `{CODIGO}_flashcards_pt.json` ou
  `{CODIGO}_quiz_00X_pt.json` já existem, pula essa etapa inteira.
- Auto-correção de F1 fora do limite (front≤15, back≤25 palavras).
- Repara JSON truncado automaticamente.

### Erros conhecidos
- `JSONDecodeError` na geração de flashcards (F1-F4): não há checkpoint
  para flashcards — rodar o comando de novo do zero (rápido, ~1-2 min).
  Geralmente resolve na 2ª tentativa.
- Tempo total por domínio: ~25-30 minutos (1600-1900s).
- Custo: ~$1.65/domínio (input ~44k tokens, output ~100k tokens).

### Se parecer travado (sem output novo por >5min)
```powershell
dir *.json
dir *.partial.json
```
- Se existem arquivos finais → reaproveitados automaticamente ao
  re-rodar.
- Se existe `.partial.json` → retoma do checkpoint ao re-rodar.
- Se nada existe → abortar (Ctrl+C) e rodar de novo do zero.

---

## 5. VALIDAÇÃO ESTRUTURAL (rodar sempre antes da auditoria)

```powershell
cd C:\ARAGORN\aragorn_quiz\prev_dXX_gen
python -c "
import json
for f in ['PREV_DXX_flashcards_pt.json','PREV_DXX_quiz_001_pt.json','PREV_DXX_quiz_002_pt.json']:
    d = json.load(open(f, encoding='utf-8'))
    if 'cards' in d:
        print(f, 'cards:', d['total_cards'], len(d['cards']))
        for i,c in enumerate(d['cards'],1):
            if c['layer']=='F1':
                fw=len(c['front'].split()); bw=len(c['back'].split())
                if fw>15 or bw>25:
                    print('  F1 OVER LIMIT card', i, 'front=',fw,'back=',bw)
    else:
        print(f, 'questoes:', d['total_questoes'], len(d['questoes']))
        niveis = {}
        for q in d['questoes']:
            niveis[q['nivel']] = niveis.get(q['nivel'],0)+1
        print('  niveis:', niveis)
"
```
Esperado: 48 cards, 50+50 questões, distribuição {EASY:10, STANDARD:20,
HARD:20} em cada quiz, nenhum F1 acima do limite.

---

## 6. AUDITORIA DE QUALIDADE (CRÍTICO — não pular)

Passos obrigatórios antes do deploy:

1. **Listar todas as 100 perguntas** (50+50) — varredura rápida de
   fraseado quebrado (ex: defeitos de template tipo "Qual X não é Y, mas
   qual Z...") e **siglas/instituições suspeitas**.

2. **CASO REAL DE ALUCINAÇÃO DETECTADO (PREV_D02, quiz_002, Q5):**
   O modelo inventou a sigla "ANSA" ("Agravo de Notificação em Situação
   de Alerta") como se fosse nomenclatura oficial do MS — não existe.
   Foi substituída por uma questão real sobre DNCI (Doença de
   Notificação Compulsória Imediata, Portaria GM/MS nº 1.061/2020).
   **Lição: qualquer sigla/instituição/lei citada que não seja
   reconhecível ou verificável deve ser tratada com suspeita e
   verificada/substituída antes do deploy.**

3. **Checar repetição de temas/casos entre quiz_001 e quiz_002** do
   mesmo domínio (não deve haver).

4. **Amostra de 2 questões HARD** (uma de cada quiz) — ler
   pergunta + alternativas + justification_correct + justification_wrong
   completas, verificar:
   - Referências/guidelines citadas são reais e atuais (ano/fonte
     plausível: SBP, MS, ATA, EULAR, ACR, ISTH, ILAE, FDA/EMA, etc.)
   - Raciocínio clínico/estatístico está correto
   - As justificativas "wrong" realmente refutam as alternativas
     incorretas com fundamento técnico

5. **Áreas de atenção especial** (alto risco de erro sutil):
   - Imunização em imunossupressão (viva vs inativada, CRIE, cocooning)
   - Doses/idade corrigida em prematuros
   - Farmacocinética em insuficiência renal/hepática (Child-Pugh)
   - Gestação/lactação (categorias de risco, contraindicações)
   - Critérios de não-inferioridade ITT vs PP (regulatório FDA/EMA)

6. **Se encontrar problema**: corrigir a questão específica via edição
   pontual do JSON (não regenerar o domínio inteiro), copiar para
   outputs, baixar e substituir o arquivo antes do deploy. Documentar a
   correção na mensagem de commit.

Se passou em tudo: **aprovado**.

---

## 7. PROTOCOLO DE DEPLOY

Ajustar `NOMEPASTA` (minúsculas, sem acento) e `CODIGO`:

```powershell
cd C:\ARAGORN\aragorn_quiz
New-Item -ItemType Directory -Force -Path "flashcards\med\medicina_preventiva\NOMEPASTA"
New-Item -ItemType Directory -Force -Path "quizzes\med\medicina_preventiva\NOMEPASTA"

Copy-Item -Force ".\prev_dXX_gen\PREV_DXX_flashcards_pt.json" -Destination "flashcards\med\medicina_preventiva\NOMEPASTA\"
Copy-Item -Force ".\prev_dXX_gen\PREV_DXX_quiz_001_pt.json" -Destination "quizzes\med\medicina_preventiva\NOMEPASTA\"
Copy-Item -Force ".\prev_dXX_gen\PREV_DXX_quiz_002_pt.json" -Destination "quizzes\med\medicina_preventiva\NOMEPASTA\"

python -c "import json; json.load(open('flashcards\\med\\medicina_preventiva\\NOMEPASTA\\PREV_DXX_flashcards_pt.json', encoding='utf-8-sig')); print('flashcards OK')"
python -c "import json; json.load(open('quizzes\\med\\medicina_preventiva\\NOMEPASTA\\PREV_DXX_quiz_001_pt.json', encoding='utf-8-sig')); print('quiz1 OK')"
python -c "import json; json.load(open('quizzes\\med\\medicina_preventiva\\NOMEPASTA\\PREV_DXX_quiz_002_pt.json', encoding='utf-8-sig')); print('quiz2 OK')"

git add .
git commit -m "feat: PREV_DXX NomeDominio - 48 flashcards + 100 questoes (quiz 001/002, via API)"
git push
```

### Antes de QUALQUER deploy, verificar se já não foi feito:
```powershell
git log --oneline -- flashcards/med/medicina_preventiva/NOMEPASTA
```
Se já existe commit, não repetir o processo.

### Limpeza de arquivos órfãos
Se um domínio foi interrompido/cancelado, remover os arquivos de
geração órfãos antes ou junto do próximo commit:
```powershell
git rm -r prev_dXX_gen
git commit -m "chore: remove arquivos orfaos de geracao PREV_DXX (nao utilizado)"
git push
```

---

## 8. REGRAS GERAIS DE COMUNICAÇÃO E EXECUÇÃO

- Respostas concisas, sem walkthrough/comentário desnecessário,
  execução imediata.
- Comunicação em português informal do Brasil.
- Endereçar Alexandre como "Alexandre" (Agente PF, NUNCA "Delegado").
- Sempre que houver dúvida sobre status de algo (já gerado? já
  commitado?), checar via `git log`/`dir`/arquivos reais — NUNCA
  assumir com base apenas em handoffs escritos anteriores.
- Alexandre tem créditos na API (platform.claude.com/settings/billing)
  para custear a geração — ~$1.65/domínio.

---

## 9. PRÓXIMA AÇÃO IMEDIATA

Gerar PREV_D05 Saúde da Família e Atenção Primária (SUS/ESF):
```powershell
cd C:\ARAGORN\aragorn_quiz
New-Item -ItemType Directory -Force -Path "prev_d05_gen"
Copy-Item -Force ".\prev_d04_gen\gerar_dominio.py" -Destination ".\prev_d05_gen\"
cd prev_d05_gen
python gerar_dominio.py PREV_D05 "Saude da Familia e Atencao Primaria" "Medicina Preventiva e Social"
```

Depois: validação → auditoria (atenção a alucinações de
siglas/instituições) → deploy → seguir para PREV_D06.
