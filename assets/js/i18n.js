/**
 * i18n — Internacionalización EN/ES
 * Carga archivos JSON de traducción y aplica data-i18n attributes.
 */
const i18n = {
  currentLang: 'es',
  texts: {},

  async init() {
    // Detectar idioma del navegador
    const browserLang = navigator.language.split('-')[0];
    const saved = localStorage.getItem('portfolio-lang');
    this.currentLang = saved || (['en', 'es'].includes(browserLang) ? browserLang : 'es');
    await this.apply();
  },

  async setLang(lang) {
    this.currentLang = lang;
    localStorage.setItem('portfolio-lang', lang);
    await this.apply();
    // Actualizar clase activa en toggle
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  },

  async apply() {
    try {
      const resp = await fetch(`/i18n/${this.currentLang}.json`);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      this.texts = await resp.json();
    } catch (e) {
      console.warn('i18n: fallback a español', e);
      // Fallback: cargar español
      const resp = await fetch('/i18n/es.json');
      this.texts = await resp.json();
      this.currentLang = 'es';
    }

    // Aplicar traducciones a elementos con data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      if (this.texts[key] !== undefined) {
        el.innerHTML = this.texts[key];
      }
    });

    // Actualizar atributo lang del HTML
    document.documentElement.lang = this.currentLang;

    // Actualizar etiquetas hreflang dinámicas
    const baseUrl = 'https://jmartinez.dev';
    const links = document.querySelectorAll('link[hreflang]');
    links.forEach(link => {
      const hreflang = link.getAttribute('hreflang');
      if (hreflang === 'es') {
        link.href = `${baseUrl}/`;
      } else if (hreflang === 'en') {
        link.href = `${baseUrl}/en/`;
      }
    });

    // Disparar evento para otros scripts
    document.dispatchEvent(new CustomEvent('i18n-ready', { detail: { lang: this.currentLang } }));
  }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => i18n.init());
} else {
  i18n.init();
}
