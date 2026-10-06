# Erzeugt alle Seiten in website/ (einheitlicher Header/Footer). Aufruf: python tools/build_site.py
#
# Technische Angaben stammen aus den Unterlagen des Herstellers Winiger Pump System AG
# (www.wps-ag.ch, Flyer WPS-U-2.2019d und WPS-HT-4.2018d) sowie den Testberichten der
# Berner Fachhochschule (KTI-Projekt 8971.1, 2009). Texte bitte nicht wörtlich vom Hersteller übernehmen.
import json, pathlib, hashlib, re, shutil, subprocess, urllib.parse, html as h

OUT = pathlib.Path(__file__).resolve().parent.parent / "website"
BASE = "https://moertelpumpe.ch"

# Öffentliche Adressen (ohne .html). Interne Schlüssel = alte Dateinamen; nginx leitet alte URLs per 301 um.
URLS = {
    "index": "",
    "produkte": "wps-moertelpumpe",
    "anwendungen": "anwendungen",
    "anwendung-untermoerteln": "untermoerteln-holzschwellen",
    "anwendung-stahlzargen": "stahlzargen-einmoerteln",
    "anwendung-naturstein": "natursteinmauer-verfugen",
    "anwendung-klinker": "klinker-verfugen",
    "anwendung-betonfugen": "betonfugen-ausmoerteln",
    "anwendung-spannbeton": "deckenfugen-ausmoerteln",
    "anwendung-maueranker": "maueranker-verpressen",
    "anwendung-daemmplatten": "daemmplatten-kleben",
    "moertel-bedarf-rechner": "moertelrechner",
    "faq": "faq",
    "kontakt": "kontakt",
    "impressum": "impressum",
}
OLD_EXTRA = {"anwendung-fugen": "natursteinmauer-verfugen"}  # 2026 entfernte Seite

def relink(text):
    """Alle internen Verweise auf die neuen Adressen umschreiben (Links, Canonicals, JSON-LD, Sitemap, llms.txt)."""
    for old in sorted(URLS, key=len, reverse=True):
        new = URLS[old]
        text = re.sub(rf'(https://moertelpumpe\.ch/){re.escape(old)}\.html', rf'\g<1>{new}', text)
        text = re.sub(rf'((?:href|action)="){re.escape(old)}\.html', rf'\g<1>/{new}', text)
    return text

# Cache-Busting: nginx liefert CSS/JS mit 30 Tagen Cache aus
def ver(name):
    return hashlib.md5((OUT / name).read_bytes()).hexdigest()[:8]
PHONE, PHONE_HREF = "+41 43 388 70 60", "tel:+41433887060"
MAIL = "info@wilcowa.ch"
WPS = "https://www.wps-ag.ch"
BFH1 = WPS + "/_files/ugd/2c6046_10690fbcfa7a4cc7a547367ef935d9da.pdf"
BFH2 = WPS + "/_files/ugd/2c6046_1f045459d32246bab141014ac17bd106.pdf"

def icon(name):
    return f'<svg class="i" aria-hidden="true"><use href="assets/icons.svg#{name}"/></svg>'

# slug, Menütitel, Titel, Kurztext, Bild
APPS = [
    ("anwendung-untermoerteln", "Untermörteln", "Untermörteln von Schwellen und Elementen", "Holzschwellen, Betonelemente, Stahlplatten und Pfetten vollflächig unterfüttern.", "Beton_Stahl_Konstruktion"),
    ("anwendung-stahlzargen", "Stahlzargen", "Stahlzargen einmörteln", "Zargen auch in Sichtbauweise und bei 1 bis 2 cm Spalt sauber hinterfüllen.", "Stahlschalung_Saeule"),
    ("anwendung-naturstein", "Naturstein und Randsteine", "Natur- und Bruchsteinmauern verfugen", "Mauerwerk, Gewölbe und Randsteine maschinell ausfugen.", "Natursteinwand_Fugen"),
    ("anwendung-klinker", "Klinker", "Klinker-Verblender verfugen", "Schmale Fassadenfugen von 5 bis 10 mm mit angepasster Fugendüse.", "Klinker-Verblender_gefugt"),
    ("anwendung-betonfugen", "Betonfugen", "Fugen von Betonelementen", "V-Fugen und Stossfugen an Betonfertigteilen ausmörteln.", "Fugen_Deckenelemente"),
    ("anwendung-spannbeton", "Deckenfugen", "Deckenplatten-Fugen ausmörteln", "Fugen und Verankerungen bei Spannbeton- und Porenbetondecken.", "Ausgiessen_Spannbetonplatten"),
    ("anwendung-maueranker", "Anker", "Mauer- und Felsanker verpressen", "Bohrlöcher mit der Rohrdüse von hinten nach vorne füllen.", "Mauer-Anker_verpressen"),
    ("anwendung-daemmplatten", "Dämmplatten", "Mörtelkleber auf Dämmplatten", "Kleber dosiert auf Dämm- und Brandschutzplatten auftragen.", "Daemmplatten_Kleber"),
]

PDFS = {
    "untermoerteln": ("assets/Flyer_Untermorteln_2019.pdf", "Flyer Untermörteln von Holzschwellen", "PDF, 1.3 MB"),
    "fugen": ("assets/Anwendung_Fugen.pdf", "Anwendungsblatt Fugen mit getesteten Fugenmörteln", "PDF, 5 Seiten"),
    "tiefbau": ("assets/Flyer_Strassen-Hoch-Tiefbau.pdf", "Flyer Hochbau, Strassen- und Tiefbau", "PDF"),
    "bfh1": (BFH1, "Testbericht 1, Berner Fachhochschule (2009)", "PDF, extern"),
    "bfh2": (BFH2, "Testbericht 2, Berner Fachhochschule (2009)", "PDF, extern"),
}

# Öffnungszeiten: einmal definiert, überall gleich dargestellt. Live-Status per script.js (Zeitzone Zürich).
HOURS = [("Mo–Do", "07:00–12:00", "13:00–17:00"), ("Fr", "07:00–12:00", "13:00–16:00"), ("Sa–So", "geschlossen", "")]
HOURS_DATA = "1-4:07:00-12:00,13:00-17:00;5:07:00-12:00,13:00-16:00"

def hours_html(cls=""):
    rows = "".join(f'<tr><th scope="row">{d}</th><td>{a}</td><td>{b}</td></tr>' for d, a, b in HOURS)
    return (f'<div class="hours {cls}"><p class="open-status" data-hours="{HOURS_DATA}" hidden></p>'
            f'<table class="hours-table"><caption class="sr-only">Öffnungszeiten</caption><tbody>{rows}</tbody></table></div>')

def downloads(*keys):
    lis = "".join(f'<li><a href="{PDFS[k][0]}" target="_blank" rel="noopener">{icon("file")}{PDFS[k][1]}<span>{PDFS[k][2]}</span></a></li>' for k in keys)
    return f'<ul class="downloads">{lis}</ul>'

def head(p):
    canonical = BASE + "/" + ("" if p["file"] == "index.html" else p["file"])
    share = p["file"].replace(".html", ".jpg")
    og_img = f"{BASE}/assets/share/{share}"
    og_alt = h.escape(p.get("share", (p["title"], ""))[0])
    robots = '\n    <meta name="robots" content="noindex, follow">' if p.get("noindex") else ""
    ld = "".join(f'\n    <script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n    </script>' for x in p.get("ld", []))
    return f'''<!DOCTYPE html>
<html lang="de-CH">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p["title"]}</title>
    <meta name="description" content="{h.escape(p["desc"])}">{robots}
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="{p.get("og_type", "website")}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{h.escape(p["title"])}">
    <meta property="og:description" content="{h.escape(p["desc"])}">
    <meta property="og:image" content="{og_img}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{og_alt}">
    <meta property="og:site_name" content="WPS-Mörtelpumpe · Wilcowa AG">
    <meta property="og:locale" content="de_CH">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{h.escape(p["title"])}">
    <meta name="twitter:description" content="{h.escape(p["desc"])}">
    <meta name="twitter:image" content="{og_img}">
    <link rel="icon" href="favicon.ico" sizes="32x32">
    <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
    <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
    <meta name="theme-color" content="#27446f">
    <link rel="preload" href="assets/fonts/roboto-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="assets/fonts/barlow-semi-condensed-600-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="style.css?v={ver('style.css')}">{ld}
</head>
<body>
'''

# Querschnitt-Icons fürs Menü (grau = Bauteil, orange = Mörtel)
APP_ICONS = {
    "anwendung-untermoerteln": '<rect x="18" y="8" width="36" height="22" class="s-wood"/><rect x="18" y="30" width="36" height="6" class="s-mortar"/><rect x="2" y="36" width="68" height="10" class="s-solid"/>',
    "anwendung-stahlzargen": '<path d="M8 46V4h56v42h-8V12H16v34z" class="s-solid"/><path d="M16 46V12h40v34h-4V16H20v30z" class="s-mortar"/><path d="M20 46V16h32v30h-3V19H23v27z" class="s-steel"/>',
    "anwendung-naturstein": '<rect x="2" y="2" width="68" height="44" class="s-mortar"/><path d="M4 4h22l2 14-4 6H4zM30 4h20l-2 12H31zM53 4h15v18H51zM4 27h18l4 8-2 9H4zM28 27l4-8h16l5 10-3 15H28zM56 25h12v19H54l-2-10z" class="s-solid"/>',
    "anwendung-klinker": '<rect x="2" y="4" width="68" height="40" class="s-mortar"/><path d="M4 6h20v10H4zM27 6h20v10H27zM50 6h18v10H50zM4 19h8v10H4zM15 19h20v10H15zM38 19h20v10H38zM61 19h7v10h-7zM4 32h20v10H4zM27 32h20v10H27zM50 32h18v10H50z" class="s-solid"/>',
    "anwendung-betonfugen": '<path d="M4 10h20l12 22v12H4z" class="s-solid"/><path d="M68 10H48L36 32v12h32z" class="s-solid"/><path d="M24 10h24L36 32z" class="s-mortar"/>',
    "anwendung-spannbeton": '<path d="M2 16h31v22H2zM39 16h31v22H39z" class="s-solid"/><path d="M33 16h6v22h-6z" class="s-mortar"/><circle cx="12" cy="27" r="4" class="s-hole"/><circle cx="24" cy="27" r="4" class="s-hole"/><circle cx="48" cy="27" r="4" class="s-hole"/><circle cx="60" cy="27" r="4" class="s-hole"/>',
    "anwendung-maueranker": '<rect x="22" y="2" width="48" height="44" class="s-solid"/><rect x="22" y="19" width="40" height="10" class="s-mortar"/><path d="M4 24h56" class="s-rod"/><path d="M8 18v12" class="s-rod"/>',
    "anwendung-daemmplatten": '<rect x="2" y="6" width="22" height="38" class="s-solid"/><rect x="34" y="6" width="22" height="38" class="s-wood"/><circle cx="29" cy="14" r="3.5" class="s-mortar"/><circle cx="29" cy="25" r="3.5" class="s-mortar"/><circle cx="29" cy="36" r="3.5" class="s-mortar"/>',
}

MENU_GROUPS = [
    ("Holz- und Hochbau", ["anwendung-untermoerteln", "anwendung-stahlzargen", "anwendung-daemmplatten"]),
    ("Fugen", ["anwendung-naturstein", "anwendung-klinker", "anwendung-betonfugen", "anwendung-spannbeton"]),
    ("Verankerung", ["anwendung-maueranker"]),
]

MENU_LABELS = {
    "anwendung-untermoerteln": ("Untermörteln", "Holzschwellen, Elemente, Stahlplatten"),
    "anwendung-stahlzargen": ("Stahlzargen einmörteln", "auch Sichtbauweise, 1–2 cm Spalt"),
    "anwendung-daemmplatten": ("Kleber auf Dämmplatten", "Dämm- und Brandschutzplatten"),
    "anwendung-naturstein": ("Natur- und Bruchstein", "Mauern, Gewölbe, Randsteine"),
    "anwendung-klinker": ("Klinker-Verblender", "Fassadenfugen 5–10 mm"),
    "anwendung-betonfugen": ("Betonfugen", "V-Fugen und Stossfugen"),
    "anwendung-spannbeton": ("Deckenplatten-Fugen", "Spannbeton, Porenbeton"),
    "anwendung-maueranker": ("Mauer- und Felsanker", "Verpressen mit der Rohrdüse"),
}

PRODUCT_MENU = [
    ("produkte.html", "Übersicht und Funktionsprinzip", "So arbeitet die Pumpe"),
    ("produkte.html#technische-daten", "Technische Daten", "Leistung, Anschluss, Gewicht"),
    ("produkte.html#zubehoer", "Düsen und Zubehör", "Düsen, Kompressor, Mischer"),
    ("faq.html", "Häufige Fragen", "Kompressor, Mörtel, Miete"),
]

HOME_CALC = ('<a class="app-calc" href="moertel-bedarf-rechner.html"><strong>Lohnt sich die WPS für Ihr Projekt?</strong>'
             '<span>Arbeitszeit, Kosten und Mörtel im Vergleich zur Handarbeit berechnen.</span><em>Zum Mörtelrechner</em></a>')

