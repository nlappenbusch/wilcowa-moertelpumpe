# Erzeugt alle Seiten in website/ (einheitlicher Header/Footer). Aufruf: python tools/build_site.py
#
# Technische Angaben stammen aus den Unterlagen des Herstellers Winiger Pump System AG
# (www.wps-ag.ch, Flyer WPS-U-2.2019d und WPS-HT-4.2018d) sowie den Testberichten der
# Berner Fachhochschule (KTI-Projekt 8971.1, 2009). Texte bitte nicht wörtlich vom Hersteller übernehmen.
import json, pathlib, html as h

OUT = pathlib.Path(__file__).resolve().parent.parent / "website"
BASE = "https://moertelpumpe.ch"
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
    ("anwendung-stahlzargen", "Stahlzargen", "Stahlzargen einmörteln", "Zargen auch in Sichtbauweise und bei 1 bis 2 cm Spalt sauber hinterfüllen.", "Ausmorteln_Stahltrager"),
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

def downloads(*keys):
    lis = "".join(f'<li><a href="{PDFS[k][0]}" target="_blank" rel="noopener">{icon("file")}{PDFS[k][1]}<span>{PDFS[k][2]}</span></a></li>' for k in keys)
    return f'<ul class="downloads">{lis}</ul>'

def head(p):
    canonical = BASE + "/" + ("" if p["file"] == "index.html" else p["file"])
    og_img = BASE + "/assets/" + p.get("og_image", "Untermorteln_Stahltragerplatte.avif")
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
    <meta property="og:locale" content="de_CH">
    <link rel="icon" type="image/png" href="assets/wilcowa-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap">
    <link rel="stylesheet" href="style.css">{ld}
</head>
<body>
'''

def header(active):
    def item(href, label, key):
        cls = ' class="active"' if key == active else ""
        return f'<li><a href="{href}"{cls}>{label}</a></li>'
    sub = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, n, t, *_ in APPS)
    return f'''    <header class="site-header">
        <div class="container">
            <a class="logo" href="index.html"><img src="assets/wilcowa-logo.png" alt="Wilcowa AG" width="1600" height="400"></a>
            <nav class="main-nav" aria-label="Hauptnavigation">
                <ul>
                    {item("produkte.html", "WPS-Mörtelpumpe", "produkt")}
                    <li class="has-sub"><a href="anwendungen.html"{' class="active"' if active == "anwendungen" else ""}>Anwendungen</a>
                        <ul class="submenu"><li><a href="anwendungen.html">Übersicht</a></li>{sub}</ul>
                    </li>
                    {item("moertel-bedarf-rechner.html", "Mörtelrechner", "rechner")}
                    {item("faq.html", "Fragen", "faq")}
                    {item("kontakt.html", "Kontakt", "kontakt")}
                    <li class="nav-mobile-only"><a href="{PHONE_HREF}">Telefon {PHONE}</a></li>
                </ul>
            </nav>
            <div class="header-contact">
                <a class="header-phone" href="{PHONE_HREF}">{PHONE}</a>
                <a class="btn btn-primary" href="kontakt.html">Anfrage</a>
            </div>
            <button class="nav-toggle" type="button" aria-label="Menü" aria-expanded="false"><svg class="i i-menu" aria-hidden="true"><use href="assets/icons.svg#menu"/></svg><svg class="i i-close" aria-hidden="true"><use href="assets/icons.svg#close"/></svg></button>
        </div>
    </header>
'''

def contact_strip():
    return f'''
    <section class="contact-strip">
        <div class="container">
            <div>
                <h2>Beratung, Miete und Verkauf</h2>
                <p>Wilcowa AG Baumaschinen, Riedthofstrasse 172, 8105 Regensdorf</p>
            </div>
            <div class="btn-row">
                <a class="btn btn-primary" href="{PHONE_HREF}">{PHONE}</a>
                <a class="btn btn-secondary" href="kontakt.html">Anfrage senden</a>
            </div>
        </div>
    </section>
