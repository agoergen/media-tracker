"""
LeisureLedger - PythonAnywhere API & CDN Outbound Connectivity Checker

This standalone script tests outbound HTTP connectivity against all external
APIs, scraping targets, and image CDNs required by LeisureLedger.

Usage:
  1. CLI Mode (Bash Console):
     python poc_pa_checker.py

  2. Web Mode (Flask / WSGI):
     python poc_pa_checker.py --web
     (or point PythonAnywhere WSGI configuration to 'from poc_pa_checker import app as application')
"""

import os
import sys
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Read credentials from environment if available
TMDB_TOKEN = os.environ.get("TMDB_READ_TOKEN") or os.environ.get("TMDB_API_KEY")
GOOGLE_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")

# Test targets matching LeisureLedger's integrations
TEST_TARGETS = [
    {
        "category": "Movies & TV",
        "service": "TMDB API",
        "url": f"https://api.themoviedb.org/3/search/movie?query=Inception" if TMDB_TOKEN else "https://api.themoviedb.org/3/configuration",
        "headers": {"Authorization": f"Bearer {TMDB_TOKEN}"} if TMDB_TOKEN else {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Reaches TMDB API servers"
    },
    {
        "category": "Movies & TV",
        "service": "TMDB Image CDN",
        "url": "https://image.tmdb.org/t/p/w200/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Poster artwork CDN"
    },
    {
        "category": "Gaming",
        "service": "Twitch OAuth (IGDB Auth)",
        "url": "https://id.twitch.tv/oauth2/token",
        "method": "POST",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Twitch authentication endpoint"
    },
    {
        "category": "Gaming",
        "service": "IGDB API",
        "url": "https://api.igdb.com/v4/games",
        "method": "POST",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "IGDB games database endpoint"
    },
    {
        "category": "Gaming",
        "service": "IGDB Image CDN",
        "url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Game cover image CDN"
    },
    {
        "category": "Books",
        "service": "Google Books API",
        "url": f"https://www.googleapis.com/books/v1/volumes?q=Dune&key={GOOGLE_KEY}" if GOOGLE_KEY else "https://www.googleapis.com/books/v1/volumes?q=Dune&maxResults=1",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Google Books API"
    },
    {
        "category": "Books",
        "service": "OpenLibrary API",
        "url": "https://openlibrary.org/search.json?title=Dune&limit=1",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "OpenLibrary fallback book search"
    },
    {
        "category": "Books",
        "service": "OpenLibrary Covers CDN",
        "url": "https://covers.openlibrary.org/b/id/10522966-M.jpg",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0"},
        "note": "Book cover image CDN"
    },
    {
        "category": "Theater",
        "service": "IBDB (Internet Broadway Database)",
        "url": "https://www.ibdb.com",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "note": "Stage show search & scraping target"
    },
    {
        "category": "Theater",
        "service": "Wikipedia API",
        "url": "https://en.wikipedia.org/w/api.php?action=query&titles=Hamilton_(musical)&format=json",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0 (contact@leisureledger.local)"},
        "note": "Theater details & summary scraping"
    },
    {
        "category": "Theater",
        "service": "Wikimedia Upload CDN",
        "url": "https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/200px-Wikipedia-logo-v2.svg.png",
        "headers": {"User-Agent": "LeisureLedger-Tester/1.0 (contact@leisureledger.local)"},
        "note": "Wikipedia/Wikimedia artwork CDN"
    }
]


def test_target(target):
    """Execute request and classify connectivity status."""
    method = target.get("method", "GET")
    url = target["url"]
    headers = target.get("headers", {})
    
    start_time = time.time()
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)
        elapsed_ms = int((time.time() - start_time) * 1000)

        # In PythonAnywhere's free tier, blocked endpoints return a 403 / Proxy Error from proxy.server
        is_pa_proxy_block = (
            response.status_code == 403 and
            ("proxy" in response.text.lower() or "whitelist" in response.text.lower() or "allowlist" in response.text.lower())
        )

        if is_pa_proxy_block:
            status = "BLOCKED (PA Allowlist)"
            passed = False
        elif response.status_code in [200, 201, 204, 301, 302, 304, 400, 401, 429]:
            # 400/401/429 indicates outbound TCP/HTTP connected successfully to the destination server
            status = f"PASSED (HTTP {response.status_code})"
            passed = True
        else:
            status = f"FAILED (HTTP {response.status_code})"
            passed = False

        return {
            "category": target["category"],
            "service": target["service"],
            "url": url,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
            "status": status,
            "passed": passed,
            "error": None if passed else response.text[:200]
        }
    except requests.exceptions.ProxyError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "category": target["category"],
            "service": target["service"],
            "url": url,
            "status_code": None,
            "elapsed_ms": elapsed_ms,
            "status": "BLOCKED (Proxy Error)",
            "passed": False,
            "error": str(e)
        }
    except requests.exceptions.RequestException as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "category": target["category"],
            "service": target["service"],
            "url": url,
            "status_code": None,
            "elapsed_ms": elapsed_ms,
            "status": "CONNECTION ERROR",
            "passed": False,
            "error": str(e)
        }


def run_all_tests():
    """Run all connectivity tests and return structured results."""
    return [test_target(t) for t in TEST_TARGETS]


