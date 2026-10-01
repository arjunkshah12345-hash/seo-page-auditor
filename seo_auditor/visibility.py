"""Search-visibility probes via TinyFish Search.

Answers the visibility half of the audit with live, rank-stable search results:
  * does the page appear for the target query, and at what position?
  * who outranks it (the exact competitor pages an owner will recognize)?
  * is the brand navigational query covered ("tinyfish" -> tinyfish.ai)?
  * does the search snippet match what the page actually says?

All searches run through TinyFish Search with the audit `purpose` attached.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from . import tinyfish_client as tf

# Two-label public suffixes we treat as one "registrable" suffix.
_TWO_PART_SUFFIXES = {
    "co.uk",
    "org.uk",
    "ac.uk",
    "com.au",
    "net.au",
    "co.jp",
    "com.br",
    "co.in",
    "com.mx",
    "co.nz",
    "com.sg",
    "com.tr",
    "co.za",
    "com.cn",
    "co.kr",
}


@dataclass
class VariantProbe:
    query: str
    total_results: int = 0
    page_rank: int | None = None
    page_entry_title: str | None = None
    page_entry_snippet: str | None = None
    top_results: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class VisibilityReport:
    url: str
    target_query: str | None
    domain: str = ""
    registrable_domain: str = ""
    brand: str = ""
    probes: list[VariantProbe] = field(default_factory=list)
    exact_rank: int | None = None
    exact_snippet: str | None = None
    competitors: list[dict[str, Any]] = field(default_factory=list)
    brand_rank: int | None = None  # this exact page, brand query
    brand_site_rank: int | None = None  # any page of this registrable domain, brand query
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def registrable_domain(host: str) -> str:
    host = host.lower().removeprefix("www.")
    labels = host.split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in _TWO_PART_SUFFIXES:
        return ".".join(labels[-3:])
    if len(labels) >= 2:
        return ".".join(labels[-2:])
    return host


_MIN_BRAND_TOKEN_LEN = 5


def _brand_token(host: str) -> str:
    """The brand token a searcher would type: first host label.

    TLD-ish labels (de, io, com via subdomains), version tokens and short
    fragments are not brands — searching "de" or "v2" is meaningless, so the
    brand probe is skipped entirely rather than producing a false
    'site not found for brand query' finding.
    """
    host = host.lower().removeprefix("www.")
    token = host.split(".")[0]
    if len(token) < _MIN_BRAND_TOKEN_LEN or not token.isalpha():
        return ""
    return token


def _url_identity(url: str) -> tuple[str, str]:
    parts = urlsplit(url)
    host = (parts.netloc or "").lower().removeprefix("www.")
    path = (parts.path or "").rstrip("/")
    return host, path


def _matches_page(result_url: str, page_url: str) -> bool | None:
    """True if result URL is the audited page (same host+path). None-ish False otherwise."""
    return _url_identity(result_url) == _url_identity(page_url)


def _same_site(result_url: str, page_registrable: str) -> bool:
    host = (urlsplit(result_url).netloc or "").lower().removeprefix("www.")
    return registrable_domain(host) == page_registrable


def _slug_words(url: str) -> list[str]:
    path = urlsplit(url).path or ""
    tail = [seg for seg in path.split("/") if seg][-1:]
    if not tail:
        return []
    words = [w for w in re.split(r"[-_.]+", tail[0]) if w.isalpha() and len(w) > 2]
    return words[:6]


def run_visibility(
    url: str,
    target_query: str | None,
    *,
    page_title: str | None = None,
    location: str | None = None,
    language: str | None = None,
) -> VisibilityReport:
    """Run 2-3 live TinyFish searches and report rank/competitors/snippet."""
    parts = urlsplit(url)
    host = (parts.netloc or "").lower()
    rep = VisibilityReport(url=url, target_query=target_query)
    rep.domain = host
    rep.registrable_domain = registrable_domain(host)
    rep.brand = _brand_token(host)

    variants: list[str] = []
    if target_query:
        variants.append(target_query)
        if rep.brand and rep.brand not in target_query.lower():
            variants.append(f"{target_query} {rep.brand}")
    else:
        slug = " ".join(_slug_words(url))
        base = page_title or slug or rep.brand
        if rep.brand:
            variants.append(base if rep.brand in base.lower() else f"{base} {rep.brand}")
        else:
            variants.append(base)
    if rep.brand:
        variants.append(rep.brand)  # navigational / brand probe

    seen_queries: set[str] = set()
    for i, q in enumerate(variants):
        if q.lower() in seen_queries:
            continue
        seen_queries.add(q.lower())
        probe = VariantProbe(query=q)
        try:
            results = tf.search(q, purpose=tf.AUDIT_PURPOSE, location=location, language=language)
        except tf.TinyFishError as exc:
            rep.notes.append(f"search '{q}' failed: {exc}")
            continue
        probe.total_results = len(results)
        probe.top_results = [
            {
                "position": r.position,
                "title": r.title,
                "url": r.url,
                "site_name": r.site_name,
                "snippet": r.snippet,
            }
            for r in results[:10]
        ]
        for r in results:
            if _matches_page(r.url, url):
                probe.page_rank = r.position
                probe.page_entry_title = r.title
                probe.page_entry_snippet = r.snippet
                break
        rep.probes.append(probe)

        if i == 0:
            rep.exact_rank = probe.page_rank
            rep.exact_snippet = probe.page_entry_snippet
            rep.competitors = [
                tr for tr in probe.top_results if not _same_site(tr["url"], rep.registrable_domain)
            ][:5]
        if probe.query == rep.brand:
            rep.brand_rank = probe.page_rank
            for r in results:
                if _same_site(r.url, rep.registrable_domain):
                    rep.brand_site_rank = r.position
                    break

    if target_query and rep.exact_rank is None:
        rep.notes.append(
            "Page did not appear in the first page (top 10) of TinyFish results for the exact query."
        )
    return rep


@dataclass
class CompetitorGap:
    url: str
    position: int
    title: str
    benchmark: dict[str, Any]  # {words, h2, has_faq_schema}

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def collect_content_gaps(
    rep: VisibilityReport,
    *,
    max_competitors: int = 2,
) -> list[CompetitorGap]:
    """Fetch the pages outranking the audited page (live, TinyFish Fetch) and
    benchmark their extracted depth against it.

    Uses the same markdown-format fetch as the audit's own readability probe so
    the numbers are directly comparable. Failures degrade silently: a competitor
    that cannot be fetched simply contributes no benchmark.
    """
    probe = next((p for p in rep.probes if p.query == rep.target_query), None)
    if probe is None:
        return []
    rankers = [t for t in probe.top_results if not _same_site(t["url"], rep.registrable_domain)]
    rankers = [t for t in rankers if t["position"] < (probe.page_rank or 99)][:max_competitors]
    if not rankers:
        return []

    urls = [t["url"] for t in rankers]
    results, _errors = tf.fetch(urls, fmt="markdown", purpose=tf.AUDIT_PURPOSE, ttl=0)
    by_url = {r.url: r for r in results}
    gaps: list[CompetitorGap] = []
    for t in rankers:
        r = by_url.get(t["url"])
        if r is None or not r.text:
            continue
        md = r.text
        gaps.append(
            CompetitorGap(
                url=t["url"],
                position=t["position"],
                title=t["title"],
                benchmark={
                    "words": len(_md_words(md)),
                    "h2": sum(
                        1
                        for ln in md.splitlines()
                        if ln.lstrip().startswith("## ") and not ln.lstrip().startswith("### ")
                    ),
                    "has_faq_schema": False,  # markdown probe cannot see head JSON-LD
                },
            )
        )
    return gaps


def _md_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z'-]+", text)
