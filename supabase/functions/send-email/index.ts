import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')!;
const DOMAIN_VERIFIED = Deno.env.get('DOMAIN_VERIFIED') === 'true';
const FROM = DOMAIN_VERIFIED
  ? 'nexor_med <noreply@nexorengine.com>'
  : 'nexor_med <onboarding@resend.dev>';

// ── Templates ──────────────────────────────────────────────────────────────

function tplBoasVindas(nome: string): { subject: string; html: string } {
  return {
    subject: 'Bem-vindo ao nexor_med 🩺',
    html: `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bem-vindo ao nexor_med</title></head>
<body style="margin:0;padding:0;background:#070A0E;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#070A0E;padding:40px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
  <tr><td style="padding:0 24px 32px;">
    <p style="margin:0 0 8px;font-size:13px;color:#0EA5E9;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">nexor_med</p>
    <h1 style="margin:0 0 24px;font-size:28px;font-weight:700;color:#F0F6FB;line-height:1.2;">Olá, ${nome}! Seja bem-vindo.</h1>
    <p style="margin:0 0 16px;font-size:15px;color:#B0BEC5;line-height:1.6;">Seu acesso ao <strong style="color:#F0F6FB;">nexor_med</strong> está ativo. Você tem <strong style="color:#0EA5E9;">7 dias gratuitos</strong> para explorar tudo:</p>
    <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
      <tr><td style="padding:6px 0;font-size:14px;color:#B0BEC5;">✓&nbsp;&nbsp;<strong style="color:#F0F6FB;">4.500+ questões</strong> comentadas com gabarito analítico</td></tr>
      <tr><td style="padding:6px 0;font-size:14px;color:#B0BEC5;">✓&nbsp;&nbsp;<strong style="color:#F0F6FB;">Flashcards</strong> com revisão espaçada FractalLearning™</td></tr>
      <tr><td style="padding:6px 0;font-size:14px;color:#B0BEC5;">✓&nbsp;&nbsp;<strong style="color:#F0F6FB;">Resumos analíticos</strong> por domínio e especialidade</td></tr>
      <tr><td style="padding:6px 0;font-size:14px;color:#B0BEC5;">✓&nbsp;&nbsp;<strong style="color:#F0F6FB;">Scorecard</strong> de desempenho em tempo real</td></tr>
    </table>
    <table cellpadding="0" cellspacing="0"><tr><td style="background:#0EA5E9;border-radius:6px;">
      <a href="https://nexorengine.com" style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:700;color:#070A0E;text-decoration:none;letter-spacing:0.04em;">COMEÇAR AGORA</a>
    </td></tr></table>
  </td></tr>
  <tr><td style="padding:24px 24px 0;border-top:1px solid rgba(255,255,255,0.06);">
    <p style="margin:0;font-size:12px;color:#4A5568;line-height:1.6;">nexor_med · Residência Médica · Powered by FractalLearning™<br>
    Dúvidas? <a href="mailto:admin@nexorengine.com" style="color:#0EA5E9;text-decoration:none;">admin@nexorengine.com</a></p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`,
  };
}

function tplTrialAviso(nome: string, dias: number): { subject: string; html: string } {
  return {
    subject: `Faltam ${dias} dias no seu trial — nexor_med`,
    html: `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070A0E;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#070A0E;padding:40px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
  <tr><td style="padding:0 24px 32px;">
    <p style="margin:0 0 8px;font-size:13px;color:#FCA311;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">nexor_med · aviso de trial</p>
    <h1 style="margin:0 0 24px;font-size:28px;font-weight:700;color:#F0F6FB;line-height:1.2;">${nome}, faltam ${dias} dia${dias > 1 ? 's' : ''} no seu trial.</h1>
    <p style="margin:0 0 24px;font-size:15px;color:#B0BEC5;line-height:1.6;">Seu período gratuito termina em breve. Assine agora para continuar estudando sem interrupção — todo seu progresso fica salvo.</p>
    <table cellpadding="0" cellspacing="0" style="margin:0 0 16px;"><tr>
      <td style="background:#FCA311;border-radius:6px;margin-right:12px;">
        <a href="https://nexorengine.com/upgrade.html" style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:700;color:#070A0E;text-decoration:none;letter-spacing:0.04em;">ASSINAR AGORA</a>
      </td>
    </tr></table>
    <p style="margin:0;font-size:13px;color:#4A5568;">Plano Anual: R$297/ano (37% OFF) · Plano Mensal: R$39/mês</p>
  </td></tr>
  <tr><td style="padding:24px 24px 0;border-top:1px solid rgba(255,255,255,0.06);">
    <p style="margin:0;font-size:12px;color:#4A5568;line-height:1.6;">nexor_med · Residência Médica<br>
    <a href="mailto:admin@nexorengine.com" style="color:#0EA5E9;text-decoration:none;">admin@nexorengine.com</a></p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`,
  };
}

