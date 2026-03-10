from __future__ import annotations

import http.server
import os
import socketserver
import urllib.parse
import webbrowser
from pathlib import Path

PORT = 3000
REDIRECT_URI = f"http://localhost:{PORT}"
SCOPES = "chat:read+chat:edit"


def _load_env_file() -> None:
    """Best-effort local .env loader without external dependencies."""

    candidate_paths = [
        Path.cwd() / "v2" / ".env",
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]

    for path in candidate_paths:
        if not path.exists():
            continue

        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
        return


_load_env_file()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID") or os.getenv("CLIENT_ID")


class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.fragment:
            params = urllib.parse.parse_qs(parsed_url.fragment)
            token = params.get("access_token", [""])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Token captured. You can close this window.</h2>")
            print(f"\nYour Twitch OAuth Token:\n\noauth:{token}\n")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Waiting for Twitch redirect...</h2>")


def start_server() -> None:
    if not CLIENT_ID:
        raise RuntimeError(
            "Missing Twitch client id. Set TWITCH_CLIENT_ID (preferred) or CLIENT_ID in your environment/.env."
        )

    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=token"
            f"&scope={SCOPES}"
        )
        print(f"Opening Twitch authorization page:\n{auth_url}\n")
        webbrowser.open(auth_url)
        httpd.serve_forever()


if __name__ == "__main__":
    start_server()