'''

def footer():
    apps = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, n, t, *_ in APPS[:6])
    return f'''
    <footer class="site-footer">
        <div class="container footer-grid">
            <div>
                <h2>Wilcowa AG Baumaschinen</h2>
                <address>Riedthofstrasse 172<br>8105 Regensdorf<br><a href="{PHONE_HREF}">{PHONE}</a><br><a href="mailto:{MAIL}">{MAIL}</a></address>
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
                <p>Mo–Do 07:00–12:00, 13:00–17:00<br>Fr 07:00–12:00, 13:00–16:00</p>
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

    <script src="script.js"></script>
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

def page_head(crumbs, title, lead):
    return f'''
    <section class="page-head">
        <div class="container">
            {breadcrumbs(crumbs)}
            <h1>{title}</h1>
            <p class="lead">{lead}</p>
        </div>
    </section>
'''

def side_contact():
    return f'''<section class="side-contact">
                    <h2>Beratung und Miete</h2>
                    <p>Wilcowa AG, Regensdorf</p>
                    <a class="phone" href="{PHONE_HREF}">{PHONE}</a>
                    <p><a href="kontakt.html">Anfrage senden</a></p>
                </section>'''

def side_apps(current):
    lis = "".join(f'<li><a href="{s}.html"{" aria-current=" + chr(34) + "page" + chr(34) if s == current else ""}>{t}</a></li>' for s, n, t, *_ in APPS)
    return f'<section><h2>Anwendungen</h2><ul class="side-links">{lis}</ul></section>'

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

SPECS = [
    ("Förderprinzip", "Druckluft mit Vibrator, ohne Schnecke oder Rotor"),
    ("Fördermenge", "0 bis 15 l/min, stufenlos regelbar"),
    ("Förderdruck", "max. 2.5 bar"),
    ("Förderweite", "bis 4 m (bei Stahlzargen 3.2 m)"),
    ("Luftbedarf", "200 l/min bei 8 bis 9 bar"),
    ("Behälter", "60 l, davon 50 l nutzbar"),
    ("Einfüllhöhe", "900 mm"),
    ("Abmessungen (L × B × H)", "600 × 520 × 1140 mm"),
    ("Gewicht", "50 bis 55 kg, je nach Zubehör"),
]

def spec_table(rows):
    trs = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td></tr>" for a, b in rows)
    return f'<table class="table"><tbody>{trs}</tbody></table>'

FAQ = [
    ("Braucht die WPS-Mörtelpumpe einen Kompressor?",
     "Ja. Die Pumpe wird mit Druckluft betrieben und braucht rund 200 l/min bei 8 bis 9 bar. Für Untermörteln und Stahlzargen reicht ein 230-V-Kompressor mit 2.2 kW, für Fugenarbeiten wird ein Kompressor mit 3 kW (400 V) empfohlen. Wir beraten Sie gerne zum passenden Gerät."),
    ("Welche Mörtel lassen sich pumpen?",
     "Die WPS fördert auch Mörtel, die als nicht maschinengängig gelten, zum Beispiel normalen Zement-Mauermörtel. Viele handelsübliche Fugenmörtel sind bereits auf Pumpfähigkeit getestet, die Liste finden Sie im Anwendungsblatt Fugen. Entscheidend ist die richtige Konsistenz. Mörtel, die noch nicht getestet sind, sollten vor dem Einsatz geprüft werden."),
    ("Wie lässt sich die Fördermenge regeln?",
     "Über den Luftdruck im Behälter stufenlos von 0 bis 15 l/min. Mit einem Kugelhahn an der Düse wird der Mörtelfluss sofort gestoppt und wieder gestartet. Der Förderdruck ist auf 2.5 bar begrenzt."),
    ("Wie niedrig darf eine Fuge beim Untermörteln sein?",
     "Die Fuge sollte mindestens 11 mm hoch sein, damit die Breitschlitzdüse mit Schnabel unter die Schwelle geschoben werden kann. In den Versuchen der Berner Fachhochschule wurden Höhen von 10 bis 50 mm untersucht, gut gefüllt wurden vor allem 20 bis 40 mm."),
    ("Kann ich bei tiefen Temperaturen arbeiten?",
     "In den Versuchen der Berner Fachhochschule härtete der Mörtel auch bei 0 °C Aussentemperatur aus, sofern er beim Einpumpen mindestens 6 °C warm war. Massgebend sind immer die Angaben des Mörtelherstellers."),
    ("Wie aufwendig ist die Reinigung?",
     "Inbetriebnahme und Reinigung dauern jeweils etwa 5 bis 10 Minuten. Weil der Mörtel ohne Schnecke oder Rotor gefördert wird, gibt es kaum Verschleissteile."),
    ("Wie schwer ist die Pumpe, und passt sie aufs Gerüst?",
     "Die Pumpe wiegt je nach Zubehör 50 bis 55 kg und ist als Sackkarre gebaut. Sie lässt sich so auf der Baustelle und auf dem Gerüst verschieben. Die Einfüllhöhe beträgt 900 mm."),
    ("Kann ich die Pumpe mieten?",
     "Ja. Sie können die WPS-Mörtelpumpe bei uns mieten, zum Beispiel für ein einzelnes Projekt oder um sie vor dem Kauf mit Ihrem Mörtel zu testen. Verfügbarkeit und Konditionen erhalten Sie telefonisch oder über das Anfrageformular."),
]

