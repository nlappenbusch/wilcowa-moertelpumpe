# Erzeugt alle Seiten in website/ (einheitlicher Header/Footer). Aufruf: python tools/build_site.py
import json, pathlib, html as h

OUT = pathlib.Path(__file__).resolve().parent.parent / "website"
BASE = "https://moertelpumpe.ch"
PHONE, PHONE_HREF = "+41 43 388 70 60", "tel:+41433887060"
MAIL = "info@wilcowa.ch"
HOURS = "Mo–Do 07:00–12:00 / 13:00–17:00 · Fr bis 16:00"

def icon(name, cls="i"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="assets/icons.svg#{name}"/></svg>'

APPS = [  # slug, Navigationstitel, Kachel-Titel, Kurztext, Bild
    ("anwendung-stahlzargen", "Stahlzargen", "Stahlzargen einmörteln", "Zargen hohlraumfrei hinterfüllen – ohne Leibungsschäden, brandschutzgerecht.", "Stahlschalung_Saeule"),
    ("anwendung-untermoerteln", "Untermörteln", "Untermörteln von Schwellen", "Setzschwellen, Stahlplatten und Elemente vollflächig unterfüttern.", "Untermorteln_Stahltragerplatte"),
    ("anwendung-naturstein", "Naturstein & Denkmalpflege", "Natursteinmauern verfugen", "Unregelmässige Fugen sauber füllen, ohne den Stein zu verschmutzen.", "Natursteinwand_Fugen"),
    ("anwendung-maueranker", "Maueranker", "Maueranker verpressen", "Bohrlöcher mit der Lanze von hinten nach vorne lunkerfrei verfüllen.", "Mauer-Anker_verpressen"),
    ("anwendung-spannbeton", "Spannbeton", "Spannbetonfugen vergiessen", "Fugen zwischen Hohldecken-Elementen im Stehen vollvolumig vergiessen.", "Ausgiessen_Spannbetonplatten"),
    ("anwendung-daemmplatten", "Dämmplatten", "Dämmplatten kleben", "Kleberaupen dosiert auf Platte oder Untergrund auftragen.", "Daemmplatten_Kleber"),
    ("anwendung-fugen", "Fugen & Sanierung", "Fugen & Sanierung", "Klinker, Randsteine und Sichtmauerwerk maschinell neu verfugen.", "Klinker-Verblender_gefugt"),
]

PDFS = {
    "untermoerteln": ("assets/Flyer_Untermorteln_2019.pdf", "Flyer Untermörteln", "PDF · Übersicht & Zubehör"),
    "fugen": ("assets/Anwendung_Fugen.pdf", "Anwendungsblatt Fugen", "PDF · Technische Hinweise"),
    "tiefbau": ("assets/Flyer_Strassen-Hoch-Tiefbau.pdf", "Flyer Strassen-, Hoch- & Tiefbau", "PDF · Einsatzbeispiele"),
}

def download(key):
    href, title, meta = PDFS[key]
    return f'<a class="download" href="{href}" target="_blank" rel="noopener">{icon("file")}<div><strong>{title}</strong><span>{meta}</span></div></a>'

def head(page):
    canonical = BASE + "/" + ("" if page["file"] == "index.html" else page["file"])
    og_img = BASE + "/assets/" + page.get("og_image", "Untermorteln_Stahltragerplatte.avif")
    robots = '\n    <meta name="robots" content="noindex, follow">' if page.get("noindex") else ""
    ld = "".join(f'\n    <script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n    </script>' for x in page.get("ld", []))
    return f'''<!DOCTYPE html>
<html lang="de-CH">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page["title"]}</title>
    <meta name="description" content="{h.escape(page["desc"])}">{robots}
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="{page.get("og_type", "website")}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{h.escape(page["title"])}">
    <meta property="og:description" content="{h.escape(page["desc"])}">
    <meta property="og:image" content="{og_img}">
    <meta property="og:locale" content="de_CH">
    <link rel="icon" type="image/png" href="assets/wilcowa-logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
    <link rel="stylesheet" href="style.css">{ld}
</head>
<body>
'''

def header(active):
    def a(href, label, key):
        cls = ' class="active"' if key == active else ""
        cur = ' aria-current="page"' if href == active_file[0] else ""
        return f'<a href="{href}"{cls}{cur}>{label}</a>'
    sub = "\n".join(f'                            <li><a href="{s}.html">{n}</a></li>' for s, n, *_ in APPS)
    return f'''    <div class="topbar">
        <div class="container">
            <span class="topbar-hide-md">Exklusivvertrieb der WPS-Mörtelpumpe in der Schweiz</span>
            <div class="topbar-items">
                <span class="topbar-hide-md">{icon("clock")}{HOURS}</span>
                <a href="{PHONE_HREF}">{icon("phone")}{PHONE}</a>
                <a href="mailto:{MAIL}">{icon("mail")}{MAIL}</a>
            </div>
        </div>
    </div>

    <header class="site-header">
        <div class="container">
            <a class="logo" href="index.html"><img src="assets/wilcowa-logo.png" alt="Wilcowa AG" width="1600" height="400"></a>
            <nav class="main-nav" aria-label="Hauptnavigation">
                <ul>
                    <li>{a("produkte.html", "Produkt &amp; Daten", "produkt")}</li>
                    <li class="has-sub">
                        <a href="anwendungen.html"{' class="active"' if active == "anwendungen" else ""}>Anwendungen {icon("chevron")}</a>
                        <ul class="submenu">
                            <li><a href="anwendungen.html">Alle Anwendungen</a></li>
{sub}
                        </ul>
                    </li>
                    <li>{a("moertel-bedarf-rechner.html", "Mörtelrechner", "rechner")}</li>
                    <li>{a("faq.html", "FAQ", "faq")}</li>
                    <li>{a("kontakt.html", "Kontakt", "kontakt")}</li>
                    <li class="nav-mobile-cta"><a class="btn btn-primary" href="kontakt.html">Offerte anfragen</a></li>
                </ul>
            </nav>
            <div class="header-cta">
                <a class="btn btn-primary" href="kontakt.html">Offerte anfragen</a>
                <button class="nav-toggle" type="button" aria-label="Menü" aria-expanded="false">{icon("menu", "i i-menu")}{icon("close", "i i-close")}</button>
            </div>
        </div>
    </header>
'''

active_file = [""]

def contact_band():
    return f'''
    <section class="contact-band">
        <div class="container">
            <div>
                <p class="eyebrow">Beratung &amp; Offerte</p>
                <h2>Passt die WPS zu Ihrem Material und Ihrer Baustelle?</h2>
                <p>Unser Team in Regensdorf berät Sie zu Mörtel, Düsen und Zubehör – und stellt Ihnen die Pumpe auf Wunsch zum Testen zur Verfügung.</p>
            </div>
            <div>
                <a class="contact-band-phone" href="{PHONE_HREF}">{icon("phone")}{PHONE}</a>
                <p class="contact-band-hours">{HOURS}</p>
                <div class="contact-band-actions">
                    <a class="btn btn-light" href="kontakt.html">Anfrage senden</a>
                    <a class="btn btn-ghost-light" href="mailto:{MAIL}">{MAIL}</a>
                </div>
            </div>
        </div>
    </section>
'''

def footer():
    apps = "\n".join(f'                        <li><a href="{s}.html">{t}</a></li>' for s, n, t, *_ in APPS[:5])
    return f'''
    <footer class="site-footer">
        <div class="container footer-grid">
            <div class="footer-brand">
                <img src="assets/wilcowa-logo.png" alt="Wilcowa AG" width="1600" height="400">
                <address>
                    Wilcowa AG Baumaschinen<br>
                    Riedthofstrasse 172<br>
                    8105 Regensdorf
                </address>
            </div>
            <div>
                <h3>Produkt</h3>
                <ul>
                    <li><a href="produkte.html">WPS-Mörtelpumpe</a></li>
                    <li><a href="produkte.html#technische-daten">Technische Daten</a></li>
                    <li><a href="produkte.html#systemvergleich">Systemvergleich</a></li>
                    <li><a href="moertel-bedarf-rechner.html">Mörtelrechner</a></li>
                    <li><a href="faq.html">Häufige Fragen</a></li>
                </ul>
            </div>
            <div>
                <h3>Anwendungen</h3>
                <ul>
{apps}
                </ul>
            </div>
            <div>
                <h3>Kontakt</h3>
                <ul>
                    <li><a href="{PHONE_HREF}">{PHONE}</a></li>
                    <li><a href="mailto:{MAIL}">{MAIL}</a></li>
                    <li>Mo–Do 07:00–17:00</li>
                    <li>Fr 07:00–16:00</li>
                </ul>
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
    lis = []
    for i, (label, href) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li><span aria-current="page">{label}</span></li>')
        else:
            lis.append(f'<li><a href="{href}">{label}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Brotkrumen"><ol>{"".join(lis)}</ol></nav>'

def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": label, "item": BASE + "/" + (href if href != "index.html" else "")}
        for i, (label, href) in enumerate(items)]}

def page_head(crumbs, eyebrow, title, lead):
    return f'''
    <section class="page-head">
        <div class="container">
            {breadcrumbs(crumbs)}
            <p class="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
            <p class="lead">{lead}</p>
        </div>
    </section>
'''

def contact_box():
    return f'''<div class="side-box side-box-dark">
                        <h3>Beratung</h3>
                        <p>Fragen zu Material, Düsen oder Miete?</p>
                        <a class="side-phone" href="{PHONE_HREF}">{icon("phone")}{PHONE}</a>
                        <p>Mo–Do bis 17:00, Fr bis 16:00</p>
                        <a class="btn btn-light btn-block" href="kontakt.html">Anfrage senden</a>
                    </div>'''

CUR = ' aria-current="page"'

def app_links(current):
    lis = "\n".join(
        f'                            <li><a href="{s}.html"{CUR if s == current else ""}>{t}{icon("arrow")}</a></li>'
        for s, n, t, *_ in APPS)
    return f'''<div class="side-box">
                        <h3>Anwendungen</h3>
                        <ul class="link-list">
{lis}
                        </ul>
                    </div>'''

LOCAL_BUSINESS = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Wilcowa AG Baumaschinen",
    "url": BASE + "/",
    "logo": BASE + "/assets/wilcowa-logo.png",
    "image": BASE + "/assets/Untermorteln_Stahltragerplatte.avif",
    "telephone": "+41433887060",
    "email": MAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "Riedthofstrasse 172", "addressLocality": "Regensdorf", "postalCode": "8105", "addressRegion": "ZH", "addressCountry": "CH"},
    "areaServed": "CH",
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"], "opens": "07:00", "closes": "17:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "07:00", "closes": "16:00"},
    ],
    "description": "Exklusivvertrieb, Vermietung und Service der WPS-Mörtelpumpe in der Schweiz.",
}

FAQ = [
    ("Welche Materialien kann ich mit der WPS-Mörtelpumpe verarbeiten?", "Alle pumpfähigen, werksgemischten Trockenmörtel mit einer Korngrösse bis 4 mm. Die Mischung sollte plastisch bis leicht fliessfähig eingestellt sein. Zementsuspensionen und reine Kalkmörtel sind ebenfalls möglich."),
    ("Kann ich die Pumpe mieten?", "Ja. Sie können die WPS-Mörtelpumpe zu einer Tagespauschale mieten – ideal, um sie auf Ihrer Baustelle und mit Ihrem Material zu testen. Fragen Sie die Verfügbarkeit telefonisch oder über das Kontaktformular an."),
    ("Benötige ich einen Kompressor?", "Nein. Die WPS-Pumpe arbeitet rein elektrisch (230 V) mit einer Förderschnecke. Das macht sie leise und überall einsetzbar, auch in bewohnten Räumen."),
    ("Wie hoch ist der Arbeitsdruck?", "Je nach Materialkonsistenz ca. 1 bis 2.5 bar. Das reicht, um Hohlräume vollständig zu füllen, ohne das Mauerwerk durch zu hohen Druck zu beschädigen – wichtig in der Denkmalpflege."),
    ("Wie reinige ich die Pumpe?", "Nur Schlauch und Pumpenkopf kommen mit Material in Berührung. Den Schlauch spülen Sie mit Wasser durch, den Trichter wischen Sie feucht aus."),
    ("Kann eine Person die Pumpe allein bedienen?", "Ja. Dank kompakter Bauweise und Fernbedienung an der Lanze ist echte Einmannbedienung möglich."),
    ("Gibt es Ersatzteile und Zubehör?", "Ja. Als Schweizer Vertriebspartner halten wir Verschleissteile wie Schläuche, Düsen und Dichtungen in Regensdorf an Lager. Der Versand erfolgt in der Regel innert 24 Stunden."),
    ("Ist eine Schulung notwendig?", "Das Gerät ist einfach zu bedienen. Eine kurze Einweisung bei der Übergabe genügt in der Regel. Bei anspruchsvollen Projekten beraten wir Sie gerne vorab."),
]

# ---------------------------------------------------------------- Startseite
def page_index():
    tiles = "\n".join(f'''                <a class="tile" href="{s}.html">
                    <div class="tile-media"><img src="assets/{img}.avif" alt="{t} mit der WPS-Mörtelpumpe" loading="lazy" width="900" height="675"></div>
                    <div class="tile-body">
                        <span class="tile-index">{i+1:02d}</span>
                        <h3>{t}</h3>
                        <p>{txt}</p>
                    </div>
                </a>''' for i, (s, n, t, txt, img) in enumerate(APPS))
    return f'''
    <main>
    <section class="hero">
        <div class="container">
            <div>
                <p class="eyebrow">WPS-Mörtelpumpe · Miete und Verkauf in der Schweiz</p>
                <h1>Die dosierbare Mörtelpumpe für <span>Fugen, Zargen und Hohlräume</span></h1>
                <p class="lead">Mit der WPS-Mörtelpumpe bringen Sie Mörtel stufenlos dosiert genau dorthin, wo er hingehört – hohlraumfrei, ohne Verschmutzung der Oberflächen und von einer Person bedienbar.</p>
                <div class="hero-actions">
                    <a class="btn btn-primary" href="kontakt.html?type=miete">Miete oder Kauf anfragen {icon("arrow")}</a>
                    <a class="btn btn-outline" href="produkte.html">Technische Daten</a>
                </div>
                <p class="hero-note">{icon("check")}Ersatzteile und Zubehör ab Lager Regensdorf</p>
            </div>
            <figure class="hero-figure">
                <img src="assets/Untermorteln_Stahltragerplatte.avif" alt="Untermörteln einer Stahlträgerplatte mit der WPS-Mörtelpumpe" width="914" height="682" fetchpriority="high">
                <figcaption>Untermörteln einer Stahlträgerplatte</figcaption>
            </figure>
        </div>
    </section>

    <section class="specs-band">
        <div class="container">
            <div class="specs">
                <div class="specs-item"><span class="specs-value">0.5–12<small>l/min</small></span><span class="specs-label">Fördermenge, stufenlos dosierbar</span></div>
                <div class="specs-item"><span class="specs-value">0–4<small>mm</small></span><span class="specs-label">Korngrösse des Mörtels</span></div>
                <div class="specs-item"><span class="specs-value">230<small>V</small></span><span class="specs-label">Elektrisch, ohne Kompressor</span></div>
                <div class="specs-item"><span class="specs-value">1<small>Person</small></span><span class="specs-label">Bedienung mit Fernsteuerung an der Lanze</span></div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-head-row">
                <div class="section-head">
                    <p class="eyebrow">Anwendungen</p>
                    <h2>Eine Pumpe für viele Aufgaben auf der Baustelle</h2>
                    <p class="lead">Vom Hinterfüllen einer Stahlzarge bis zur Fugensanierung im Denkmalschutz – mit den passenden Düsen deckt die WPS ein breites Spektrum ab.</p>
                </div>
                <a class="link-arrow" href="anwendungen.html">Alle Anwendungen {icon("arrow")}</a>
            </div>
            <div class="tiles">
{tiles}
                <a class="tile tile-cta" href="moertel-bedarf-rechner.html">
                    <div>
                        <span class="tile-index">Werkzeug</span>
                        <h3>Mörtelbedarf berechnen</h3>
                        <p>Volumen und Trockenmaterial für Fugen und Hohlräume in Sekunden ermitteln.</p>
                    </div>
                    <span class="link-arrow">Zum Rechner {icon("arrow")}</span>
                </a>
            </div>
        </div>
    </section>

    <section class="section bg-alt">
        <div class="container split">
            <div>
                <p class="eyebrow">Warum WPS</p>
                <h2>Präzise statt von Hand – und deutlich schneller</h2>
                <p class="lead">Mangelhaft verfüllte Zargen oder verschmutzte Natursteinflächen kosten Zeit und Nacharbeit. Die WPS-Mörtelpumpe fördert den Mörtel gleichmässig und kontrolliert – von Zürich über Bern bis Basel und St. Gallen im Einsatz.</p>
                <p style="margin-top:20px">Ob Zementleim, Kalkmörtel, Brandschutz- oder Fugenmörtel: Die Schneckenpumpe verarbeitet unterschiedlichste Materialien zuverlässig.</p>
                <a class="link-arrow" href="produkte.html" style="margin-top:28px">Produkt und technische Daten {icon("arrow")}</a>
            </div>
            <div class="points">
                <div class="point"><span class="point-no">01</span><div><h3>Hohlraumfrei</h3><p>Der Mörtel wird von unten nach oben eingebracht – ohne Lufteinschlüsse, für kraftschlüssige und brandschutzgerechte Verbindungen.</p></div></div>
                <div class="point"><span class="point-no">02</span><div><h3>Sauber</h3><p>Punktgenaue Dosierung statt Kellenwurf: keine Leibungsschäden, kein Zementschleier auf Stein und Klinker.</p></div></div>
                <div class="point"><span class="point-no">03</span><div><h3>Schnell</h3><p>Kontinuierliche Förderung statt Eimer und Spritztüte – spürbar weniger Arbeitszeit pro Laufmeter.</p></div></div>
                <div class="point"><span class="point-no">04</span><div><h3>Handlich</h3><p>230-V-Anschluss genügt. Kein Kompressor, leiser Betrieb, auch in bewohnten Räumen einsetzbar.</p></div></div>
            </div>
        </div>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-head">
                <p class="eyebrow">Miete oder Kauf</p>
                <h2>So kommen Sie zur WPS-Mörtelpumpe</h2>
            </div>
            <div class="offers">
                <div class="offer">
                    <h3>Mieten</h3>
                    <p>Für einzelne Projekte oder um die Pumpe mit Ihrem Material zu testen.</p>
                    <ul class="check-list">
                        <li>Faire Tagespauschale</li>
                        <li>Einweisung bei der Übergabe</li>
                        <li>Passende Düsen und Zubehör inklusive Beratung</li>
                    </ul>
                    <a class="btn btn-primary" href="kontakt.html?type=miete">Mietanfrage senden</a>
                </div>
                <div class="offer">
                    <h3>Kaufen</h3>
                    <p>Für Betriebe, die regelmässig verfugen, hinterfüllen oder untermörteln.</p>
                    <ul class="check-list">
                        <li>Beratung zur Ausstattung für Ihre Anwendungen</li>
                        <li>Ersatz- und Verschleissteile ab Lager Regensdorf</li>
                        <li>Service und Unterstützung durch den Schweizer Vertrieb</li>
                    </ul>
                    <a class="btn btn-outline" href="kontakt.html?type=kauf">Offerte anfordern</a>
                </div>
            </div>
        </div>
    </section>

    <section class="section-tight bg-alt">
        <div class="container">
            <div class="section-head">
                <p class="eyebrow">Downloads</p>
                <h2>Unterlagen zur WPS-Mörtelpumpe</h2>
            </div>
            <div class="downloads">
                {download("untermoerteln")}
                {download("fugen")}
                {download("tiefbau")}
            </div>
        </div>
    </section>
{contact_band()}
    </main>
'''

# ---------------------------------------------------------------- Produkt
def page_produkt():
    crumbs = [("Start", "index.html"), ("Produkt &amp; Daten", "produkte.html")]
    return page_head(crumbs, "Produkt", "WPS-Mörtelpumpe: Technik und Daten",
                     "Eine kompakte, elektrisch angetriebene Schneckenpumpe, die thixotrope und fliessfähige Mörtel stufenlos dosiert in Fugen und schwer zugängliche Hohlräume fördert.") + f'''
    <main class="section">
        <div class="container layout">
            <article class="prose">
                <figure class="feature-figure">
                    <img src="assets/Untermorteln_Holzbau.avif" alt="WPS-Mörtelpumpe mit Trichter und Fahrgestell" width="790" height="906" style="object-fit:contain;background:#f3f4f6">
                </figure>

                <h2>Funktionsprinzip</h2>
                <p>Die WPS-Mörtelpumpe wurde gezielt dafür entwickelt, Mörtel präzise in enge Spalten und Hohlräume einzubringen. Das geschlossene System verhindert Lufteinschlüsse und sorgt für eine vollflächige, statisch einwandfreie Verbindung. Die Fördermenge lässt sich stufenlos regeln – von der feinen Fuge bis zum grösseren Hohlraum.</p>

                <h2 id="technische-daten">Technische Daten</h2>
                <div class="table-wrap">
                    <table class="spec-table">
                        <tbody>
                            <tr><th scope="row">Antrieb</th><td>Elektrisch, 230 V</td></tr>
                            <tr><th scope="row">Fördermenge</th><td>ca. 0.5–12 l/min, stufenlos dosierbar</td></tr>
                            <tr><th scope="row">Arbeitsdruck</th><td>ca. 1–2.5 bar (materialabhängig)</td></tr>
                            <tr><th scope="row">Korngrösse</th><td>0–4 mm</td></tr>
                            <tr><th scope="row">Behälter</th><td>12-Liter-Trichter</td></tr>
                            <tr><th scope="row">Gewicht</th><td>8.5 kg (leer)</td></tr>
                            <tr><th scope="row">Bedienung</th><td>Einmannbedienung, Fernsteuerung an der Lanze</td></tr>
                        </tbody>
                    </table>
                </div>
                <p class="table-note">Angaben gerundet. Verbindliche Werte entnehmen Sie dem Datenblatt oder erfragen Sie bei uns.</p>

                <h2>Geeignete Materialien</h2>
                <ul class="check-list">
                    <li><strong>Injektionsmörtel</strong> für kraftschlüssige Verbindungen</li>
                    <li><strong>Zementleim und Zementsuspensionen</strong> für Hohlraumfüllung und Rissverpressung</li>
                    <li><strong>Kalkmörtel</strong>, besonders schonend in der Denkmalpflege</li>
                    <li><strong>Brandschutzmörtel</strong> bei Zargen und Durchführungen</li>
                    <li><strong>Epoxidharzmörtel</strong> für hochfeste Anwendungen (nach Rücksprache)</li>
                </ul>

                <h2 id="systemvergleich">Systemvergleich</h2>
                <p>Die WPS-Technik im Vergleich zu Handverfugung und Spritzverfahren.</p>
                <div class="table-wrap">
                    <table class="compare-table">
                        <thead>
                            <tr><th scope="col">Kriterium</th><th scope="col" class="is-wps">WPS-Mörtelpumpe</th><th scope="col">Handverfugung</th><th scope="col">Spritzverfahren</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>Arbeitsgeschwindigkeit</td><td class="is-wps">Hoch, kontinuierlich</td><td>Niedrig</td><td>Sehr hoch</td></tr>
                            <tr><td>Materialverlust</td><td class="is-wps">Minimal, punktgenau</td><td>Mittel</td><td>Hoch (Rückprall)</td></tr>
                            <tr><td>Sauberkeit</td><td class="is-wps">Sehr sauber</td><td>Verschmutzung</td><td>Sprühnebel</td></tr>
                            <tr><td>Hohlraumfüllung</td><td class="is-wps">Vollständig</td><td>Lufteinschlüsse möglich</td><td>Gut</td></tr>
                            <tr><td>Geräteaufwand</td><td class="is-wps">Gering, 230 V</td><td>Minimal</td><td>Gross (Kompressor)</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="notice">
                    <h3>Materialbedarf planen</h3>
                    <p>Mit dem <a href="moertel-bedarf-rechner.html">Mörtelrechner</a> ermitteln Sie Volumen und Trockenmaterial für Ihre Fugen und Hohlräume. Antworten auf technische Fragen finden Sie in den <a href="faq.html">häufigen Fragen</a>.</p>
                </div>
            </article>

            <aside class="sidebar">
                <div class="side-box">
                    <h3>Downloads</h3>
                    <div class="download-list">
                        {download("untermoerteln")}
                        {download("fugen")}
                        {download("tiefbau")}
                    </div>
                </div>
                {contact_box()}
            </aside>
        </div>
    </main>
'''

# ---------------------------------------------------------------- Anwendungen (Übersicht)
ROWS = [
    ("anwendung-stahlzargen", "Ausmorteln_Stahltrager", "Montage von Stahlzargen",
     "<p>Stahlzargen werden oft nachträglich eingebaut. Da der Spalt zur Leibung meist nur <strong>1–2 cm</strong> beträgt, ist das Einbringen von Mörtel von Hand mühsam – und bei klassischer Verschalung drohen Schäden am fertigen Putz.</p>",
     "Der Zargenhohlraum wird mit der Breitschlitzdüse sauber von unten nach oben ausgemörtelt. Eine Verschalung entfällt."),
    ("anwendung-untermoerteln", "Beton_Stahl_Konstruktion", "Untermörteln von Schwellen",
     "<p>Im <strong>Holzrahmenbau</strong> und bei <strong>Betonelementen</strong> müssen Setzschwellen vollflächig unterfüttert werden, damit Lasten sauber abgetragen werden.</p>",
     "Breitschlitzdüsen bis 100 mm Breite bringen den Mörtel schnell und satt unter die Schwelle – ohne Hohlräume."),
    ("anwendung-naturstein", "Ausfugen_Sandsteingewolbe", "Denkmalpflege und Naturstein",
     "<p>Historische Bausubstanz verlangt Fingerspitzengefühl. Zementflecken auf Sandstein lassen sich oft nicht mehr entfernen.</p>",
     "Die Dosierung ist so fein, dass kein Material auf die Sichtfläche gelangt – ideal auch für Reprofilierungsmörtel."),
    ("anwendung-maueranker", "Mauer-Anker_verpressen", "Maueranker verpressen",
     "<p>Für die statische Sicherung von Mauerwerk müssen Anker lunkerfrei verfüllt werden – oft in tiefen Bohrlöchern.</p>",
     "Mit der Lanze wird das Bohrloch von hinten nach vorne vollständig gefüllt."),
    ("anwendung-daemmplatten", "Daemmplatten_Kleber", "Dämmplatten kleben",
     "<p>Ob Innendämmung oder Fassade: Kleber von Hand aufzuziehen ist kräftezehrend.</p>",
     "Kleberaupen werden maschinell und dosiert direkt auf Platte oder Wand aufgetragen."),
    ("anwendung-spannbeton", "Ausgiessen_Spannbetonplatten", "Spannbeton und Fertigteile",
     "<p>Fugen zwischen Spannbeton-Hohldecken müssen für die Scheibenwirkung vollvolumig vergossen werden.</p>",
     "Ergonomischer Verguss im Stehen – auf grossen Flächen eine erhebliche Zeitersparnis."),
    ("anwendung-fugen", "Klinker-Verblender_gefugt", "Fugen und Sanierung",
     "<p>Das Neuverfugen von Klinkerfassaden, Natursteinwänden und Randsteinen ist klassische Handarbeit – und entsprechend aufwendig.</p>",
     "Der Fugenmörtel wird tief und gleichmässig eingebracht, ohne die Steinoberfläche zu verschlämmen."),
]

GALLERY = [
    ("Ausmorteln_Stahltrager", "Stahlträger", "Lückenlose Füllung komplexer Profile"),
    ("Ausgiessen_Spannbetonplatten", "Spannbetonplatten", "Fugenverguss ohne Hohlräume"),
    ("Fugen_Randsteine", "Randsteine", "Verfugen im Strassen- und Tiefbau"),
    ("Mauer-Anker_verpressen", "Maueranker", "Tiefeninjektion zur Sicherung"),
    ("Klinker-Verblender_gefugt", "Klinkerfassade", "Fugenbild ohne Zementschleier"),
    ("Untermorteln_Stahltragerplatte", "Stahlträgerplatte", "Kraftschlüssige Unterfütterung"),
    ("Fugen_Deckenelemente", "Deckenelemente", "Verfugen von Betonfertigteilen"),
    ("Daemmplatten_Kleber", "Dämmplatten", "Kleberauftrag mit Breitschlitzdüse"),
    ("Stahlschalung_Saeule", "Stahlsäule", "Hohlräume in Stahlprofilen füllen"),
    ("Natursteinwand_Fugen", "Natursteinwand", "Fugen in unregelmässigem Mauerwerk"),
    ("Ausfugen_Sandsteingewolbe", "Sandsteingewölbe", "Ausfugen in der Denkmalpflege"),
    ("Beton_Stahl_Konstruktion", "Beton-Stahl-Konstruktion", "Ausmörteln von Anschlüssen"),
]

def page_anwendungen():
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html")]
    rows = "\n".join(f'''                <div class="app-row">
                    <img src="assets/{img}.avif" alt="{t} mit der WPS-Mörtelpumpe" loading="lazy">
                    <div>
                        <span class="tile-index">{i+1:02d} / {len(ROWS)+1:02d}</span>
                        <h2>{t}</h2>
                        {problem}
                        <p class="solution"><strong>Mit der WPS:</strong> {sol}</p>
                        <a class="link-arrow" href="{s}.html">Mehr erfahren {icon("arrow")}</a>
                    </div>
                </div>''' for i, (s, img, t, problem, sol) in enumerate(ROWS))
    tief = f'''                <div class="app-row">
                    <img src="assets/Fugen_Randsteine.avif" alt="Randsteine verfugen mit der WPS-Mörtelpumpe" loading="lazy">
                    <div>
                        <span class="tile-index">{len(ROWS)+1:02d} / {len(ROWS)+1:02d}</span>
                        <h2>Strassen-, Hoch- und Tiefbau</h2>
                        <p>Vom Verfugen von Randsteinen bis zum Untergiessen von Schachtringen – im Tiefbau zählen Robustheit und Tempo.</p>
                        <ul class="check-list" style="margin-top:16px">
                            <li><strong>Betonfertigteile:</strong> dauerhafte Fugenverbindungen</li>
                            <li><strong>Schachtsanierung:</strong> nachträgliches Verfüllen von Fugen</li>
                            <li><strong>Pflasterfugen:</strong> auch bei grossen Formaten und hoher Verkehrslast</li>
                        </ul>
                        <a class="btn btn-outline" href="assets/Flyer_Strassen-Hoch-Tiefbau.pdf" target="_blank" rel="noopener">{icon("file")}Flyer Tiefbau (PDF)</a>
                    </div>
                </div>'''
    gal = "\n".join(f'''                <figure><img src="assets/{img}.avif" alt="{t}: {c}" loading="lazy"><figcaption><strong>{t}</strong>{c}</figcaption></figure>''' for img, t, c in GALLERY)
    return page_head(crumbs, "Anwendungen", "Einsatzgebiete der WPS-Mörtelpumpe",
                     "Hinterfüllen, untermörteln, verpressen, verfugen: Mit dem passenden Düsensystem löst die WPS-Mörtelpumpe Aufgaben, die von Hand viel Zeit kosten.") + f'''
    <main>
        <section class="section">
            <div class="container app-rows">
{rows}
{tief}
            </div>
        </section>

        <section class="section bg-alt">
            <div class="container">
                <div class="section-head">
                    <p class="eyebrow">Bildergalerie</p>
                    <h2>Aus der Praxis</h2>
                </div>
                <div class="gallery">
{gal}
                </div>
            </div>
        </section>
{contact_band()}
    </main>
'''

# ---------------------------------------------------------------- Detailseiten
DETAILS = {
    "anwendung-stahlzargen": dict(
        title="Stahlzargen einmörteln mit der Mörtelpumpe | WPS – Wilcowa",
        desc="Stahlzargen hohlraumfrei und brandschutzgerecht hinterfüllen: Mit der WPS-Mörtelpumpe und Breitschlitzdüse sauber, ohne Leibungsschäden und bis zu 4x schneller.",
        h1="Stahlzargen einmörteln und hinterfüllen",
        lead="Sauber, schnell und brandschutzgerecht – auch bei Spalten von nur 1–2 cm zur Leibung.",
        img=("Ausmorteln_Stahltrager", "Ausmörteln mit der WPS-Mörtelpumpe", 874, 1166),
        body="""<h2>Hohlraumfrei statt Kellenwurf</h2>
                <p>Umfassungszargen aus Stahl müssen hohlraumfrei in der Leibung eingemörtelt werden, damit Stabilität und Brandschutzanforderungen (z.&nbsp;B. T30, T90) erfüllt sind. Da der Spalt zur Leibung oft nur 1–2 cm beträgt, wird die Leibung beim Kellenwurf mit Einwurföffnungen häufig beschädigt oder verschmutzt.</p>
                <p>Mit der dosierbaren <strong>WPS-Mörtelpumpe</strong> und der <strong>Breitschlitzdüse</strong> hinterfüllen Sie Stahlzargen ohne Leibungsverletzungen – praktisch unsichtbar. Das spart Reinigungsaufwand und sorgt für eine vollflächige Verbindung zwischen Zarge und Wand.</p>
                <h2>Ihre Vorteile</h2>
                <ul class="check-list">
                    <li>Sauberes Hinterfüllen auch bei engen Spalten von 1–2 cm</li>
                    <li>Keine Beschädigung von Leibung, Putz und Tapeten</li>
                    <li>Exakte Dosierung des Zargenmörtels</li>
                    <li>Bis zu 4x schneller als im Handverfahren</li>
                    <li>Hohlraumfreie Verfüllung für den Brandschutz</li>
                </ul>""",
        pdf="tiefbau"),
    "anwendung-untermoerteln": dict(
        title="Untermörteln von Schwellen und Elementen | WPS-Mörtelpumpe",
        desc="Setzschwellen im Holzbau, Stahlplatten und Betonelemente vollflächig untermörteln: Die WPS-Mörtelpumpe mit Breitschlitzdüse fördert Quell- und Vergussmörtel sauber und hohlraumfrei.",
        h1="Untermörteln von Schwellen und Elementen",
        lead="Vollflächige Unterfütterung im Holz-, Beton- und Stahlbau – für eine stabile Lastabtragung.",
        img=("Untermorteln_Stahltragerplatte", "Untermörteln einer Stahlträgerplatte mit der WPS-Mörtelpumpe", 914, 682),
        body="""<h2>Lasten sauber abtragen</h2>
                <p>Im Holzrahmenbau müssen Setzschwellen und Holzwände, im Betonbau Fertigteile vollflächig mit Mörtel – etwa Quell- oder Vergussmörtel – unterfüttert werden. Nur so sind eine stabile Lastabtragung und eine dichte Fuge gewährleistet.</p>
                <p>Die konstante Förderung der <strong>WPS-Mörtelpumpe</strong> verhindert Hohlräume unter den Schwellen. Mit den beiden <strong>Breitschlitzdüsen</strong> bringen Sie Montagemörtel unter Stahlplatten oder Holzschwellen effizient und sauber ein.</p>
                <h2>Einsatzbereiche</h2>
                <ul class="check-list">
                    <li>Holzrahmenbau: Setzschwellen luftdicht untermörteln</li>
                    <li>Montage und Fugenverguss von Betonfertigteilen</li>
                    <li>Unterfüllen von Stahlträgerplatten und Maschinenfüssen</li>
                    <li>Verarbeitung von Verguss- und Quellmörteln</li>
                </ul>
                <figure><img src="assets/Beton_Stahl_Konstruktion.avif" alt="Ausmörteln an einer Beton-Stahl-Konstruktion" loading="lazy" width="666" height="890"><figcaption>Ausmörteln an einer Beton-Stahl-Konstruktion</figcaption></figure>""",
        pdf="untermoerteln"),
    "anwendung-naturstein": dict(
        title="Natursteinmauern verfugen und sanieren | WPS-Mörtelpumpe",
        desc="Natursteinmauern und historische Bauten schonend verfugen: Die WPS-Mörtelpumpe bringt Fugenmörtel präzise in tiefe, unregelmässige Fugen – ohne Verschmutzung des Steins.",
        h1="Natursteinmauern verfugen",
        lead="Werterhalt in der Denkmalpflege: präzise Fugen ohne Mörtelflecken auf dem Stein.",
        img=("Natursteinwand_Fugen", "Natursteinwand verfugen mit der WPS-Mörtelpumpe", 896, 992),
        body="""<h2>Ästhetische und dauerhafte Fugen</h2>
                <p>Natursteinmauern stellen hohe Anforderungen an die Verfugung. Unregelmässige Fugenbreiten und -tiefen machen das Verfugen von Hand mühsam, und die Steinoberfläche wird schnell mit Mörtel verschmutzt.</p>
                <p>Die WPS-Mörtelpumpe bringt Fugenmörtel sauber auch in tiefe und unregelmässige Fugen ein. Verschiedene Düsenaufsätze passen den Mörtelstrang an die Fugenbreite an. Das spart Zeit beim Einbringen und reduziert den Reinigungsaufwand deutlich.</p>
                <h2>Typische Objekte</h2>
                <ul class="check-list">
                    <li>Bruchstein- und Trockenmauern</li>
                    <li>Sandsteingewölbe und historische Fassaden</li>
                    <li>Stützmauern im Garten- und Landschaftsbau</li>
                </ul>
                <figure><img src="assets/Ausfugen_Sandsteingewolbe.avif" alt="Ausfugen eines Sandsteingewölbes" loading="lazy" width="912" height="1216"><figcaption>Ausfugen eines Sandsteingewölbes</figcaption></figure>""",
        pdf="fugen"),
    "anwendung-maueranker": dict(
        title="Maueranker verpressen | WPS-Mörtelpumpe",
        desc="Maueranker und Injektionsanker lunkerfrei verpressen: Mit Lanze und regelbarer Förderung füllt die WPS-Mörtelpumpe Bohrlöcher vollständig – für maximale Tragkraft.",
        h1="Maueranker verpressen",
        lead="Lunkerfreie Verfüllung von Bohrlöchern für die statische Sicherung von Mauerwerk.",
        img=("Mauer-Anker_verpressen", "Maueranker verpressen mit der WPS-Mörtelpumpe", 888, 660),
        body="""<h2>Volle Kraftübertragung</h2>
                <p>Für die statische Sicherung oder Verstärkung von Mauerwerk werden Injektionsanker in bestehendes Mauerwerk gesetzt und mit Verpressmörtel fixiert. Entscheidend ist, dass der Mörtel das Bohrloch vollständig ausfüllt.</p>
                <p>Mit der <strong>WPS-Mörtelpumpe</strong> injizieren Sie den Mörtel sauber und kontrolliert tief ins Bohrloch. Dank regelbarer Fördergeschwindigkeit wird der Hohlraum um den Anker blasenfrei verfüllt. Auch für allgemeine Hohlraumverfüllungen ist das System geeignet.</p>
                <h2>Ihre Vorteile</h2>
                <ul class="check-list">
                    <li>Tiefes Injizieren mit Lanze oder Schlauch</li>
                    <li>Lunkerfreie Verfüllung für maximale Tragkraft</li>
                    <li>Kein Materialverlust, sauberes Arbeiten</li>
                    <li>Für mineralische Mörtel und Suspensionen</li>
                </ul>""",
        pdf="tiefbau"),
    "anwendung-daemmplatten": dict(
        title="Dämmplatten kleben mit der Mörtelpumpe | WPS – Wilcowa",
        desc="Kleber und Brandschutzmörtel rationell auf Dämm- und Brandschutzplatten auftragen: Die WPS-Mörtelpumpe trägt Kleberaupen dosiert auf – schneller als mit dem Zahnspachtel.",
        h1="Dämmplatten kleben",
        lead="Kleberaupen maschinell und dosiert auftragen – für Innendämmung, Fassade und Brandschutz.",
        img=("Daemmplatten_Kleber", "Kleberauftrag auf Dämmplatten mit der WPS-Mörtelpumpe", 900, 674),
        body="""<h2>Schneller als mit dem Zahnspachtel</h2>
                <p>Bei Innen- oder Fassadendämmung ist der Kleberauftrag ein wichtiger Kostenfaktor. Von Hand mit dem Zahnspachtel ist er zeitaufwendig und körperlich anstrengend.</p>
                <p>Mit der WPS-Mörtelpumpe tragen Sie Kleberaupen direkt auf die Platte oder den Untergrund auf. Durch die Dosierung kommt genau die richtige Menge Material an – ohne Verschwendung.</p>
                <h2>Anwendungsbereiche</h2>
                <ul class="check-list">
                    <li>Innendämmung von Kellerdecken und Wänden</li>
                    <li>Fassadendämmplatten</li>
                    <li>Brandschutzplatten</li>
                </ul>""",
        pdf="tiefbau"),
    "anwendung-spannbeton": dict(
        title="Spannbetonfugen vergiessen | WPS-Mörtelpumpe",
        desc="Fugen zwischen Spannbeton-Hohldecken vollvolumig vergiessen: Mit der WPS-Mörtelpumpe ergonomisch im Stehen, schnell und ohne Lufteinschlüsse.",
        h1="Spannbetonfugen vergiessen",
        lead="Fugenverguss bei Fertigteildecken – ergonomisch, schnell und vollvolumig.",
        img=("Ausgiessen_Spannbetonplatten", "Vergiessen von Spannbetonfugen mit der WPS-Mörtelpumpe", 884, 660),
        body="""<h2>Fugenverguss bei Fertigteildecken</h2>
                <p>Bei Spannbeton-Hohldecken müssen die Fugen zwischen den Elementen sorgfältig und vollvolumig vergossen werden, damit Scheibenwirkung und Brandschutz der Decke gewährleistet sind.</p>
                <p>Die WPS-Mörtelpumpe beschleunigt diesen Arbeitsschritt gegenüber dem Vergiessen von Hand erheblich: Das Material wird direkt aus dem Trichter in die Fuge gepumpt – ohne Eimerschleppen und Bücken.</p>
                <h2>Vorteile der maschinellen Verarbeitung</h2>
                <ul class="check-list">
                    <li>Ergonomisches Arbeiten in aufrechter Haltung</li>
                    <li>Hohe Verlegeleistung pro Stunde</li>
                    <li>Saubere Baustelle durch gezieltes Einbringen</li>
                </ul>
                <figure><img src="assets/Fugen_Deckenelemente.avif" alt="Verfugen von Deckenelementen" loading="lazy" width="874" height="1166"><figcaption>Verfugen von Deckenelementen</figcaption></figure>""",
        pdf="tiefbau"),
    "anwendung-fugen": dict(
        title="Fugen und Fugensanierung mit der Mörtelpumpe | WPS – Wilcowa",
        desc="Klinker, Natursteinwände und Randsteine maschinell verfugen: Die WPS-Mörtelpumpe bringt Fugenmörtel wie Trasskalk oder Zementmörtel tief ein – ohne Verschlämmung der Oberfläche.",
        h1="Fugen und Fugensanierung",
        lead="Klinker, Naturstein und Randsteine maschinell und sauber neu verfugen.",
        img=("Klinker-Verblender_gefugt", "Gefugte Klinker-Verblender", 912, 784),
        body="""<h2>Fugensanierung ohne Verschlämmung</h2>
                <p>Das Neuverfugen von Natursteinwänden, Randsteinen und Klinkerfassaden ist aufwendige Handarbeit. Mit der WPS-Mörtelpumpe wird die Fugensanierung schneller und gleichmässiger.</p>
                <p>Durch die präzise Dosierung bringen Sie den Fugenmörtel – etwa Trasskalk- oder Zementmörtel – tief in die Fuge ein, ohne die Steinoberfläche zu verschlämmen. Das ist bei historischen Bauten und Sichtmauerwerk besonders wichtig.</p>
                <h2>Anwendungsbeispiele</h2>
                <ul class="check-list">
                    <li>Natursteinmauern effizient verfugen</li>
                    <li>Randsteine und Pflasterfugen im Strassenbau</li>
                    <li>Sanierung und Neuverfugung von Klinkerfassaden</li>
                    <li>Schonende Bearbeitung von Denkmalschutzobjekten</li>
                </ul>
                <div class="figure-pair">
                    <img src="assets/Natursteinwand_Fugen.avif" alt="Natursteinwand verfugen" loading="lazy">
                    <img src="assets/Fugen_Randsteine.avif" alt="Randsteine maschinell verfugen" loading="lazy">
                </div>""",
        pdf="fugen"),
}

def page_detail(slug):
    d = DETAILS[slug]
    name = next(t for s, n, t, *_ in APPS if s == slug)
    crumbs = [("Start", "index.html"), ("Anwendungen", "anwendungen.html"), (name, f"{slug}.html")]
    img, alt, w, hgt = d["img"]
    body = d["body"].replace("<ul class=\"check-list\">", "<ul class=\"check-list\">")
    return page_head(crumbs, "Anwendung", d["h1"], d["lead"]) + f'''
    <main class="section">
        <div class="container layout">
            <article class="prose">
                <figure class="feature-figure"><img src="assets/{img}.avif" alt="{alt}" width="{w}" height="{hgt}"></figure>
                {body}
            </article>
            <aside class="sidebar">
                <div class="side-box">
                    <h3>Download</h3>
                    {download(d["pdf"])}
                </div>
                {contact_box()}
                {app_links(slug)}
            </aside>
        </div>
    </main>
'''

# ---------------------------------------------------------------- Rechner
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
    return page_head(crumbs, "Werkzeug", "Mörtel-Bedarfsrechner für Fugen und Hohlräume",
                     "Berechnen Sie Volumen und Trockenmaterial für Fugen, Zargen und Hohlräume – für die Baustellenplanung und Materialbestellung.") + f'''
    <main class="section">
        <div class="container split">
            <div class="calc">
                <div class="calc-body">
                        {calc_row("length", "Fugenlänge", "m", 10, 100, 0.5)}
                        {calc_row("width", "Fugenbreite", "mm", 15, 100, 1)}
                        {calc_row("depth", "Fugentiefe", "mm", 50, 200, 1)}
                    <div class="calc-selects">
                        <div class="field">
                            <label for="calc-density">Materialdichte</label>
                            <select id="calc-density" onchange="calculateMortar()">
                                <option value="1.8" selected>Standardmörtel (1.8 kg/l)</option>
                                <option value="1.2">Leichtmörtel (1.2 kg/l)</option>
                                <option value="2.0">Beton (2.0 kg/l)</option>
                                <option value="2.2">Schwerbeton (2.2 kg/l)</option>
                            </select>
                        </div>
                        <div class="field">
                            <label for="calc-wastage">Zuschlag für Verschnitt</label>
                            <select id="calc-wastage" onchange="calculateMortar()">
                                <option value="0">0 %</option>
                                <option value="5">5 %</option>
                                <option value="10" selected>10 % (Standard)</option>
                                <option value="20">20 %</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="calc-result" aria-live="polite">
                    <div><span>Benötigtes Volumen</span><output id="result-liters">0.0</output><small style="color:#9fb1c9">Liter</small></div>
                    <div><span>Trockenmaterial ca.</span><output id="result-kg">0.0</output><small style="color:#9fb1c9">kg</small></div>
                </div>
                <p class="calc-foot">Inklusive gewähltem Zuschlag. Richtwert – massgebend sind die Angaben des Mörtelherstellers.</p>
            </div>

            <div class="prose">
                <h2>Wofür der Rechner gedacht ist</h2>
                <p>Ob Sie <strong>Stahlzargen hinterfüllen</strong>, <strong>Mauerwerk verfugen</strong> oder <strong>Spannbetonfugen vergiessen</strong>: Eine genaue Materialplanung spart Kosten und verhindert Unterbrüche auf der Baustelle.</p>
                <p>Der Rechner ermittelt aus Länge, Breite und Tiefe das Hohlraumvolumen und schätzt den Bedarf an Trockenmörtel. Er funktioniert für jede Verarbeitungsmethode – von Hand, mit der Spritztüte oder mit der Mörtelpumpe.</p>
                <h3>So gehen Sie vor</h3>
                <ul class="check-list">
                    <li>Länge, Breite und Tiefe der Fuge eingeben</li>
                    <li>Materialdichte wählen (Standard ca. 1.8 kg/l)</li>
                    <li>Zuschlag für Verschnitt festlegen</li>
                    <li>Ergebnis ablesen und für die Bestellung verwenden</li>
                </ul>
                <div class="notice">
                    <h3>Grössere Mengen zu verarbeiten?</h3>
                    <p>Mit der <a href="produkte.html">WPS-Mörtelpumpe</a> bringen Sie den Mörtel dosiert und ohne Materialverlust ein. Gerne beraten wir Sie zu Miete oder Kauf.</p>
                </div>
            </div>
        </div>
    </main>
{contact_band()}
'''

# ---------------------------------------------------------------- FAQ
def page_faq():
    crumbs = [("Start", "index.html"), ("Häufige Fragen", "faq.html")]
    items = "\n".join(f'''                <details>
                    <summary>{q}{icon("plus")}</summary>
                    <div class="answer"><p>{a}</p></div>
                </details>''' for q, a in FAQ)
    return page_head(crumbs, "FAQ", "Häufige Fragen zur WPS-Mörtelpumpe",
                     "Antworten zu Material, Bedienung, Reinigung, Miete und Ersatzteilen.") + f'''
    <main class="section">
        <div class="container layout">
            <div class="faq">
{items}
            </div>
            <aside class="sidebar">
                <div class="side-box">
                    <h3>Weiterlesen</h3>
                    <ul class="link-list">
                        <li><a href="produkte.html#technische-daten">Technische Daten{icon("arrow")}</a></li>
                        <li><a href="produkte.html#systemvergleich">Systemvergleich{icon("arrow")}</a></li>
                        <li><a href="anwendungen.html">Anwendungen{icon("arrow")}</a></li>
                        <li><a href="moertel-bedarf-rechner.html">Mörtelrechner{icon("arrow")}</a></li>
                    </ul>
                </div>
                {contact_box()}
            </aside>
        </div>
    </main>
'''

# ---------------------------------------------------------------- Kontakt
def page_kontakt():
    crumbs = [("Start", "index.html"), ("Kontakt", "kontakt.html")]
    return page_head(crumbs, "Kontakt", "Beratung, Miete und Offerte",
                     "Sie haben eine technische Frage, möchten die Pumpe testen oder brauchen eine Offerte? Unser Team in Regensdorf ist für Sie da.") + f'''
    <main class="section">
        <div class="container contact-grid">
            <div>
                <ul class="contact-list">
                    <li>{icon("phone")}<div><strong>Telefon</strong><a href="{PHONE_HREF}">{PHONE}</a></div></li>
                    <li>{icon("mail")}<div><strong>E-Mail</strong><a href="mailto:{MAIL}">{MAIL}</a></div></li>
                    <li>{icon("pin")}<div><strong>Adresse</strong>Wilcowa AG Baumaschinen<br>Riedthofstrasse 172<br>8105 Regensdorf<br><a class="link-arrow" style="margin-top:8px;font-size:.92rem" href="https://www.google.com/maps/search/?api=1&amp;query=Wilcowa+AG+Riedthofstrasse+172+8105+Regensdorf" target="_blank" rel="noopener">Route planen {icon("external")}</a></div></li>
                    <li>{icon("clock")}<div><strong>Öffnungszeiten</strong>Mo–Do 07:00–12:00 und 13:00–17:00<br>Fr 07:00–12:00 und 13:00–16:00</div></li>
                </ul>
            </div>

            <div class="card">
                <h2>Anfrage senden</h2>
                <p>Das Formular öffnet Ihr E-Mail-Programm mit einer vorbereiteten Nachricht an {MAIL}.</p>
                <form id="contact-form" class="form-grid">
                    <div class="field"><label for="f-vorname">Vorname *</label><input id="f-vorname" name="vorname" autocomplete="given-name" required></div>
                    <div class="field"><label for="f-nachname">Nachname *</label><input id="f-nachname" name="nachname" autocomplete="family-name" required></div>
                    <div class="field field-full"><label for="f-firma">Firma</label><input id="f-firma" name="firma" autocomplete="organization"></div>
                    <div class="field"><label for="f-email">E-Mail *</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
                    <div class="field"><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
                    <div class="field field-full">
                        <label for="f-betreff">Anliegen</label>
                        <select id="f-betreff" name="betreff">
                            <option>Offerte Kauf WPS-Mörtelpumpe</option>
                            <option>Mietanfrage WPS-Mörtelpumpe</option>
                            <option>Technische Frage</option>
                            <option>Vorführung vereinbaren</option>
                            <option>Ersatzteile und Zubehör</option>
                            <option>Sonstiges</option>
                        </select>
                    </div>
                    <div class="field field-full"><label for="f-msg">Nachricht *</label><textarea id="f-msg" name="nachricht" rows="6" required placeholder="Anwendung, Material, gewünschter Zeitraum …"></textarea></div>
                    <div class="field-full form-actions">
                        <button class="btn btn-primary" type="submit">Anfrage per E-Mail senden {icon("arrow")}</button>
                        <span class="form-note">* Pflichtfelder</span>
                    </div>
                </form>
            </div>
        </div>
    </main>
'''

# ---------------------------------------------------------------- Impressum
def page_impressum():
    crumbs = [("Start", "index.html"), ("Impressum", "impressum.html")]
    return page_head(crumbs, "Rechtliches", "Impressum", "Angaben zum Anbieter dieser Website.") + f'''
    <main class="section">
        <div class="container legal">
            <h2>Kontaktadresse</h2>
            <p>Wilcowa AG Baumaschinen<br>Riedthofstrasse 172<br>8105 Regensdorf<br>Schweiz</p>
            <p>Telefon: <a href="{PHONE_HREF}">{PHONE}</a><br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>

            <h2>Vertretungsberechtigte Person</h2>
            <p>Philippe Tobler</p>

            <h2>Handelsregistereintrag</h2>
            <p>Eingetragener Firmenname: Wilcowa AG Baumaschinen<br>UID: CHE-105.750.310<br>Handelsregisteramt: Kanton Zürich</p>

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

# ---------------------------------------------------------------- Seitenliste
PAGES = [
    dict(file="index.html", active="", body=page_index,
         title="Mörtelpumpe mieten & kaufen in der Schweiz | WPS-Mörtelpumpe – Wilcowa",
         desc="WPS-Mörtelpumpe mieten oder kaufen: stufenlos dosierbar (0.5–12 l/min) für Stahlzargen, Fugen, Maueranker und Untermörteln. Schweizer Vertrieb, Ersatzteile ab Lager Regensdorf.",
         ld=[LOCAL_BUSINESS]),
    dict(file="produkte.html", active="produkt", body=page_produkt, og_type="product",
         og_image="Untermorteln_Holzbau.avif",
         title="WPS-Mörtelpumpe: Technische Daten & Systemvergleich | Wilcowa",
         desc="Technische Daten der WPS-Mörtelpumpe: 230 V, 0.5–12 l/min stufenlos, Korngrösse bis 4 mm, ca. 1–2.5 bar. Geeignete Materialien und Vergleich mit Handverfugung.",
         ld=[{"@context": "https://schema.org", "@type": "Product", "name": "WPS-Mörtelpumpe",
              "image": BASE + "/assets/Untermorteln_Holzbau.avif",
              "description": "Dosierbare, elektrisch angetriebene Mörtelpumpe (230 V) für Fugen, Zargen, Maueranker und Hohlräume. Fördermenge ca. 0.5–12 l/min, Korngrösse 0–4 mm.",
              "brand": {"@type": "Brand", "name": "WPS"},
              "offers": {"@type": "Offer", "url": BASE + "/kontakt.html", "priceCurrency": "CHF", "availability": "https://schema.org/InStock",
                         "seller": {"@type": "Organization", "name": "Wilcowa AG Baumaschinen"}}}]),
    dict(file="anwendungen.html", active="anwendungen", body=page_anwendungen,
         og_image="Ausmorteln_Stahltrager.avif",
         title="Anwendungen der Mörtelpumpe: Zargen, Fugen, Anker | WPS – Wilcowa",
         desc="Einsatzgebiete der WPS-Mörtelpumpe: Stahlzargen hinterfüllen, Schwellen untermörteln, Naturstein verfugen, Maueranker verpressen, Spannbeton vergiessen und Dämmplatten kleben."),
    dict(file="moertel-bedarf-rechner.html", active="rechner", body=page_rechner,
         title="Mörtelrechner: Mörtelbedarf für Fugen online berechnen | Wilcowa",
         desc="Kostenloser Mörtel-Bedarfsrechner: Volumen und Trockenmaterial für Fugen, Zargen und Hohlräume aus Länge, Breite und Tiefe berechnen – inkl. Verschnitt."),
    dict(file="faq.html", active="faq", body=page_faq,
         title="Mörtelpumpe FAQ: Häufige Fragen zur WPS-Mörtelpumpe | Wilcowa",
         desc="Antworten zur WPS-Mörtelpumpe: geeignete Mörtel, Miete, Arbeitsdruck, Reinigung, Einmannbedienung, Ersatzteile und Einweisung.",
         ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
             {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]),
    dict(file="kontakt.html", active="kontakt", body=page_kontakt,
         title="Kontakt: Mörtelpumpe anfragen | Wilcowa AG Regensdorf",
         desc="Kontakt zur Wilcowa AG in Regensdorf: Beratung, Mietanfrage oder Offerte für die WPS-Mörtelpumpe. Telefon +41 43 388 70 60, info@wilcowa.ch.",
         ld=[LOCAL_BUSINESS]),
    dict(file="impressum.html", active="", body=page_impressum, noindex=True,
         title="Impressum | Wilcowa AG", desc="Impressum der Website moertelpumpe.ch der Wilcowa AG Baumaschinen, Regensdorf."),
]
for slug, d in DETAILS.items():
    PAGES.append(dict(file=f"{slug}.html", active="anwendungen", body=(lambda s=slug: page_detail(s)), og_type="article",
                      og_image=d["img"][0] + ".avif", title=d["title"], desc=d["desc"]))

CRUMBS = {"produkte.html": [("Start", "index.html"), ("Produkt & Daten", "produkte.html")],
          "anwendungen.html": [("Start", "index.html"), ("Anwendungen", "anwendungen.html")],
          "moertel-bedarf-rechner.html": [("Start", "index.html"), ("Mörtelrechner", "moertel-bedarf-rechner.html")],
          "faq.html": [("Start", "index.html"), ("Häufige Fragen", "faq.html")],
          "kontakt.html": [("Start", "index.html"), ("Kontakt", "kontakt.html")]}
for s, n, t, *_ in APPS:
    CRUMBS[f"{s}.html"] = [("Start", "index.html"), ("Anwendungen", "anwendungen.html"), (t, f"{s}.html")]

def swiss(text):
    return text.replace("ß", "ss")

for p in PAGES:
    active_file[0] = p["file"]
    if p["file"] in CRUMBS:
        p.setdefault("ld", [])
        p["ld"] = p["ld"] + [breadcrumb_ld(CRUMBS[p["file"]])]
    html_out = head(p) + header(p["active"]) + p["body"]() + footer()
    (OUT / p["file"]).write_text(swiss(html_out), encoding="utf-8", newline="\n")
    print("ok", p["file"])

# Sitemap
urls = [p["file"] for p in PAGES if not p.get("noindex")]
prio = {"index.html": "1.0", "produkte.html": "0.9", "anwendungen.html": "0.9"}
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    loc = BASE + "/" + ("" if u == "index.html" else u)
    sm.append(f"  <url><loc>{loc}</loc><lastmod>2026-10-06</lastmod><priority>{prio.get(u, '0.7')}</priority></url>")
sm.append("</urlset>")
(OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")
print("ok sitemap.xml")
