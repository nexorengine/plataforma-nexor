# nexor_med — Playbook Arquitetônico
> Fonte da verdade para localização de todos os artefatos, bancos de dados e serviços.
> Atualizado: 2026-06-21

---

## 1. Visão Geral do Produto

**nexor_med** — plataforma de preparação para Residência Médica.
**Stack**: HTML/CSS/JS puro · Supabase (Auth + DB) · Stripe (pagamentos) · GitHub Pages (hospedagem)
**Domínio live**: https://nexorengine.com
**Repositório**: https://github.com/nexorengine/plataforma-nexor

---

## 2. Repositório Git

| Item | Valor |
|------|-------|
| Remote | `https://github.com/nexorengine/plataforma-nexor.git` |
| Branch de produção | `gh-pages` — o que está no ar |
| Branch de desenvolvimento | `main` |
| Diretório local | `C:\ARAGORN\plataforma-nexor\` |

> **Regra**: todo trabalho novo vai em `main`, depois merge para `gh-pages` para publicar.
> O diretório local está atualmente na branch `gh-pages`.

---

## 3. Mapa de Arquivos Locais

### 3.1 Raiz do Projeto `C:\ARAGORN\plataforma-nexor\`

```
CNAME                        → domínio personalizado (nexorengine.com)
PLAYBOOK.md                  → este arquivo
index.html                   → C0: landing page de vendas (nexorengine.com)
login.html                   → página de autenticação (magic link + Google)
c1-med.html                  → C1: home / hub de especialidades
c2-med.html                  → C2: seleção de domínio
c3-med.html                  → C3: modo de estudo (flashcard vs quiz)
c4a-flashcard.html           → C4a: modo flashcard
c4b-quiz.html                → C4b: modo quiz (questões + resumo analítico)
c4c-scorecard.html           → C4c: scorecard / histórico de resultados
upgrade.html                 → página de planos e assinatura (Stripe)
success.html                 → confirmação pós-pagamento
```

### 3.2 Assets `C:\ARAGORN\plataforma-nexor\assets\`

| Arquivo | Função |
|---------|--------|
| `auth.js` | Supabase Auth — magic link, Google OAuth, session guard, subscription check |
| `catalog.js` | Objeto `CATALOG` — mapa de todas as especialidades e domínios |
| `nx.css` | Stylesheet principal — tokens, layout, componentes |
| `nexor.css` | CSS base do **nexor_cert** (projeto futuro) — NÃO DELETAR |
| `nexor-med-instagram.svg` | Logotipo SVG para redes sociais |
| `notif.js` | Push notifications (badge, alertas) |
| `profile.js` | Sheet de perfil lateral — stats, configurações, suporte WhatsApp |
| `tts.js` | Text-to-speech dos resumos analíticos |

### 3.3 Conteúdo `C:\ARAGORN\plataforma-nexor\content\`

#### Quizzes (90 arquivos · 4.500 questões)
```
content/quizzes/{area}/{dominio}/quiz_001.json
content/quizzes/{area}/{dominio}/quiz_002.json
```
**Estrutura JSON:**
```json
{
  "area": "cirurgia_geral",
  "dominio": "abdome_agudo",
  "quiz": "001",
  "total": 50,
  "questions": [
    {
      "q": "enunciado",
      "opts": ["A", "B", "C", "D"],
      "c": 3,
      "exp": "explicação curta (~138 chars) — NÃO é o resumo analítico completo"
    }
  ]
}
```
> `exp` = explicação rápida embutida no quiz. O resumo analítico completo fica em `content/resumos/`.

#### Flashcards (45 arquivos · ~20 cards por domínio)
```
content/flashcards/{area}/{dominio}/flashcards.json
```
**Estrutura JSON:**
```json
{
  "area": "...",
  "dominio": "...",
  "cards": [{ "frente": "...", "verso": "..." }]
}
```

#### Resumos Analíticos (90 arquivos · 4.500 resumos)
```
content/resumos/{area}/{dominio}/quiz_001_resumos.json
content/resumos/{area}/{dominio}/quiz_002_resumos.json
```
**Estrutura JSON:**
```json
{
  "area": "cirurgia_geral",
  "dominio": "abdome_agudo",
  "quiz": "001",
  "modelo": "claude-opus-4-8",
  "resumos": [
    {
      "num": 1,
      "texto": "resumo analítico completo (~1.337 chars média atual · alvo: 600–900 chars)"
    }
  ]
}
```
> **Status de retrofit**: 4.500 resumos · média atual 1.337 chars · alvo 600–900 chars.
> 1.789 (39,8%) já na faixa. 2.711 precisam ser comprimidos via Sonnet.

#### Áreas e Domínios (5 especialidades · 45 domínios · 2 quizzes cada)
```
cirurgia_geral         → 9 domínios
clinica_medica         → 9 domínios
gineco_obstetricia     → 9 domínios
medicina_preventiva    → 9 domínios
pediatria              → 9 domínios
```

### 3.4 Scripts `C:\ARAGORN\plataforma-nexor\scripts\`
```
scripts/retrofit/patch_resumos.py   → aplica patches pontuais em resumos específicos
scripts/retrofit/regen_resumos.py   → regenera resumos individuais via API Anthropic
```

### 3.5 Supabase Functions `C:\ARAGORN\plataforma-nexor\supabase\`
```
supabase/functions/stripe-webhook/index.ts     → webhook Stripe (checkout + cancel + falha)
supabase/functions/stripe-webhook/config.toml  → verify_jwt: false (webhook externo)
supabase/migrations/001_subscriptions.sql      → schema da tabela subscriptions
```

---

## 4. Supabase (Backend / Banco de Dados)

| Item | Valor |
|------|-------|
| Projeto | `nexor_med` |
| Project Ref | `bprpbfqxrlthjeymhkec` |
| URL | `https://bprpbfqxrlthjeymhkec.supabase.co` |
| Painel | https://supabase.com/dashboard/project/bprpbfqxrlthjeymhkec |
| Org ID | `rzunitgyzitncklikqfp` |

