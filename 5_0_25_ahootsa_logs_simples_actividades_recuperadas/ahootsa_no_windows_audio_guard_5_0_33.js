/* ============================================================
 * Ahootsa 5.0.33 - SIN AUDIO WINDOWS / NAVEGADOR
 *
 * Politica global:
 *   - Solo debe hablar Ahootsa.
 *   - Se bloquea la TTS del navegador/Windows: Web Speech API.
 *   - No se bloquean etiquetas <audio>, porque Ahootsa/Realtime puede usarlas.
 * ============================================================ */
(function installAhootsaNoWindowsAudioGuard(rootWindow) {
  function apply(win) {
    try {
      if (!win || win.__AHOOTSA_5033_NO_WINDOWS_AUDIO__) return;
      win.__AHOOTSA_5033_NO_WINDOWS_AUDIO__ = true;

      win.AHOOTSA_AUDIO_POLICY = win.AHOOTSA_AUDIO_POLICY || {};
      win.AHOOTSA_AUDIO_POLICY.onlyAhootsaVoice = true;
      win.AHOOTSA_AUDIO_POLICY.blockWindowsSpeechSynthesis = true;
      win.AHOOTSA_AUDIO_POLICY.blockedBy = "Ahootsa 5.0.33";

      function quietLog(msg) {
        try {
          if (win.AHOOTSA_DEBUG_AUDIO === true && win.console) {
            win.console.info("[Ahootsa 5.0.33] Audio Windows bloqueado", msg || "");
          }
        } catch (e) {}
      }

      function cancelNativeSpeech() {
        try {
          if (win.speechSynthesis && typeof win.speechSynthesis.cancel === "function") {
            win.speechSynthesis.cancel();
          }
        } catch (e) {}
      }

      function installSpeechBlock() {
        try {
          cancelNativeSpeech();

          if (win.speechSynthesis) {
            var synth = win.speechSynthesis;

            var blockedSpeak = function(utterance) {
              try {
                quietLog(utterance && (utterance.text || utterance.lang || (utterance.voice && utterance.voice.name)));
              } catch (e) {}
              cancelNativeSpeech();
              return undefined;
            };
            blockedSpeak.__ahootsa5033Blocked = true;

            var blockedGetVoices = function() { return []; };

            try { synth.speak = blockedSpeak; } catch (e1) {
              try { Object.defineProperty(synth, "speak", { value: blockedSpeak, configurable: true, writable: true }); } catch (e2) {}
            }
            try { synth.getVoices = blockedGetVoices; } catch (e3) {
              try { Object.defineProperty(synth, "getVoices", { value: blockedGetVoices, configurable: true, writable: true }); } catch (e4) {}
            }
            try { synth.resume = cancelNativeSpeech; } catch (e5) {}
          }

          // Neutraliza tambien la construccion de utterances usada por algunas actividades.
          try {
            var OriginalUtterance = win.SpeechSynthesisUtterance;
            if (OriginalUtterance && !win.__AHOOTSA_ORIGINAL_UTTERANCE_5033__) {
              win.__AHOOTSA_ORIGINAL_UTTERANCE_5033__ = OriginalUtterance;
            }
            var BlockedUtterance = function(text) {
              this.text = "";
              this.lang = "es-ES";
              this.volume = 0;
              this.rate = 1;
              this.pitch = 1;
              this.voice = null;
              this.__ahootsaBlockedUtterance = true;
              quietLog(text || "SpeechSynthesisUtterance");
            };
            BlockedUtterance.prototype = OriginalUtterance && OriginalUtterance.prototype ? OriginalUtterance.prototype : {};
            try { win.SpeechSynthesisUtterance = BlockedUtterance; } catch (e6) {
              try { Object.defineProperty(win, "SpeechSynthesisUtterance", { value: BlockedUtterance, configurable: true, writable: true }); } catch (e7) {}
            }
          } catch (e8) {}
        } catch (e) {}
      }

      installSpeechBlock();

      // Algunas librerias restauran speechSynthesis despues de cargar. Reaplicar mas tiempo.
      var n = 0;
      var timer = win.setInterval(function() {
        n += 1;
        installSpeechBlock();
        if (n >= 240) { try { win.clearInterval(timer); } catch (e) {} }
      }, 250);

      try { win.addEventListener("focus", installSpeechBlock, true); } catch (e) {}
      try { win.addEventListener("pageshow", installSpeechBlock, true); } catch (e) {}
      try { win.document && win.document.addEventListener("visibilitychange", installSpeechBlock, true); } catch (e) {}
      try { win.document && win.document.addEventListener("DOMContentLoaded", installSpeechBlock, true); } catch (e) {}

      // Aplicar tambien a iframes same-origin si los hubiera.
      function patchFrames() {
        try {
          var frames = win.document ? win.document.querySelectorAll("iframe") : [];
          for (var i = 0; i < frames.length; i++) {
            try { apply(frames[i].contentWindow); } catch (e) {}
          }
        } catch (e) {}
      }
      patchFrames();
      try {
        if (win.MutationObserver && win.document && win.document.documentElement) {
          var mo = new win.MutationObserver(function() { patchFrames(); installSpeechBlock(); });
          mo.observe(win.document.documentElement, { childList: true, subtree: true });
        }
      } catch (e) {}

      win.ahootsaAudio = win.ahootsaAudio || {};
      win.ahootsaAudio.isWindowsSpeechBlocked = function() { return true; };
      win.ahootsaAudio.cancelWindowsSpeech = cancelNativeSpeech;
      win.ahootsaAudio.blockWindowsSpeechNow = installSpeechBlock;
    } catch (e) {}
  }
  apply(rootWindow || window);
})(typeof window !== "undefined" ? window : null);
/* Fin Ahootsa 5.0.33 - SIN AUDIO WINDOWS / NAVEGADOR */