# ------------------------------------------------------------------ Startseite
def page_index():
    tiles = "".join(f'''
                <li><a href="{s}.html"><img src="assets/{img}.avif" alt="{t}" loading="lazy" width="900" height="675"><h3>{t}</h3><p>{txt}</p></a></li>''' for s, n, t, txt, img in APPS)
    return f'''
    <main>
    <section class="hero">
        <div class="container">
            <div>
                <h1>WPS-Mörtelpumpe zum Untermörteln, Fugen und Einmörteln von Stahlzargen</h1>
                <p class="lead">Die druckluftbetriebene WPS-Mörtelpumpe fördert auch Mörtel, die sich mit herkömmlichen Maschinen nicht pumpen lassen. Der Mörtelfluss lässt sich jederzeit stoppen und wieder starten. Die Wilcowa AG in Regensdorf verkauft und vermietet die Pumpe mit Zubehör.</p>
                <div class="btn-row">
                    <a class="btn btn-primary" href="kontakt.html">Anfrage senden</a>
                    <a class="btn btn-secondary" href="produkte.html">Technische Daten</a>
                </div>
            </div>
            <img src="assets/Untermorteln_Stahltragerplatte.avif" alt="Untermörteln einer Stahlplatte mit der WPS-Mörtelpumpe" width="914" height="682" fetchpriority="high">
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
                <h3 style="margin-bottom:10px">Technische Daten</h3>
                {spec_table(SPECS[:7])}
                <p class="table-note">Herstellerangaben. Leistungsdaten hängen von Mörtel und Anwendung ab.</p>
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
                <h2>Geprüft an der Berner Fachhochschule</h2>
                <p>Im Rahmen eines KTI-Forschungsprojekts zu Fugensystemen im Holzbau hat die Berner Fachhochschule (Architektur, Holz und Bau, Biel) 2009 das Untermörteln von Holzschwellen mit der WPS-Mörtelpumpe untersucht.</p>
                <ul class="bullets" style="margin-top:14px">
                    <li>Schwellen von 100 mm Breite wurden bei 20 bis 40 mm Fugenhöhe vollständig unterfüttert.</li>
                    <li>Mit der Schnabeldüse gelang die volle Unterstopfung ab 10 mm Höhe.</li>
                    <li>Bei 0 °C Aussentemperatur härtete der Mörtel aus, wenn er beim Einpumpen mindestens 6 °C hatte.</li>
                    <li>Das Mörtelbett mit der WPS war günstiger als ein herkömmliches Mörtelbett.</li>
                </ul>
            </div>
            <div>
                <h2>Kauf und Miete</h2>
                <p>Sie können die WPS-Mörtelpumpe bei uns kaufen oder mieten. Die Miete eignet sich für einzelne Projekte oder um die Pumpe vor dem Kauf mit Ihrem eigenen Mörtel auszuprobieren.</p>
                <p>Wir beraten Sie zur Ausrüstung für Ihre Anwendung, also zu Düsen, Kompressor und Mörtelmischer, und liefern das Zubehör.</p>
                <h3 style="margin-top:28px;margin-bottom:8px">Unterlagen</h3>
                {downloads("untermoerteln", "fugen", "bfh1", "bfh2")}
            </div>
        </div>
    </section>
{contact_strip()}
    </main>
'''

