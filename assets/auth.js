// nexor_med · Auth module
// Supabase credentials — preenchidos após criação do projeto
const SUPABASE_URL  = 'https://bprpbfqxrlthjeymhkec.supabase.co';
const SUPABASE_ANON = 'sb_publishable_gVQsQqPn0nCPJapEXBXNJQ_nkXR80r7';

const _sb = supabase.createClient(SUPABASE_URL, SUPABASE_ANON);
window._sb = _sb;

// iOS Safari: ativa :active em elementos <div> sem precisar de <a>/<button>
document.addEventListener('touchstart', function(){}, {passive:true});

const Auth = {
  // Retorna sessão atual (null se não logado)
  async session() {
    const { data } = await _sb.auth.getSession();
    return data.session;
  },

  // Redireciona para login se não autenticado
  async requireAuth() {
    const s = await this.session();
    if (!s) {
      window.location.href = 'login.html?next=' + encodeURIComponent(window.location.pathname + window.location.hash);
      return null;
    }
    return s;
  },

  // Magic link
  async sendMagicLink(email) {
    const { error } = await _sb.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: 'https://nexorengine.github.io/plataforma-nexor/c1-med.html' }
    });
    return error;
  },

  // Google OAuth
  async loginGoogle() {
    await _sb.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: 'https://nexorengine.github.io/plataforma-nexor/c1-med.html' }
    });
  },

  // Logout
  async logout() {
    await _sb.auth.signOut();
    window.location.href = 'login.html';
  },

  // Dados do usuário atual
  async user() {
    const s = await this.session();
    return s ? s.user : null;
  },

  // Preenche avatar/nome no header se logado
  async fillHeader() {
    const u = await this.user();
    if (!u) return;
    const avatarEl = document.querySelector('.nx-avatar-btn');
    if (avatarEl) {
      const initials = (u.user_metadata?.full_name || u.email || 'U')
        .split(' ').map(w => w[0]).join('').toUpperCase().slice(0,2);
      avatarEl.textContent = initials;
    }
  },

  // Garante registro de trial ao primeiro acesso
  async ensureTrial(userId) {
    const { data } = await _sb.from('subscriptions').select('id').eq('user_id', userId).maybeSingle();
    if (!data) {
      const trialEnd = new Date();
      trialEnd.setDate(trialEnd.getDate() + 7);
      await _sb.from('subscriptions').insert({
        user_id: userId,
        plan: 'trial',
        status: 'active',
        trial_ends_at: trialEnd.toISOString()
      });
    }
  },

  // Verifica se o usuário tem acesso ativo (trial válido ou plano pago)
  async checkAccess() {
    const s = await this.session();
    if (!s) return false;
    await this.ensureTrial(s.user.id);
    const { data } = await _sb.from('subscriptions')
      .select('plan,status,trial_ends_at,current_period_end')
      .eq('user_id', s.user.id)
      .maybeSingle();
    if (!data) return false;
    if (data.status !== 'active') return false;
    if (data.plan === 'trial') {
      return data.trial_ends_at ? new Date(data.trial_ends_at) > new Date() : false;
    }
    if (data.plan === 'monthly' || data.plan === 'annual') {
      return data.current_period_end ? new Date(data.current_period_end) > new Date() : true;
    }
    return false;
  },

  // Redireciona para upgrade se sem acesso
  async requireAccess() {
    const ok = await this.checkAccess();
    if (!ok) {
      window.location.href = 'upgrade.html';
      return false;
    }
    return true;
  },

  // Retorna dados da assinatura atual
  async subscription() {
    const s = await this.session();
    if (!s) return null;
    const { data } = await _sb.from('subscriptions')
      .select('*')
      .eq('user_id', s.user.id)
      .maybeSingle();
    return data;
  }
};
