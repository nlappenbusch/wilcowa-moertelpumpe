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

// Mörtel-Bedarfsrechner
function syncInput(type, source) {
    const input = document.getElementById(`calc-${type}-input`);
    const range = document.getElementById(`calc-${type}-range`);
    if (source === 'range') {
        input.value = range.value;
    } else {
        range.value = input.value;
    }
    calculateMortar();
}

function calculateMortar() {
    const length = parseFloat(document.getElementById('calc-length-input').value) || 0;
    const width = parseFloat(document.getElementById('calc-width-input').value) || 0;
    const depth = parseFloat(document.getElementById('calc-depth-input').value) || 0;
    const density = parseFloat(document.getElementById('calc-density').value) || 1.8;
    const wastage = parseFloat(document.getElementById('calc-wastage').value) || 0;

    // L (m) × B (mm) × T (mm) / 1000 = Liter
    const liters = (length * width * depth) / 1000 * (1 + wastage / 100);
    const kg = liters * density;

    const fmt = (n, d) => n.toLocaleString('de-CH', { minimumFractionDigits: d, maximumFractionDigits: d });
    document.getElementById('result-liters').textContent = fmt(liters, 1);
    document.getElementById('result-kg').textContent = fmt(kg, 1);
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('result-liters')) calculateMortar();
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