def app_icon(slug):
    return f'<svg class="menu-icon" viewBox="0 0 72 48" aria-hidden="true">{APP_ICONS[slug]}</svg>'

SKIP = '    <a class="skip-link" href="#inhalt">Zum Inhalt springen</a>\n'

def header(active):
    info = {s: (t, txt) for s, n, t, txt, img in APPS}
    def item(href, label, key):
        cls = ' class="active"' if key == active else ""
        return f'<li><a href="{href}"{cls}>{label}</a></li>'
    feature = ('<a class="mega-feature" href="moertel-bedarf-rechner.html"><strong>Was spart die WPS?</strong>'
               '<span>Arbeitszeit, Kosten und Mörtel im Vergleich zur Handarbeit.</span><em>Zum Mörtelrechner</em></a>')
    groups = ""
    for n, (title, slugs) in enumerate(MENU_GROUPS):
        links = "".join(f'<li><a href="{s}.html">{app_icon(s)}<span><strong>{MENU_LABELS[s][0]}</strong><small>{MENU_LABELS[s][1]}</small></span></a></li>' for s in slugs)
        extra = feature if n == len(MENU_GROUPS) - 1 else ""
        groups += f'<div class="mega-group"><p class="mega-title">{title}</p><ul>{links}</ul>{extra}</div>'
    prod = "".join(f'<li><a href="{u}"><strong>{t}</strong><small>{d}</small></a></li>' for u, t, d in PRODUCT_MENU)
    chev = '<svg class="i" aria-hidden="true"><use href="assets/icons.svg#chevron"/></svg>'
    act = lambda k: ' active' if k == active else ''
    return f'''    <header class="site-header">
        <div class="container">
            <a class="logo" href="index.html"><img src="assets/wilcowa-logo.png" alt="Wilcowa AG" width="1600" height="400"></a>
            <nav class="main-nav" aria-label="Hauptnavigation">
                <ul>
                    <li class="has-sub has-drop">
                        <a class="nav-top{act("produkt")}" href="produkte.html" aria-haspopup="true">WPS-Mörtelpumpe {chev}</a>
                        <div class="drop"><ul>{prod}</ul></div>
                    </li>
                    <li class="has-sub has-mega">
                        <a class="nav-top{act("anwendungen")}" href="anwendungen.html" aria-haspopup="true">Anwendungen {chev}</a>
                        <div class="mega">
                            <div class="container mega-inner">
                                <div class="mega-groups">{groups}</div>
                            </div>
                            <div class="container mega-foot"><a href="anwendungen.html">Alle Anwendungen und Bilder ansehen</a></div>
                        </div>
                    </li>
                    {item("moertel-bedarf-rechner.html", "Mörtelrechner", "rechner")}
                    {item("faq.html", "Fragen", "faq")}
                    {item("kontakt.html", "Kontakt", "kontakt")}
                    <li class="nav-mobile-only"><a href="{PHONE_HREF}">Telefon {PHONE}</a></li>
                </ul>
            </nav>
            <div class="header-contact">
                <a class="header-phone" href="{PHONE_HREF}">{PHONE}</a>
                <a class="btn btn-accent" href="kontakt.html">Anfrage</a>
            </div>
            <a class="nav-call" href="{PHONE_HREF}" aria-label="Anrufen: {PHONE}"><svg class="i" aria-hidden="true"><use href="assets/icons.svg#phone"/></svg></a>
            <button class="nav-toggle" type="button" aria-label="Menü" aria-expanded="false"><svg class="i i-menu" aria-hidden="true"><use href="assets/icons.svg#menu"/></svg><svg class="i i-close" aria-hidden="true"><use href="assets/icons.svg#close"/></svg></button>
        </div>
    </header>
'''

def footer():
    apps = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, n, t, *_ in APPS[:6])
    return f'''
    <section class="cta">
        <div class="container">
            <div>
                <h2>Beratung, Miete und Verkauf</h2>
                <p>Wir beraten Sie zu Düsen, Kompressor und Mörtel für Ihre Anwendung. Die WPS-Mörtelpumpe können Sie kaufen oder für Ihr Projekt mieten.</p>
            </div>
            <div class="cta-contact">
                <a class="cta-phone" href="{PHONE_HREF}">{icon("phone")}{PHONE}</a>
                {hours_html("hours-dark")}
                <div class="btn-row">
                    <a class="btn btn-accent" href="kontakt.html">Anfrage senden</a>
                    <a class="btn btn-outline-light" href="mailto:{MAIL}">{MAIL}</a>
                </div>
            </div>
        </div>
    </section>

    <footer class="site-footer">
        <div class="container footer-grid">
            <div class="footer-brand">
                <a href="index.html"><img src="assets/wilcowa-logo.png" alt="Wilcowa AG" width="1600" height="400" loading="lazy"></a>
                <address>Wilcowa AG Baumaschinen<br>Riedthofstrasse 172<br>8105 Regensdorf<br><a href="{PHONE_HREF}">{PHONE}</a><br><a href="mailto:{MAIL}">{MAIL}</a></address>
            </div>
            <div>
                <h2>WPS-Mörtelpumpe</h2>
                <ul>
                    <li><a href="produkte.html">Funktionsprinzip</a></li>
                    <li><a href="produkte.html#technische-daten">Technische Daten</a></li>
                    <li><a href="produkte.html#zubehoer">Düsen und Zubehör</a></li>
                    <li><a href="moertel-bedarf-rechner.html">Mörtelrechner</a></li>
                    <li><a href="faq.html">Häufige Fragen</a></li>
                </ul>
            </div>
            <div>
                <h2>Anwendungen</h2>
                <ul>{apps}</ul>
            </div>
            <div>
                <h2>Öffnungszeiten</h2>
                {hours_html("hours-dark")}
            </div>
        </div>
        <div class="footer-bottom">
            <div class="container">
                <span>© 2026 Wilcowa AG Baumaschinen · <a href="https://wilcowa.ch/" target="_blank" rel="noopener">wilcowa.ch</a></span>
                <ul>
                    <li><a href="impressum.html">Impressum</a></li>
                    <li><a href="https://wilcowa.ch/datenschutzerklaerung/" target="_blank" rel="noopener">Datenschutz</a></li>
                </ul>
            </div>
        </div>
    </footer>

    <script src="script.js?v={ver('script.js')}"></script>
</body>
</html>
'''

def breadcrumbs(items):
    lis = "".join(f'<li><span aria-current="page">{l}</span></li>' if i == len(items) - 1 else f'<li><a href="{u}">{l}</a></li>' for i, (l, u) in enumerate(items))
    return f'<nav class="breadcrumbs" aria-label="Brotkrumen"><ol>{lis}</ol></nav>'

def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": l.replace("&amp;", "&"), "item": BASE + "/" + ("" if u == "index.html" else u)}
        for i, (l, u) in enumerate(items)]}

def page_head(crumbs, title, lead, extra=""):
    return f'''
    <section class="page-head">
        <div class="container">
            {breadcrumbs(crumbs)}
            <h1>{title}</h1>
            <p class="lead">{lead}</p>
            {extra}
        </div>
    </section>
'''

def side_contact():
    return f'''<section class="side-contact">
                    <h2>Beratung und Miete</h2>
                    <a class="side-contact-phone" href="{PHONE_HREF}">{icon("phone")}{PHONE}</a>
                    <p class="open-status side-contact-hours" data-hours="{HOURS_DATA}">Mo–Do 07–17 Uhr, Fr bis 16 Uhr</p>
                    <a class="btn btn-accent" href="kontakt.html">Anfrage senden</a>
                    <a class="side-contact-mail" href="mailto:{MAIL}">{icon("mail")}{MAIL}</a>
                </section>'''

def side_apps(current):
    lis = "".join(f'<li><a href="{s}.html"{" aria-current=" + chr(34) + "page" + chr(34) if s == current else ""}>{t}</a></li>' for s, n, t, *_ in APPS)
    return f'<section><h2>Anwendungen</h2><ul class="side-links">{lis}</ul></section>'

WEBSITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "name": "WPS-Mörtelpumpe · Wilcowa AG", "url": BASE + "/", "inLanguage": "de-CH",
              "publisher": {"@type": "Organization", "name": "Wilcowa AG Baumaschinen", "url": "https://wilcowa.ch/", "logo": BASE + "/assets/wilcowa-logo.png"}}

LOCAL_BUSINESS = {
    "@context": "https://schema.org", "@type": "LocalBusiness",
    "name": "Wilcowa AG Baumaschinen", "url": BASE + "/", "logo": BASE + "/assets/wilcowa-logo.png",
    "image": BASE + "/assets/Untermorteln_Stahltragerplatte.avif",
    "telephone": "+41433887060", "email": MAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "Riedthofstrasse 172", "addressLocality": "Regensdorf", "postalCode": "8105", "addressRegion": "ZH", "addressCountry": "CH"},
    "areaServed": "CH",
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "07:00", "closes": "17:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "07:00", "closes": "16:00"}],
    "description": "Verkauf und Vermietung der WPS-Mörtelpumpe mit Zubehör in der Schweiz.",
}

# Datenblatt nach Herstellerangaben (wps-ag.ch, Flyer WPS-U-2.2019d, WPS-HT-4.2018d)
SPEC_GROUPS = [
    ("Leistung", [
        ("Fördermenge", "0–15 l/min, stufenlos über den Luftdruck"),
        ("Förderdruck", "max. 2.5 bar"),
        ("Förderweite", "bis 4 m, bei Stahlzargen 3.2 m"),
        ("Dosierung", "Kugelhahn an der Düse, sofort stopp- und startbar"),
    ]),
    ("Mörtel", [
        ("Geeignet für", "Zement-Mauermörtel, Fugen-, Kleber- und Vergussmörtel, auch nicht maschinengängige"),
        ("Untermörteln", "ab 11 mm Fugenhöhe, bis über 400 mm Tiefe"),
    ]),
    ("Anschluss", [
        ("Antrieb", "Druckluft, kein Stromanschluss an der Pumpe"),
        ("Luftbedarf", "200 l/min bei 8–9 bar"),
        ("Kompressor", "ab 2.2 kW (230 V), für Fugenarbeiten 3 kW (400 V)"),
    ]),
    ("Gerät", [
        ("Behälter", "60 l, davon 50 l nutzbar"),
        ("Einfüllhöhe", "900 mm"),
        ("Abmessungen L × B × H", "600 × 520 × 1140 mm"),
        ("Gewicht", "50–55 kg, je nach Zubehör"),
        ("Bauweise", "Sackkarre, gerüsttauglich"),
        ("Rüsten / Reinigen", "je ca. 5–10 Minuten"),
    ]),
]

SPECS_SHORT = [
    ("Fördermenge", "0–15 l/min"),
    ("Förderdruck", "max. 2.5 bar"),
    ("Förderweite", "bis 4 m"),
    ("Nutzinhalt", "50 l"),
    ("Antrieb", "Druckluft, 200 l/min bei 8–9 bar"),
    ("Gewicht", "50–55 kg"),
]

def spec_table(groups=None, rows=None, title="Technische Daten", note="Herstellerangaben"):
    body = ""
    if groups:
        for g, items in groups:
            body += f'<tr class="spec-group"><th colspan="2" scope="rowgroup">{g}</th></tr>'
            body += "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in items)
    else:
        body = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    return f'''<table class="spec">
                    <thead><tr class="spec-head"><th colspan="2" scope="col"><span class="spec-note">{note}</span>{title}</th></tr></thead>
                    <tbody>{body}</tbody>
                </table>'''