# ------------------------------------------------------------------ Produkt
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
    return page_head(crumbs, "WPS-Mörtelpumpe", "Druckluftbetriebene Mörtelpumpe der Winiger Pump System AG, Wald ZH. Patentiert, verschleissfrei und für Standardmörtel ausgelegt.") + f'''
    <main class="section">
        <div class="container layout">
            <article class="prose">
                <figure class="lead-figure"><img src="assets/Untermorteln_Holzbau.avif" alt="WPS-Mörtelpumpe mit Behälter und Fahrgestell" width="790" height="906" style="object-fit:contain;background:#f4f5f6"></figure>

                <h2>Funktionsprinzip</h2>
                <p>Die WPS-Mörtelpumpe arbeitet ohne Schnecke, Rotor oder Kolben. Ein auf den Mörtel abgestimmter Druckluftvibrator macht die Masse im Behälter fliessfähig, der Luftdruck darüber fördert sie durch den Schlauch zur Düse. So entsteht keine mechanische Reibungswärme und der Mörtel entmischt sich nicht. Auch Mörtel, die als nicht maschinengängig gelten, führen deshalb nicht zu Stopfern.</p>
                <p>Der Förderdruck ist auf 2.5 bar begrenzt. Damit lässt sich der Mörtel genau dosieren: Ein Kugelhahn an der Düse stoppt und startet den Mörtelfluss sofort. Bei motorgetriebenen Schnecken- oder Schlauchpumpen müsste dafür der Motor abgeschaltet werden.</p>

                <h2>Eigenschaften</h2>
                <ul class="bullets">
                    <li>pumpt auch nicht maschinengängige Mörtel, zum Beispiel Zement-Mauermörtel</li>
                    <li>Fördermenge stufenlos über den Luftdruck einstellbar</li>
                    <li>Mörtelfluss am Kugelhahn sofort stopp- und startbar</li>
                    <li>verschleissfreies Pumpsystem, geringe Betriebskosten</li>
                    <li>in rund 5 Minuten betriebsbereit und in 5 bis 10 Minuten gereinigt</li>
                    <li>Sackkarren-Bauweise, gerüsttauglich</li>
                </ul>

                <h2 id="technische-daten">Technische Daten</h2>
                {spec_table(SPECS)}
                <p class="table-note">Angaben des Herstellers. Leistungsdaten sind Erfahrungswerte und hängen von Anwendung und Mörtelkonsistenz ab.</p>

                <h2 id="zubehoer">Düsen und Zubehör</h2>
                <div class="table-wrap"><table class="table"><thead><tr><th>Teil</th><th>Einsatz</th></tr></thead><tbody>{noz}</tbody></table></div>

                <h3>Kompressor</h3>
                <p>Für den Betrieb braucht es einen Kompressor. Welche Leistung nötig ist, hängt von der Anwendung ab:</p>
                <div class="table-wrap"><table class="table"><thead><tr><th>Modell</th><th>Daten</th><th>Geeignet für</th></tr></thead><tbody>{com}</tbody></table></div>

                <h3>Mörtelmischer</h3>
                <p>Zum Anmachen des Mörtels eignet sich ein horizontaler Zwangsmischer wie der IPERBET, der wenig Luft in den Mörtel einträgt. Für Fugenarbeiten kommen ein Handrührwerk zum Nachmischen und eine Schlauchtrommel dazu.</p>

                <h2>Hersteller</h2>
                <p>Die WPS-Mörtelpumpe wird von der Winiger Pump System AG in Wald ZH entwickelt und gebaut. Das Unternehmen wurde 2005 von Hans-Rudolf und Gerhard Winiger gegründet, die Pumpe ist seit 2006 im Einsatz. Pumpsystem und Design sind patentiert.</p>
                <p class="source-note">Weitere Informationen und Anwendungsvideos finden Sie auf der Website des Herstellers: <a href="{WPS}/" target="_blank" rel="noopener">wps-ag.ch</a></p>
            </article>
            <aside class="sidebar">
                <section><h2>Unterlagen</h2>{downloads("untermoerteln", "fugen", "tiefbau")}</section>
                {side_contact()}
            </aside>
        </div>
    </main>
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
    img=("Ausmorteln_Stahltrager", "Einmörteln mit der WPS-Mörtelpumpe", 874, 1166),
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
                    <figure><img src="assets/Ausfugen_Sandsteingewolbe.avif" alt="Ausfugen eines Sandstein-Kellergewölbes" loading="lazy"><figcaption>Sandstein-Kellergewölbe</figcaption></figure>
                    <figure><img src="assets/Fugen_Randsteine.avif" alt="Randsteine verfugen" loading="lazy"><figcaption>Randsteine im Strassenbau</figcaption></figure>
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

def page_detail(slug):
    d = DETAILS[slug]
    t = next(t for s, n, t, *_ in APPS if s == slug)
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html"), (t, f"{slug}.html")]
    img, alt, w, hh = d["img"]
    return page_head(crumbs, t, d["lead"]) + f'''
    <main class="section">
        <div class="container layout">
            <article class="prose">
                <figure class="lead-figure"><img src="assets/{img}.avif" alt="{alt}" width="{w}" height="{hh}"></figure>
                {d["body"]}
                <p class="source-note">Technische Angaben nach Unterlagen des Herstellers Winiger Pump System AG. Videos zu dieser Anwendung: <a href="{WPS}/{d["wps"]}" target="_blank" rel="noopener">wps-ag.ch</a></p>
            </article>
            <aside class="sidebar">
                {side_contact()}
                <section><h2>Unterlagen</h2>{downloads(*d["pdfs"])}</section>
                {side_apps(slug)}
            </aside>
        </div>
    </main>
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

