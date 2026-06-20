// nexor_med · Auth module
// Supabase credentials — preenchidos após criação do projeto
const SUPABASE_URL  = 'https://bprpbfqxrlthjeymhkec.supabase.co';
const SUPABASE_ANON = 'sb_publishable_gVQsQqPn0nCPJapEXBXNJQ_nkXR80r7';

const _sb = supabase.createClient(SUPABASE_URL, SUPABASE_ANON);

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
      options: { emailRedirectTo: 'https://nexorengine.github.io/plataforma-nexor/' }
    });
    return error;
  },

  // Google OAuth
  async loginGoogle() {
    await _sb.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin + '/prototipo-med/index.html' }
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
  }
};