# Häufige Fragen, nach Themen gruppiert. Antworten dürfen Links enthalten; für schema.org wird der Text ohne HTML verwendet.
FAQ_GROUPS = [
    ("geraet", "Gerät und Anschluss", [
        ("Braucht die WPS-Mörtelpumpe einen Kompressor?",
         "Ja. Die Pumpe wird mit Druckluft betrieben und braucht rund 200 l/min bei 8 bis 9 bar. Für Untermörteln und Stahlzargen reicht ein 230-V-Kompressor mit 2.2 kW, für Fugenarbeiten wird ein Kompressor mit 3 kW (400 V) empfohlen. <a href=\"produkte.html#kompressor\">Passende Kompressoren</a>"),
        ("Braucht die Pumpe einen Stromanschluss?",
         "Die Pumpe selbst nicht, sie arbeitet nur mit Druckluft. Strom braucht der Kompressor, je nach Modell 230 V oder 400 V."),
        ("Worin unterscheidet sich die WPS von einer Schnecken- oder Schlauchpumpe?",
         "Die WPS arbeitet ohne Schnecke, Rotor oder Kolben. Ein Druckluftvibrator macht den Mörtel fliessfähig, der Luftdruck fördert ihn. So entsteht keine Reibungswärme, der Mörtel entmischt sich nicht und das Pumpsystem verschleisst praktisch nicht. Den Mörtelfluss stoppen Sie am Kugelhahn, ohne die Pumpe abzustellen."),
        ("Wie weit kann ich den Mörtel fördern?",
         "Bis 4 m, bei Stahlzargen bis 3.2 m. Standardmässig wird ein Füllschlauch DN 25 mit 4 m Länge verwendet."),
        ("Wie schwer ist die Pumpe, und passt sie aufs Gerüst?",
         "Die Pumpe wiegt je nach Zubehör 50 bis 55 kg und ist als Sackkarre gebaut. Sie lässt sich so auf der Baustelle und auf dem Gerüst verschieben. Die Einfüllhöhe beträgt 900 mm."),
        ("Wie aufwendig ist die Reinigung?",
         "Inbetriebnahme und Reinigung dauern jeweils etwa 5 bis 10 Minuten. Weil der Mörtel ohne Schnecke oder Rotor gefördert wird, gibt es kaum Verschleissteile."),
    ]),
    ("moertel", "Mörtel und Anwendung", [
        ("Welche Mörtel lassen sich pumpen?",
         "Die WPS fördert auch Mörtel, die als nicht maschinengängig gelten, zum Beispiel normalen Zement-Mauermörtel. Viele handelsübliche Fugenmörtel sind bereits auf Pumpfähigkeit getestet, die Liste steht im <a href=\"assets/Anwendung_Fugen.pdf\" target=\"_blank\" rel=\"noopener\">Anwendungsblatt Fugen</a>. Entscheidend ist die richtige Konsistenz. Noch nicht getestete Mörtel sollten vor dem Einsatz geprüft werden."),
        ("Welche Düse brauche ich?",
         "Für Fugen die Fugendüse Ø 22 mm, für Klinker auf 4.5 mm zusammengedrückt. Zum Untermörteln die Breitschlitzdüse 10 × 155 mm bis ca. 120 mm Tiefe oder die Variante mit Schnabel bis über 400 mm. Für Anker die Rohrdüse DN 34. <a href=\"produkte.html#zubehoer\">Alle Düsen</a>"),
        ("Wie lässt sich die Fördermenge regeln?",
         "Über den Luftdruck im Behälter stufenlos von 0 bis 15 l/min. Mit dem Kugelhahn an der Düse wird der Mörtelfluss sofort gestoppt und wieder gestartet. Der Förderdruck ist auf 2.5 bar begrenzt."),
        ("Wie niedrig darf eine Fuge beim Untermörteln sein?",
         "Die Fuge sollte mindestens 11 mm hoch sein, damit die Breitschlitzdüse mit Schnabel unter die Schwelle geschoben werden kann. In den Versuchen der Berner Fachhochschule wurden Höhen von 10 bis 50 mm untersucht, gut gefüllt wurden vor allem 20 bis 40 mm."),
        ("Kann ich bei tiefen Temperaturen arbeiten?",
         "In den Versuchen der Berner Fachhochschule härtete der Mörtel auch bei 0 °C Aussentemperatur aus, sofern er beim Einpumpen mindestens 6 °C warm war. Massgebend sind immer die Angaben des Mörtelherstellers."),
        ("Wie viel schafft man mit der Pumpe?",
         "Laut Hersteller beim Untermörteln bis 25 Laufmeter pro Stunde. Bei V-Fugen an Betonfertigteilen schaffen zwei Personen rund 200 m pro Tag, eine Standard-Stahlzarge ist in rund 47 Minuten gesetzt und ausgemörtelt. Für Ihr Projekt rechnet es der <a href=\"moertel-bedarf-rechner.html\">Mörtelrechner</a>."),
    ]),
    ("miete", "Miete und Kauf", [
        ("Kann ich die Pumpe mieten?",
         "Ja. Sie können die WPS-Mörtelpumpe bei uns mieten, zum Beispiel für ein einzelnes Projekt oder um sie vor dem Kauf mit Ihrem Mörtel zu testen."),
        ("Was kostet die Miete oder der Kauf?",
         "Das hängt von Mietdauer und Ausrüstung ab, etwa ob Kompressor und Mischer dazukommen. Eine Offerte erhalten Sie telefonisch unter " + PHONE + " oder über das <a href=\"kontakt.html\">Anfrageformular</a>."),
        ("Bekomme ich eine Einweisung?",
         "Ja. Die Bedienung ist einfach, eine Einweisung bei der Übergabe genügt in der Regel. Bei anspruchsvollen Projekten beraten wir Sie gerne vorab zu Mörtel, Düse und Vorgehen."),
    ]),
]
FAQ = [(q, a) for _, _, items in FAQ_GROUPS for q, a in items]

def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text).strip()


# Kundenbewertung: Durchschnitt aus den gesammelten Rückmeldungen der Wilcowa AG (Excel).
# Strukturierte Daten (AggregateRating) erst ausgeben, wenn die Anzahl Bewertungen bekannt ist:
# Google verlangt ratingCount, und die Werte müssen zur sichtbaren Angabe passen.
RATING = {"value": "4.8", "best": "5", "count": 26}

def rating_badge(dark=False):
    stars = "".join('<svg class="star" aria-hidden="true"><use href="assets/icons.svg#star"/></svg>' for _ in range(5))
    count = f"{RATING['count']} Kundenbewertungen" if RATING["count"] else "Kundenbewertungen"
    cls = "rating rating-dark" if dark else "rating"
    return (f'<a class="{cls}" href="index.html#erfahrungen"><span class="stars" aria-hidden="true">{stars}</span>'
            f'<strong>{RATING["value"]}</strong><span>von {RATING["best"]}</span><span class="rating-src">{count}</span></a>')

# Belegte Aussagen, wörtlich zitiert. Keine erfundenen Kundenstimmen.
PROOF = [
    ("100 %", "Füllgrad ab 10 mm Fugenhöhe", "Schnabeldüse gewährleistet volle Unterstopfung ab 10 mm Unterstopfhöhe",
     "Berner Fachhochschule", "Testbericht 2, 2009", BFH2),
    ("200 m", "V-Fugen pro Tag zu zweit", "In der Regel verfugen 2 Betonkosmetiker pro Tag um die 200 m Beton-V-Fugen.",
     "Winiger Pump System AG", "Anwendung Betonfugen", WPS + "/betonfugen"),
    ("0 °C", "Aussentemperatur", "Die Verarbeitung funktioniert ab 0 °C Aussentemperatur (Mörteltemperatur mind. 6 °C)",
     "Berner Fachhochschule", "Testbericht 2, 2009", BFH2),
    ("günstiger", "als das herkömmliche Mörtelbett", "Das WPS-Mörtelbett ist günstiger als das herkömmliche Mörtelbett",
     "Berner Fachhochschule", "Testbericht 2, 2009", BFH2),
]

def proof_cards():
    stars = "".join('<svg class="star" aria-hidden="true"><use href="assets/icons.svg#star"/></svg>' for _ in range(5))
    count = f"{RATING['count']} Rückmeldungen" if RATING["count"] else "Rückmeldungen"
    rating = f'''
                <div class="proof-rating">
                    <p class="proof-rating-value">{RATING["value"]}<small>von {RATING["best"]}</small></p>
                    <p class="stars">{stars}</p>
                    <p>Durchschnitt der {count} von Kundinnen und Kunden der Wilcowa AG</p>
                    <a href="mailto:{MAIL}?subject=Erfahrung%20mit%20der%20WPS-M%C3%B6rtelpumpe">Sie arbeiten mit der WPS? Erzählen Sie uns von Ihrem Projekt.</a>
                </div>'''
    cards = "".join(f'''
                    <figure class="proof">
                        <p class="proof-figure">{fig}</p>
                        <p class="proof-label">{label}</p>
                        <blockquote><p>«{quote}»</p></blockquote>
                        <figcaption><strong>{who}</strong><a href="{url}" target="_blank" rel="noopener">{src}</a></figcaption>
                    </figure>''' for fig, label, quote, who, src, url in PROOF)
    return f'<div class="proof-wrap">{rating}\n                <div class="proofs">{cards}\n                </div>\n            </div>'

# ------------------------------------------------------------------ Startseite
def page_index():
    tiles = "".join(f'''
                <li{' class="tile-featured"' if k == 0 else ''}><a href="{s_}.html"><img src="assets/{img}.avif" alt="{t}" loading="lazy" width="900" height="675"><h3>{t}</h3><p>{txt}</p></a></li>''' for k, (s_, n, t, txt, img) in enumerate(APPS))
    tiles += '''
                <li class="tile-calc"><a href="moertel-bedarf-rechner.html"><h3>Lohnt sich die WPS für Ihr Projekt?</h3><p>Arbeitszeit, Kosten und Mörtel im Vergleich zur Handarbeit berechnen.</p><span>Zum Mörtelrechner</span></a></li>'''
    return f'''
    <main>
    <section class="hero">
        <div class="container">
            <div>
                <h1>WPS-Mörtelpumpe zum Untermörteln, Fugen und Einmörteln von Stahlzargen</h1>
                <p class="lead">Die druckluftbetriebene WPS-Mörtelpumpe fördert auch Mörtel, die sich mit herkömmlichen Maschinen nicht pumpen lassen. Der Mörtelfluss lässt sich jederzeit stoppen und wieder starten. Die Wilcowa AG in Regensdorf verkauft und vermietet die Pumpe mit Zubehör.</p>
                <div class="btn-row">
                    <a class="btn btn-accent" href="kontakt.html">Anfrage senden</a>
                    <a class="btn btn-outline-light" href="produkte.html">Technische Daten</a>
                </div>
                {rating_badge(dark=True)}
            </div>
            <img src="assets/Untermorteln_Stahltragerplatte.avif" alt="Untermörteln einer Stahlplatte mit der WPS-Mörtelpumpe" width="914" height="682" fetchpriority="high">
        </div>
    </section>

    <section class="section" id="erfahrungen">
        <div class="container">
            <div class="section-title">
                <h2>Erfahrungen aus Prüfung und Praxis</h2>
                <p>Bewertung unserer Kunden sowie Aussagen der Berner Fachhochschule und des Herstellers, im Wortlaut zitiert.</p>
            </div>
            {proof_cards()}
        </div>
    </section>

    <section class="section bg-alt">
        <div class="container intro">
            <div>
                <h2>So funktioniert die Pumpe</h2>
                <p>Ein druckluftbetriebener Vibrator versetzt den Mörtel im Behälter in Schwingung, der Überdruck im Behälter drückt ihn durch Schlauch und Düse. Da keine Schnecke und kein Rotor im Spiel sind, entsteht keine Reibungswärme, und der Mörtel entmischt sich nicht. Darum lassen sich auch klassische Baustellenmörtel verarbeiten.</p>
                <p>Der Förderdruck ist auf 2.5 bar begrenzt. Über einen Kugelhahn an der Düse dosieren Sie den Mörtel genau und unterbrechen ihn, ohne die Pumpe abzustellen.</p>
                <p><a href="produkte.html">Mehr zur WPS-Mörtelpumpe</a></p>
            </div>
            <div>
                {spec_table(rows=SPECS_SHORT, title="WPS-Mörtelpumpe")}
                <p class="table-note">Leistungsdaten hängen von Mörtel und Anwendung ab. <a href="produkte.html#technische-daten">Vollständiges Datenblatt</a></p>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-title">
                <h2>Anwendungen</h2>
                <p>Mit der passenden Düse eignet sich die WPS für eine ganze Reihe von Arbeiten im Hoch-, Holz- und Tiefbau. <a href="anwendungen.html">Alle Anwendungen</a></p>
            </div>
            <ul class="tiles">{tiles}
            </ul>
        </div>
    </section>

    <section class="section bg-alt">
        <div class="container two-col">
            <div>
                <h2>Kauf und Miete</h2>
                <p>Sie können die WPS-Mörtelpumpe bei uns kaufen oder mieten. Die Miete eignet sich für einzelne Projekte oder um die Pumpe vor dem Kauf mit Ihrem eigenen Mörtel auszuprobieren.</p>
                <p>Wir beraten Sie zur Ausrüstung für Ihre Anwendung, also zu Düsen, Kompressor und Mörtelmischer, und liefern das Zubehör.</p>
            </div>
            <div>
                <h3 style="margin-bottom:8px">Unterlagen</h3>
                {downloads("untermoerteln", "fugen", "bfh1", "bfh2")}
            </div>
        </div>
    </section>
    </main>
'''

# ------------------------------------------------------------------ Produkt
# Schema der Pumpe: Kompressor -> Druckluft -> Behälter mit Vibrator -> Schlauch -> Kugelhahn/Düse
PUMP_DIAGRAM = """<svg class="pump-diagram" viewBox="0 0 680 300" role="img" aria-labelledby="pd-t">
  <title id="pd-t">Funktionsschema der WPS-Mörtelpumpe: Kompressor, Behälter mit Vibrator, Schlauch, Düse mit Kugelhahn</title>
  <rect x="16" y="150" width="104" height="72" rx="8" class="pd-box"/>
  <text x="68" y="191" class="pd-label" text-anchor="middle">Kompressor</text>
  <path d="M120 170H170V46H262V64" class="pd-air"/>
  <path d="M256 58l6 9 6-9" class="pd-air-head"/>
  <rect x="200" y="64" width="124" height="176" rx="16" class="pd-tank"/>
  <rect x="208" y="122" width="108" height="110" rx="10" class="pd-mortar"/>
  <path d="M226 177l10-12 10 24 10-24 10 24 10-24 10 24 10-12" class="pd-vib"/>
  <path d="M262 240v14c0 34 70 34 120 14s110-20 150-26" class="pd-hose"/>
  <circle cx="546" cy="228" r="11" class="pd-valve"/>
  <path d="M546 217v22" class="pd-valve-line"/>
  <path d="M557 222h64l26 6-26 6h-64z" class="pd-nozzle"/>
  <path d="M650 228c8 0 14 4 14 10" class="pd-out"/>
  <g class="pd-num"><circle cx="190" cy="40" r="13"/><text x="190" y="45" text-anchor="middle">1</text></g>
  <g class="pd-num"><circle cx="340" cy="150" r="13"/><text x="340" y="155" text-anchor="middle">2</text></g>
  <g class="pd-num"><circle cx="420" cy="268" r="13"/><text x="420" y="273" text-anchor="middle">3</text></g>
  <g class="pd-num"><circle cx="546" cy="196" r="13"/><text x="546" y="201" text-anchor="middle">4</text></g>
</svg>"""

