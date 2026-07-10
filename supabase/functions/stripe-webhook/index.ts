import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const STRIPE_WEBHOOK_SECRET = Deno.env.get('STRIPE_WEBHOOK_SECRET')!;
const SUPABASE_URL          = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_KEY  = Deno.env.get('SERVICE_ROLE_KEY')!;
const SEND_EMAIL_URL        = `${SUPABASE_URL}/functions/v1/send-email`;

serve(async (req) => {
  // Permite chamadas sem JWT (necessário para webhooks externos)
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: { 'Access-Control-Allow-Origin': '*' } });
  }

  const signature = req.headers.get('stripe-signature');
  if (!signature) return new Response('Missing signature', { status: 400 });

  const body = await req.text();

  // Verifica assinatura do webhook Stripe
  let event: any;
  try {
    const encoder = new TextEncoder();
    const parts = signature.split(',');
    const ts = parts.find((p: string) => p.startsWith('t='))?.split('=')[1];
    const sig = parts.find((p: string) => p.startsWith('v1='))?.split('=')[1];
    const payload = `${ts}.${body}`;
    const key = await crypto.subtle.importKey(
      'raw', encoder.encode(STRIPE_WEBHOOK_SECRET),
      { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    );
    const computed = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
    const hex = Array.from(new Uint8Array(computed)).map(b => b.toString(16).padStart(2,'0')).join('');
    if (hex !== sig) return new Response('Invalid signature', { status: 400 });
    event = JSON.parse(body);
  } catch (e) {
    return new Response('Webhook error: ' + e.message, { status: 400 });
  }

  const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = session.client_reference_id;
    const customerId = session.customer;
    const subscriptionId = session.subscription;

    if (!userId) {
      console.error('No client_reference_id in session:', session.id);
      return new Response('No user id', { status: 200 });
    }

    const amountTotal = session.amount_total || 0;

    // Preços atuais (centavos) — atualizar aqui se o Stripe mudar de valor.
    // Comparação por valor exato (não por faixa/limiar) para evitar classificação
    // silenciosa errada caso um preço mude e passe a colidir com o outro plano.
    const PRICE_MONTHLY_CENTS = 3900;  // R$39/mês
    const PRICE_ANNUAL_CENTS  = 29700; // R$297/ano

    let plan: string;
    if (amountTotal === PRICE_MONTHLY_CENTS) {
      plan = 'monthly';
    } else if (amountTotal === PRICE_ANNUAL_CENTS) {
      plan = 'annual';
    } else {
      console.error(
        `Valor de checkout não reconhecido: ${amountTotal} centavos (session ${session.id}). ` +
        `Esperado mensal=${PRICE_MONTHLY_CENTS} ou anual=${PRICE_ANNUAL_CENTS}. ` +
        `Assinatura NÃO registrada — requer revisão manual e atualização destas constantes.`
      );
      return new Response('Unrecognized amount - manual review required', { status: 200 });
    }

    const periodEnd = new Date();
    if (plan === 'monthly') periodEnd.setMonth(periodEnd.getMonth() + 1);
    else periodEnd.setFullYear(periodEnd.getFullYear() + 1);

    const { error } = await sb.from('subscriptions').upsert({
      user_id: userId,
      plan,
      status: 'active',
      stripe_customer_id: customerId,
      stripe_subscription_id: subscriptionId,
      current_period_end: periodEnd.toISOString()
    }, { onConflict: 'user_id' });

    if (error) {
      console.error('Supabase upsert error:', error);
    } else {
      console.log('Subscription updated:', userId, plan);
      // Envia email de confirmação de plano
      const { data: userData } = await sb.auth.admin.getUserById(userId);
      if (userData?.user) {
        const email = userData.user.email!;
        const nome = userData.user.user_metadata?.full_name
          || userData.user.user_metadata?.name
          || email.split('@')[0];
        await fetch(SEND_EMAIL_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'plano_ativo', to: email, nome, plano: plan }),
        });
      }
    }
  }

  if (event.type === 'customer.subscription.deleted') {
    const sub = event.data.object;
    await sb.from('subscriptions')
      .update({ status: 'cancelled' })
      .eq('stripe_subscription_id', sub.id);
  }

  if (event.type === 'invoice.payment_failed') {
    const invoice = event.data.object;
    await sb.from('subscriptions')
      .update({ status: 'expired' })
      .eq('stripe_customer_id', invoice.customer);
  }

  return new Response('ok', { status: 200 });
}, {
  // Desabilita verificação de JWT do Supabase para esta função
});
