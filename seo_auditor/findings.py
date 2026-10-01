"""Findings engine: turns measured probes into specific, evidence-backed findings.

Design rule (from the bounty): every finding must cite the measured evidence and
give a fix concrete enough to act on the same day — exact tag to add, exact
robots.txt line to remove, exact schema JSON to paste. No generic SEO tips.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from .browser_probe import BrowserReport
from .readability import ReadabilityReport
from .technical import HeadReport, LlmsTxtReport, RobotsReport
from .visibility import VisibilityReport


class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}


@dataclass
class Finding:
    id: str
    severity: str
    area: str  # readability | access | visibility | structure | authority
    title: str
    evidence: str
    fix: str
    source: str  # which TinyFish endpoint / probe produced it

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


# ------------------------------------------------------------------ helpers

_WORDS = re.compile(r"[a-zA-Z][a-zA-Z'-]+")

_STOP = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "to",
        "was",
        "were",
        "will",
        "with",
        "you",
        "your",
        "we",
        "our",
        "us",
        "can",
        "do",
        "does",
        "how",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "not",
        "no",
        "yes",
        "all",
        "any",
        "more",
        "most",
        "other",
        "some",
        "such",
        "than",
        "only",
        "own",
        "same",
        "so",
        "too",
        "very",
        "just",
        "also",
        "about",
    ]
)


def _tokens(text: str) -> set[str]:
    return {w for w in (m.group(0).lower() for m in _WORDS.finditer(text)) if w not in _STOP}


def _overlap_ratio(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _quote(s: str, limit: int = 140) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= limit else s[: limit - 1] + "…"


# ------------------------------------------------------------------ fetch / readability


def findings_from_readability(rep: ReadabilityReport) -> list[Finding]:
    out: list[Finding] = []

    if rep.errors and rep.md_chars == 0:
        # Fetch got nothing at all: mark the report empty so scoring/projection see
        # the same "no content" state an empty page would produce.
        rep.looks_empty = True
        out.append(
            Finding(
                id="fetch-failed",
                severity=Severity.CRITICAL,
                area="readability",
                title="AI fetchers cannot extract this page",
                evidence=(
                    f"TinyFish Fetch returned no content ({'; '.join(rep.errors)}). Any AI tool "
                    "that fetches this URL gets nothing to reason on."
                ),
                fix=(
                    "Check the URL returns 200 for non-browser clients (curl -I <url>), remove bot-walls "
                    "for known AI crawler user agents, and make sure the page does not require cookies "
                    "or a session to render content."
                ),
                source="TinyFish Fetch",
            )
        )
        return out

    if rep.looks_empty:
        out.append(
            Finding(
                id="empty-extraction",
                severity=Severity.CRITICAL,
                area="readability",
                title="Extraction sees almost no content",
                evidence=(
                    f"TinyFish Fetch extracted only {rep.md_words} words "
                    f"({rep.md_chars} chars) from the rendered page. An AI assistant fed this page "
                    "cannot answer questions about it."
                ),
                fix=(
                    "Put the substantive page content into server-rendered HTML (SSR/SSG) instead of "
                    "client-side JS injection, and verify with: curl -s <url> | python3 -c "
                    "'import sys,re;print(len(re.findall(r\"[A-Za-z]+\",sys.stdin.read())))'"
                ),
                source="TinyFish Fetch",
            )
        )
    elif rep.md_words < 300:
        out.append(
            Finding(
                id="thin-content",
                severity=Severity.MEDIUM,
                area="readability",
                title="Thin extracted content",
                evidence=f"TinyFish Fetch extracted {rep.md_words} words; answer engines favor pages with enough text to quote (300+).",
                fix=(
                    "Add substantive, quotable passages: a direct answer paragraph under the H1, "
                    "an FAQ block, and a summary list. Aim for content that answers the page's core "
                    "question in the first 100 words."
                ),
                source="TinyFish Fetch",
            )
        )

    if rep.looks_truncated:
        out.append(
            Finding(
                id="truncated-extraction",
                severity=Severity.MEDIUM,
                area="readability",
                title="Extraction looks cut off mid-content",
                evidence="The extracted markdown ends without terminal punctuation or with a trailing fragment, a typical sign of lazy-loaded or cut-off content.",
                fix="Make sure the full body renders without scroll-triggered loading; move paginated content onto one page or use real pagination links.",
                source="TinyFish Fetch",
            )
        )

    if rep.repeated_boilerplate_ratio > 0.25:
        out.append(
            Finding(
                id="boilerplate-heavy",
                severity=Severity.LOW,
                area="readability",
                title="Heavy repeated boilerplate in extraction",
                evidence=f"{rep.repeated_boilerplate_ratio:.0%} of extracted lines repeat 3+ times (nav/footer/promo residue) — this dilutes the content an AI quotes.",
                fix="Wrap navigation and repeated promo blocks in <nav>/<footer> or remove them from the content area so extractors can drop them.",
                source="TinyFish Fetch",
            )
        )

    # Metadata (Fetch prefers og:title over <title>)
    title = rep.title or ""
    if not title:
        out.append(
            Finding(
                id="missing-title",
                severity=Severity.HIGH,
                area="visibility",
                title="No title detected",
                evidence="Neither <title> nor og:title is present on the page — search engines and AI answer engines have nothing to show for this page.",
                fix='Add to <head>: <title>Primary Keyword — Brand</title> and <meta property="og:title" content="…"> with the same text.',
                source="TinyFish Fetch",
            )
        )
    elif not (20 <= len(title) <= 70):
        out.append(
            Finding(
                id="weak-title",
                severity=Severity.MEDIUM,
                area="visibility",
                title="Title length outside the display window",
                evidence=f"Title is {len(title)} chars: “{_quote(title)}”. Search snippets truncate around 60 chars.",
                fix="Rewrite to 50–60 chars, front-load the primary keyword, keep the brand suffix: e.g. “<Primary Keyword> — <Brand>”.",
                source="TinyFish Fetch",
            )
        )

    desc = rep.description or ""
    if not desc:
        out.append(
            Finding(
                id="missing-description",
                severity=Severity.HIGH,
                area="visibility",
                title="No meta description / og:description",
                evidence="Fetch found no description — search engines will improvise snippets and AI answer engines lose the page's self-description.",
                fix='Add to <head>: <meta name="description" content="One sentence (140–160 chars) stating what this page answers, including the primary keyword."> and mirror it in og:description.',
                source="TinyFish Fetch",
            )
        )
    elif not (70 <= len(desc) <= 200):
        out.append(
            Finding(
                id="weak-description",
                severity=Severity.LOW,
                area="visibility",
                title="Meta description length off the display window",
                evidence=f"Description is {len(desc)} chars (ideal 140–160): “{_quote(desc)}”.",
                fix="Rewrite to 140–160 chars: what the page answers + one differentiator + a verb.",
                source="TinyFish Fetch",
            )
        )

    # Structure
    if rep.h1_count == 0 and not rep.looks_empty:
        out.append(
            Finding(
                id="no-h1",
                severity=Severity.MEDIUM,
                area="structure",
                title="No H1 survives extraction",
                evidence="The extracted HTML contains no <h1> — answer engines use it to anchor what the page is about.",
                fix="Make the page headline an <h1> containing the primary keyword, exactly once.",
                source="TinyFish Fetch",
            )
        )
    elif rep.h1_count > 1:
        out.append(
            Finding(
                id="multi-h1",
                severity=Severity.LOW,
                area="structure",
                title=f"{rep.h1_count} H1 tags on one page",
                evidence=f"Extraction found {rep.h1_count} <h1> elements; a single H1 makes the page topic unambiguous.",
                fix="Demote all but the main headline to <h2>.",
                source="TinyFish Fetch",
            )
        )

    if rep.md_words >= 300 and rep.h2_count == 0:
        out.append(
            Finding(
                id="flat-structure",
                severity=Severity.MEDIUM,
                area="structure",
                title="Long page with zero H2 sections",
                evidence=f"{rep.md_words} words but no <h2> anywhere in the extracted HTML — answer engines chunk pages by headings when citing sources.",
                fix="Split the content into 3–6 sections with descriptive <h2> headings phrased as the questions users ask.",
                source="TinyFish Fetch",
            )
        )

    if not rep.semantic_tags and rep.h2_count == 0 and not rep.looks_empty:
        out.append(
            Finding(
                id="no-semantic-structure",
                severity=Severity.LOW,
                area="structure",
                title="No semantic landmarks in extracted HTML",
                evidence="No <main>/<article>/<section> elements survive extraction — everything is generic containers, so extractors must guess what is content.",
                fix="Wrap the primary content in <main><article>…</article></main> and each section in <section>.",
                source="TinyFish Fetch",
            )
        )

    if rep.author is None and rep.published_date is None:
        out.append(
            Finding(
                id="no-authorship",
                severity=Severity.LOW,
                area="authority",
                title="No author or date metadata",
                evidence="Fetch found no author and no published date — AI answer engines weight provenance when choosing sources to cite.",
                fix='Add author byline markup: <meta name="author" content="…">, a visible byline, and datePublished/author in JSON-LD.',
                source="TinyFish Fetch",
            )
        )

    # ---- GEO signals: what answer engines like to quote
    if rep.md_words >= 300 and rep.stat_sentences == 0:
        out.append(
            Finding(
                id="no-quotable-stats",
                severity=Severity.LOW,
                area="authority",
                title="No quotable statistics on the page",
                evidence=f"{rep.md_words} words extracted, but not one sentence contains a concrete number or stat (counts, percentages, timings). Answer engines disproportionately cite passages with verifiable figures.",
                fix="Add 2–3 concrete, sourced numbers to the body (e.g. 'cut p95 latency from 40s to 12s across 1,200 runs') near the top of the page.",
                source="TinyFish Fetch",
            )
        )

    if rep.md_words >= 500 and rep.h2_count >= 3 and not rep.question_headings:
        out.append(
            Finding(
                id="no-question-headings",
                severity=Severity.LOW,
                area="structure",
                title="No question-phrased headings",
                evidence=f"{rep.h2_count} H2 sections, none phrased as a question (Who/What/How/…?). Answer engines chunk pages by headings and match them to user questions when deciding what to cite.",
                fix="Rephrase 2–3 H2s as the questions users actually type (e.g. 'How much does … cost?'), and answer each in its first paragraph.",
                source="TinyFish Fetch",
            )
        )

    if rep.longest_paragraph_words > 160:
        out.append(
            Finding(
                id="wall-of-text",
                severity=Severity.LOW,
                area="readability",
                title="Paragraphs too long to quote cleanly",
                evidence=f"Longest extracted paragraph is {rep.longest_paragraph_words} words. Answer engines lift short, self-contained passages; a 160+-word paragraph rarely survives citation intact.",
                fix="Break paragraphs at ~75 words; put the key claim in the first sentence of each paragraph so it can be quoted standalone.",
                source="TinyFish Fetch",
            )
        )

    return out


# ------------------------------------------------------------------ competitor content gap


def findings_content_gap(
    visibility: VisibilityReport,
    readability: ReadabilityReport,
    head: HeadReport,
    gaps: list[dict[str, Any]],
) -> list[Finding]:
    """Benchmark the page against the pages outranking it (fetched live via TinyFish Fetch)."""
    if not gaps:
        return []
    b = gaps[0]["benchmark"]
    rankers = ", ".join(g["url"] for g in gaps)
    out: list[Finding] = []

    word_ratio = (readability.md_words / b["words"]) if b["words"] else 1.0
    h2_ratio = (readability.h2_count / b["h2"]) if b["h2"] else 1.0

    if word_ratio < 0.5 and (b["words"] - readability.md_words) > 200:
        out.append(
            Finding(
                id="content-depth-gap",
                severity=Severity.MEDIUM,
                area="visibility",
                title="Materially thinner than the pages outranking it",
                evidence=(
                    f"Pages above it for '{visibility.target_query}' carry {b['words']:,} words and {b['h2']} H2 sections "
                    f"(median of the top {len(gaps)} fetched live: {rankers}); this page extracts {readability.md_words:,} words "
                    f"and {readability.h2_count} H2s. Depth is a proxy for answer completeness."
                ),
                fix=(
                    f"Add roughly {max(200, b['words'] - readability.md_words):,} words covering the sub-questions the leaders "
                    f"answer in their {b['h2']} sections — and ship an FAQ block; pages with FAQPage schema are "
                    "disproportionately lifted into AI answers."
                ),
                source="TinyFish Search + Fetch (competitor benchmark)",
            )
        )
    elif h2_ratio < 0.5 and b["h2"] >= 4:
        out.append(
            Finding(
                id="content-depth-gap",
                severity=Severity.LOW,
                area="visibility",
                title="Fewer content sections than the pages outranking it",
                evidence=(
                    f"The top-ranked pages for '{visibility.target_query}' average {b['h2']} H2 sections; this page has "
                    f"{readability.h2_count}. Sections are how answer engines chunk and cite a page."
                ),
                fix=f"Split the content into ~{b['h2']} question-titled H2 sections, each answerable standalone.",
                source="TinyFish Search + Fetch (competitor benchmark)",
            )
        )
    return out


# ------------------------------------------------------------------ origin / technical


def _jsonld_template(head: HeadReport, registrable: str) -> str:
    org = json.dumps(registrable)
    page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": (head.title or "Page title")[:110],
        "description": (head.meta_description or "")[:290] or "One-sentence page description",
        "url": head.final_url or "",
        "isPartOf": {"@type": "WebSite", "name": registrable, "url": f"https://{registrable}"},
        "publisher": {"@type": "Organization", "name": registrable},
    }
    body = json.dumps(page, indent=2, ensure_ascii=False)
    return (
        "Add this JSON-LD block inside <head> (pre-filled with this page's own data):\n"
        f'<script type="application/ld+json">\n{body}\n</script>\n'
        f"If the page is an article/product, change @type accordingly (Article, Product, …) and add "
        f"sameAs links to the {org} social profiles."
    )


def findings_from_technical(
    head: HeadReport,
    robots: RobotsReport,
    llms: LlmsTxtReport,
    readability: ReadabilityReport,
    registrable: str,
) -> list[Finding]:
    out: list[Finding] = []

    if head.status is None or head.status == 0:
        out.append(
            Finding(
                id="origin-unreachable",
                severity=Severity.CRITICAL,
                area="access",
                title="Origin page could not be retrieved",
                evidence="Direct HTTP fetch of the URL failed (network/DNS/timeout) — neither search nor AI crawlers can index it.",
                fix="Verify the URL resolves publicly (no VPN/firewall gating) and returns 200 within a few seconds.",
                source="origin HTTP",
            )
        )
        return out
    if head.status != 200:
        gated = head.ua_retried
        out.append(
            Finding(
                id="origin-non-200",
                severity=Severity.CRITICAL,
                area="access",
                title=f"Origin returns HTTP {head.status}",
                evidence=(
                    f"GET {head.final_url or 'the URL'} → HTTP {head.status}. Crawlers that receive "
                    "this status drop the page from indexing."
                    + (
                        " The status persisted for an honest crawler user-agent too — deliberate bot gating, not a header quirk."
                        if gated
                        else ""
                    )
                ),
                fix=(
                    "Whitelist the user agents AI crawlers use (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, …) "
                    "at your CDN/edge or WAF, and make sure bot-protection rules don't challenge non-browser clients."
                    if gated
                    else f"Resolve the {head.status}: fix the broken route or 301-redirect it to the live equivalent page (and update internal links to point at the new URL)."
                ),
                source="origin HTTP",
            )
        )
    elif head.redirect:
        out.append(
            Finding(
                id="redirect-chain",
                severity=Severity.LOW,
                area="access",
                title="URL redirects before serving content",
                evidence=f"Requested URL redirects to {head.final_url}. Each hop loses a little crawl equity and slows AI fetchers.",
                fix="Point internal links and sitemap entries directly at the final URL and keep a single 301 hop.",
                source="origin HTTP",
            )
        )

    is_pdf = bool(head.content_type and "application/pdf" in head.content_type.lower())
    head_ok = head.status == 200 and not is_pdf

    if is_pdf:
        out.append(
            Finding(
                id="pdf-content",
                severity=Severity.CRITICAL,
                area="readability",
                title="Page is a PDF — AI tools read it poorly or not at all",
                evidence=(
                    f"Origin serves Content-Type: {head.content_type}. Some answer engines skip PDFs entirely, "
                    "and those that parse them extract flat text with no headings, links, or structure."
                ),
                fix=(
                    "Publish an HTML version of this document and link it prominently; keep the PDF as a download "
                    "alternative and make the HTML page the canonical URL."
                ),
                source="origin HTTP",
            )
        )
        return out

    if head_ok and head.ua_retried:
        out.append(
            Finding(
                id="origin-blocked-bot-ua",
                severity=Severity.MEDIUM,
                area="access",
                title="Origin gates generic browser user-agents",
                evidence=(
                    "The page returned an access-denied status to a browser user-agent and served content only to an "
                    "honest crawler UA. AI fetchers that send browser-like headers may be turned away even though "
                    "declared crawlers are allowed."
                ),
                fix=(
                    "If you gate user agents at the edge, allow-list the AI crawler UAs (GPTBot, ClaudeBot, "
                    "PerplexityBot, Google-Extended, …) and return 200 to generic clients for public pages."
                ),
                source="origin HTTP",
            )
        )

    # JS-only rendering: raw HTML carries almost no content tags while Fetch (a real
    # browser) extracted plenty — crawlers that don't execute JS see an empty shell.
    if (
        readability.md_words >= 100
        and head_ok
        and head.raw_content_tags < 10
        and readability.md_words > head.raw_content_tags * 10
    ):
        out.append(
            Finding(
                id="js-only-rendering",
                severity=Severity.CRITICAL,
                area="readability",
                title="Content only renders via JavaScript",
                evidence=(
                    f"Raw server HTML contains only {head.raw_content_tags} content tags (<p>/<h>/<li>), while "
                    f"TinyFish Fetch — a full browser — extracted {readability.md_words} words. Crawlers that "
                    "don't execute JS (and many AI fetchers) see an empty shell."
                ),
                fix="Serve the primary content in the initial HTML (SSR/SSG or pre-rendering). Verify: curl -s <url> | grep -c '<p' returns the real paragraph count.",
                source="origin HTTP + TinyFish Fetch",
            )
        )

    # Meta robots
    if head.robots_meta and "noindex" in head.robots_meta.lower():
        out.append(
            Finding(
                id="meta-noindex",
                severity=Severity.CRITICAL,
                area="access",
                title="Page is marked noindex",
                evidence=f'<meta name="robots" content="{_quote(head.robots_meta)}"> — search engines and AI indexes are explicitly told to exclude this page.',
                fix="Remove the noindex directive (and any X-Robots-Tag: noindex HTTP header) from this page, then request reindexing in Search Console.",
                source="origin HTTP",
            )
        )

    # Canonical
    if not head.canonical and head_ok:
        out.append(
            Finding(
                id="no-canonical",
                severity=Severity.LOW,
                area="structure",
                title="No canonical link",
                evidence='No <link rel="canonical"> in the raw HTML — duplicate URLs (params, trailing slashes) can split ranking signals.',
                fix=f'Add to <head>: <link rel="canonical" href="{head.final_url or "https://…"}">.',
                source="origin HTTP",
            )
        )
    elif head_ok and head.final_url and head.canonical:
        canon = head.canonical
        canon_abs = canon if canon.startswith("http") else f"https://{registrable}{canon}"
        if urlsplit(canon_abs.rstrip("/")).path != urlsplit(head.final_url.rstrip("/")).path:
            out.append(
                Finding(
                    id="canonical-mismatch",
                    severity=Severity.MEDIUM,
                    area="structure",
                    title="Canonical points at a different page",
                    evidence=f"This page declares canonical = {head.canonical} but serves at {head.final_url}. Ranking credit flows to the canonical URL, not this one.",
                    fix="If the canonical URL is the real one, consolidate this page into it (301). Otherwise update the canonical tag to this page's URL.",
                    source="origin HTTP",
                )
            )

    # JSON-LD
    if head.jsonld_blocks == 0 and head_ok:
        out.append(
            Finding(
                id="no-jsonld",
                severity=Severity.HIGH,
                area="structure",
                title="No structured data (JSON-LD)",
                evidence="Zero application/ld+json blocks in the raw HTML — answer engines and AI search rely on schema to classify and cite pages reliably.",
                fix=_jsonld_template(head, registrable),
                source="origin HTTP",
            )
        )
    else:
        if head.jsonld_parse_error:
            out.append(
                Finding(
                    id="jsonld-invalid",
                    severity=Severity.HIGH,
                    area="structure",
                    title="JSON-LD block fails to parse",
                    evidence=f"{head.jsonld_blocks} JSON-LD block(s) found, but at least one is invalid JSON ({head.jsonld_parse_error}). Invalid schema is ignored entirely.",
                    fix="Paste the block into a JSON linter and fix the syntax error; validate the result at validator.schema.org.",
                    source="origin HTTP",
                )
            )
        types = head.jsonld_types
        if types and not any(
            t
            in (
                "Article",
                "BlogPosting",
                "Product",
                "FAQPage",
                "HowTo",
                "WebPage",
                "Organization",
                "LocalBusiness",
            )
            for t in types
        ):
            out.append(
                Finding(
                    id="jsonld-thin",
                    severity=Severity.MEDIUM,
                    area="structure",
                    title="Structured data lacks a page-level type",
                    evidence=f"JSON-LD declares only {', '.join(sorted(set(types))[:5])} — no WebPage/Article/Product entity for the page itself.",
                    fix="Add a page-level @type (WebPage, Article, or Product) with name/description/url mirroring the visible content.",
                    source="origin HTTP",
                )
            )

    # Open Graph
    if head_ok and (not head.og_title or not head.og_description):
        out.append(
            Finding(
                id="missing-og",
                severity=Severity.LOW,
                area="visibility",
                title="Incomplete Open Graph tags",
                evidence=f"og:title={'present' if head.og_title else 'MISSING'}, og:description={'present' if head.og_description else 'MISSING'} — previews in social/chat surfaces (a growing AI-referral channel) render blank.",
                fix="Add og:title, og:description, og:image, og:url mirroring the <title> and meta description.",
                source="origin HTTP",
            )
        )

    # Images
    if head.img_count and head.img_missing_alt:
        pct = head.img_missing_alt / head.img_count
        if pct >= 0.2:
            out.append(
                Finding(
                    id="img-alt-missing",
                    severity=Severity.LOW,
                    area="structure",
                    title="Many images without alt text",
                    evidence=f"{head.img_missing_alt} of {head.img_count} images ({pct:.0%}) have no alt attribute — invisible to vision-free AI crawlers and image search.",
                    fix='Add descriptive alt text to content images (what the image shows, in context); mark decorative ones alt="".',
                    source="origin HTTP",
                )
            )

    # robots.txt
    if robots.status == 0:
        out.append(
            Finding(
                id="robots-unreachable",
                severity=Severity.MEDIUM,
                area="access",
                title="robots.txt could not be retrieved",
                evidence="GET /robots.txt failed — some crawlers treat repeated failures as a signal to crawl less.",
                fix="Serve a robots.txt (even minimal) at the domain root with a Sitemap: line.",
                source="origin HTTP",
            )
        )
    elif not robots.exists:
        out.append(
            Finding(
                id="robots-missing",
                severity=Severity.MEDIUM,
                area="access",
                title="No robots.txt",
                evidence=f"GET /robots.txt returned HTTP {robots.status}. Crawlers default to full access, but you also lose the channel to declare AI policy and sitemaps.",
                fix=(
                    "Create robots.txt at the domain root:\n"
                    "```\nUser-agent: *\nAllow: /\n\nSitemap: https://"
                    f"{registrable}/sitemap.xml\n```"
                ),
                source="origin HTTP",
            )
        )
    else:
        if robots.ai_blocked:
            names = ", ".join(robots.ai_blocked)
            lines = "\n".join(robots.raw_excerpts.get(ua, "") for ua in robots.ai_blocked[:3])
            out.append(
                Finding(
                    id="robots-blocks-ai",
                    severity=Severity.HIGH if len(robots.ai_blocked) < 5 else Severity.CRITICAL,
                    area="access",
                    title=f"robots.txt blocks AI crawlers: {names}",
                    evidence=(
                        f"robots.txt disallows this path for {names}. Those systems will never see the page, "
                        f"so AI answer engines cannot cite or recommend it. Matching rules: {lines}"
                    ),
                    fix=(
                        "Edit robots.txt and remove/replace the Disallow rules for these user agents on this "
                        "path. To allow all AI crawlers explicitly:\n```\n"
                        + "\n".join(f"User-agent: {ua}\nAllow: /" for ua in robots.ai_blocked[:5])
                        + "\n```"
                    ),
                    source="origin HTTP",
                )
            )
        if not robots.sitemap_urls:
            out.append(
                Finding(
                    id="no-sitemap-declared",
                    severity=Severity.MEDIUM,
                    area="access",
                    title="robots.txt declares no sitemap",
                    evidence="No `Sitemap:` line in robots.txt — crawlers must discover URLs by links alone.",
                    fix=f"Add `Sitemap: https://{registrable}/sitemap.xml` to robots.txt (and make sure that sitemap exists and includes this URL).",
                    source="origin HTTP",
                )
            )

    # llms.txt — emerging discovery standard, framed as opportunity
    if not llms.exists:
        out.append(
            Finding(
                id="llms-txt-missing",
                severity=Severity.INFO,
                area="authority",
                title="No llms.txt (opportunity)",
                evidence="No /llms.txt found — the emerging convention AI tools use to fetch a curated, markdown map of a site.",
                fix=(
                    "Publish /llms.txt listing your key pages in markdown with one-line descriptions:\n"
                    "```\n# <Site name>\n\n> One-sentence what this site is.\n\n"
                    "## Pages\n- [This page](<url>): what it answers\n- [Docs](<url>): …\n```"
                ),
                source="origin HTTP",
            )
        )

    return out


# ------------------------------------------------------------------ search visibility


def findings_from_visibility(rep: VisibilityReport) -> list[Finding]:
    out: list[Finding] = []
    target = rep.target_query

    if target:
        exact = next((p for p in rep.probes if p.query == target), None)
        if exact is not None:
            if exact.page_rank is None:
                comp = ", ".join(f"{c['site_name']} (#{c['position']})" for c in rep.competitors[:4])
                out.append(
                    Finding(
                        id="not-ranked",
                        severity=Severity.HIGH,
                        area="visibility",
                        title=f"Not in top-10 for “{target}”",
                        evidence=(
                            f"TinyFish Search top-10 for “{target}” is dominated by: {comp or 'other domains'}. "
                            "This page does not appear — AI search engines inherit this ordering when citing sources."
                        ),
                        fix=(
                            f"Align the page to the query: put “{target}” (or a close variant) in the <title>, H1, "
                            "first paragraph and one H2; add an FAQ section answering the question behind the "
                            "query; then interlink to this page from your two highest-authority pages."
                        ),
                        source="TinyFish Search",
                    )
                )
            elif exact.page_rank > 3:
                out.append(
                    Finding(
                        id="low-rank",
                        severity=Severity.MEDIUM,
                        area="visibility",
                        title=f"Ranks #{exact.page_rank} for “{target}”",
                        evidence=(
                            f"Position {exact.page_rank} for the target query. AI answer engines draw "
                            "overwhelmingly from top-3 sources; snippet shown: “"
                            + _quote(exact.page_entry_snippet or "—")
                            + "”"
                        ),
                        fix="Improve on the pages above you: compare their titles/H1s and content depth, then expand this page's answer section and internal links to it.",
                        source="TinyFish Search",
                    )
                )
            else:
                out.append(
                    Finding(
                        id="ranked-top3",
                        severity=Severity.INFO,
                        area="visibility",
                        title=f"Ranks #{exact.page_rank} for “{target}”",
                        evidence=f"Strong: position {exact.page_rank} for the target query. Protect it.",
                        fix="Keep this page fresh (update stats/dates) and watch the competitors listed in the report.",
                        source="TinyFish Search",
                    )
                )

            # Query-term coverage in title
            if exact.page_rank is None or exact.page_rank > 3:
                title = rep.probes[0].page_entry_title or ""
                page_words = _tokens(target) - _tokens(rep.brand)
                missing = page_words - _tokens(f"{title} {rep.url}")
                if page_words and missing:
                    out.append(
                        Finding(
                            id="title-missing-query-terms",
                            severity=Severity.MEDIUM,
                            area="visibility",
                            title="Title/URL miss part of the target query",
                            evidence=f"Query terms absent from the page's title and URL: {', '.join(sorted(missing))}.",
                            fix=f"Work these terms into the <title> and H1 naturally (e.g. “… {', '.join(sorted(missing))} …”).",
                            source="TinyFish Search",
                        )
                    )

    brand_rank = rep.brand_rank
    brand_site_rank = getattr(rep, "brand_site_rank", None)
    if rep.brand and brand_rank is None and brand_site_rank is None:
        out.append(
            Finding(
                id="brand-not-found",
                severity=Severity.HIGH,
                area="authority",
                title=f"Site not found for brand query “{rep.brand}”",
                evidence=(
                    f"A search for the site's own brand token “{rep.brand}” surfaced no page from "
                    f"{rep.registrable_domain} in the top 10 — a sign of weak indexing or brand signals."
                ),
                fix=(
                    "Make sure the domain/brand string appears in the <title>, H1, JSON-LD Organization name, and "
                    "is linked from the homepage nav; submit the URL in Search Console."
                ),
                source="TinyFish Search",
            )
        )

    # Snippet vs page self-description
    exact = rep.probes[0] if rep.probes else None
    if exact and exact.page_entry_snippet:
        snippet = exact.page_entry_snippet
        # compare against fetch description if we have it via callers; here use title+snippet self-check only
        if target and _overlap_ratio(target, snippet) < 0.25:
            out.append(
                Finding(
                    id="snippet-offtopic",
                    severity=Severity.LOW,
                    area="visibility",
                    title="Search snippet barely matches the query",
                    evidence=f"Snippet shown for “{target}”: “{_quote(snippet)}” — little term overlap with the query, so engines may be improvising this page's description.",
                    fix="Rewrite the meta description to answer the query directly; search engines often adopt a well-written description verbatim.",
                    source="TinyFish Search",
                )
            )

    return out


# ------------------------------------------------------------------ browser (agent)


def findings_from_browser(rep: BrowserReport) -> list[Finding]:
    out: list[Finding] = []
    if not rep.attempted:
        return out
    if rep.run_error:
        out.append(
            Finding(
                id="agent-run-failed",
                severity=Severity.MEDIUM,
                area="readability",
                title="Browser probe could not complete",
                evidence=f"TinyFish Agent run failed: {rep.run_error}",
                fix="Retry later; if it recurs while Fetch works, the page may be blocking automated browsers — check for anti-bot interstitials.",
                source="TinyFish Agent",
            )
        )
        return out

    if rep.understood is False:
        out.append(
            Finding(
                id="agent-not-understood",
                severity=Severity.HIGH,
                area="readability",
                title="A browsing AI could not tell what the page is about",
                evidence=f"After opening the page in a real browser, the agent reported: {rep.summary or 'no coherent summary possible'}.",
                fix="State the page's purpose in the first screen: clear H1, one-sentence subtitle, and remove interstitials that push content below the fold.",
                source="TinyFish Agent",
            )
        )
    elif rep.understood and rep.summary:
        out.append(
            Finding(
                id="agent-understood",
                severity=Severity.INFO,
                area="readability",
                title="A browsing AI understands the page",
                evidence=f"Agent's one-line read: “{_quote(rep.summary)}”. Key facts it extracted: "
                + ("; ".join(_quote(f, 80) for f in rep.key_facts[:3]) or "none offered"),
                fix="Keep the opening screen this clear; make sure the key facts stay in static text.",
                source="TinyFish Agent",
            )
        )

    if rep.render_blockers:
        out.append(
            Finding(
                id="render-blockers",
                severity=Severity.HIGH,
                area="access",
                title=f"Reading blocked by: {', '.join(rep.render_blockers[:3])}",
                evidence=f"The browsing agent hit these walls before content: {', '.join(rep.render_blockers)}.",
                fix="Remove or defer the interstitial (cookie/consent/paywall) for first-time crawlers, or at minimum make content reachable without dismissal.",
                source="TinyFish Agent",
            )
        )

    if rep.js_required is True:
        out.append(
            Finding(
                id="agent-js-required",
                severity=Severity.MEDIUM,
                area="readability",
                title="Useful content requires JavaScript to render",
                evidence="The browsing agent confirms content only appears after JS execution — full-browser fetchers cope, lighter AI fetchers and some search crawlers do not.",
                fix="Pre-render the primary content server-side (SSR/SSG).",
                source="TinyFish Agent",
            )
        )

    if rep.rendered_chars is not None and rep.rendered_chars < 500 and not rep.run_error:
        out.append(
            Finding(
                id="agent-thin-render",
                severity=Severity.MEDIUM,
                area="readability",
                title="Rendered page is text-light",
                evidence=f"Agent estimated ~{rep.rendered_chars} visible characters on the rendered page.",
                fix="Add substantive text content: answer paragraph, FAQ, specs/details in static HTML.",
                source="TinyFish Agent",
            )
        )

    return out


# ------------------------------------------------------------------ scoring

# Nominal per-finding point values, used for the per-finding "impact" line and
# kept in lockstep with compute_scores below (a tripwire test asserts this).
_READ_PENALTIES: dict[str, float] = {
    "empty-extraction": 45,
    "js-only-rendering": 30,
    "meta-noindex": 40,
    "agent-not-understood": 12,
    "render-blockers": 10,
    "no-jsonld": 8,
    "jsonld-invalid": 8,
    "jsonld-thin": 4,
    "missing-title": 8,
    "missing-description": 6,
    "weak-title": 4,
    "no-h1": 5,
    "multi-h1": 2,
    "flat-structure": 5,
    "no-semantic-structure": 3,
    "truncated-extraction": 4,
    "thin-content": 6,
    "boilerplate-heavy": 3,
    "no-authorship": 3,
    "missing-og": 2,
    "img-alt-missing": 2,
    "agent-thin-render": 4,
    "agent-js-required": 4,
    "agent-run-failed": 2,
    "llms-txt-missing": 2,
    "no-quotable-stats": 3,
    "no-question-headings": 2,
    "wall-of-text": 2,
    "content-depth-gap": 4,
    "pdf-content": 40,
    "origin-blocked-bot-ua": 2,
}

_VIS_PENALTIES: dict[str, float] = {
    "meta-noindex": 100,  # visibility is zeroed entirely
    "robots-blocks-ai": 45,
    "brand-not-found": 30,
    "not-ranked": 40,
    "low-rank": 18,
    "ranked-top3": -8,  # reward
    "title-missing-query-terms": 8,
    "snippet-offtopic": 6,
    "missing-title": 10,
    "weak-title": 4,
    "missing-description": 5,
    "weak-description": 2,
    "no-canonical": 3,
    "canonical-mismatch": 6,
    "no-sitemap-declared": 4,
    "robots-missing": 4,
    "robots-unreachable": 4,
    "origin-non-200": 60,
    "redirect-chain": 3,
    "missing-og": 2,
    "no-jsonld": 4,
    "content-depth-gap": 6,
    "origin-blocked-bot-ua": 25,
}

# Findings whose readability penalty is total (score set to 0).
_TOTAL_READ_KILL = {"fetch-failed", "origin-unreachable"}


def finding_impact(finding: Finding, *, has_target_query: bool) -> dict[str, Any]:
    """Points this finding is worth if fixed (nominal, isolated contribution)."""
    read_pts = _READ_PENALTIES.get(finding.id, 0.0)
    if finding.id in _TOTAL_READ_KILL:
        read_pts = 100.0
    vis_pts = _VIS_PENALTIES.get(finding.id, 0.0)
    w = 0.6 if has_target_query else 0.7
    overall = round(w * read_pts + (1 - w) * vis_pts)
    if read_pts == 0 and vis_pts == 0:
        overall = 0
    return {
        "readability": round(read_pts),
        "visibility": round(vis_pts),
        "overall": max(overall, 0),
    }


def project_after_fixes(
    findings: list[Finding],
    *,
    has_target_query: bool,
    fix_severities: tuple[str, ...] = (Severity.CRITICAL, Severity.HIGH),
) -> dict[str, Any]:
    """Scores if every finding at the given severities were fixed today."""
    remaining = [f for f in findings if f.severity not in fix_severities]
    return compute_scores(remaining, has_target_query=has_target_query)


def compute_scores(findings: list[Finding], *, has_target_query: bool) -> dict[str, Any]:
    """Deterministic penalty model; every deduction is traceable to a finding id."""
    ids = {f.id for f in findings}
    read = 100.0
    vis = 100.0

    # readability: total kills, then floored penalties (order preserved), then the rest
    if ids & _TOTAL_READ_KILL:
        read = 0.0
    for fid, floor in (
        ("empty-extraction", 10.0),
        ("js-only-rendering", 25.0),
        ("pdf-content", 20.0),
        ("meta-noindex", 5.0),
    ):
        if fid in ids:
            read = max(floor, read - _READ_PENALTIES[fid])
    for fid, amt in _READ_PENALTIES.items():
        if fid in ids and fid not in ("empty-extraction", "js-only-rendering", "pdf-content", "meta-noindex"):
            read -= amt

    # visibility: noindex zeroes it; floored penalties; then the rest
    if "meta-noindex" in ids:
        vis = 0.0
    for fid, floor in (("robots-blocks-ai", 10.0), ("brand-not-found", 15.0)):
        if fid in ids:
            vis = max(floor, vis - _VIS_PENALTIES[fid])
    for fid, amt in _VIS_PENALTIES.items():
        if fid in ids and fid not in ("meta-noindex", "robots-blocks-ai", "brand-not-found"):
            vis -= amt

    read = max(0.0, min(100.0, read))
    vis = max(0.0, min(100.0, vis))
    w_read = 0.6 if has_target_query else 0.7
    overall = round(w_read * read + (1 - w_read) * vis)

    if overall >= 85:
        verdict = "AI-ready: readable by AI tools and visible in search. Keep it fresh."
    elif overall >= 70:
        verdict = "Readable with gaps: an AI can use this page, but the fixes below will materially lift AI-search visibility."
    elif overall >= 45:
        verdict = "Significant barriers: AI tools struggle to read or find this page. Work the critical/high findings first."
    else:
        verdict = "Effectively invisible to AI search: most AI tools cannot read this page or never see it. Start with the critical fixes."

    return {
        "ai_readability_score": round(read),
        "ai_visibility_score": round(vis),
        "overall_score": overall,
        "verdict": verdict,
        "weights": {"readability": w_read, "visibility": round(1 - w_read, 2)},
    }


def prioritize(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (_ORDER.get(f.severity, 9), f.area, f.id))