def page_anwendungen():
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html")]
    rows = "".join(f'''
                <li>
                    <img src="assets/{img}.avif" alt="{t}" loading="lazy">
                    <div>
                        <h2><a href="{s}.html" style="color:inherit;text-decoration:none">{t}</a></h2>
                        <p>{DETAILS[s]["lead"]}</p>
                        <a class="more" href="{s}.html">{t}: Vorgehen und Ausrüstung</a>
                    </div>
                </li>''' for s, n, t, txt, img in APPS)
    gal = "".join(f'<figure><img src="assets/{img}.avif" alt="{c}" loading="lazy"><figcaption>{c}</figcaption></figure>' for img, c in GALLERY)
    return page_head(crumbs, "Anwendungen der WPS-Mörtelpumpe", "Untermörteln, Einmörteln, Verfugen und Verpressen im Hoch-, Holz- und Tiefbau.") + f'''
    <main>
        <section class="section">
            <div class="container">
                <ul class="app-list">{rows}
                </ul>
            </div>
        </section>
        <section class="section bg-alt">
            <div class="container two-col">
                <div>
                    <h2>Weitere Einsätze</h2>
                    <p>Die WPS wurde ausserdem schon für diese Arbeiten verwendet:</p>
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
                <div class="section-title"><h2>Bilder von Baustellen</h2></div>
                <div class="gallery">{gal}</div>
            </div>
        </section>
{contact_strip()}
    </main>
'''

# ------------------------------------------------------------------ Rechner
def calc_row(key, label, unit, val, mx, step):
    return f'''<div class="calc-row">
                        <div class="calc-row-head">
                            <label for="calc-{key}-input">{label}</label>
                            <div class="calc-num"><input type="number" id="calc-{key}-input" value="{val}" min="0" step="{step}" inputmode="decimal" oninput="syncInput('{key}', 'input')"><span>{unit}</span></div>
                        </div>
                        <input type="range" id="calc-{key}-range" min="0" max="{mx}" value="{val}" step="{step}" aria-label="{label}" oninput="syncInput('{key}', 'range')">
                    </div>'''

