// Navigation (mobil)
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.nav-toggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            const open = document.body.classList.toggle('nav-open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }
});

// Mörtelrechner
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calc');
    if (!form) return;

    const MODES = {
        fuge:  { b: 'Breite', c: 'Tiefe', factor: 1, defaults: [15, 20],
                 hint: 'Rechteckige Fuge, z. B. Natursteinmauer, Klinker oder Stossfuge.' },
        vfuge: { b: 'Breite oben', c: 'Tiefe', factor: 0.5, defaults: [30, 20],
                 hint: 'V-Fuge an Betonfertigteilen, die in der Tiefe gegen null ausläuft.' },
        unter: { b: 'Schwellenbreite', c: 'Fugenhöhe', factor: 1, defaults: [100, 20],
                 hint: 'Untermörtelung von Schwelle, Element oder Platte. Für die WPS mindestens 11 mm Fugenhöhe.' },
    };
    const $ = id => document.getElementById(id);
    const val = id => Math.max(0, parseFloat(String($(id).value).replace(',', '.')) || 0);
    const fmt = (n, d = 0) => n.toLocaleString('de-CH', { minimumFractionDigits: d, maximumFractionDigits: d });
    const mode = () => form.querySelector('[name=mode]:checked').value;

    function calc() {
        const m = MODES[mode()];
        const liters = val('calc-a') * val('calc-b') * val('calc-c') / 1000 * m.factor * (1 + val('calc-extra') / 100);
        const kg = Math.ceil(liters * val('calc-yield'));
        const sack = val('calc-sack');
        const sacks = sack ? Math.ceil(kg / sack) : 0;
        $('out-liters').textContent = fmt(liters, 1);
        $('out-kg').textContent = fmt(kg);
        $('out-sacks').textContent = fmt(sacks);
        $('out-sacks-unit').textContent = `${sacks === 1 ? 'Sack' : 'Säcke'} à ${sack} kg`;
        $('out-fills').textContent = fmt(Math.ceil(liters / 50));
    }

    function setMode() {
        const m = MODES[mode()];
        $('calc-b-label').textContent = m.b;
        $('calc-c-label').textContent = m.c;
        $('calc-b').value = m.defaults[0];
        $('calc-c').value = m.defaults[1];
        $('calc-hint').textContent = m.hint;
        calc();
    }

    form.querySelectorAll('[name=mode]').forEach(r => r.addEventListener('change', setMode));
    form.addEventListener('input', calc);
    setMode();
});

// Bildergalerie
document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('.gallery img');
    if (!images.length) return;

    const box = document.createElement('div');
    box.className = 'lightbox';
    box.hidden = true;
    box.innerHTML = '<button type="button" aria-label="Schliessen"><svg class="i"><use href="assets/icons.svg#close"/></svg></button><img alt="">';
    document.body.appendChild(box);
    const big = box.querySelector('img');

    const close = () => { box.hidden = true; document.body.style.overflow = ''; };
    images.forEach(img => img.addEventListener('click', () => {
        big.src = img.src;
        big.alt = img.alt;
        box.hidden = false;
        document.body.style.overflow = 'hidden';
    }));
    box.addEventListener('click', e => { if (e.target !== big) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !box.hidden) close(); });
});

// Kontaktformular: öffnet das Mailprogramm mit vorausgefüllter Nachricht
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const topic = new URLSearchParams(location.search).get('type');
    const select = form.querySelector('[name=betreff]');
    if (topic === 'miete') select.value = 'Mietanfrage WPS-Mörtelpumpe';
    if (topic === 'kauf') select.value = 'Offerte WPS-Mörtelpumpe';

    form.addEventListener('submit', e => {
        e.preventDefault();
        const d = new FormData(form);
        const sender = [
            `${d.get('vorname')} ${d.get('nachname')}`,
            d.get('firma'),
            d.get('telefon'),
            d.get('email'),
        ].filter(Boolean).join('\n');
        const body = `${d.get('nachricht')}\n\n---\n${sender}`;
        location.href = `mailto:info@wilcowa.ch?subject=${encodeURIComponent(d.get('betreff'))}&body=${encodeURIComponent(body)}`;
    });
});