def page_produkt():
    crumbs = [("Start", "index.html"), ("WPS-Mörtelpumpe", "produkte.html")]
    nozzles = [
        ("Fugendüse Ø 22 × 1 mm", "Natursteinmauern, Randsteine, Betonfugen. Standardlänge 13 cm, andere Längen auf Wunsch. Für Klinkerfugen auf 4.5 mm Innenmass gedrückt."),
        ("Breitschlitzdüse 10 × 155 mm mit Absperrklappe", "Untermörteln bis ca. 120 mm Tiefe"),
        ("Breitschlitzdüse 8 × 155 mm mit Schnabel 110 × 9.5 mm", "Untermörteln ab 120 mm bis über 400 mm Tiefe, Mindestfugenhöhe 11 mm"),
        ("Rohrdüse DN 34", "Verpressen von Mauer- und Felsankern"),
        ("Füllschlauch DN 25, 4 m", "mit drehbaren GEKA-Kupplungen"),
        ("Stahlbügel und Edelstahlstosser", "Zubehör für die Montage von U-Stahlzargen, Zubehör für Blockzargen auf Anfrage"),
    ]
    comp = [
        ("Gentilin C330/03", "230 V, 2.2 kW, 200 l/min bei 5 bar, 32 kg", "Untermörteln, Stahlzargen"),
        ("FIAC Pony AB 515", "400 V, 3 kW, 375 l/min bei 8 bar, 72 kg", "Fugenarbeiten"),
        ("FIAC Pony AB 858", "400 V, 5.5 kW, 640 l/min bei 8 bar, 135 kg", "Spritzarbeiten und übrige Anwendungen"),
    ]
    noz = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td></tr>" for a, b in nozzles)
    com = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in comp)
    picks = "".join(f'<li><a href="{a}.html">{app_icon(a)}<span>{MENU_LABELS[a][0]}</span></a></li>'
                    for title, slugs in MENU_GROUPS for a in slugs)
    toc = [("funktion", "So funktioniert die Pumpe"), ("einsatz", "Einsatzbereiche"), ("eigenschaften", "Eigenschaften"),
           ("technische-daten", "Technische Daten"), ("zubehoer", "Düsen und Zubehör"), ("kompressor", "Kompressor und Mischer"),
           ("hersteller", "Hersteller")]
    toc_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
    return f'''
    <section class="page-head page-head-media page-head-product">
        <div class="container">
            <div class="page-head-text">
                {breadcrumbs(crumbs)}
                <h1>WPS-Mörtelpumpe</h1>
                <p class="lead">Druckluftbetriebene Mörtelpumpe der Winiger Pump System AG, Wald ZH. Patentiert, verschleissfrei und für Standardmörtel ausgelegt.</p>
                <div class="btn-row">
                    <a class="btn btn-accent" href="kontakt.html?type=miete">Miete oder Kauf anfragen</a>
                    <a class="btn btn-outline-light" href="#technische-daten">Technische Daten</a>
                </div>
                {rating_badge(dark=True)}
            </div>
            <img src="assets/Untermorteln_Holzbau.avif" alt="WPS-Mörtelpumpe mit Behälter, Fahrgestell und Schlauch" width="790" height="906" fetchpriority="high">
        </div>
    </section>

    <div class="section">
        <div class="container layout">
            <article class="prose">
                <h2 id="funktion">So funktioniert die Pumpe</h2>
                <figure class="diagram">
                    {PUMP_DIAGRAM}
                    <ol class="diagram-legend">
                        <li><strong>Druckluft</strong> vom Kompressor setzt den Behälter unter Druck, begrenzt auf max. 2.5 bar.</li>
                        <li><strong>Vibrator</strong> im Behälter macht den Mörtel fliessfähig, ohne ihn zu entmischen.</li>
                        <li><strong>Schlauch</strong> DN 25 fördert den Mörtel bis 4 m weit, ohne Schnecke oder Rotor.</li>
                        <li><strong>Kugelhahn</strong> an der Düse stoppt und startet den Mörtelfluss sofort.</li>
                    </ol>
                </figure>
                <p>Weil keine Schnecke und kein Rotor im Spiel sind, entsteht keine mechanische Reibungswärme. Auch Mörtel, die als nicht maschinengängig gelten, führen deshalb nicht zu Stopfern. Bei motorgetriebenen Schnecken- oder Schlauchpumpen muss zum Unterbrechen der Motor abgestellt werden, bei der WPS genügt der Kugelhahn.</p>

                <h2 id="einsatz">Einsatzbereiche</h2>
                <p>Mit der passenden Düse für Arbeiten im Hoch-, Holz- und Tiefbau:</p>
                <ul class="picks">{picks}</ul>

                <h2 id="eigenschaften">Eigenschaften</h2>
                <ul class="bullets">
                    <li>pumpt auch nicht maschinengängige Mörtel, zum Beispiel Zement-Mauermörtel</li>
                    <li>Fördermenge stufenlos über den Luftdruck einstellbar</li>
                    <li>Mörtelfluss am Kugelhahn sofort stopp- und startbar</li>
                    <li>verschleissfreies Pumpsystem, geringe Betriebskosten</li>
                    <li>in rund 5 Minuten betriebsbereit und in 5 bis 10 Minuten gereinigt</li>
                    <li>Sackkarren-Bauweise, gerüsttauglich</li>
                </ul>

                <h2 id="technische-daten">Technische Daten</h2>
                {spec_table(groups=SPEC_GROUPS, title="WPS-Mörtelpumpe")}
                <p class="table-note">Leistungsdaten sind Erfahrungswerte des Herstellers und hängen von Anwendung und Mörtelkonsistenz ab.</p>

                <h2 id="zubehoer">Düsen und Zubehör</h2>
                <div class="table-wrap"><table class="table"><thead><tr><th>Teil</th><th>Einsatz</th></tr></thead><tbody>{noz}</tbody></table></div>

                <h2 id="kompressor">Kompressor und Mischer</h2>
                <p>Für den Betrieb braucht es einen Kompressor. Welche Leistung nötig ist, hängt von der Anwendung ab:</p>
                <div class="table-wrap"><table class="table"><thead><tr><th>Modell</th><th>Daten</th><th>Geeignet für</th></tr></thead><tbody>{com}</tbody></table></div>
                <p>Zum Anmachen des Mörtels eignet sich ein horizontaler Zwangsmischer wie der IPERBET, der wenig Luft in den Mörtel einträgt. Für Fugenarbeiten kommen ein Handrührwerk zum Nachmischen und eine Schlauchtrommel dazu.</p>

                <h2 id="hersteller">Hersteller</h2>
                <p>Die WPS-Mörtelpumpe wird von der Winiger Pump System AG in Wald ZH entwickelt und gebaut. Das Unternehmen wurde 2005 von Hans-Rudolf und Gerhard Winiger gegründet, die Pumpe ist seit 2006 im Einsatz. Pumpsystem und Design sind patentiert.</p>
                <p class="source-note">Weitere Informationen und Anwendungsvideos finden Sie auf der Website des Herstellers: <a href="{WPS}/" target="_blank" rel="noopener">wps-ag.ch</a></p>
            </article>
            <aside class="sidebar">
                <nav class="toc" aria-label="Auf dieser Seite"><h2>Auf dieser Seite</h2><ul>{toc_html}</ul></nav>
                {side_contact()}
                <section><h2>Unterlagen</h2>{downloads("untermoerteln", "fugen", "tiefbau")}</section>
            </aside>
        </div>
    </div>
'''


