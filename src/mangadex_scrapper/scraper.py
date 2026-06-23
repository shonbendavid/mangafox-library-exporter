"""Minimal async scraper utilities."""
from typing import List, Optional, Tuple, Dict
import secrets
import hashlib
import base64
import webbrowser
import threading
import http.server
import socketserver
import urllib.parse
import time

LOGIN_URL = "https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/auth?client_id=mangadex-frontend-stable&redirect_uri=https%3A%2F%2Fmangadex.org%2Fauth%2Flogin%3FafterAuthentication%3D%2F%26shouldRedirect%3Dtrue%26wasPopup%3Dfalse&response_type=code&scope=openid+email+groups+profile+roles&state=d5ca10c8de164d7aa4233139aba31eed&code_challenge=Y09vPpeVNKWOu48u0MAdov3Ulob1eqKcxyfIgNh8uGQ&code_challenge_method=S256"  # MangaDex OIDC authorization endpoint

async def fetch_html(url: str) -> str:
    """Fetch HTML content asynchronously.

    Imports httpx lazily so importing this module doesn't require httpx to be installed
    until this function is actually used.
    """
    try:
        import httpx
    except Exception as exc:
        raise RuntimeError("httpx is required to fetch HTML; install requirements.txt") from exc

    async with httpx.AsyncClient(http2=True, timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


def parse_titles_from_html(html: str) -> List[str]:
    """Parse titles from HTML using BeautifulSoup (lazy import).

    This is a small helper kept separate for testability.
    """
    try:
        from bs4 import BeautifulSoup
    except Exception as exc:
        raise RuntimeError("beautifulsoup4 is required to parse HTML; install requirements.txt") from exc

    soup = BeautifulSoup(html, "lxml")
    # Placeholder parsing; real logic should select actual title nodes.
    return [t.get_text(strip=True) for t in soup.select("h1")]

async def login_mangafox(username: str, password: str, login_url: Optional[str] = None) -> bool:
    """Attempt to log in to MangaFox-like site.

    Important: The default `LOGIN_URL` is an OpenID Connect (OIDC) authorization endpoint used by MangaDex
    to start the OAuth2/OIDC authorization-code flow. That endpoint requires browser redirects, user interaction,
    and an authorization code exchange — it does NOT accept direct username/password POSTs.

    This helper function performs a simple POST of credentials to `login_url` and returns True/False based on
    the response. It is intended for unit tests and for sites that support direct credential POSTs. For real
    MangaDex integration you must implement the full OAuth2/OIDC flow (e.g., using an OAuth2 library or
    browser automation to obtain tokens) and then use those tokens for authenticated requests.

    For testing, continue to mock `httpx.AsyncClient` responses; do not embed real credentials in source.
    """
    url = login_url or LOGIN_URL
    try:
        import httpx
    except Exception as exc:
        raise RuntimeError("httpx is required to perform login; install requirements.txt") from exc

    data = {"username": username, "password": password}

    # Allow callers to rely on session cookies by using AsyncClient; create one for a single request.
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data)
        # Simple heuristic: 200 + JSON success flag or 200 implies success
        if resp.status_code == 200:
            try:
                j = resp.json()
                return bool(j.get("success", True))
            except Exception:
                return True
        return False

def _generate_pkce_pair() -> Tuple[str, str]:
    """Generate a PKCE code_verifier and code_challenge (S256).

    Returns (code_verifier, code_challenge).
    """
    verifier = secrets.token_urlsafe(64)
    # Create a S256 challenge
    challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge_b64 = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode("ascii")
    return verifier, challenge_b64


def _start_local_http_server(port: int, path: str, timeout: int = 120) -> Dict[str, str]:
    """Start a temporary local HTTP server to capture a single redirect with query params.

    Returns a dict of query parameters received. Blocks until a request is received or timeout.
    """
    result: Dict[str, str] = {}

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != path:
                # respond 404
                self.send_response(404)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            # Flatten values
            for k, v in qs.items():
                result[k] = v[0] if v else ""
            # Send a simple response to the browser
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authentication received. You can close this tab.</h1></body></html>")

        def log_message(self, format, *args):
            # Silence logs
            return

    with socketserver.TCPServer(("localhost", port), _Handler) as httpd:
        httpd.timeout = timeout
        # handle a single request or until timeout
        start = time.time()
        while True:
            httpd.handle_request()
            if result:
                break
            if (time.time() - start) > timeout:
                break
    return result


async def oidc_authorize_with_pkce(
    client_id: str,
    scopes: Tuple[str, ...] = ("openid", "email", "profile"),
    auth_endpoint: str = LOGIN_URL,
    token_endpoint: Optional[str] = None,
    redirect_port: int = 8000,
    timeout: int = 120,
) -> Dict[str, object]:
    """Perform an OAuth2/OIDC authorization-code flow with PKCE.

    Steps:
    1. Generate PKCE code_verifier and code_challenge.
    2. Build the authorization URL and open it in the user's browser.
    3. Start a local HTTP server at http://localhost:{redirect_port}/callback to capture the redirect containing the authorization code.
    4. Exchange the authorization code and PKCE verifier at the token endpoint for tokens.

    Returns the token response (JSON) on success.

    Notes:
    - `auth_endpoint` should be the OIDC authorization endpoint (where the user logs in).
    - `token_endpoint` should be the OIDC token endpoint (e.g., replace /auth with /token); if omitted we try to infer it by replacing '/auth' with '/token' in the auth_endpoint.
    - This function opens a browser window and requires user interaction.
    - Keep client_id and any secrets out of source control.
    """
    if token_endpoint is None:
        # naive inference: replace '/auth' with '/token' in the URL path
        token_endpoint = auth_endpoint.replace("/auth", "/token")

    code_verifier, code_challenge = _generate_pkce_pair()

    redirect_path = "/callback"
    redirect_uri = f"http://localhost:{redirect_port}{redirect_path}"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = auth_endpoint
    if "?" in auth_url:
        auth_url = auth_url.split("?")[0]
    auth_url = auth_url + "?" + urllib.parse.urlencode(params)

    # Open the browser for user to authenticate
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    # Start local server in separate thread to capture the redirect
    captured: Dict[str, str] = {}
    def _server_target():
        nonlocal captured
        captured = _start_local_http_server(redirect_port, redirect_path, timeout=timeout)

    t = threading.Thread(target=_server_target, daemon=True)
    t.start()
    # Wait for the server thread to capture or timeout
    t.join(timeout + 5)

    if not captured or "code" not in captured:
        raise RuntimeError("Authorization code not received (timeout or user aborted)")

    code = captured["code"]

    # Exchange code for tokens
    try:
        import httpx
    except Exception as exc:
        raise RuntimeError("httpx is required to exchange token; install requirements.txt") from exc

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_endpoint, data=data)
        resp.raise_for_status()
        return resp.json()

