import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const STRIPE_WEBHOOK_SECRET = Deno.env.get('STRIPE_WEBHOOK_SECRET')!;
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_KEY = Deno.env.get('SERVICE_ROLE_KEY')!;

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
    const plan = amountTotal <= 4500 ? 'monthly' : 'annual';

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

    if (error) console.error('Supabase upsert error:', error);
    else console.log('Subscription updated:', userId, plan);
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