# ------------------------------------------------------------------ Detailseiten
DETAILS = {
"anwendung-untermoerteln": dict(
    title="Untermörteln von Holzschwellen und Elementen mit der Mörtelpumpe | WPS",
    desc="Holzschwellen, Betonelemente und Stahlplatten hohlraumfrei untermörteln: WPS-Mörtelpumpe mit Breitschlitz- und Schnabeldüse, ab 11 mm Fugenhöhe, getestet von der Berner Fachhochschule.",
    lead="Holzschwellen, Betonelemente, Stahlträger, Stahlplatten und Dachpfetten vollflächig und hohlraumfrei unterfüttern.",
    img=("Untermorteln_Stahltragerplatte", "Untermörteln einer Stahlplatte mit der Breitschlitzdüse", 914, 682),
    pdfs=("untermoerteln", "bfh1", "bfh2"), wps="unterfuettern-von-schwellen-und-ele",
    body=f"""<h2>Warum Untermörteln von Hand so schwierig ist</h2>
                <p>Holzelemente im modernen Holzbau stehen meist auf einer Betonplatte und brauchen eine stabile, vollflächige Auflage. Schon kleine Abweichungen können später zu Setzungen führen, mit Rissen in der Beplankung oder klemmenden Fenstern und Türen. Hohlräume unter der Schwelle begünstigen ausserdem Fäulnis und Insektenbefall.</p>
                <p>Ein exaktes Mörtelbett erreicht auf der Baustelle selten die nötige Geradheit von ±2 mm über die ganze Länge. Wird mit Unterklotzung ausgeglichen, muss der Spalt danach untermörtelt werden. Von Hand lassen sich Hohlräume, die bis zu 40 cm tief und nur 1 bis 4 cm hoch sind, kaum vollständig füllen. Fliessmörtel wiederum verlangt Schalung und Steiger.</p>

                <h2>Vorgehen mit der WPS-Mörtelpumpe</h2>
                <p>Die WPS verarbeitet plastischen Mörtel mit ausreichender Stehhöhe, auch einen normalen Zement-Mauermörtel oder einen hochfesten Spezialmörtel. Der Spalt sollte mindestens 11 mm hoch sein. Die Düse wählen Sie nach der Tiefe:</p>
                <div class="table-wrap"><table class="table"><thead><tr><th>Düse</th><th>Tiefe der Untermörtelung</th></tr></thead><tbody>
                    <tr><td>Breitschlitzdüse 10 × 155 mm mit Absperrklappe</td><td>bis ca. 120 mm, etwa für Schwellen bis 12 cm Wandstärke</td></tr>
                    <tr><td>Breitschlitzdüse 8 × 155 mm mit Schnabel 110 × 9.5 mm</td><td>ab 120 mm bis über 400 mm; der Schnabel wird 11 cm unter die Schwelle geschoben</td></tr>
                </tbody></table></div>
                <p>Der Hersteller nennt eine Unterfütterungsleistung von bis zu 25 Laufmetern pro Stunde.</p>

                <h2>Geeignete Mörtel</h2>
                <p>Zement-Mauermörtel mit einer Druckfestigkeit von mindestens 10 N/mm², zum Beispiel weber.mur 920 oder Fixit 920. Für hohe statische Lasten eignet sich etwa EuroGrout Plast. Das Stehvermögen des Mörtels sollte mindestens der doppelten Unterfütterungshöhe entsprechen.</p>

                <h2>Ergebnisse der Berner Fachhochschule</h2>
                <p>Die Berner Fachhochschule (Architektur, Holz und Bau, Biel) hat 2009 im KTI-Projekt 8971.1 das Untermörteln von Schwellen mit der WPS in zwei Versuchsreihen geprüft, unter anderem mit weber maxit mur 920.</p>
                <ul class="bullets">
                    <li>Innenwände (Schwelle 100 mm): bei 20 bis 40 mm Fugenhöhe vollständig gefüllt, Empfehlung 10 bis 40 mm mit Abgrenzung auf der Gegenseite.</li>
                    <li>Aussenwände (Schwelle 220 mm): Empfehlung 20 bis 40 mm, Abgrenzung auf beiden Seiten.</li>
                    <li>Mit der Schnabeldüse ist eine volle Unterstopfung ab 10 mm möglich. Bei Innenwänden kann darauf verzichtet werden.</li>
                    <li>Ab 40 mm Fugenhöhe sollte das Mörtelbett nach etwa 2 Stunden nachgedrückt werden.</li>
                    <li>Verarbeitung ab 0 °C Aussentemperatur, wenn der Mörtel beim Einpumpen mindestens 6 °C hat.</li>
                    <li>Das Mörtelbett mit der WPS war günstiger als das herkömmliche Mörtelbett.</li>
                </ul>
                <figure><img src="assets/Beton_Stahl_Konstruktion.avif" alt="Untermörteln an einer Beton-Stahl-Konstruktion" loading="lazy" width="666" height="890"><figcaption>Untermörteln an einer Beton-Stahl-Konstruktion</figcaption></figure>
                <h2>Zusätzliche Ausrüstung</h2>
                <p>Mörtelmischer, zum Beispiel IPERBET, ein Kompressor mit mindestens 2 kW Antriebsleistung und eine Schlauchtrommel.</p>"""),
"anwendung-stahlzargen": dict(
    title="Stahlzargen einmörteln mit der Mörtelpumpe | WPS – Wilcowa",
    desc="Stahlzargen in Sichtbauweise und rauchdichter Ausführung einmörteln: Mit der WPS-Mörtelpumpe den Spalt von 1–2 cm zur Leibung sauber und hohlraumfrei verfüllen.",
    lead="Auch in Sichtbauweise und bei rauchdichter Ausführung: Der Spalt zwischen Leibung und Zarge wird sauber und vollständig verfüllt.",
    img=("Stahlschalung_Saeule", "Ausmörteln einer Stahlschalung mit der WPS-Mörtelpumpe", 874, 1164),
    pdfs=("tiefbau",), wps="einmoerteln-von-stahlzargen",
    body="""<h2>Das Problem auf der Baustelle</h2>
                <p>Zwischen Leibung und Zargenspiegel bleibt oft nur ein Spalt von 1 bis 2 cm. Wird eine Montage in Sichtbauweise oder in rauchdichter Ausführung verlangt, ist es von Hand kaum möglich, den Mörtel dort sauber einzubringen. Auch ohne diese Anforderungen ist das Einwerfen des Mörtels anstrengend und zeitraubend.</p>
                <h2>Einmörteln mit der WPS</h2>
                <p>Die WPS-Mörtelpumpe füllt den Zargenhohlraum über den Schlauch und dosiert den Mörtel dabei genau. Weil der Mörtelfluss sofort gestoppt werden kann, bleiben Leibung und Zarge sauber. Für das Abschalen und Nachstopfen gibt es abgestimmtes Zubehör.</p>
                <ul class="bullets">
                    <li>Stahlbügel zum Fixieren der Abdecklatten an der Leibung (Standardsatz 24 Stück)</li>
                    <li>Edelstahlstosser zum Nachstopfen, vor allem im Sturz und im oberen Leibungsbereich</li>
                    <li>Zubehör für Blockzargen, zum Beispiel von Hörmann</li>
                </ul>
                <p>Die Förderweite beträgt bei Stahlzargen bis 3.2 m. Als Kompressor genügt ein 230-V-Gerät mit 2.2 kW.</p>
                <h2>Was das für Ihren Betrieb bedeutet</h2>
                <p>Metallbauer, Schreiner und Montagefirmen können Stahlzargen mit der WPS selbst einmörteln, auch unsichtbar, und müssen diese Arbeit nicht mehr vergeben. Das Einwerfen des Mörtels von Hand und die damit verbundene Belastung der Handgelenke entfallen.</p>"""),
"anwendung-naturstein": dict(
    title="Natursteinmauern und Randsteine verfugen mit der Mörtelpumpe | WPS",
    desc="Natur- und Bruchsteinmauern, Sandsteingewölbe und Randsteine maschinell verfugen: Die WPS-Mörtelpumpe dosiert Fugenmörtel genau, die Steinflanken bleiben sauber.",
    lead="Natur- und Bruchsteinmauern, Gewölbe und Strassenrandsteine maschinell ausfugen.",
    img=("Natursteinwand_Fugen", "Natursteinwand verfugen mit der WPS-Mörtelpumpe", 896, 992),
    pdfs=("fugen", "tiefbau"), wps="fugen-von-natur-bruchsteinmauern",
    body="""<h2>Fugen ohne Kelle und Dressiersack</h2>
                <p>Mit der WPS-Mörtelpumpe verkürzt sich das Ausfugen von Natur- und Bruchsteinmauern oder Randsteinen deutlich gegenüber der Arbeit mit Fugenkelle oder Dressiersack. Vor allem der Dressiersack belastet die Sehnen stark und führt häufig zu Sehnenscheidenentzündungen.</p>
                <p>Wichtig ist, dass die Flanken der Steine sauber bleiben, sonst wird die Reinigung aufwendig. Die Fugendüse wird deshalb auf Fugenbreite und maximale Fugentiefe ausgelegt, und der Mörtelfluss lässt sich am Kugelhahn sofort stoppen und wieder starten.</p>
                <h2>Vorbereitung und Nachbehandlung</h2>
                <p>Saugende Steine und trockene Fugen werden vor dem Verfugen leicht angefeuchtet, damit der Mörtel gut haftet. Nach dem Fugen ist eine fachgerechte Nachbehandlung nötig. Vorgaben zu Vorbehandlung und Nachbehandlung macht der Mörtelhersteller.</p>
                <h2>Getestete Fugenmörtel</h2>
                <p>Zahlreiche handelsübliche Fugenmörtel für Naturstein wurden auf ihre Pumpfähigkeit geprüft, darunter Produkte von Röfix, Fixit, PCI, Sakret, tubag, Schwenk, Murexin, MC-Bauchemie, Mapei und weber. Die vollständige Liste steht im Anwendungsblatt Fugen.</p>
                <h2>Ausrüstung</h2>
                <ul class="bullets">
                    <li>Fugendüse, Standardlänge 13 cm, auf Wunsch angepasst</li>
                    <li>Füllschlauch DN 25, 4 m, mit Fugendüse</li>
                    <li>Kompressor 3 kW, 400 V; bei Arbeit mit Unterbrüchen genügen 2 kW</li>
                    <li>Horizontaler Mörtelmischer, Handrührwerk zum Nachmischen, Schlauchtrommel</li>
                </ul>
                <div class="figure-pair">
                    <figure><img src="assets/Ausfugen_Sandsteingewolbe.avif" alt="Ausfugen eines Sandstein-Kellergewölbes" loading="lazy" width="912" height="1216"><figcaption>Sandstein-Kellergewölbe</figcaption></figure>
                    <figure><img src="assets/Fugen_Randsteine.avif" alt="Randsteine verfugen" loading="lazy" width="910" height="682"><figcaption>Randsteine im Strassenbau</figcaption></figure>
                </div>"""),
"anwendung-klinker": dict(
    title="Klinker-Verblender verfugen mit der Mörtelpumpe | WPS – Wilcowa",
    desc="Schmale Fugen von 5–10 mm an Klinker-Verblendern und Natursteinplatten maschinell verfugen: WPS-Mörtelpumpe mit angepasster Fugendüse, Vorbereitung mit Antihaft-Primer.",
    lead="Schmale Fassadenfugen von 5 bis 10 mm an Klinker-Verblendern und Natursteinplatten.",
    img=("Klinker-Verblender_gefugt", "Gefugte Klinker-Verblender", 912, 784),
    pdfs=("fugen",), wps="fugen-von-klinkerplatten",
    body="""<h2>Auch für schmale Fugen geeignet</h2>
                <p>Bei Klinker-Verblendern und Natursteinplatten an der Fassade sind die Fugen meist 5 bis 10 mm breit und 10 bis 20 mm tief. Dafür wird die runde Fugendüse auf ein Innenmass von 4.5 mm zusammengedrückt. Der flache Querschnitt entspricht dann etwa einem Rohr von 13 mm Durchmesser und liefert genug Mörtel für zügiges Arbeiten.</p>
                <p>Gegenüber dem Verfugen mit Fugenbrett, Fugenkelle oder Dressiersack sparen Sie viel Zeit, und die körperliche Belastung sinkt deutlich.</p>
                <h2>Vorbereitung</h2>
                <ul class="bullets">
                    <li>Empfindliche Klinker vorher mit einem Antihaft-Primer schützen, zum Beispiel Zuckerlösung 1:1, aufgetragen mit dem Schaumstoffroller. Die Fugen dürfen dabei nicht benetzt werden.</li>
                    <li>So lassen sich Mörtelreste auf den Steinen nach dem Fugen rückstandsfrei entfernen.</li>
                    <li>Saugende Platten und trockene Fugen vor dem Verfugen mit einem Wassersprüher leicht befeuchten.</li>
                </ul>"""),
"anwendung-betonfugen": dict(
    title="Betonfugen und V-Fugen an Fertigteilen ausmörteln | WPS-Mörtelpumpe",
    desc="Betonkosmetik mit der Mörtelpumpe: V-Fugen von 1–4 cm und Stossfugen an Betonfertigteilen maschinell ausmörteln, mit Fugendüse Ø 22 mm und feinem Kalk-Zementmörtel.",
    lead="V-Fugen und Stossfugen an Betonfertigteilen maschinell statt mit der Kelle ausmörteln.",
    img=("Fugen_Deckenelemente", "Verfugen von Betonelementen", 874, 1166),
    pdfs=("tiefbau",), wps="betonfugen",
    body="""<h2>V-Fugen bei der Betonkosmetik</h2>
                <p>Bei der Montage von Betonfertigteilen entstehen meist V-Fugen, die nachträglich verfugt werden. Sie sind in der Regel 1 bis 4 cm breit und laufen in der Tiefe gegen null aus. Verwendet wird ein feiner Kalk-Zementmörtel 0–1 mm mit guter Flankenhaftung. Vorbehandlung, Vorfeuchten und Nachbehandlung richten sich nach den Vorgaben des Mörtelherstellers.</p>
                <p>Meist wird diese Arbeit noch mit Maurer- und Glättkelle erledigt. Mit der WPS-Mörtelpumpe füllen Sie die Fugen hohlraumfrei und mit deutlich weniger Kraftaufwand. Nach Angaben des Herstellers verfugen zwei Betonkosmetiker so rund 200 Laufmeter V-Fugen pro Tag.</p>
                <h2>Stossfugen</h2>
                <p>Stossfugen zwischen Betonelementen, die über die ganze Elementtiefe reichen, sind meist 2 bis 4 cm breit. Sie werden mit einem thixotropen Zement-Mauermörtel mit guter Flankenhaftung ausgemörtelt.</p>
                <h2>Ausrüstung</h2>
                <ul class="bullets">
                    <li>Fugendüse Ø 22 × 1 mm, Standardlänge 13 cm oder nach Wunsch</li>
                    <li>Füllschlauch DN 25, 4 m, mit drehbaren GEKA-Kupplungen</li>
                </ul>"""),
"anwendung-spannbeton": dict(
    title="Deckenplatten-Fugen und Spannbeton ausmörteln | WPS-Mörtelpumpe",
    desc="Fugen von Deckenplatten, Spannbeton-Verankerungen und Porenbeton-Deckenplatten mit der WPS-Mörtelpumpe ausmörteln: ergonomisch im Stehen, dosiert und hohlraumfrei.",
    lead="Fugen zwischen Deckenelementen und Verankerungen von Spannbetonplatten ausmörteln.",
    img=("Ausgiessen_Spannbetonplatten", "Ausmörteln von Fugen zwischen Spannbetonplatten", 884, 660),
    pdfs=("tiefbau",), wps="uebrige-anwendungen",
    body="""<h2>Fugen von Deckenplatten</h2>
                <p>Die Fugen zwischen Deckenelementen werden direkt aus dem Behälter über Schlauch und Düse ausgemörtelt. Sie arbeiten im Stehen und müssen keine Eimer schleppen. Weil der Mörtelfluss am Kugelhahn sofort unterbrochen werden kann, gelangt kein Material neben die Fuge.</p>
                <h2>Weitere Arbeiten an Decken</h2>
                <p>Mit der WPS wurden unter anderem bereits ausgeführt:</p>
                <ul class="bullets">
                    <li>Ausmörteln von Verankerungen bei Spannbetonplatten</li>
                    <li>Ausfugen von Porenbeton-Deckenplatten (Ytong)</li>
                    <li>Partielles Ausmörteln von Deckenelementen als Brandschutz</li>
                    <li>Ausgiessen von Stossfugen bei Betonelementen mit Vergussmörtel</li>
                </ul>"""),
"anwendung-maueranker": dict(
    title="Mauer- und Felsanker verpressen mit der Mörtelpumpe | WPS",
    desc="Mauer-, Fels- und Wandanker mit der WPS-Mörtelpumpe verpressen: Mörtelinjektion mit Rohrdüse DN 34, Zementschlämme für Erdanker, dosiert und lunkerfrei.",
    lead="Mörtelinjektion für Mauer-, Fels- und Wandanker sowie Zementschlämme für Erdanker.",
    img=("Mauer-Anker_verpressen", "Maueranker verpressen mit der WPS-Mörtelpumpe", 888, 660),
    pdfs=("tiefbau",), wps="uebrige-anwendungen",
    body="""<h2>Anker vollständig verfüllen</h2>
                <p>Bei der Sicherung oder Verstärkung von Mauerwerk und Fels muss der Mörtel das Bohrloch um den Anker vollständig füllen. Mit der Rohrdüse DN 34 wird der Mörtel von hinten nach vorne eingebracht, die Fördermenge lässt sich dabei stufenlos anpassen.</p>
                <h2>Bisherige Einsätze</h2>
                <ul class="bullets">
                    <li>Auspressen von Mauer- und Felsankern</li>
                    <li>Ausgiessen von Wandankern mit Zement-Mauermörtel</li>
                    <li>Pumpen einer Zementschlämme für Erdanker</li>
                </ul>"""),
"anwendung-daemmplatten": dict(
    title="Mörtelkleber auf Dämmplatten auftragen mit der Mörtelpumpe | WPS",
    desc="Mörtelkleber mit der WPS-Mörtelpumpe auf Dämm- und Brandschutzplatten auftragen: dosiert, gleichmässig und ohne Zahnspachtel.",
    lead="Mörtelkleber dosiert auf Dämm- und Brandschutzplatten oder auf den Untergrund auftragen.",
    img=("Daemmplatten_Kleber", "Mörtelkleber auf Dämmplatten auftragen", 900, 674),
    pdfs=("tiefbau",), wps="uebrige-anwendungen",
    body="""<h2>Kleberauftrag mit der Pumpe</h2>
                <p>Beim Kleben von Dämmplatten, etwa bei Kellerdecken, Innendämmung oder Fassade, wird der Mörtelkleber sonst mit der Kelle und dem Zahnspachtel aufgezogen. Mit der WPS tragen Sie den Kleber als Raupe direkt auf die Platte oder den Untergrund auf und dosieren die Menge am Kugelhahn.</p>
                <h2>Verwandte Anwendungen</h2>
                <ul class="bullets">
                    <li>Ausmörteln von Brandschutzklappen</li>
                    <li>Ausmörteln von Mauerschlitzen</li>
                    <li>Spritzen von Spezialmörtel oder -putz bis etwa 1 cm Schichtdicke</li>
                </ul>"""),
}