def oidc_authorize_with_pkce_manual(
    client_id: str,
    scopes: Tuple[str, ...] = ("openid", "email", "profile"),
    auth_endpoint: str = LOGIN_URL,
    token_endpoint: Optional[str] = None,
    redirect_port: int = 8000,
) -> Dict[str, object]:
    """Manual fallback for OIDC PKCE flow.

    Prints an authorization URL and prompts the user to paste the full redirect URL
    (where the provider redirected the browser). Extracts the authorization code
    from the pasted URL and exchanges it for tokens at the token endpoint.

    This is useful when running on machines where starting a local HTTP server
    is not possible or when the provider won't redirect to localhost automatically.
    """
    if token_endpoint is None:
        token_endpoint = auth_endpoint.replace("/auth", "/token")

    code_verifier, code_challenge = _generate_pkce_pair()
    redirect_path = "/callback"
    redirect_uri = f"http://localhost:{redirect_port}{redirect_path}"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = auth_endpoint
    if "?" in auth_url:
        auth_url = auth_url.split("?")[0]
    auth_url = auth_url + "?" + urllib.parse.urlencode(params)

    print("Open the following URL in your browser and complete authentication:")
    print(auth_url)
    print("")
    print("After authentication, you will be redirected to a URL. Paste that full URL here.")

    redirected = input("Redirected URL: ").strip()
    if not redirected:
        raise RuntimeError("No redirect URL provided")

    # Extract code from provided URL
    parsed = urllib.parse.urlparse(redirected)
    qs = urllib.parse.parse_qs(parsed.query)
    code = qs.get("code", [None])[0]
    if not code:
        # Maybe user pasted only the code
        if "code=" in redirected:
            # try to parse after code=
            code = redirected.split("code=", 1)[1].split("&", 1)[0]
    if not code:
        raise RuntimeError("Authorization code not found in provided URL")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }

    try:
        import httpx
    except Exception as exc:
        raise RuntimeError("httpx is required to exchange token; install requirements.txt") from exc

    # Use sync httpx for simplicity in this interactive flow
    resp = httpx.post(token_endpoint, data=data)
    resp.raise_for_status()
    return resp.json()

def generate_pkce_auth_url(
    client_id: str,
    scopes: Tuple[str, ...] = ("openid", "email", "profile"),
    auth_endpoint: str = LOGIN_URL,
    redirect_port: int = 8000,
) -> Tuple[str, str, str]:
    """Generate an authorization URL and corresponding PKCE verifier.

    Returns a tuple (auth_url, code_verifier, redirect_uri). The caller should open
    auth_url in a browser, complete authentication, capture the redirect URL, and
    then call oidc_authorize_with_pkce_from_redirect with the redirect URL and
    the returned code_verifier to obtain tokens.
    """
    code_verifier, code_challenge = _generate_pkce_pair()
    redirect_path = "/callback"
    redirect_uri = f"http://localhost:{redirect_port}{redirect_path}"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = auth_endpoint
    if "?" in auth_url:
        auth_url = auth_url.split("?")[0]
    auth_url = auth_url + "?" + urllib.parse.urlencode(params)

    return auth_url, code_verifier, redirect_uri


def oidc_authorize_with_pkce_from_redirect(
    redirected_url: str,
    code_verifier: str,
    client_id: str,
    token_endpoint: Optional[str] = None,
    redirect_uri: Optional[str] = None,
) -> Dict[str, object]:
    """Exchange an authorization code (extracted from redirected_url) for tokens.

    This is the non-interactive exchange step. It expects the caller to have kept
    the code_verifier returned by generate_pkce_auth_url.
    """
    if token_endpoint is None:
        token_endpoint = LOGIN_URL.replace("/auth", "/token")

    parsed = urllib.parse.urlparse(redirected_url)
    qs = urllib.parse.parse_qs(parsed.query)
    code = qs.get("code", [None])[0]
    if not code:
        # Accept raw code as input as a fallback
        code = redirected_url
    if not code:
        raise RuntimeError("Authorization code not found in provided URL or input")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }

    try:
        import httpx
    except Exception as exc:
        raise RuntimeError("httpx is required to exchange token; install requirements.txt") from exc

    resp = httpx.post(token_endpoint, data=data)
    resp.raise_for_status()
    return resp.json()

# Example synchronous wrapper for the CLI example

def fetch_titles(query: str, limit: int = 5) -> List[str]:
    """Stub: Return fake titles for a query. Replace with real async scraper logic."""
    return [f"{query} - title {i+1}" for i in range(limit)]
