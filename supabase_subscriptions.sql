-- Tabela de assinaturas nexor_med
create table if not exists public.subscriptions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null unique,
  plan text not null default 'trial' check (plan in ('trial','monthly','annual')),
  status text not null default 'active' check (status in ('active','expired','cancelled')),
  stripe_customer_id text,
  stripe_subscription_id text,
  trial_ends_at timestamptz,
  current_period_end timestamptz,
  created_at timestamptz default now()
);

-- RLS
alter table public.subscriptions enable row level security;

create policy "Usuário lê própria assinatura"
  on public.subscriptions for select
  using (auth.uid() = user_id);

create policy "Usuário insere própria assinatura"
  on public.subscriptions for insert
  with check (auth.uid() = user_id);

-- Service role pode atualizar (usado pelo webhook)
create policy "Service role atualiza assinatura"
  on public.subscriptions for update
  using (true);
