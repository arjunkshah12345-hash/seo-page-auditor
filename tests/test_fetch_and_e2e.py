"""Fetch parsing tests + full offline end-to-end audit (all HTTP mocked)."""

from __future__ import annotations

import pytest

from seo_auditor import tinyfish_client as tf
from seo_auditor.audit import run_audit


class _Resp:
    def __init__(self, status_code=200, payload=None, text="", url="https://blogguide.example/post"):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.url = url
        self.history = []
        self.headers = {"content-type": "text/html; charset=utf-8"}

    def json(self):
        return self._payload


MD_RESULT = {
    "url": "https://blogguide.example/post",
    "final_url": "https://blogguide.example/post",
    "title": "Guide to X",
    "description": "All about X.",
    "language": "en",
    "author": "A. Author",
    "published_date": "2026-08-01",
    "text": "# Guide to X\n\n" + "word " * 400,
}
HTML_RESULT = {
    "url": "https://blogguide.example/post",
    "final_url": "https://blogguide.example/post",
    "title": "Guide to X",
    "description": None,
    "language": None,
    "author": None,
    "published_date": None,
    "text": "<main><article><h1>Guide to X</h1><h2>Why</h2><p>…</p><ul><li>a</li></ul></article></main>",
}
SEARCH_PAYLOAD = {
    "results": [
        {
            "position": 1,
            "title": "Competitor guide",
            "url": "https://other.example/x",
            "snippet": "Their take.",
            "site_name": "other.example",
        },
        {
            "position": 2,
            "title": "Guide to X — blogguide.example",
            "url": "https://blogguide.example/post",
            "snippet": "All about X, ranked.",
            "site_name": "blogguide.example",
        },
    ],
    "total_results": 2,
    "page": 0,
}
AGENT_PAYLOAD = {
    "run_id": "r1",
    "status": "COMPLETED",
    "num_of_steps": 4,
    "result": {
        "page_understood": True,
        "what_is_this_page": "A guide explaining X.",
        "key_facts": ["fact one", "fact two", "fact three"],
        "main_topic_guess": "X",
        "nav_links_seen": 12,
        "rendered_content_chars": 9000,
        "js_required": False,
        "render_blockers": [],
    },
    "error": None,
}
ROBOTS_TXT = "User-agent: *\nDisallow: /admin/\n\nSitemap: https://blogguide.example/sitemap.xml\n"
ORIGIN_HTML = (
    "<html><head><title>Guide to X — blogguide.example</title>"
    '<meta name="description" content="All about X.">'
    '<link rel="canonical" href="https://blogguide.example/post">'
    '<meta property="og:title" content="Guide to X">'
    '<meta property="og:image" content="https://blogguide.example/og.jpg">'
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article"}</script>'
    "</head><body><h1>Guide to X</h1><h2>Why X matters</h2>"
    "<p>X is the core of the guide.</p><p>Readers get a full walkthrough.</p>"
    "<p>Each section covers one step.</p><p>Examples are included.</p>"
    "<ul><li>step one</li><li>step two</li><li>step three</li><li>step four</li></ul>"
    "<p>That is the whole process.</p></body></html>"
)


@pytest.fixture()
def live_mock(monkeypatch):
    """Wire every HTTP path the audit touches to canned responses."""
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")
    calls = {"fetch": [], "search": [], "agent": [], "origin": []}

    def fake_post(url, json=None, headers=None, timeout=None, **_kw):
        if url == tf.FETCH_URL:
            calls["fetch"].append(json)
            fmt = json["format"]
            result = dict(MD_RESULT if fmt == "markdown" else HTML_RESULT)
            result["url"] = json["urls"][0]  # echo the requested URL (mocks are per-URL in reality)
            result["final_url"] = json["urls"][0]
            return _Resp(200, {"results": [result], "errors": []})
        if url == tf.AGENT_URL:
            calls["agent"].append(json)
            return _Resp(200, AGENT_PAYLOAD)
        raise AssertionError(f"unexpected POST {url}")

    def fake_get(url, params=None, headers=None, timeout=None, **_kw):
        if url == tf.SEARCH_URL:
            calls["search"].append(params)
            return _Resp(200, SEARCH_PAYLOAD)
        calls["origin"].append(url)
        if url.endswith("/robots.txt"):
            return _Resp(200, text=ROBOTS_TXT)
        if "llms.txt" in url:
            return _Resp(404, text="not found")
        if url == "https://blogguide.example/post":
            return _Resp(200, text=ORIGIN_HTML)
        raise AssertionError(f"unexpected GET {url}")

    monkeypatch.setattr(tf.httpx, "post", fake_post)
    monkeypatch.setattr(tf.httpx, "get", fake_get)
    import seo_auditor.technical as tech

    monkeypatch.setattr(tech.httpx, "post", fake_post)
    monkeypatch.setattr(tech.httpx, "get", fake_get)
    return calls