def page_rechner():
    crumbs = [("Start", "index.html"), ("Mörtelrechner", "moertel-bedarf-rechner.html")]
    return page_head(crumbs, "Mörtelbedarf für Fugen und Hohlräume berechnen", "Volumen und Trockenmaterial aus Länge, Breite und Tiefe der Fuge, inklusive Zuschlag für Verschnitt.") + f'''
    <main class="section">
        <div class="container two-col">
            <div class="calc">
                <div class="calc-body">
                    {calc_row("length", "Länge", "m", 10, 100, 0.5)}
                    {calc_row("width", "Breite", "mm", 15, 100, 1)}
                    {calc_row("depth", "Tiefe", "mm", 50, 200, 1)}
                    <div class="calc-selects">
                        <div class="field">
                            <label for="calc-density">Frischmörtel-Rohdichte</label>
                            <select id="calc-density" onchange="calculateMortar()">
                                <option value="1.8" selected>1.8 kg/l (Normalmörtel)</option>
                                <option value="1.2">1.2 kg/l (Leichtmörtel)</option>
                                <option value="2.0">2.0 kg/l</option>
                                <option value="2.2">2.2 kg/l</option>
                            </select>
                        </div>
                        <div class="field">
                            <label for="calc-wastage">Zuschlag</label>
                            <select id="calc-wastage" onchange="calculateMortar()">
                                <option value="0">0 %</option>
                                <option value="5">5 %</option>
                                <option value="10" selected>10 %</option>
                                <option value="20">20 %</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="calc-result" aria-live="polite">
                    <div><span>Volumen</span><output id="result-liters">0.0</output><small>Liter</small></div>
                    <div><span>Mörtel ca.</span><output id="result-kg">0.0</output><small>kg</small></div>
                </div>
                <p class="calc-foot">Richtwert. Den genauen Bedarf pro Liter Fuge entnehmen Sie dem Datenblatt des Mörtels.</p>
            </div>
            <div class="prose">
                <h2>Hinweise zur Berechnung</h2>
                <p>Das Volumen ergibt sich aus Länge × Breite × Tiefe. Bei V-Fugen, die in der Tiefe auslaufen, rechnen Sie mit der halben Tiefe. Beim Untermörteln entspricht die Breite der Schwellenbreite und die Tiefe der Fugenhöhe.</p>
                <p>Die Mörtelmenge wird über die Rohdichte des Frischmörtels geschätzt. Wie viel Trockenmörtel Sie pro Liter Frischmörtel brauchen, steht als Ergiebigkeit im Datenblatt des Mörtelherstellers.</p>
                <h3>Beispiel</h3>
                <p>Eine Schwelle von 10 m Länge und 100 mm Breite wird mit 20 mm Fugenhöhe untermörtelt: 10 × 100 × 20 / 1000 = 20 Liter, mit 10 % Zuschlag 22 Liter.</p>
                <p>Für grössere Mengen lohnt sich die <a href="produkte.html">WPS-Mörtelpumpe</a>, die bis zu 50 Liter Mörtel pro Füllung aufnimmt.</p>
            </div>
        </div>
    </main>
{contact_strip()}
'''

