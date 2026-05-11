(function () {
    const i18n = globalThis.__i18n || {};

    function detectLanguage() {
        const saved = localStorage.getItem('lang');
        if (saved === 'pt' || saved === 'en') return saved;
        const lang = globalThis.navigator?.language || '';
        return lang.startsWith('pt') ? 'pt' : 'en';
    }

    function applyLocale(lang) {
        const shortLang = (lang || '').slice(0, 2);
        const locale = i18n[shortLang] || i18n.en;
        const btnText = document.getElementById('open-wa-text');
        const phoneInput = document.getElementById('phone');
        const aboutBlurb = document.getElementById('about-blurb');
        if (btnText) btnText.textContent = locale.buttonLabel;
        if (phoneInput) phoneInput.placeholder = locale.phonePlaceholder;
        if (aboutBlurb) aboutBlurb.textContent = locale.aboutBlurb;
        globalThis.__errorEmpty = locale.errorEmpty;
        globalThis.__errorInvalid = locale.errorInvalid;
        globalThis.__currentLang = shortLang === 'pt' ? 'pt' : 'en';
    }

    globalThis.detectLanguage = detectLanguage;
    globalThis.applyLocale = applyLocale;
})();
