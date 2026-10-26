// Mobilā izvēlne
const menuBtn = document.getElementById('menu-btn');
const nav = document.getElementById('main-nav');
if (menuBtn && nav) {
  menuBtn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
}

// Gads kājenē
const yr = document.getElementById('yr');
if (yr) yr.textContent = new Date().getFullYear();

// Kontaktforma: sagatavo e-pastu lietotāja pasta programmā (bez trešo pušu servisiem)
const form = document.getElementById('contact-form');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const d = new FormData(form);
    const subject = `Pieprasījums: ploteris ${d.get('modelis')}`;
    const body = [
      `Interesējošais modelis: ${d.get('modelis')}`,
      `Vārds, uzvārds: ${d.get('vards')}`,
      `Tālrunis: ${d.get('talrunis')}`,
      '',
      d.get('jautajums') || ''
    ].join('\n');
    window.location.href = `mailto:sales@bratus.lv?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
}