# ------------------------------------------------------------------ FAQ
def page_faq():
    crumbs = [("Start", "index.html"), ("Häufige Fragen", "faq.html")]
    items = "".join(f'''
                <details><summary>{q}</summary><div class="answer"><p>{a}</p></div></details>''' for q, a in FAQ)
    return page_head(crumbs, "Häufige Fragen zur WPS-Mörtelpumpe", "Zu Kompressor, Mörtel, Bedienung, Untermörteln und Miete.") + f'''
    <main class="section">
        <div class="container layout">
            <div class="faq">{items}
            </div>
            <aside class="sidebar">
                {side_contact()}
                <section><h2>Unterlagen</h2>{downloads("untermoerteln", "fugen")}</section>
            </aside>
        </div>
    </main>
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
                <li>{icon("clock")}<div><strong>Öffnungszeiten</strong>Mo–Do 07:00–12:00, 13:00–17:00<br>Fr 07:00–12:00, 13:00–16:00</div></li>
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
                    <div class="field-full form-actions"><button class="btn btn-primary" type="submit">E-Mail erstellen</button><span class="muted small">* Pflichtfelder</span></div>
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
              "manufacturer": {"@type": "Organization", "name": "Winiger Pump System AG", "url": WPS + "/"},
              "offers": {"@type": "Offer", "url": BASE + "/kontakt.html", "priceCurrency": "CHF", "availability": "https://schema.org/InStock",
                         "seller": {"@type": "Organization", "name": "Wilcowa AG Baumaschinen"}}}

PAGES = [
    dict(file="index.html", active="", body=page_index, ld=[LOCAL_BUSINESS],
         title="Mörtelpumpe mieten und kaufen | WPS-Mörtelpumpe – Wilcowa AG",
         desc="WPS-Mörtelpumpe kaufen oder mieten bei Wilcowa in Regensdorf: druckluftbetrieben, 0–15 l/min, pumpt auch Standardmörtel. Für Untermörteln, Fugen, Stahlzargen und Anker."),
    dict(file="produkte.html", active="produkt", body=page_produkt, og_type="product", og_image="Untermorteln_Holzbau.avif", ld=[PRODUCT_LD],
         title="WPS-Mörtelpumpe: Technische Daten, Düsen und Kompressor | Wilcowa",
         desc="Technische Daten der WPS-Mörtelpumpe: 0–15 l/min, max. 2.5 bar, Förderweite bis 4 m, Behälter 60 l, Luftbedarf 200 l/min. Düsen, Kompressoren und Mörtelmischer."),
    dict(file="anwendungen.html", active="anwendungen", body=page_anwendungen, og_image="Natursteinwand_Fugen.avif",
         title="Anwendungen der Mörtelpumpe: Untermörteln, Fugen, Stahlzargen | WPS",
         desc="Einsatzgebiete der WPS-Mörtelpumpe: Holzschwellen untermörteln, Stahlzargen einmörteln, Naturstein und Klinker verfugen, Betonfugen, Deckenfugen und Anker verpressen."),
    dict(file="moertel-bedarf-rechner.html", active="rechner", body=page_rechner,
         title="Mörtelrechner: Mörtelbedarf für Fugen berechnen | Wilcowa",
         desc="Mörtelbedarf online berechnen: Volumen und Mörtelmenge für Fugen, Untermörtelungen und Hohlräume aus Länge, Breite und Tiefe, inklusive Zuschlag."),
    dict(file="faq.html", active="faq", body=page_faq,
         ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}],
         title="Fragen zur WPS-Mörtelpumpe: Kompressor, Mörtel, Miete | Wilcowa",
         desc="Antworten zur WPS-Mörtelpumpe: Welcher Kompressor, welche Mörtel, minimale Fugenhöhe beim Untermörteln, Arbeiten bei Kälte, Reinigung, Gewicht und Miete."),
    dict(file="kontakt.html", active="kontakt", body=page_kontakt, ld=[LOCAL_BUSINESS],
         title="Kontakt: WPS-Mörtelpumpe anfragen | Wilcowa AG Regensdorf",
         desc="Wilcowa AG Baumaschinen, Riedthofstrasse 172, 8105 Regensdorf. Beratung, Miete und Offerte für die WPS-Mörtelpumpe: +41 43 388 70 60, info@wilcowa.ch."),
    dict(file="impressum.html", active="", body=page_impressum, noindex=True,
         title="Impressum | Wilcowa AG", desc="Impressum von moertelpumpe.ch, Wilcowa AG Baumaschinen, Regensdorf."),
]
for slug, d in DETAILS.items():
    PAGES.append(dict(file=f"{slug}.html", active="anwendungen", body=(lambda s=slug: page_detail(s)), og_type="article",
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
    out = head(p) + header(p["active"]) + p["body"]() + footer()
    (OUT / p["file"]).write_text(out.replace("ß", "ss"), encoding="utf-8", newline="\n")
    print("ok", p["file"])

# nicht mehr verwendete Seiten entfernen
for old in ["anwendung-fugen.html"]:
    f = OUT / old
    if f.exists():
        f.unlink()
        print("entfernt", old)

prio = {"index.html": "1.0", "produkte.html": "0.9", "anwendungen.html": "0.9"}
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in PAGES:
    if p.get("noindex"):
        continue
    loc = BASE + "/" + ("" if p["file"] == "index.html" else p["file"])
    sm.append(f"  <url><loc>{loc}</loc><lastmod>2026-10-06</lastmod><priority>{prio.get(p['file'], '0.7')}</priority></url>")
sm.append("</urlset>")
(OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")
print("ok sitemap.xml")