def run_cli():
    """Run tests in CLI format."""
    print("=" * 80)
    print("  LeisureLedger -> PythonAnywhere Outbound API Connectivity Check")
    print("=" * 80)
    print(f"Testing {len(TEST_TARGETS)} endpoints across Movies/TV, Games, Books, and Theater...\n")

    results = []
    for idx, target in enumerate(TEST_TARGETS, 1):
        print(f"[{idx:02d}/{len(TEST_TARGETS):02d}] Testing {target['service']}...", end=" ", flush=True)
        res = test_target(target)
        results.append(res)
        if res["passed"]:
            print(f"OK ({res['status']}, {res['elapsed_ms']}ms)")
        else:
            print(f"FAIL ({res['status']})")
            if res["error"]:
                print(f"       Details: {res['error'][:150]}")

    print("\n" + "=" * 80)
    print("  Summary Results")
    print("=" * 80)
    print(f"{'Service':<32} | {'Category':<12} | {'Latency':<8} | {'Result':<22}")
    print("-" * 80)
    
    passed_count = sum(1 for r in results if r["passed"])
    for r in results:
        print(f"{r['service']:<32} | {r['category']:<12} | {str(r['elapsed_ms']) + 'ms':<8} | {r['status']:<22}")
    
    print("-" * 80)
    print(f"Total: {passed_count}/{len(results)} passed.")
    if passed_count == len(results):
        print("\nAll LeisureLedger external services are fully accessible on this environment!")
    else:
        print("\nOne or more external endpoints are blocked or failing. Review details above.")
    print("=" * 80)


# Flask Web Dashboard Setup
try:
    from flask import Flask, render_template_string
    app = Flask(__name__)

    HTML_TEMPLATE = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>LeisureLedger - PythonAnywhere API Diagnostic</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f1117; color: #e2e8f0; margin: 0; padding: 2rem; }
        .container { max-width: 960px; margin: 0 auto; }
        h1 { font-size: 1.5rem; margin-bottom: 0.5rem; color: #fff; }
        p.subtitle { color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem; }
        .card { background: #1a1e29; border: 1px solid #2d3748; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }
        th { padding: 0.75rem 1rem; border-bottom: 1px solid #2d3748; color: #94a3b8; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
        td { padding: 0.75rem 1rem; border-bottom: 1px solid #1e2638; vertical-align: top; }
        .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .badge-pass { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }
        .badge-fail { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
        .url { color: #60a5fa; font-family: monospace; font-size: 0.8rem; word-break: break-all; }
        .btn { background: #3b82f6; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: 500; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #2563eb; }
        .summary-box { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
        .metric { background: #1a1e29; border: 1px solid #2d3748; border-radius: 8px; padding: 1rem; flex: 1; text-align: center; }
        .metric-val { font-size: 1.75rem; font-weight: 700; margin-top: 0.25rem; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>LeisureLedger &mdash; PythonAnywhere Outbound API Diagnostic</h1>
        <p class="subtitle">Verifies outbound network connectivity across all LeisureLedger APIs, image CDNs, and scraping targets.</p>
        
        <div class="summary-box">
          <div class="metric">
            <div style="color: #94a3b8; font-size: 0.8rem;">TOTAL ENDPOINTS</div>
            <div class="metric-val">{{ results|length }}</div>
          </div>
          <div class="metric">
            <div style="color: #94a3b8; font-size: 0.8rem;">PASSED</div>
            <div class="metric-val" style="color: #4ade80;">{{ passed_count }}</div>
          </div>
          <div class="metric">
            <div style="color: #94a3b8; font-size: 0.8rem;">BLOCKED / FAILED</div>
            <div class="metric-val" style="color: {{ '#f87171' if (results|length - passed_count) > 0 else '#94a3b8' }};">{{ results|length - passed_count }}</div>
          </div>
        </div>

        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-size: 1.1rem; margin: 0;">Diagnostic Results</h2>
            <a href="/" class="btn">Re-run Tests</a>
          </div>
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Service</th>
                <th>Status</th>
                <th>Latency</th>
                <th>Endpoint</th>
              </tr>
            </thead>
            <tbody>
              {% for r in results %}
              <tr>
                <td>{{ r.category }}</td>
                <td><strong>{{ r.service }}</strong></td>
                <td>
                  <span class="badge {{ 'badge-pass' if r.passed else 'badge-fail' }}">{{ r.status }}</span>
                  {% if r.error %}
                  <div style="font-size: 0.75rem; color: #f87171; margin-top: 0.35rem; font-family: monospace;">{{ r.error }}</div>
                  {% endif %}
                </td>
                <td>{{ r.elapsed_ms }}ms</td>
                <td><span class="url">{{ r.url }}</span></td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
    """

    @app.route("/")
    def index():
        results = run_all_tests()
        passed_count = sum(1 for r in results if r["passed"])
        return render_template_string(HTML_TEMPLATE, results=results, passed_count=passed_count)

except ImportError:
    app = None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        if app:
            app.run(host="0.0.0.0", port=5000, debug=True)
        else:
            print("Flask is not installed. Install Flask or run in CLI mode: python poc_pa_checker.py")
    else:
        run_cli()
