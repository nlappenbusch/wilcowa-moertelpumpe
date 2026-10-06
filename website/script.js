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

// Mörtelrechner: Vergleich Handarbeit / WPS
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calc');
    if (!form) return;

    // WPS-Werte nach Herstellerunterlagen, Handwerte sind Annahmen zum Überschreiben
    const MODES = {
        unter: {
            dims: [['Länge', 'm', 50], ['Schwellenbreite', 'mm', 100], ['Fugenhöhe', 'mm', 20]],
            factor: 1, rateUnit: 'm/h',
            hand: 6, wps: 20, wpsTag: 'Hersteller', wpsHint: 'Hersteller: bis 25 m/h',
            name: 'Untermörtelung', lenRange: [1, 300], rateRange: [1, 40],
        },
        vfuge: {
            dims: [['Länge', 'm', 100], ['Breite oben', 'mm', 30], ['Tiefe', 'mm', 20]],
            factor: 0.5, rateUnit: 'm/h',
            hand: 10, wps: 25, wpsTag: 'Hersteller', wpsHint: 'Hersteller: ca. 200 m pro Tag zu zweit',
            name: 'V-Fugen', lenRange: [10, 1000], rateRange: [1, 50],
        },
        fuge: {
            dims: [['Länge', 'm', 50], ['Breite', 'mm', 15], ['Tiefe', 'mm', 20]],
            factor: 1, rateUnit: 'm/h',
            hand: 4, wps: 10, wpsTag: 'Annahme', wpsHint: 'Hersteller nennt keinen Wert',
            name: 'Fugen', lenRange: [1, 300], rateRange: [1, 30],
        },
        zarge: {
            dims: [['Anzahl Zargen', 'Stk.', 12]],
            perPiece: 22, rateUnit: 'min/Stk.',
            hand: 90, wps: 47, wpsTag: 'Hersteller', wpsHint: 'Hersteller: 47 min pro Standardzarge',
            name: 'Stahlzargen', lenRange: [1, 100], rateRange: [15, 240],
        },
    };

    const $ = id => document.getElementById(id);
    const num = id => Math.max(0, parseFloat(String($(id).value).replace(',', '.')) || 0);
    const fmt = (n, d = 0) => n.toLocaleString('de-CH', { minimumFractionDigits: d, maximumFractionDigits: d });
    const mode = () => form.querySelector('[name=mode]:checked').value;

    // Schieberegler mit Zahlenfeld koppeln
    const ranges = [...form.querySelectorAll('.range')];
    const fill = r => r.style.setProperty('--p', `${(r.value - r.min) / (r.max - r.min) * 100}%`);
    const syncRange = id => {
        const r = $(`${id}-range`);
        if (!r) return;
        r.value = $(id).value;
        fill(r);
    };
    const setRange = (id, [min, max]) => {
        const r = $(`${id}-range`);
        r.min = min;
        r.max = max;
        syncRange(id);
    };
    ranges.forEach(r => {
        const id = r.id.replace(/-range$/, '');
        r.addEventListener('input', () => {
            $(id).value = r.value;
            fill(r);
        });
        $(id).addEventListener('input', () => syncRange(id));
        fill(r);
    });

    function setMode() {
        const m = MODES[mode()];
        ['a', 'b', 'c'].forEach((k, i) => {
            const d = m.dims[i];
            $(`calc-${k}-field`).hidden = !d;
            if (!d) return;
            $(`calc-${k}-label`).textContent = d[0];
            $(`calc-${k}-unit`).textContent = d[1];
            $(`calc-${k}`).value = d[2];
        });
        $('hand-rate').value = m.hand;
        $('wps-rate').value = m.wps;
        $('hand-rate-unit').textContent = m.rateUnit;
        $('wps-rate-unit').textContent = m.rateUnit;
        $('hand-rate-label').textContent = m.perPiece ? 'Zeit pro Zarge' : 'Leistung im Team';
        $('wps-rate-label').textContent = m.perPiece ? 'Zeit pro Zarge' : 'Leistung im Team';
        $('wps-rate-tag').textContent = m.wpsTag;
        $('wps-rate-tag').className = 'tag' + (m.wpsTag === 'Hersteller' ? ' tag-source' : '');
        $('wps-rate-hint').textContent = m.wpsHint;
        setRange('calc-a', m.lenRange);
        setRange('hand-rate', m.rateRange);
        setRange('wps-rate', m.rateRange);
        calc();
    }

    function bar(id, value, max) {
        $(id).style.width = max > 0 ? `${Math.max(2, value / max * 100)}%` : '0';
    }

    function calc() {
        const key = mode();
        const m = MODES[key];
        const qty = num('calc-a');
        const liters = m.perPiece ? qty * m.perPiece : qty * num('calc-b') * num('calc-c') / 1000 * m.factor;
        const hours = rate => {
            if (!rate) return 0;
            return m.perPiece ? qty * rate / 60 : qty / rate;
        };
        const handH = hours(num('hand-rate'));
        const wpsH = hours(num('wps-rate'));
        const kg = loss => liters * num('calc-yield') * (1 + loss / 100);
        const handKg = kg(num('hand-loss'));
        const wpsKg = kg(num('wps-loss'));
        const cost = h => h * num('calc-team') * num('calc-wage');
        const saveChf = cost(handH) - cost(wpsH);

        $('out-save-chf').textContent = `CHF ${fmt(Math.round(saveChf))}`;
        $('out-save-h').textContent = fmt(handH - wpsH, 1);
        $('out-save-kg').textContent = fmt(handKg - wpsKg);
        $('out-hand-h').textContent = `${fmt(handH, 1)} h`;
        $('out-wps-h').textContent = `${fmt(wpsH, 1)} h`;
        $('out-hand-kg').textContent = `${fmt(handKg)} kg`;
        $('out-wps-kg').textContent = `${fmt(wpsKg)} kg`;
        bar('bar-hand-h', handH, Math.max(handH, wpsH));
        bar('bar-wps-h', wpsH, Math.max(handH, wpsH));
        bar('bar-hand-kg', handKg, Math.max(handKg, wpsKg));
        bar('bar-wps-kg', wpsKg, Math.max(handKg, wpsKg));

        const sacks30 = Math.ceil(wpsKg / 30);
        $('out-sacks').textContent = `${fmt(Math.ceil(wpsKg))} kg, ${sacks30} ${sacks30 === 1 ? 'Sack' : 'Säcke'} à 30 kg`;

        const warn = $('calc-warn');
        if (key === 'unter' && num('calc-c') > 0 && num('calc-c') < 11) {
            warn.textContent = 'Für das Untermörteln mit der WPS sollte die Fuge mindestens 11 mm hoch sein.';
            warn.hidden = false;
        } else {
            warn.hidden = true;
        }

        const size = m.perPiece ? `${fmt(qty)} Stahlzargen` : `${fmt(qty, 1)} m ${m.name}, ${fmt(num('calc-b'))} × ${fmt(num('calc-c'))} mm`;
        const msg = `Anfrage aus dem Mörtelrechner: ${size}, ca. ${fmt(liters, 1)} l Mörtel. Ich interessiere mich für die WPS-Mörtelpumpe.`;
        $('calc-cta').href = `kontakt.html?type=miete&msg=${encodeURIComponent(msg)}`;
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
    const msg = new URLSearchParams(location.search).get('msg');
    if (msg) form.querySelector('[name=nachricht]').value = msg;

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
