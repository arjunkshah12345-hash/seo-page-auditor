"""Client-layer tests: HTTP fully mocked; verifies parsing, retries, and auth handling."""

from __future__ import annotations

import httpx
import pytest

from seo_auditor import tinyfish_client as tf


class _Resp:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or ("" if payload is None else "json")

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def test_missing_key_raises_helpful_error(monkeypatch):
    monkeypatch.delenv("TINYFISH_API_KEY", raising=False)
    with pytest.raises(tf.TinyFishError, match="TINYFISH_API_KEY"):
        tf.search("q")


def test_search_parses_results(monkeypatch):
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")
    seen = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        seen["url"] = url
        seen["params"] = params
        seen["headers"] = headers
        return _Resp(
            200,
            {
                "results": [
                    {
                        "position": 1,
                        "title": "T",
                        "url": "https://x.example/",
                        "snippet": "s",
                        "site_name": "x.example",
                    },
                    {
                        "position": 2,
                        "title": "U",
                        "url": "https://y.example/",
                        "snippet": "s2",
                        "site_name": "y.example",
                    },
                ],
                "total_results": 2,
                "page": 0,
            },
        )

    monkeypatch.setattr(tf.httpx, "get", fake_get)
    out = tf.search("best shoes", purpose="audit")
    assert seen["url"] == tf.SEARCH_URL
    assert seen["params"]["query"] == "best shoes"
    assert seen["params"]["purpose"] == "audit"
    assert seen["headers"]["X-API-Key"] == "test-key"
    assert [r.position for r in out] == [1, 2]
    assert out[0].site_name == "x.example"


def test_search_rate_limit_retries_then_succeeds(monkeypatch):
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")
    calls = {"n": 0}

    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            return _Resp(429, text="rate limited")
        return _Resp(
            200,
            {
                "results": [
                    {"position": 1, "title": "T", "url": "https://x/", "snippet": "", "site_name": "x"}
                ]
            },
        )

    monkeypatch.setattr(tf.httpx, "get", fake_get)
    monkeypatch.setattr(tf.time, "sleep", lambda s: None)
    out = tf.search("q")
    assert calls["n"] == 3
    assert out[0].position == 1


def test_search_4xx_is_fatal_not_retried(monkeypatch):
    monkeypatch.setenv("TINYFISH_API_KEY", "test-key")
    calls = {"n": 0}

    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        return _Resp(401, text="unauthorized")

    monkeypatch.setattr(tf.httpx, "get", fake_get)
    with pytest.raises(tf.TinyFishError, match="401"):
        tf.search("q")
    assert calls["n"] == 1


_ = httpx  # keep import meaningful for type-checkers; httpx used via tf.httpx