# Kennzahlen im Seitenkopf der Anwendungsseiten (Quelle: Herstellerunterlagen, BFH-Testberichte)
FACTS = {
    "anwendung-untermoerteln": ("unter", [("Fugenhöhe", "ab 11 mm"), ("Tiefe", "bis über 400 mm"), ("Düse", "Breitschlitzdüse, ab 120 mm mit Schnabel"), ("Mörtel", "Zement-Mauermörtel ab 10 N/mm²"), ("Leistung", "bis 25 m/h (Hersteller)")]),
    "anwendung-stahlzargen": ("zarge", [("Spalt", "1–2 cm zur Leibung"), ("Zeit", "ca. 47 min pro Standardzarge"), ("Mörtel", "ca. 22 l pro Zarge"), ("Förderweite", "bis 3.2 m"), ("Kompressor", "2.2 kW, 230 V")]),
    "anwendung-naturstein": ("fuge", [("Düse", "Fugendüse 13 cm, anpassbar"), ("Mörtel", "über 15 getestete Fugenmörtel"), ("Kompressor", "3 kW, 400 V"), ("Dosierung", "Kugelhahn an der Düse")]),
    "anwendung-klinker": ("fuge", [("Fugenbreite", "5–10 mm"), ("Fugentiefe", "10–20 mm"), ("Düse", "auf 4.5 mm zusammengedrückt"), ("Schutz", "Antihaft-Primer, z. B. Zuckerlösung 1:1")]),
    "anwendung-betonfugen": ("vfuge", [("V-Fugen", "1–4 cm breit"), ("Stossfugen", "2–4 cm breit"), ("Mörtel", "Kalk-Zementmörtel 0–1 mm"), ("Düse", "Fugendüse Ø 22 × 1 mm"), ("Leistung", "ca. 200 m pro Tag zu zweit")]),
    "anwendung-spannbeton": (None, [("Einsatz", "Fugen zwischen Deckenelementen"), ("Auch für", "Verankerungen, Porenbetonplatten"), ("Arbeitsweise", "im Stehen, ohne Eimer"), ("Förderdruck", "max. 2.5 bar")]),
    "anwendung-maueranker": (None, [("Düse", "Rohrdüse DN 34"), ("Anker", "Mauer-, Fels- und Wandanker"), ("Erdanker", "mit Zementschlämme"), ("Förderdruck", "max. 2.5 bar")]),
    "anwendung-daemmplatten": (None, [("Auftrag", "Kleberaupe auf Platte oder Wand"), ("Platten", "Dämm- und Brandschutzplatten"), ("Spritzen", "Spezialmörtel bis ca. 1 cm"), ("Dosierung", "Kugelhahn an der Düse")]),
}

def related(slug, n=3):
    group = next(sl for t, sl in MENU_GROUPS if slug in sl)
    others = [x for x in group if x != slug] + [s_ for s_, *_ in APPS if s_ != slug and s_ not in group]
    return others[:n]

def page_detail(slug):
    d = DETAILS[slug]
    t = next(t for s_, n, t, *_ in APPS if s_ == slug)
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html"), (t, f"{slug}.html")]
    img, alt, w, hh = d["img"]
    mode, fx = FACTS[slug]
    facts_html = spec_table(rows=fx, title="Auf einen Blick", note="")
    calc_href = f"moertel-bedarf-rechner.html?mode={mode}" if mode else "moertel-bedarf-rechner.html"
    calc_box = f'''<a class="calc-teaser" href="{calc_href}">
                    <span><strong>Was spart die WPS bei Ihrem Projekt?</strong>Masse und Ihre heutige Leistung eingeben, der Rechner vergleicht Zeit, Kosten und Mörtel.</span>
                    <em>Zum Mörtelrechner</em>
                </a>'''
    info = {s_: (tt, txt, im) for s_, n, tt, txt, im in APPS}
    rel = "".join(f'''<li><a href="{r}.html"><img src="assets/{info[r][2]}.avif" alt="{info[r][0]}" loading="lazy" width="900" height="675"><h3>{info[r][0]}</h3><p>{info[r][1]}</p></a></li>''' for r in related(slug))
    return f'''
    <section class="page-head page-head-media">
        <div class="container">
            <div class="page-head-text">
                {breadcrumbs(crumbs)}
                <h1>{t}</h1>
                <p class="lead">{d["lead"]}</p>
                <div class="btn-row">
                    <a class="btn btn-accent" href="kontakt.html?type=miete">Pumpe für diese Arbeit anfragen</a>
                    <a class="btn btn-outline-light" href="{calc_href}">Ersparnis berechnen</a>
                </div>
            </div>
            <img src="assets/{img}.avif" alt="{alt}" width="{w}" height="{hh}" fetchpriority="high">
        </div>
    </section>

    <main class="section">
        <div class="container layout">
            <article class="prose">
                {d["body"]}
                {calc_box}
                <p class="source-note">Technische Angaben nach Unterlagen des Herstellers Winiger Pump System AG. Videos zu dieser Anwendung: <a href="{WPS}/{d["wps"]}" target="_blank" rel="noopener">wps-ag.ch</a></p>
            </article>
            <aside class="sidebar">
                <section>{facts_html}</section>
                {side_contact()}
                <section><h2>Unterlagen</h2>{downloads(*d["pdfs"])}</section>
            </aside>
        </div>
    </main>

    <section class="section bg-alt">
        <div class="container">
            <div class="section-title"><h2>Weitere Anwendungen</h2></div>
            <ul class="tiles tiles-3">{rel}</ul>
            <p style="margin-top:24px"><a href="anwendungen.html">Alle Anwendungen ansehen</a></p>
        </div>
    </section>
'''

# ------------------------------------------------------------------ Anwendungen
GALLERY = [
    ("Untermorteln_Stahltragerplatte", "Untermörteln einer Stahlplatte"),
    ("Beton_Stahl_Konstruktion", "Untermörteln an einer Beton-Stahl-Konstruktion"),
    ("Ausmorteln_Stahltrager", "Ausmörteln eines Stahlträgers"),
    ("Stahlschalung_Saeule", "Ausmörteln einer Stahlschalung"),
    ("Natursteinwand_Fugen", "Natursteinwand"),
    ("Ausfugen_Sandsteingewolbe", "Sandstein-Kellergewölbe"),
    ("Fugen_Randsteine", "Randsteine"),
    ("Klinker-Verblender_gefugt", "Klinker-Verblender"),
    ("Fugen_Deckenelemente", "Fugen von Deckenelementen"),
    ("Ausgiessen_Spannbetonplatten", "Fugen von Spannbetonplatten"),
    ("Mauer-Anker_verpressen", "Maueranker verpressen"),
    ("Daemmplatten_Kleber", "Kleber auf Dämmplatten"),
]

GROUP_IDS = {"Holz- und Hochbau": "hochbau", "Fugen": "fugen", "Verankerung": "verankerung"}

def page_anwendungen():
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html")]
    info = {s_: (t, txt, img) for s_, n, t, txt, img in APPS}

    # Schnellnavigation im Seitenkopf: Piktogramme wie im Menü, springen zur Anwendung auf dieser Seite
    jump = "<ul>" + "".join(f'<li><a href="#{a}">{app_icon(a)}<span>{MENU_LABELS[a][0]}</span></a></li>'
                            for title, slugs in MENU_GROUPS for a in slugs) + "</ul>"

    def row(a):
        t, txt, img = info[a]
        mode, fx = FACTS[a]
        facts = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in fx[:3])
        calc = f'<a class="btn btn-secondary" href="moertel-bedarf-rechner.html?mode={mode}">Ersparnis berechnen</a>' if mode else ""
        return f'''
                    <article class="app-item" id="{a}">
                        <a class="app-item-media" href="{a}.html" tabindex="-1" aria-hidden="true"><img src="assets/{img}.avif" alt="" loading="lazy" width="900" height="675"></a>
                        <div class="app-item-body">
                            <h3><a href="{a}.html">{t}</a></h3>
                            <p>{DETAILS[a]["lead"]}</p>
                            <dl class="app-facts">{facts}</dl>
                            <div class="btn-row">
                                <a class="btn btn-primary" href="{a}.html">Vorgehen und Ausrüstung</a>
                                {calc}
                            </div>
                        </div>
                    </article>'''

    groups = "".join(f'''
            <section class="app-section" id="{GROUP_IDS[title]}" aria-labelledby="g-{GROUP_IDS[title]}">
                <div class="container">
                    <h2 id="g-{GROUP_IDS[title]}">{title}</h2>
                    {"".join(row(a) for a in slugs)}
                </div>
            </section>''' for title, slugs in MENU_GROUPS)

    gal = "".join(f'<figure><img src="assets/{img}.avif" alt="{c}" loading="lazy" width="900" height="900"><figcaption>{c}</figcaption></figure>' for img, c in GALLERY)
    return f'''
    <section class="page-head page-head-jump">
        <div class="container">
            <div>
                {breadcrumbs(crumbs)}
                <h1>Anwendungen der WPS-Mörtelpumpe</h1>
                <p class="lead">Untermörteln, Einmörteln, Verfugen und Verpressen im Hoch-, Holz- und Tiefbau. Wählen Sie Ihre Anwendung.</p>
            </div>
            <nav class="jump" aria-label="Anwendung wählen">{jump}</nav>
        </div>
    </section>
{groups}
    <section class="section bg-alt">
        <div class="container two-col">
            <div>
                <h2>Weitere Einsätze</h2>
                <p>Die WPS wurde ausserdem schon für diese Arbeiten verwendet. Fragen Sie uns, wenn Ihre Anwendung nicht dabei ist.</p>
                <p style="margin-top:18px"><a class="btn btn-primary" href="kontakt.html">Anwendung anfragen</a></p>
            </div>
            <ul class="bullets">
                <li>Ausgiessen einer Kranschiene mit hochfestem Mörtel</li>
                <li>Ausgiessen einer Trägerverschalung mit Vergussmörtel</li>
                <li>Untermörteln von Dachpfetten für Schallschutz und Statik</li>
                <li>Ausmörteln von Ziegelsteinen bei Wanddurchbrüchen</li>
                <li>Partielles Ausmörteln paralleler Betonelemente zur Erdbebenertüchtigung</li>
                <li>Ausmörteln von Brandschutzklappen und Mauerschlitzen</li>
            </ul>
        </div>
    </section>
    <section class="section">
        <div class="container">
            <div class="section-title"><h2>Bilder von Baustellen</h2><p>Zum Vergrössern auf ein Bild klicken.</p></div>
            <div class="gallery">{gal}</div>
        </div>
    </section>
'''

# ------------------------------------------------------------------ Rechner
CALC_SVG = {
    # Querschnitte: Stein/Element grau, Mörtel orange
    "unter": """<svg viewBox="0 0 72 48" aria-hidden="true"><rect x="18" y="8" width="36" height="22" class="s-wood"/><rect x="18" y="30" width="36" height="6" class="s-mortar"/><rect x="2" y="36" width="68" height="10" class="s-solid"/></svg>""",
    "vfuge": """<svg viewBox="0 0 72 48" aria-hidden="true"><path d="M4 10h20l12 22v12H4z" class="s-solid"/><path d="M68 10H48L36 32v12h32z" class="s-solid"/><path d="M24 10h24L36 32z" class="s-mortar"/></svg>""",
    "fuge": """<svg viewBox="0 0 72 48" aria-hidden="true"><rect x="4" y="10" width="26" height="34" class="s-solid"/><rect x="42" y="10" width="26" height="34" class="s-solid"/><rect x="30" y="10" width="12" height="20" class="s-mortar"/></svg>""",
    "zarge": """<svg viewBox="0 0 72 48" aria-hidden="true"><path d="M8 46V4h56v42h-8V12H16v34z" class="s-solid"/><path d="M16 46V12h40v34h-4V16H20v30z" class="s-mortar"/><path d="M20 46V16h32v30h-3V19H23v27z" class="s-steel"/></svg>""",
}

