"""Local dev server that mirrors Cloudflare Pages' .html handling.

Pages serves `/foo.html` at `/foo` and 308-redirects the `.html` form to the
extensionless canonical. Python's built-in http.server doesn't do either, so
every nav link in the site 404s locally. This wrapper fixes that.
"""

import http.server
import os
import sys


class PagesLikeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self._maybe_redirect():
            return
        self._rewrite_extensionless()
        super().do_GET()

    def do_HEAD(self):
        if self._maybe_redirect():
            return
        self._rewrite_extensionless()
        super().do_HEAD()

    def _maybe_redirect(self):
        path, _, query = self.path.partition("?")

        if path.endswith(".html") and path != "/index.html":
            return self._redirect(path[: -len(".html")], query)

        if path == "/index.html":
            return self._redirect("/", query)

        if len(path) > 1 and path.endswith("/"):
            stripped = path.rstrip("/")
            if os.path.isfile(self.translate_path(stripped + ".html")):
                return self._redirect(stripped, query)

        return False

    def _redirect(self, new_path, query):
        location = new_path + (f"?{query}" if query else "")
        self.send_response(308)
        self.send_header("Location", location)
        self.end_headers()
        return True

    def _rewrite_extensionless(self):
        path, sep, query = self.path.partition("?")
        if path in ("", "/") or "." in path.rsplit("/", 1)[-1]:
            return
        if os.path.isfile(self.translate_path(path + ".html")):
            self.path = path + ".html" + (sep + query if sep else "")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with http.server.ThreadingHTTPServer(("", port), PagesLikeHandler) as httpd:
        print(f"Serving on http://localhost:{port}")
        httpd.serve_forever()
