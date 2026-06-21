import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const SUPABASE_URL        = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_KEY = Deno.env.get('SERVICE_ROLE_KEY')!;
const SEND_EMAIL_URL      = `${SUPABASE_URL}/functions/v1/send-email`;

const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false }
});

async function sendEmail(type: string, to: string, nome: string, extra?: object) {
  await fetch(SEND_EMAIL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, to, nome, ...extra }),
  });
}

serve(async () => {
  const now = new Date();

  // Busca todos os trials ativos com trial_ends_at definido
  const { data: trials, error } = await sb
    .from('subscriptions')
    .select('user_id, trial_ends_at')
    .eq('plan', 'trial')
    .eq('status', 'active')
    .not('trial_ends_at', 'is', null);

  if (error) {
    console.error('Erro ao buscar trials:', error);
    return new Response('DB error', { status: 500 });
  }

  let avisos = 0, expirados = 0;

  for (const sub of trials ?? []) {
    const ends = new Date(sub.trial_ends_at);
    const diffDias = Math.ceil((ends.getTime() - now.getTime()) / 86400000);

    // Busca email e nome do usuário
    const { data: userData } = await sb.auth.admin.getUserById(sub.user_id);
    if (!userData?.user) continue;

    const email = userData.user.email!;
    const nome = userData.user.user_metadata?.full_name
      || userData.user.user_metadata?.name
      || email.split('@')[0];

    if (diffDias === 2) {
      // Dia 5 do trial — faltam 2 dias
      await sendEmail('trial_aviso', email, nome, { dias: 2 });
      avisos++;
    } else if (diffDias <= 0) {
      // Trial expirado — atualiza status e envia email
      await sb.from('subscriptions')
        .update({ status: 'expired' })
        .eq('user_id', sub.user_id);
      await sendEmail('trial_expirou', email, nome);
      expirados++;
    }
  }

  console.log(`check-trials: ${avisos} avisos, ${expirados} expirados`);
  return new Response(JSON.stringify({ avisos, expirados }), {
    headers: { 'Content-Type': 'application/json' },
  });
});
