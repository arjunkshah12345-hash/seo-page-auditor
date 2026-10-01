"""TinyFish API client: thin wrappers over Search, Fetch, and Agent.

Auth: single API key from TINYFISH_API_KEY (env) — never embedded in the repo.
Search and Fetch are free endpoints; Agent is metered and used sparingly
(one goal-driven browser run per audit).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

SEARCH_URL = "https://api.search.tinyfish.ai"
FETCH_URL = "https://api.fetch.tinyfish.ai"
AGENT_URL = "https://agent.tinyfish.ai/v1/automation/run"

AUDIT_PURPOSE = (
    "SEO audit: check how this page is represented in search results and whether "
    "AI agents can read and understand it"
)


class TinyFishError(RuntimeError):
    """Raised when a TinyFish API call fails after retries."""


@dataclass
class SearchResult:
    position: int
    title: str
    url: str
    snippet: str
    site_name: str
    date: str | None = None

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> SearchResult:
        return cls(
            position=int(d.get("position", 0)),
            title=d.get("title") or "",
            url=d.get("url") or "",
            snippet=d.get("snippet") or "",
            site_name=d.get("site_name") or "",
            date=d.get("date"),
        )


@dataclass
class FetchResult:
    url: str
    final_url: str
    title: str | None
    description: str | None
    language: str | None
    author: str | None
    published_date: str | None
    text: str | None
    links: list[str] = field(default_factory=list)
    image_links: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> FetchResult:
        return cls(
            url=d.get("url") or "",
            final_url=d.get("final_url") or "",
            title=d.get("title"),
            description=d.get("description"),
            language=d.get("language"),
            author=d.get("author"),
            published_date=d.get("published_date"),
            text=d.get("text"),
            links=[str(x) for x in (d.get("links") or [])],
            image_links=[str(x) for x in (d.get("image_links") or [])],
        )


@dataclass
class AgentResult:
    status: str
    result: dict[str, Any]
    steps: int | None = None
    error: str | None = None

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> AgentResult:
        err = d.get("error")
        err_str = None
        if isinstance(err, dict):
            err_str = str(err.get("message") or err)
        elif err is not None:
            err_str = str(err)
        result = d.get("result")
        return cls(
            status=str(d.get("status") or ""),
            result=result if isinstance(result, dict) else {},
            steps=d.get("num_of_steps"),
            error=err_str,
        )


def _api_key() -> str:
    key = os.environ.get("TINYFISH_API_KEY", "").strip()
    if not key:
        raise TinyFishError(
            "TINYFISH_API_KEY is not set. Export it (never commit it): export TINYFISH_API_KEY=your-key"
        )
    return key


def _retry(fn_desc: str, fn: Any, attempts: int = 3) -> Any:
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except TinyFishError:
            raise
        except (httpx.HTTPError, OSError) as exc:
            last_exc = exc
            if attempt < attempts - 1:
                time.sleep(1.5 * (attempt + 1))
    raise TinyFishError(f"{fn_desc} failed after retries: {last_exc}") from last_exc


def search(
    query: str,
    *,
    purpose: str | None = None,
    location: str | None = None,
    language: str | None = None,
    include_domains: str | None = None,
    timeout: float = 30.0,
) -> list[SearchResult]:
    """TinyFish Search: ranked, rank-stable web results built for agents."""
    params: dict[str, str] = {"query": query}
    if purpose:
        params["purpose"] = purpose
    if location:
        params["location"] = location
    if language:
        params["language"] = language
    if include_domains:
        params["include_domains"] = include_domains
    headers = {"X-API-Key": _api_key()}

    def do() -> Any:
        resp = httpx.get(SEARCH_URL, params=params, headers=headers, timeout=timeout)
        if resp.status_code == 429:
            raise httpx.HTTPError("rate limited (429)")
        if resp.status_code != 200:
            raise TinyFishError(f"Search API HTTP {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    data = _retry("TinyFish Search", do)
    return [SearchResult.from_api(r) for r in (data.get("results") or [])]


def fetch(
    urls: list[str],
    *,
    fmt: str = "markdown",
    links: bool = False,
    image_links: bool = False,
    purpose: str | None = None,
    ttl: int | None = 0,
    timeout: float = 60.0,
) -> tuple[list[FetchResult], list[dict[str, Any]]]:
    """TinyFish Fetch: full-browser render -> clean extracted content per URL.

    ttl=0 forces a live fetch (audits must reflect the page as it is now).
    Returns (successful results, per-URL errors).
    """
    body: dict[str, Any] = {"urls": urls[:10], "format": fmt, "links": links, "image_links": image_links}
    if purpose:
        body["purpose"] = purpose
    if ttl is not None:
        body["ttl"] = ttl
    headers = {"X-API-Key": _api_key(), "Content-Type": "application/json"}

    def do() -> Any:
        resp = httpx.post(FETCH_URL, json=body, headers=headers, timeout=timeout)
        if resp.status_code == 429:
            raise httpx.HTTPError("rate limited (429)")
        if resp.status_code != 200:
            raise TinyFishError(f"Fetch API HTTP {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    data = _retry("TinyFish Fetch", do)
    results = [FetchResult.from_api(r) for r in (data.get("results") or [])]
    errors = [e for e in (data.get("errors") or []) if isinstance(e, dict)]
    return results, errors


def agent_run(
    url: str,
    goal: str,
    *,
    output_schema: dict[str, Any] | None = None,
    timeout: float = 300.0,
) -> AgentResult:
    """TinyFish Agent: one goal-driven browser run (metered) with structured output."""
    body: dict[str, Any] = {"url": url, "goal": goal}
    if output_schema is not None:
        body["output_schema"] = output_schema
    headers = {"X-API-Key": _api_key(), "Content-Type": "application/json"}

    def do() -> Any:
        resp = httpx.post(AGENT_URL, json=body, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            raise TinyFishError(f"Agent API HTTP {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    data = _retry("TinyFish Agent", do)
    return AgentResult.from_api(data)


def result_to_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