### Tabelas

| Tabela | Colunas principais | Função |
|--------|-------------------|--------|
| `auth.users` | id, email, created_at | Usuários (gerenciado pelo Supabase) |
| `subscriptions` | user_id, plan, status, stripe_customer_id, stripe_subscription_id, current_period_end | Assinaturas e trials |
| `study_sessions` | user_id, created_at, dominio, tipo, score | Histórico de estudo (streak, progresso) |

### Secrets (Supabase Dashboard → Project Settings → Edge Functions)
| Segredo | Uso |
|---------|-----|
| `STRIPE_WEBHOOK_SECRET` | Verificação de assinatura do webhook Stripe |
| `SERVICE_ROLE_KEY` | Service role key do Supabase (usada na Edge Function) |

### Auth Configurado
- Magic Link (email sem senha)
- Google OAuth
- Redirect URL: `https://nexorengine.com/login.html`

---

## 5. Stripe (Pagamentos)

| Item | Valor |
|------|-------|
| Painel | https://dashboard.stripe.com |
| Modo atual | **TEST** (mudar para live quando pronto) |
| Webhook endpoint | `https://bprpbfqxrlthjeymhkec.supabase.co/functions/v1/stripe-webhook` |

### Payment Links (TEST — substituir por links LIVE antes do lançamento)
| Plano | Link |
|-------|------|
| Mensal R$39/mês | `https://buy.stripe.com/test_dRm8wR8iA2Np1uvcJz2Fa00` |
| Anual R$297/ano | `https://buy.stripe.com/test_7sY14p9mEgEfc999xn2Fa01` |

> Os links ficam em `upgrade.html` — atualizar para links LIVE antes de lançar.

---

## 6. GitHub Pages (Hospedagem)

| Item | Valor |
|------|-------|
| Repositório | `nexorengine/plataforma-nexor` |
| Branch publicada | `gh-pages` |
| URL padrão | `https://nexorengine.github.io/plataforma-nexor/` |
| Domínio customizado | `https://nexorengine.com` |
| CNAME file | `CNAME` na raiz do repo (conteúdo: `nexorengine.com`) |

---

## 7. Suporte WhatsApp

| Item | Valor |
|------|-------|
| Número atual | `47-992544143` (temporário — número pessoal do Alexandre) |
| Link WhatsApp | `https://wa.me/5547992544143?text=...` |
| Arquivo | `assets/profile.js` linha 295 |
| Pendência | Substituir por número dedicado de suporte quando disponível |

---

## 8. Fluxo de Deploy

```
Editar código → commit em gh-pages → push origin gh-pages → live em ~30s
```

Para trabalho em desenvolvimento:
```
Criar branch main → editar → commit main → merge para gh-pages → push
```

---

## 9. Pendências Técnicas

| # | Item | Prioridade |
|---|------|-----------|
| P1 | Retrofit dos resumos analíticos (2.711 via Sonnet) | Alta |
| P2 | Stripe: trocar links TEST por links LIVE | Alta (pré-lançamento) |
| P3 | WhatsApp: substituir número pessoal por número de suporte | Média |
| P4 | `assets/nexor.css` — verificar se ainda é usado ou pode ser deletado | Baixa |
| P5 | E-mail transacional (boas-vindas + confirmação de plano) | Fase futura |
