(() => {
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let choice;
  function readChoice() {
    try {
      const saved = localStorage.getItem('theme');
      return saved === 'light' || saved === 'dark' ? saved : undefined;
    } catch {
      return choice;
    }
  }
  choice = readChoice();

  function applyTheme() {
    const theme = choice || (system.matches ? 'dark' : 'light');
    root.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]').content = theme === 'dark' ? '#111923' : '#ffffff';
    document.querySelectorAll('[data-theme-choice]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.themeChoice === theme));
    });
  }

  applyTheme();
  window.addEventListener('pageshow', () => {
    // Back/forward may restore a page whose theme predates the saved choice.
    choice = readChoice();
    applyTheme();
  });
  system.addEventListener('change', () => {
    if (!choice) applyTheme();
  });
  document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('.site-header');
    // Keep sticky navigation and anchor targets below the header after font or viewport changes.
    new ResizeObserver(() => {
      root.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
    }).observe(header);
    const controls = document.querySelector('.theme-switch');
    controls.hidden = false;
    controls.addEventListener('click', event => {
      const button = event.target.closest('[data-theme-choice]');
      if (!button) return;
      choice = button.dataset.themeChoice;
      applyTheme();
      try {
        localStorage.setItem('theme', choice);
      } catch {
        // Keep the choice for this page even if it cannot be saved.
      }
    });
    applyTheme();
  });
})();
