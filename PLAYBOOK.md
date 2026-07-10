# nexor_med — Playbook Arquitetônico
> Fonte da verdade para localização de todos os artefatos, bancos de dados e serviços.
> Atualizado: 2026-07-10

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
| Diretório local | `C:\NEXOR_MED\plataforma-nexor\` |

> **Regra**: todo trabalho novo vai em `main`, depois merge para `gh-pages` para publicar.
> O diretório local está atualmente na branch `gh-pages`.
> **Fonte da verdade é o GitHub, não o diretório local.** Este arquivo documenta o caminho local como referência, mas em caso de divergência o repositório remoto prevalece.

---

## 3. Mapa de Arquivos Locais

### 3.1 Raiz do Projeto `C:\NEXOR_MED\plataforma-nexor\`

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

### 3.2 Assets `C:\NEXOR_MED\plataforma-nexor\assets\`

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

### 3.3 Conteúdo `C:\NEXOR_MED\plataforma-nexor\content\`

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

### 3.4 Scripts `C:\NEXOR_MED\plataforma-nexor\scripts\`
```
scripts/retrofit/patch_resumos.py   → aplica patches pontuais em resumos específicos
scripts/retrofit/regen_resumos.py   → regenera resumos individuais via API Anthropic
```

### 3.5 Supabase Functions `C:\NEXOR_MED\plataforma-nexor\supabase\`
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
| Modo atual | **LIVE** (produção) |
| Webhook endpoint | `https://bprpbfqxrlthjeymhkec.supabase.co/functions/v1/stripe-webhook` — configurado no Stripe Dashboard (destino ativo, eventos: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted), signing secret sincronizado com `STRIPE_WEBHOOK_SECRET` no Supabase. Testado via requisição sintética assinada — retorno `ok`. |

### Payment Links (LIVE — em produção em `upgrade.html`)
| Plano | Link |
|-------|------|
| Mensal R$39/mês | `https://buy.stripe.com/00wfZi9Q48ZcqB9BeQM00` |
| Anual R$297/ano | `https://buy.stripe.com/fZu8wQd2P0WN8950CheQM01` |

> Injeção de `client_reference_id` e `prefilled_email` feita via JS em `upgrade.html` no momento do clique.

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

### ✅ Concluído nesta sessão
| Item | Detalhe |
|------|---------|
| Glass system C0 + todas as páginas | nx-glass.css aplicado em 9 páginas |
| Plan cards horizontal compacto | C0 e upgrade.html |
| Guarantee text | Texto corrigido na cápsula verde C0 |
| Trial warning system | Banner ≤2 dias em C1 + banner expirado em upgrade.html |
| iOS hover/active fix | :active states + touchstart listener |
| Contraste textos secundários | #AAA→#C0C0C0, #888→#A8A8A8 etc. em nx.css |
| Perfil: dados reais do Supabase | Nome, email, iniciais, plano via _loadProfileUser() |
| Suporte via e-mail | admin@nexorengine.com no sheet de perfil |
| **P2** Stripe links LIVE | Mensal + Anual em produção em upgrade.html |

---

### 🔄 Em andamento
| # | Item | Status |
|---|------|--------|
| P1 | Retrofit resumos — 2ª passagem Sonnet nos 1.463 acima de 900 chars | ⏳ Rodando em background |

---

### 📋 Próximas fases em ordem

**FASE A — PWA (próxima sessão)**
| # | Item | Detalhe |
|---|------|---------|
| A1 | Design do ícone | SVG minimalista — fundo #070A0E + símbolo nexor_med |
| A2 | Exportar PNGs | 512×512, 192×192, 180×180 (Apple Touch) + maskable |
| A3 | manifest.json | name, short_name, theme_color, icons, display:standalone |
| A4 | service-worker.js | Cache offline básico |
| A5 | Registrar SW em todas as páginas | Script de registro no head |

**FASE B — E-mails transacionais**
| # | Item | Detalhe |
|---|------|---------|
| P9 | Infra: Supabase Edge Function + Resend | Pré-requisito de P5-P8 |
| P5 | E-mail boas-vindas ao cadastrar | Trigger: novo usuário |
| P6 | E-mail "faltam 2 dias no trial" | Trigger: dia 5 do trial |
| P7 | E-mail "trial expirou" | Trigger: dia 7 |
| P8 | E-mail confirmação de plano | Trigger: webhook Stripe |

**FASE C — Operacional**
| # | Item | Detalhe |
|---|------|---------|
| P3 | WhatsApp número dedicado | Substituir 47-992544143 em profile.js linha 295 |
| P4 | nexor.css — NÃO DELETAR | Reservado para nexor_cert (produto futuro) |

**FASE D — Crescimento (pós-lançamento)**
| # | Item | Detalhe |
|---|------|---------|
| D1 | Retrofit resumos — validação final | Conferir qualidade dos comprimidos |
| D2 | Modo claro (opcional) | Refatorar nx.css para CSS Custom Properties primeiro |
| D3 | nexor_cert | Novo produto da família NEXOR |