function tplTrialExpirou(nome: string): { subject: string; html: string } {
  return {
    subject: 'Seu trial nexor_med expirou — continue estudando',
    html: `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070A0E;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#070A0E;padding:40px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
  <tr><td style="padding:0 24px 32px;">
    <p style="margin:0 0 8px;font-size:13px;color:#f87171;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">nexor_med · trial expirado</p>
    <h1 style="margin:0 0 24px;font-size:28px;font-weight:700;color:#F0F6FB;line-height:1.2;">${nome}, seu acesso gratuito chegou ao fim.</h1>
    <p style="margin:0 0 24px;font-size:15px;color:#B0BEC5;line-height:1.6;">Seu progresso está salvo e te esperando. Assine um plano para voltar a estudar de onde parou.</p>
    <table cellpadding="0" cellspacing="0" style="margin:0 0 16px;"><tr>
      <td style="background:#FCA311;border-radius:6px;">
        <a href="https://nexorengine.com/upgrade.html" style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:700;color:#070A0E;text-decoration:none;letter-spacing:0.04em;">REATIVAR ACESSO</a>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:24px 24px 0;border-top:1px solid rgba(255,255,255,0.06);">
    <p style="margin:0;font-size:12px;color:#4A5568;line-height:1.6;">nexor_med · Residência Médica<br>
    <a href="mailto:admin@nexorengine.com" style="color:#0EA5E9;text-decoration:none;">admin@nexorengine.com</a></p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`,
  };
}

function tplPlanoAtivo(nome: string, plano: string): { subject: string; html: string } {
  const label = plano === 'annual' ? 'Anual' : 'Mensal';
  const preco = plano === 'annual' ? 'R$297/ano' : 'R$39/mês';
  return {
    subject: `Plano ${label} ativo — bem-vindo ao nexor_med completo!`,
    html: `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070A0E;font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#070A0E;padding:40px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
  <tr><td style="padding:0 24px 32px;">
    <p style="margin:0 0 8px;font-size:13px;color:#4ade80;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">nexor_med · plano ativo</p>
    <h1 style="margin:0 0 24px;font-size:28px;font-weight:700;color:#F0F6FB;line-height:1.2;">Tudo certo, ${nome}! Plano ${label} confirmado.</h1>
    <p style="margin:0 0 8px;font-size:15px;color:#B0BEC5;line-height:1.6;">Seu pagamento de <strong style="color:#F0F6FB;">${preco}</strong> foi processado com sucesso. Acesso completo liberado.</p>
    <p style="margin:0 0 24px;font-size:13px;color:#4A5568;">Recibo enviado pelo Stripe para este e-mail.</p>
    <table cellpadding="0" cellspacing="0"><tr>
      <td style="background:#0EA5E9;border-radius:6px;">
        <a href="https://nexorengine.com" style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:700;color:#070A0E;text-decoration:none;letter-spacing:0.04em;">ACESSAR PLATAFORMA</a>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:24px 24px 0;border-top:1px solid rgba(255,255,255,0.06);">
    <p style="margin:0;font-size:12px;color:#4A5568;line-height:1.6;">nexor_med · Residência Médica · Powered by FractalLearning™<br>
    Dúvidas? <a href="mailto:admin@nexorengine.com" style="color:#0EA5E9;text-decoration:none;">admin@nexorengine.com</a></p>
  </td></tr>
</table>
</td></tr></table>
</body></html>`,
  };
}

// ── Handler principal ───────────────────────────────────────────────────────

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: { 'Access-Control-Allow-Origin': '*' } });
  }

  // Correção de segurança (auditoria 2026-07-10): antes deste fix, este endpoint
  // era publico (verify_jwt=false) e sem nenhuma validacao, permitindo que
  // qualquer pessoa disparasse e-mails arbitrarios usando a marca nexor_med e a
  // cota do Resend. Agora verify_jwt=true (config.toml) exige um JWT valido do
  // Supabase (sessao do usuario ou service role) — enforced pelo runtime antes
  // mesmo de chegar aqui. Nenhuma validacao extra e necessaria no codigo.

  let body: any;
  try {
    body = await req.json();
  } catch {
    return new Response('Invalid JSON', { status: 400 });
  }

  const { type, to, nome, dias, plano } = body;
  if (!type || !to) return new Response('Missing type or to', { status: 400 });

  let tpl: { subject: string; html: string };
  if (type === 'boas_vindas') {
    tpl = tplBoasVindas(nome || to.split('@')[0]);
  } else if (type === 'trial_aviso') {
    tpl = tplTrialAviso(nome || to.split('@')[0], dias ?? 2);
  } else if (type === 'trial_expirou') {
    tpl = tplTrialExpirou(nome || to.split('@')[0]);
  } else if (type === 'plano_ativo') {
    tpl = tplPlanoAtivo(nome || to.split('@')[0], plano ?? 'monthly');
  } else {
    return new Response('Unknown type', { status: 400 });
  }

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ from: FROM, to, subject: tpl.subject, html: tpl.html }),
  });

  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
});
