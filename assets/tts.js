const TTS = (() => {
  let current = null;

  function speak(text, btnEl) {
    if (!window.speechSynthesis) return;

    // Se já está falando, para
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setAllBtnsIdle();
      if (current === text) { current = null; return; }
    }

    current = text;
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = 'pt-BR';
    utt.rate = window._ttsSpeed || 0.95;
    utt.pitch = 1;

    // Tenta usar voz pt-BR se disponível
    const voices = window.speechSynthesis.getVoices();
    const ptVoice = voices.find(v => v.lang.startsWith('pt'));
    if (ptVoice) utt.voice = ptVoice;

    utt.onstart = () => { if (btnEl) setBtnActive(btnEl); };
    utt.onend = () => { current = null; setAllBtnsIdle(); };
    utt.onerror = () => { current = null; setAllBtnsIdle(); };

    window.speechSynthesis.speak(utt);
  }

  function stop() {
    window.speechSynthesis.cancel();
    current = null;
    setAllBtnsIdle();
  }

  function setBtnActive(btn) {
    setAllBtnsIdle();
    btn.classList.add('tts-active');
    btn.innerHTML = '<i class="ti ti-volume-3"></i>';
  }

  function setAllBtnsIdle() {
    document.querySelectorAll('.tts-btn').forEach(b => {
      b.classList.remove('tts-active');
      b.innerHTML = '<i class="ti ti-volume"></i>';
    });
  }

  return { speak, stop };
})();

// Espera vozes carregarem (necessário em alguns browsers)
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}