def test_fetch_result_parsing():
    r = tf.FetchResult.from_api(MD_RESULT)
    assert r.title == "Guide to X"
    assert r.author == "A. Author"
    assert r.text.startswith("# Guide to X")
    assert r.links == []
    err = tf.FetchResult.from_api({"url": "u", "final_url": "u", "title": None})
    assert err.title is None


def test_fetch_errors_surfaced(monkeypatch):
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")

    def fake_post(url, json=None, headers=None, timeout=None, **_kw):
        return _Resp(200, {"results": [], "errors": [{"url": "https://x/", "code": "timeout"}]})

    monkeypatch.setattr(tf.httpx, "post", fake_post)
    results, errors = tf.fetch(["https://x/"])
    assert results == []
    assert errors[0]["code"] == "timeout"


def test_e2e_audit_offline(live_mock):
    res = run_audit("https://blogguide.example/post", "guide to x", with_browser=True)
    calls = live_mock
    # All three TinyFish endpoints actually used
    assert len(calls["fetch"]) == 3  # page markdown + page html + competitor benchmark
    formats = [c["format"] for c in calls["fetch"]]
    assert formats.count("markdown") == 2 and formats.count("html") == 1
    assert any(c["urls"] == ["https://other.example/x"] for c in calls["fetch"])  # competitor fetched live
    assert len(calls["search"]) >= 2  # target query + brand probe
    assert len(calls["agent"]) == 1
    # live-fetch semantics
    assert all(c.get("ttl") == 0 for c in calls["fetch"])
    # scores present and sane
    assert 0 <= res.scores["overall_score"] <= 100
    assert res.scores["ai_readability_score"] >= 70  # healthy page
    # visibility: page ranked #2 for exact query
    assert res.visibility.exact_rank == 2
    assert res.visibility.competitors and res.visibility.competitors[0]["site_name"] == "other.example"
    # agent comprehension captured
    assert res.browser.understood is True
    assert res.browser.key_facts == ["fact one", "fact two", "fact three"]
    # report renders with the essential sections
    md = res.markdown
    for section in (
        "# AI Search & Readability Audit",
        "## Scores",
        "## Findings",
        "TinyFish Fetch",
        "TinyFish Search",
        "TinyFish Agent",
        "robots.txt",
    ):
        assert section in md
    # JSON serialization works and carries findings
    data = __import__("json").loads(res.json())
    assert data["url"] == "https://blogguide.example/post"
    assert len(data["findings"]) >= 1
    assert data["browser_agent"]["understood"] is True
    # 'Fix today' appears exactly when critical/high findings exist
    has_action = any(f["severity"] in ("critical", "high") for f in data["findings"])
    assert ("## Fix today" in md) == has_action
    # competitor benchmark surfaced in JSON and report
    assert data["competitor_benchmarks"][0]["url"] == "https://other.example/x"
    assert "competitor benchmark" in md
    # projected score block appears exactly when there are same-day actions
    assert data["scores"]["projected_after_fixes"]["overall_score"] >= data["scores"]["overall_score"]
    assert ("After fixing the list below" in md) == has_action


def test_e2e_audit_without_browser(live_mock):
    res = run_audit("https://blogguide.example/post", None, with_browser=False)
    assert res.browser is None
    assert live_mock["agent"] == []
    assert res.scores["overall_score"] >= 0


def test_agent_failure_degrades_gracefully(monkeypatch):
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")
    from seo_auditor.browser_probe import run_browser_probe

    def boom(url, goal, output_schema=None, timeout=300.0):
        raise tf.TinyFishError("agent down")

    monkeypatch.setattr(tf, "agent_run", boom)
    rep = run_browser_probe("https://x/")
    assert rep.understood is None
    assert "agent down" in rep.run_error
    findings = __import__("seo_auditor.findings", fromlist=["findings_from_browser"]).findings_from_browser(
        rep
    )
    assert any(f.id == "agent-run-failed" for f in findings)
