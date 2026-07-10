-- Correção de segurança (auditoria 2026-07-10):
-- A policy anterior de UPDATE em subscriptions usava "using (true)" sem
-- restringir a role, liberando UPDATE para qualquer cliente autenticado
-- com a anon key (exposta publicamente em assets/auth.js). Isso permitia
-- que qualquer usuário alterasse seu próprio registro de assinatura
-- (plan/status/current_period_end) diretamente via Supabase, sem nunca
-- passar pelo Stripe.
--
-- Service role SEMPRE ignora RLS — não precisa de nenhuma policy para
-- o webhook funcionar. Por isso a policy pode ser removida sem substituto.
--
-- EXECUTAR MANUALMENTE no SQL Editor do Supabase Dashboard
-- (projeto nexor_med, ref bprpbfqxrlthjeymhkec). Este arquivo documenta
-- a mudança no repositório; não é aplicado automaticamente.

drop policy if exists "Service role atualiza assinatura" on public.subscriptions;

-- Nenhuma policy de UPDATE é recriada para anon/authenticated.
-- O webhook (supabase/functions/stripe-webhook) continua funcionando
-- normalmente porque usa a SERVICE_ROLE_KEY, que bypassa RLS por padrão.
