# Lokale Vorschau mit denselben Regeln wie nginx auf dem Server: python tools/serve.py [port]
# - /kontakt liefert kontakt.html
# - alte Adressen (nginx-redirects.conf) und *.html leiten per 301 auf die Adresse ohne Endung um
import http.server, pathlib, re, sys

BASE = pathlib.Path(__file__).resolve().parent.parent
ROOT = BASE / "website"
REDIRECTS = dict(re.findall(r"location = (/\S+) \{ return 301 (/\S*?)\$is_args", (BASE / "nginx-redirects.conf").read_text(encoding="utf-8")))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def redirect(self, to):
        self.send_response(301)
        self.send_header("Location", to)
        self.end_headers()

    def send_head(self):
        path, _, query = self.path.partition("?")
        qs = "?" + query if query else ""
        if path in REDIRECTS:
            return self.redirect(REDIRECTS[path] + qs)
        if path == "/index.html":
            return self.redirect("/" + qs)
        if path.endswith(".html") and (ROOT / path.lstrip("/")).exists():
            return self.redirect(path[:-5] + qs)
        if path != "/" and "." not in path.rsplit("/", 1)[-1] and (ROOT / (path.lstrip("/") + ".html")).exists():
            self.path = path + ".html" + qs
        return super().send_head()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
