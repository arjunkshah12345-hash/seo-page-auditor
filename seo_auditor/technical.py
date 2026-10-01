"""Origin-side technical checks: raw HTML head signals, robots.txt, llms.txt.

TinyFish Fetch deliberately strips the <head> (it IS the extraction view); but
search crawlers and AI crawlers consume the raw HTML. We fetch origin HTML plus
robots.txt and llms.txt directly to measure the machine-readable signals that
decide whether AI crawlers and answer engines can see the page at all — and
whether they are *told* to stay away.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
_UA_HONEST = "TinyFishAuditBot/1.0 (AI search & readability audit)"
_TIMEOUT = 20.0
# Statuses that usually mean "UA gated" rather than "page gone": retry with an
# honest bot UA before reporting the page as unreachable (Wikipedia and many
# Cloudflare-fronted sites 403 generic browser strings but serve honest bots).
_UA_RETRY_STATUSES = {401, 403, 406, 418, 429}

# AI crawlers that decide whether answer engines ever see the site.
AI_CRAWLERS = [
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "ClaudeBot",
    "Claude-Web",
    "anthropic-ai",
    "PerplexityBot",
    "Google-Extended",
    "Bytespider",
    "CCBot",
    "Applebot-Extended",
    "meta-externalagent",
]

SEARCH_CRAWLERS = ["Googlebot", "Bingbot"]

# Regex patterns, single-quoted so no quote-escaping is needed.
_P_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_P_META_TAG = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
_P_META_NAME = re.compile(r"(?:name|property)=[\"']([^\"']+)[\"']", re.IGNORECASE)
_P_META_CONTENT = re.compile(r"content=(\"([^\"]*)\"|'([^']*)')", re.IGNORECASE | re.DOTALL)
_P_CANONICAL_TAG = re.compile(r"<link[^>]+rel=[\"']canonical[\"'][^>]*>", re.IGNORECASE)
_P_HREF = re.compile(r"href=[\"']([^\"']+)[\"']", re.IGNORECASE)
_P_HREFLANG = re.compile(r"hreflang=", re.IGNORECASE)
_P_H1 = re.compile(r"<h1\b", re.IGNORECASE)
_P_H2 = re.compile(r"<h2\b", re.IGNORECASE)
_P_IMG = re.compile(r"<img\b", re.IGNORECASE)
_P_IMG_NO_ALT = re.compile(r"<img(?![^>]*\balt=)[^>]*>", re.IGNORECASE)
_P_CONTENT_TAG = re.compile(r"<(p|h[1-6]|li|td|blockquote|pre)\b", re.IGNORECASE)
_P_JSONLD = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
_P_SITEMAP = re.compile(r"^\s*sitemap:\s*(\S+)", re.IGNORECASE | re.MULTILINE)


@dataclass
class RobotsReport:
    exists: bool = False
    status: int | None = None
    ai_blocked: list[str] = field(default_factory=list)
    ai_allowed: list[str] = field(default_factory=list)
    search_blocked: list[str] = field(default_factory=list)
    sitemap_urls: list[str] = field(default_factory=list)
    raw_excerpts: dict[str, str] = field(default_factory=dict)  # ua -> matching rules

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class LlmsTxtReport:
    exists: bool = False
    status: int | None = None
    url: str | None = None
    bytes: int = 0
    sections: int = 0
    links: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class HeadReport:
    status: int | None = None
    final_url: str | None = None
    html_bytes: int = 0
    title: str | None = None
    title_len: int = 0
    meta_description: str | None = None
    meta_description_len: int = 0
    canonical: str | None = None
    robots_meta: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None
    jsonld_types: list[str] = field(default_factory=list)
    jsonld_parse_error: str | None = None
    jsonld_blocks: int = 0
    h1_count: int = 0
    h2_count: int = 0
    img_count: int = 0
    img_missing_alt: int = 0
    hreflang_count: int = 0
    raw_content_tags: int = 0  # <p>/<h1-6>/<li>/<td>… in RAW server HTML
    redirect: bool = False
    content_type: str | None = None
    ua_retried: bool = False  # honest bot UA retry was attempted (served or still denied)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def _origin_parts(url: str) -> tuple[str, str]:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}", parts.path or "/"


def _get(url: str) -> httpx.Response:
    """GET with a browser-like UA; on UA-gate statuses retry with an honest bot UA.

    Wikipedia and several CDNs serve HTTP 403 to generic browser user-agent
    strings but happily serve descriptive bot UAs — exactly what a well-behaved
    crawler would send. The retry mirrors that before we report the page as
    blocked to every crawler.
    """
    resp = httpx.get(
        url,
        headers={"User-Agent": _UA, "Accept": "*/*"},
        timeout=_TIMEOUT,
        follow_redirects=True,
    )
    if resp.status_code in _UA_RETRY_STATUSES:
        resp._ua_retry_attempted = True  # type: ignore[attr-defined]
        try:
            alt = httpx.get(
                url,
                headers={"User-Agent": _UA_HONEST, "Accept": "*/*"},
                timeout=_TIMEOUT,
                follow_redirects=True,
            )
        except httpx.HTTPError:
            return resp
        if alt.status_code < resp.status_code:
            alt._ua_retry_attempted = True  # type: ignore[attr-defined]
            return alt
    return resp


# ---------------------------------------------------------------- raw HTML


def _extract_head_signals(html: str) -> dict[str, Any]:
    out: dict[str, Any] = {}

    m = _P_TITLE.search(html)
    title = m.group(1).strip() if m else None
    out["title"] = title
    out["title_len"] = len(title) if title else 0

    def _meta_content(name: str) -> str | None:
        for m in _P_META_TAG.finditer(html):
            tag = m.group(0)
            name_m = _P_META_NAME.search(tag)
            if not name_m or name_m.group(1).lower() != name.lower():
                continue
            c = _P_META_CONTENT.search(tag)
            if c:
                val = c.group(2) if c.group(2) is not None else c.group(3)
                return val.strip()
        return None

    out["meta_description"] = _meta_content("description")
    out["meta_description_len"] = len(out["meta_description"]) if out["meta_description"] else 0
    out["og_title"] = _meta_content("og:title")
    out["og_description"] = _meta_content("og:description")
    out["og_image"] = _meta_content("og:image")
    out["robots_meta"] = _meta_content("robots")

    out["canonical"] = None
    m = _P_CANONICAL_TAG.search(html)
    if m:
        c = _P_HREF.search(m.group(0))
        if c:
            out["canonical"] = c.group(1).strip()

    out["hreflang_count"] = len(_P_HREFLANG.findall(html))
    out["h1_count"] = len(_P_H1.findall(html))
    out["h2_count"] = len(_P_H2.findall(html))
    out["img_count"] = len(_P_IMG.findall(html))
    out["img_missing_alt"] = len(_P_IMG_NO_ALT.findall(html))
    out["raw_content_tags"] = len(_P_CONTENT_TAG.findall(html))

    # JSON-LD
    blocks = _P_JSONLD.findall(html)
    out["jsonld_blocks"] = len(blocks)
    types: list[str] = []
    parse_err: str | None = None
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError as exc:
            parse_err = str(exc)
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            if isinstance(t, list):
                types.extend(str(x) for x in t)
            elif t:
                types.append(str(t))
            graph = item.get("@graph")
            if isinstance(graph, list):
                for g in graph:
                    if isinstance(g, dict) and g.get("@type"):
                        gt = g["@type"]
                        if isinstance(gt, list):
                            types.extend(str(x) for x in gt)
                        else:
                            types.append(str(gt))
    out["jsonld_types"] = types
    out["jsonld_parse_error"] = parse_err
    return out


def probe_head(url: str) -> HeadReport:
    """Fetch raw origin HTML and extract head/technical signals."""
    rep = HeadReport()
    try:
        resp = _get(url)
    except httpx.HTTPError as exc:
        rep.status = 0
        rep.title = f"origin fetch failed: {exc}"
        return rep
    rep.status = resp.status_code
    rep.final_url = str(resp.url)
    rep.redirect = len(resp.history) > 0
    rep.content_type = resp.headers.get("content-type")
    rep.ua_retried = bool(getattr(resp, "_ua_retry_attempted", False))
    html = resp.text or ""
    rep.html_bytes = len(html.encode("utf-8", errors="replace"))
    if resp.status_code == 200 and html:
        signals = _extract_head_signals(html)
        for k, v in signals.items():
            setattr(rep, k, v)
    return rep


# ---------------------------------------------------------------- robots.txt


def _parse_robots(text: str, user_agents: list[str]) -> dict[str, dict[str, list[str]]]:
    """Return {ua_lower: {'allow': [...], 'disallow': [...]}} for requested UAs.

    Only UA-specific groups are captured here; callers merge the '*'
    (default) group themselves when a UA has no rules of its own.
    """
    wanted = {ua.lower() for ua in user_agents} | {"*"}
    rules: dict[str, dict[str, list[str]]] = {ua: {"allow": [], "disallow": []} for ua in wanted}
    current: set[str] = set()
    prev_was_ua = False
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "user-agent":
            ua = val.lower()
            if ua in rules:
                if not prev_was_ua:
                    current = set()  # rules intervened: start a new group
                current.add(ua)
            elif not prev_was_ua:
                current = set()
            prev_was_ua = True
            continue
        prev_was_ua = False
        if not current or key not in ("allow", "disallow") or not val:
            continue
        for ua in current:
            rules[ua][key].append(val)
    return rules


def _longest_match(paths: list[str], path: str) -> int:
    best = 0
    for p in paths:
        prefix = p.rstrip("*")
        if path.startswith(prefix):
            best = max(best, len(prefix))
    return best


def _ua_verdict(rules: dict[str, list[str]], path: str) -> bool:
    """True = allowed. Longest-match disallow/allow per robots spec."""
    dis = _longest_match(rules["disallow"], path)
    if dis == 0:
        return True
    allow = _longest_match(rules["allow"], path)
    return allow > dis


def probe_robots(url: str) -> RobotsReport:
    origin, path = _origin_parts(url)
    rep = RobotsReport()
    try:
        resp = _get(f"{origin}/robots.txt")
    except httpx.HTTPError:
        rep.status = 0
        return rep
    rep.status = resp.status_code
    if resp.status_code != 200 or not resp.text.strip():
        return rep
    rep.exists = True
    text = resp.text
    rep.sitemap_urls = _P_SITEMAP.findall(text)

    all_robots = _parse_robots(text, AI_CRAWLERS + SEARCH_CRAWLERS)
    star = all_robots["*"]

    def effective(ua: str) -> dict[str, list[str]]:
        specific = all_robots[ua.lower()]
        if specific["allow"] or specific["disallow"]:
            return specific
        return star

    for ua in AI_CRAWLERS:
        spec = all_robots[ua.lower()]
        if spec["allow"] or spec["disallow"]:
            rep.raw_excerpts[ua] = f"allow={spec['allow'][:3]} disallow={spec['disallow'][:3]}"
        if _ua_verdict(effective(ua), path):
            rep.ai_allowed.append(ua)
        else:
            rep.ai_blocked.append(ua)

    for ua in SEARCH_CRAWLERS:
        if not _ua_verdict(effective(ua), path):
            rep.search_blocked.append(ua)
    return rep


# ---------------------------------------------------------------- llms.txt


def probe_llms_txt(url: str) -> LlmsTxtReport:
    origin, _ = _origin_parts(url)
    rep = LlmsTxtReport()
    for candidate in (f"{origin}/llms.txt", f"{origin}/.well-known/llms.txt"):
        try:
            resp = _get(candidate)
        except httpx.HTTPError:
            continue
        if resp.status_code == 200 and resp.text.strip():
            text = resp.text
            rep.exists = True
            rep.status = 200
            rep.url = candidate
            rep.bytes = len(text.encode("utf-8", errors="replace"))
            rep.sections = len(re.findall(r"^#{1,3} ", text, re.MULTILINE))
            rep.links = len(re.findall(r"^\s*[-*] \[", text, re.MULTILINE))
            return rep
        if resp.status_code < 500:
            rep.status = resp.status_code
    return rep