def page_rechner():
    crumbs = [("Start", "index.html"), ("Mörtelrechner", "moertel-bedarf-rechner.html")]

    def field(id_, label, unit, val, step="1", tag="", hint="", rng=None):
        t = f' <em class="tag" id="{id_}-tag">{tag}</em>' if tag else ""
        h = f'<small class="field-hint" id="{id_}-hint">{hint}</small>' if hint else ""
        return (f'<div class="field" id="{id_}-field"><label for="{id_}"><span id="{id_}-label">{label}</span>{t}</label>'
                f'<div class="input-unit"><input type="number" id="{id_}" value="{val}" min="0" step="{step}" inputmode="decimal">'
                f'<span id="{id_}-unit">{unit}</span></div>'
                + (f'<input type="range" class="range" id="{id_}-range" min="{rng[0]}" max="{rng[1]}" step="{step}" value="{val}" aria-label="{label}" tabindex="-1">' if rng else '')
                + f'{h}</div>')

    modes = [("unter", "Untermörtelung", "Schwellen, Platten"),
             ("vfuge", "V-Fuge", "Betonfertigteile"),
             ("fuge", "Fuge", "Naturstein, Klinker"),
             ("zarge", "Stahlzarge", "pro Stück")]
    mode_html = "".join(
        f'<label class="mode"><input type="radio" name="mode" value="{k}"{" checked" if k == "unter" else ""}>'
        f'{CALC_SVG[k]}<strong>{t}</strong><span>{sub}</span></label>' for k, t, sub in modes)

    return page_head(crumbs, "Mörtelrechner: Was spart die WPS gegenüber Handarbeit?",
                     "Geben Sie die Masse und Ihre heutige Leistung von Hand ein. Der Rechner vergleicht Arbeitszeit, Kosten und Mörtelbedarf mit der WPS-Mörtelpumpe.") + f'''
    <main class="section">
        <div class="container">
            <form class="calc" id="calc" onsubmit="return false" novalidate>
                <div class="calc-main">
                    <fieldset class="calc-step">
                        <legend><span class="step-no">1</span>Anwendung</legend>
                        <div class="modes">{mode_html}</div>
                    </fieldset>
                    <fieldset class="calc-step">
                        <legend><span class="step-no">2</span>Masse</legend>
                        <div class="calc-grid">
                            {field("calc-a", "Länge", "m", 50, "0.5", rng=(1, 300))}
                            {field("calc-b", "Schwellenbreite", "mm", 100)}
                            {field("calc-c", "Fugenhöhe", "mm", 20)}
                        </div>
                        <p class="calc-warn" id="calc-warn" hidden></p>
                    </fieldset>
                    <fieldset class="calc-step">
                        <legend><span class="step-no">3</span>Leistung von Hand und mit der WPS</legend>
                        <div class="compare-grid">
                            <div class="compare-col">
                                <p class="compare-title">Von Hand, heute</p>
                                {field("hand-rate", "Leistung", "m/h", 6, "0.5", "Annahme", "Bitte Ihren Erfahrungswert eintragen", rng=(1, 30))}
                                {field("hand-loss", "Materialverlust", "%", 15, "1", "Annahme", rng=(0, 40))}
                            </div>
                            <div class="compare-col compare-wps">
                                <p class="compare-title">Mit der WPS</p>
                                {field("wps-rate", "Leistung", "m/h", 20, "0.5", "Hersteller", "Hersteller: bis 25 m/h", rng=(1, 40))}
                                {field("wps-loss", "Materialverlust", "%", 5, "1", "Annahme", rng=(0, 40))}
                            </div>
                        </div>
                        <div class="calc-grid calc-grid-sep">
                            {field("calc-team", "Personen", "", 2)}
                            {field("calc-wage", "Stundensatz", "CHF", 95, "5", "Annahme", "pro Person und Stunde", rng=(50, 160))}
                            {field("calc-yield", "Verbrauch Mörtel", "kg/l", 1.7, "0.05", "", "laut Datenblatt, meist um 1.7")}
                        </div>
                    </fieldset>
                </div>

                <aside class="calc-out" aria-live="polite">
                    <p class="out-label">Mit der WPS sparen Sie</p>
                    <p class="out-main"><output id="out-save-chf">–</output></p>
                    <p class="out-sub"><output id="out-save-h">–</output> Arbeitsstunden und <output id="out-save-kg">–</output> kg Mörtel</p>
                    <div class="bars">
                        <p class="bars-title">Arbeitszeit</p>
                        <div class="bar"><span>Von Hand</span><div class="bar-track"><i id="bar-hand-h"></i></div><b id="out-hand-h">–</b></div>
                        <div class="bar bar-wps"><span>WPS</span><div class="bar-track"><i id="bar-wps-h"></i></div><b id="out-wps-h">–</b></div>
                        <p class="bars-title">Trockenmörtel</p>
                        <div class="bar"><span>Von Hand</span><div class="bar-track"><i id="bar-hand-kg"></i></div><b id="out-hand-kg">–</b></div>
                        <div class="bar bar-wps"><span>WPS</span><div class="bar-track"><i id="bar-wps-kg"></i></div><b id="out-wps-kg">–</b></div>
                    </div>
                    <p class="out-order">Bestellmenge mit der WPS: <strong id="out-sacks">–</strong></p>
                    <a class="btn btn-accent" id="calc-cta" href="kontakt.html?type=miete">WPS für dieses Projekt anfragen</a>
                    <p class="out-note">Richtwerte. Felder mit «Annahme» bitte durch eigene Werte ersetzen.</p>
                </aside>
            </form>

            <div class="calc-help">
                <div>
                    <h2>Woher die WPS-Werte stammen</h2>
                    <p>Untermörteln: bis 25 Laufmeter pro Stunde laut Flyer des Herstellers, vorbelegt sind vorsichtigere 20 m/h. V-Fugen: Zwei Betonkosmetiker schaffen mit der WPS rund 200 m pro Tag. Stahlzargen: 47 Minuten und rund 22 Liter Mörtel pro Standardzarge (2000 × 875 × 100 mm) nach der Kalkulation des Herstellers.</p>
                </div>
                <div>
                    <h2>Was Sie selbst eintragen</h2>
                    <p>Ihre heutige Leistung von Hand, Ihren Stundensatz und den Materialverlust kennen nur Sie. Die vorbelegten Werte sind Annahmen, damit der Rechner sofort ein Ergebnis zeigt.</p>
                </div>
                <div>
                    <h2>So wird gerechnet</h2>
                    <p>Volumen = Länge × Breite × Tiefe, bei V-Fugen die Hälfte. Arbeitszeit = Menge ÷ Leistung. Kosten = Stunden × Personen × Stundensatz. Mörtel = Volumen × Verbrauch plus Materialverlust.</p>
                </div>
            </div>
        </div>
    </main>
'''

# ------------------------------------------------------------------ FAQ
def page_faq():
    crumbs = [("Start", "index.html"), ("Häufige Fragen", "faq.html")]
    cats = "".join(f'<a href="#{k}">{t}<span>{len(items)}</span></a>' for k, t, items in FAQ_GROUPS)
    groups = ""
    first = True
    for k, t, items in FAQ_GROUPS:
        qs = ""
        for q, a in items:
            qs += f'\n                    <details{" open" if first else ""}><summary>{q}</summary><div class="answer"><p>{a}</p></div></details>'
            first = False
        groups += f'''
                <section class="faq-group" id="{k}" aria-labelledby="h-{k}">
                    <h2 id="h-{k}">{t}</h2>
                    <div class="faq">{qs}
                    </div>
                </section>'''
    return page_head(crumbs, "Häufige Fragen zur WPS-Mörtelpumpe", "Kompressor, Mörtel, Düsen, Leistung, Miete und Kauf. Ihre Frage ist nicht dabei? Rufen Sie uns an.") + f'''
    <div class="section">
        <div class="container layout">
            <div>
                <div class="faq-tools">
                    <label class="sr-only" for="faq-search">Frage suchen</label>
                    <input type="search" id="faq-search" placeholder="Frage suchen, zum Beispiel «Kompressor» oder «Düse»" autocomplete="off">
                    <nav class="faq-cats" aria-label="Themen">{cats}</nav>
                </div>
                <p class="faq-empty" id="faq-empty" hidden>Keine passende Frage gefunden. Rufen Sie uns an unter <a href="{PHONE_HREF}">{PHONE}</a> oder senden Sie uns eine <a href="kontakt.html">Anfrage</a>.</p>
                {groups}
            </div>
            <aside class="sidebar">
                {side_contact()}
                <section><h2>Unterlagen</h2>{downloads("untermoerteln", "fugen")}</section>
            </aside>
        </div>
    </div>
'''

# ------------------------------------------------------------------ Kontakt
def page_kontakt():
    crumbs = [("Start", "index.html"), ("Kontakt", "kontakt.html")]
    return page_head(crumbs, "Kontakt", "Für Beratung, Miete oder eine Offerte zur WPS-Mörtelpumpe erreichen Sie uns in Regensdorf.") + f'''
    <main class="section">
        <div class="container contact-grid">
            <ul class="contact-list">
                <li>{icon("phone")}<div><strong>Telefon</strong><a href="{PHONE_HREF}">{PHONE}</a></div></li>
                <li>{icon("mail")}<div><strong>E-Mail</strong><a href="mailto:{MAIL}">{MAIL}</a></div></li>
                <li>{icon("pin")}<div><strong>Adresse</strong>Wilcowa AG Baumaschinen<br>Riedthofstrasse 172<br>8105 Regensdorf<br><a href="https://www.google.com/maps/search/?api=1&amp;query=Wilcowa+AG+Riedthofstrasse+172+8105+Regensdorf" target="_blank" rel="noopener">Auf Google Maps anzeigen</a></div></li>
                <li>{icon("clock")}<div><strong>Öffnungszeiten</strong>{hours_html()}</div></li>
            </ul>
            <div>
                <h2 style="margin-bottom:6px">Anfrage</h2>
                <p class="muted" style="margin-bottom:22px">Das Formular öffnet Ihr E-Mail-Programm mit einer vorbereiteten Nachricht an {MAIL}.</p>
                <form id="contact-form" class="form-grid">
                    <div class="field"><label for="f-vorname">Vorname *</label><input id="f-vorname" name="vorname" autocomplete="given-name" required></div>
                    <div class="field"><label for="f-nachname">Nachname *</label><input id="f-nachname" name="nachname" autocomplete="family-name" required></div>
                    <div class="field field-full"><label for="f-firma">Firma</label><input id="f-firma" name="firma" autocomplete="organization"></div>
                    <div class="field"><label for="f-email">E-Mail *</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
                    <div class="field"><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
                    <div class="field field-full">
                        <label for="f-betreff">Anliegen</label>
                        <select id="f-betreff" name="betreff">
                            <option>Offerte WPS-Mörtelpumpe</option>
                            <option>Mietanfrage WPS-Mörtelpumpe</option>
                            <option>Technische Frage</option>
                            <option>Düsen, Zubehör, Kompressor</option>
                            <option>Sonstiges</option>
                        </select>
                    </div>
                    <div class="field field-full"><label for="f-msg">Nachricht *</label><textarea id="f-msg" name="nachricht" rows="6" required placeholder="Anwendung, Mörtel, Zeitraum"></textarea></div>
                    <div class="field-full form-actions"><button class="btn btn-accent" type="submit">E-Mail erstellen</button><span class="muted small">* Pflichtfelder</span></div>
                </form>
            </div>
        </div>
    </main>
'''

# ------------------------------------------------------------------ Impressum
def page_impressum():
    crumbs = [("Start", "index.html"), ("Impressum", "impressum.html")]
    return page_head(crumbs, "Impressum", "Angaben zum Anbieter dieser Website.") + f'''
    <main class="section">
        <div class="container legal">
            <h2>Kontaktadresse</h2>
            <p>Wilcowa AG Baumaschinen<br>Riedthofstrasse 172<br>8105 Regensdorf<br>Schweiz</p>
            <p>Telefon <a href="{PHONE_HREF}">{PHONE}</a><br>E-Mail <a href="mailto:{MAIL}">{MAIL}</a></p>
            <h2>Vertretungsberechtigte Person</h2>
            <p>Philippe Tobler</p>
            <h2>Handelsregistereintrag</h2>
            <p>Eingetragener Firmenname: Wilcowa AG Baumaschinen<br>UID: CHE-105.750.310<br>Handelsregisteramt des Kantons Zürich</p>
            <h2>Hersteller der WPS-Mörtelpumpe</h2>
            <p>Winiger Pump System AG, Laupenstrasse 32, 8636 Wald ZH, <a href="{WPS}/" target="_blank" rel="noopener">wps-ag.ch</a></p>
            <h2>Haftungsausschluss</h2>
            <p>Der Autor übernimmt keinerlei Gewähr hinsichtlich der inhaltlichen Richtigkeit, Genauigkeit, Aktualität, Zuverlässigkeit und Vollständigkeit der Informationen. Haftungsansprüche gegen den Autor wegen Schäden materieller oder immaterieller Art, welche aus dem Zugriff oder der Nutzung bzw. Nichtnutzung der veröffentlichten Informationen, durch Missbrauch der Verbindung oder durch technische Störungen entstanden sind, werden ausgeschlossen.</p>
            <p>Alle Angebote sind unverbindlich. Der Autor behält es sich ausdrücklich vor, Teile der Seiten oder das gesamte Angebot ohne gesonderte Ankündigung zu verändern, zu ergänzen, zu löschen oder die Veröffentlichung zeitweise oder endgültig einzustellen.</p>
            <h2>Haftung für Links</h2>
            <p>Verweise und Links auf Webseiten Dritter liegen ausserhalb unseres Verantwortungsbereichs. Es wird jegliche Verantwortung für solche Webseiten abgelehnt. Der Zugriff und die Nutzung solcher Webseiten erfolgen auf eigene Gefahr des Nutzers oder der Nutzerin.</p>
            <h2>Urheberrechte</h2>
            <p>Die Urheber- und alle anderen Rechte an Inhalten, Bildern, Fotos oder anderen Dateien auf dieser Website gehören ausschliesslich der Wilcowa AG oder den speziell genannten Rechtsinhabern. Für die Reproduktion jeglicher Elemente ist die schriftliche Zustimmung der Urheberrechtsträger im Voraus einzuholen.</p>
            <h2>Datenschutz</h2>
            <p>Informationen zur Bearbeitung von Personendaten finden Sie in der <a href="https://wilcowa.ch/datenschutzerklaerung/" target="_blank" rel="noopener">Datenschutzerklärung der Wilcowa AG</a>.</p>
        </div>
    </main>
'''

# ------------------------------------------------------------------ Seiten
PRODUCT_LD = {"@context": "https://schema.org", "@type": "Product", "name": "WPS-Mörtelpumpe",
              "image": BASE + "/assets/Untermorteln_Holzbau.avif",
              "description": "Druckluftbetriebene Mörtelpumpe für Untermörteln, Fugen, Stahlzargen und Ankerverpressung. Fördermenge 0–15 l/min, Förderdruck max. 2.5 bar, Behälter 60 l.",
              "brand": {"@type": "Brand", "name": "WPS"},
              "manufacturer": {"@type": "Organization", "name": "Winiger Pump System AG", "url": WPS + "/"}}

if RATING["count"]:
    PRODUCT_LD["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": RATING["value"], "bestRating": RATING["best"], "ratingCount": str(RATING["count"])}

PAGES = [
    dict(file="index.html", active="", body=page_index, ld=[WEBSITE_LD, LOCAL_BUSINESS], share=("WPS-Mörtelpumpe", "Untermörteln, Fugen und Stahlzargen", "Untermorteln_Stahltragerplatte"),
         title="Mörtelpumpe mieten und kaufen | WPS-Mörtelpumpe – Wilcowa AG",
         desc="WPS-Mörtelpumpe kaufen oder mieten bei Wilcowa in Regensdorf: druckluftbetrieben, 0–15 l/min, pumpt auch Standardmörtel. Für Untermörteln, Fugen, Stahlzargen und Anker."),
    dict(file="produkte.html", share=("WPS-Mörtelpumpe", "Technische Daten, Düsen und Zubehör", "Untermorteln_Holzbau"), active="produkt", body=page_produkt, og_type="product", og_image="Untermorteln_Holzbau.avif", ld=[PRODUCT_LD],
         title="WPS-Mörtelpumpe: Technische Daten, Düsen und Kompressor | Wilcowa",
         desc="Technische Daten der WPS-Mörtelpumpe: 0–15 l/min, max. 2.5 bar, Förderweite bis 4 m, Behälter 60 l, Luftbedarf 200 l/min. Düsen, Kompressoren und Mörtelmischer."),
    dict(file="anwendungen.html", share=("Anwendungen", "Untermörteln, Verfugen, Verpressen", "Natursteinwand_Fugen"), active="anwendungen", body=page_anwendungen, og_image="Natursteinwand_Fugen.avif",
         title="Anwendungen der Mörtelpumpe: Untermörteln, Fugen, Stahlzargen | WPS",
         desc="Einsatzgebiete der WPS-Mörtelpumpe: Holzschwellen untermörteln, Stahlzargen einmörteln, Naturstein und Klinker verfugen, Betonfugen, Deckenfugen und Anker verpressen."),
    dict(file="moertel-bedarf-rechner.html", share=("Mörtelrechner", "Was spart die WPS gegenüber Handarbeit?", "Ausgiessen_Spannbetonplatten"), active="rechner", body=page_rechner,
         title="Mörtelrechner: Zeit, Kosten und Mörtel mit der WPS sparen | Wilcowa",
         desc="Mörtelrechner mit Vergleich: Arbeitszeit, Kosten und Mörtelbedarf beim Untermörteln, für V-Fugen, Fugen und Stahlzargen, von Hand und mit der WPS-Mörtelpumpe."),
    dict(file="faq.html", share=("Häufige Fragen", "Kompressor, Mörtel, Bedienung und Miete", "Mauer-Anker_verpressen"), active="faq", body=page_faq,
         ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in FAQ]}],
         title="Fragen zur WPS-Mörtelpumpe: Kompressor, Mörtel, Miete | Wilcowa",
         desc="Antworten zur WPS-Mörtelpumpe: Welcher Kompressor, welche Mörtel, minimale Fugenhöhe beim Untermörteln, Arbeiten bei Kälte, Reinigung, Gewicht und Miete."),
    dict(file="kontakt.html", share=("Kontakt", "Beratung, Miete und Verkauf in Regensdorf", "Untermorteln_Stahltragerplatte"), active="kontakt", body=page_kontakt, ld=[LOCAL_BUSINESS],
         title="Kontakt: WPS-Mörtelpumpe anfragen | Wilcowa AG Regensdorf",
         desc="Wilcowa AG Baumaschinen, Riedthofstrasse 172, 8105 Regensdorf. Beratung, Miete und Offerte für die WPS-Mörtelpumpe: +41 43 388 70 60, info@wilcowa.ch."),
    dict(file="impressum.html", share=("Impressum", "Wilcowa AG Baumaschinen, Regensdorf", "Untermorteln_Stahltragerplatte"), active="", body=page_impressum, noindex=True,
         title="Impressum | Wilcowa AG", desc="Impressum von moertelpumpe.ch, Wilcowa AG Baumaschinen, Regensdorf."),
]
for slug, d in DETAILS.items():
    PAGES.append(dict(file=f"{slug}.html", active="anwendungen", body=(lambda s=slug: page_detail(s)), og_type="article",
                      share=(next(t for s_, n, t, *_ in APPS if s_ == slug), MENU_LABELS[slug][1], d["img"][0]),
                      og_image=d["img"][0] + ".avif", title=d["title"], desc=d["desc"]))

CRUMBS = {
    "produkte.html": [("Start", "index.html"), ("WPS-Mörtelpumpe", "produkte.html")],
    "anwendungen.html": [("Start", "index.html"), ("Anwendungen", "anwendungen.html")],
    "moertel-bedarf-rechner.html": [("Start", "index.html"), ("Mörtelrechner", "moertel-bedarf-rechner.html")],
    "faq.html": [("Start", "index.html"), ("Häufige Fragen", "faq.html")],
    "kontakt.html": [("Start", "index.html"), ("Kontakt", "kontakt.html")],
}
for s, n, t, *_ in APPS:
    CRUMBS[f"{s}.html"] = [("Start", "index.html"), ("Anwendungen", "anwendungen.html"), (t, f"{s}.html")]

for p in PAGES:
    if p["file"] in CRUMBS:
        p["ld"] = p.get("ld", []) + [breadcrumb_ld(CRUMBS[p["file"]])]
    body = p["body"]()
    body = re.sub(r"<main\b([^>]*)>", r"<div\1>", body).replace("</main>", "</div>")
    out = head(p) + SKIP + header(p["active"]) + '\n    <main id="inhalt">' + body + '    </main>\n' + footer()
    # Icon-Sprite ebenfalls versionieren, sonst zeigen Browser mit alter Kopie neue Symbole nicht an
    out = out.replace("assets/icons.svg#", f"assets/icons.svg?v={ver('assets/icons.svg')}#")
    out = relink(out)
    target = "index.html" if p["file"] == "index.html" else URLS[p["file"][:-5]] + ".html"
    (OUT / target).write_text(out.replace("ß", "ss"), encoding="utf-8", newline="\n")
    print("ok", p["file"])

# nicht mehr verwendete Seiten entfernen
for old in ["anwendung-fugen.html"] + [f"{k}.html" for k, v in URLS.items() if k != "index" and k != v]:
    f = OUT / old
    if f.exists():
        f.unlink()
        print("entfernt", old)

prio = {"index.html": "1.0", "produkte.html": "0.9", "anwendungen.html": "0.9"}
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in PAGES:
    if p.get("noindex"):
        continue
    loc = BASE + "/" + URLS[p["file"][:-5]]
    sm.append(f"  <url><loc>{loc}</loc><lastmod>2026-10-06</lastmod><priority>{prio.get(p['file'], '0.7')}</priority></url>")
sm.append("</urlset>")
(OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")
print("ok sitemap.xml")

# Teilen-Bilder 1200x630 (Facebook, LinkedIn, WhatsApp akzeptieren kein AVIF). Neu erzeugen mit: python tools/build_site.py --share
import sys
CHROME = next((c for c in [r"C:/Program Files/Google/Chrome/Application/chrome.exe", r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                            shutil.which("google-chrome") or "", shutil.which("chromium") or ""] if c and pathlib.Path(c).exists()), None)
share_dir = OUT / "assets" / "share"
share_dir.mkdir(exist_ok=True)
tpl = (pathlib.Path(__file__).resolve().parent / "share.html").as_uri()
for p in PAGES:
    target = share_dir / p["file"].replace(".html", ".jpg")
    if target.exists() and "--share" not in sys.argv:
        continue
    if not CHROME:
        print("Kein Chrome gefunden, Teilen-Bild fehlt:", target.name)
        continue
    t, sub, img = p["share"]
    url = tpl + "?" + urllib.parse.urlencode({"t": t, "s": sub, "i": img})
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--window-size=1200,630", "--virtual-time-budget=4000", f"--screenshot={target}", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Teilen-Bild", target.name)

# llms.txt: kompakte Zusammenfassung für KI-Suchsysteme (llmstxt.org)
apps_md = "\n".join(f"- [{t}]({BASE}/{s_}.html): {txt}" for s_, n, t, txt, img in APPS)
specs_md = "\n".join(f"- {a}: {b}" for g, items in SPEC_GROUPS for a, b in items)
llms = f"""# WPS-Mörtelpumpe – Wilcowa AG

> Verkauf und Vermietung der WPS-Mörtelpumpe in der Schweiz durch die Wilcowa AG Baumaschinen, Regensdorf. Die WPS ist eine druckluftbetriebene Mörtelpumpe der Winiger Pump System AG (Wald ZH) für Untermörteln, Fugen, Stahlzargen und Ankerverpressung.

Kontakt: Wilcowa AG Baumaschinen, Riedthofstrasse 172, 8105 Regensdorf, Telefon {PHONE}, {MAIL}. Öffnungszeiten Mo–Do 07:00–12:00 und 13:00–17:00, Fr 07:00–12:00 und 13:00–16:00.

## Produkt

- [WPS-Mörtelpumpe: Funktionsprinzip, technische Daten, Düsen, Kompressor]({BASE}/produkte.html)
- [Häufige Fragen]({BASE}/faq.html)
- [Mörtelrechner: Zeit, Kosten und Mörtel im Vergleich zur Handarbeit]({BASE}/moertel-bedarf-rechner.html)

## Technische Daten (Herstellerangaben)

{specs_md}

## Anwendungen

{apps_md}

## Quellen

- [Hersteller Winiger Pump System AG]({WPS}/)
- [Testbericht 1, Berner Fachhochschule 2009]({BFH1})
- [Testbericht 2, Berner Fachhochschule 2009]({BFH2})

## Optional

- [Kontakt und Anfrage]({BASE}/kontakt.html)
- [Impressum]({BASE}/impressum.html)
"""
(OUT / "llms.txt").write_text(relink(llms), encoding="utf-8", newline="\n")
print("ok llms.txt")

# nginx: saubere Adressen und 301 von alten .html-URLs
redirects = "\n".join(f"    location = /{old}.html {{ return 301 /{new}$is_args$args; }}"
                       for old, new in {**URLS, **OLD_EXTRA}.items() if old != "index" and old != new)
(OUT.parent / "nginx-redirects.conf").write_text(
    "# Automatisch erzeugt von tools/build_site.py\n" + redirects + "\n", encoding="utf-8", newline="\n")
print("ok nginx-redirects.conf")
