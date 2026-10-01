"""Markdown report rendering: the artifact a site owner acts on."""

from __future__ import annotations

from typing import Any

from .browser_probe import BrowserReport
from .findings import Finding, Severity, finding_impact
from .readability import ReadabilityReport
from .technical import HeadReport, LlmsTxtReport, RobotsReport
from .visibility import VisibilityReport

_SEV_ICON = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}

_AREA_LABEL = {
    "readability": "AI readability",
    "access": "AI crawler access",
    "visibility": "Search visibility",
    "structure": "Machine-readable structure",
    "authority": "Authority & provenance",
}


def _yesno(v: bool | None) -> str:
    return {True: "yes", False: "no", None: "n/a"}[v]


# Compact grouping of AI crawlers into the access matrix.
_MATRIX_ROWS: list[tuple[str, str, list[str]]] = [
    ("OpenAI (ChatGPT search/chat)", "search + user-initiated", ["OAI-SearchBot", "ChatGPT-User", "GPTBot"]),
    ("Anthropic (Claude)", "search + assistants", ["ClaudeBot", "Claude-Web", "anthropic-ai"]),
    ("Perplexity", "answer engine", ["PerplexityBot"]),
    ("Google (Gemini / AI Overviews)", "grounding data", ["Google-Extended"]),
    ("Meta (Meta AI)", "training + assistants", ["meta-externalagent"]),
    ("ByteDance / CC / Apple", "other AI crawlers", ["Bytespider", "CCBot", "Applebot-Extended"]),
]


def _access_matrix(robots: RobotsReport) -> list[tuple[str, str, bool]]:
    verdict: dict[str, bool] = {}
    for crawler in robots.ai_blocked:
        verdict[crawler] = False
    for crawler in robots.ai_allowed:
        verdict.setdefault(crawler, True)
    rows: list[tuple[str, str, bool]] = []
    for label, role, crawlers in _MATRIX_ROWS:
        known = [verdict[c] for c in crawlers if c in verdict]
        if not known:
            rows.append((label, role, True))  # no rules at all => open
        else:
            rows.append((label, role, any(known)))
    return rows


def render_markdown(
    url: str,
    findings: list[Finding],
    scores: dict[str, Any],
    *,
    readability: ReadabilityReport,
    head: HeadReport,
    robots: RobotsReport,
    llms: LlmsTxtReport,
    visibility: VisibilityReport,
    browser: BrowserReport | None,
    gaps: list[dict[str, Any]] | None = None,
    generated_at: str = "",
) -> str:
    L: list[str] = []
    ap = L.append

    ap(f"# AI Search & Readability Audit — {url}")
    ap("")
    ap(f"*Generated {generated_at} · live page audit via TinyFish Search + Fetch + Agent*")
    ap("")
    ap("## Scores")
    ap("")
    ap("| Overall | AI readability | AI visibility |")
    ap("|---:|---:|---:|")
    ap(
        f"| **{scores['overall_score']}/100** | {scores['ai_readability_score']}/100 "
        f"| {scores['ai_visibility_score']}/100 |"
    )
    ap("")
    ap(f"**Verdict:** {scores['verdict']}")
    ap("")
    proj = scores.get("projected_after_fixes")
    action_items = [f for f in findings if f.severity in (Severity.CRITICAL, Severity.HIGH)]
    if proj and action_items and proj["overall_score"] > scores["overall_score"]:
        ap(
            f"**After fixing the list below:** projected overall **{proj['overall_score']}/100** "
            f"(readability {proj['ai_readability_score']}, visibility {proj['ai_visibility_score']}) — "
            f"a gain of **+{max(proj['overall_score'] - scores['overall_score'], 0)} points** from same-day fixes."
        )
        ap("")

    # Executive summary: the same-day action list with point impact
    if action_items:
        ap("## Fix today")
        ap("")
        for i, f in enumerate(action_items, 1):
            impact = finding_impact(f, has_target_query=bool(visibility.target_query))
            ap(f"{i}. **{f.title}** (worth ~+{impact['overall']} pts) — {_AREA_LABEL.get(f.area, f.area)}")
        ap("")

    # AI crawler access matrix
    ap("## Can AI crawlers read this page?")
    ap("")
    ap("| System | Role | Access |")
    ap("|---|---|:---:|")
    for label, role, allowed in _access_matrix(robots):
        ap(f"| {label} | {role} | {'✅ allowed' if allowed else '❌ blocked'} |")
    ap("")

    ap("## Findings (prioritized)")
    ap("")
    current_sev = None
    for f in findings:
        if f.severity != current_sev:
            current_sev = f.severity
            icon = _SEV_ICON.get(f.severity, "•")
            ap(f"### {icon} {f.severity.upper()}")
            ap("")
        ap(f"#### {_AREA_LABEL.get(f.area, f.area)} · {f.title}")
        ap("")
        ap(f"- **Evidence:** {f.evidence}")
        fix_lines = f.fix.splitlines()
        ap(f"- **Fix:** {fix_lines[0]}")
        for line in fix_lines[1:]:
            ap(f"  {line}")
        impact = finding_impact(f, has_target_query=bool(visibility.target_query))
        if impact["overall"] > 0:
            ap(
                f"- *Impact if fixed: ~+{impact['overall']} pts overall (readability +{impact['readability']}, "
                f"visibility +{impact['visibility']}) · Source: {f.source}*"
            )
        else:
            ap(f"- *Source: {f.source}*")
        ap("")

    # ---- Measured data appendix
    ap("## Measured data")
    ap("")

    ap("### TinyFish Fetch — what an AI extraction layer sees")
    ap("")
    ap(f"- extracted **{readability.md_words} words** / {readability.md_chars:,} chars of markdown")
    ap(f"- title: {readability.title or '—'}")
    ap(f"- description: {readability.description or '—'}")
    ap(
        f"- language: {readability.language or '—'} · author: {readability.author or '—'} · published: {readability.published_date or '—'}"
    )
    ap(
        f"- structure in extracted HTML: {readability.h1_count} H1 · {readability.h2_count} H2 · "
        f"{readability.h3_count} H3 · {readability.paragraphs} <p> · {readability.lists} lists · {readability.tables} tables"
    )
    ap(f"- semantic landmarks: {', '.join(readability.semantic_tags) or 'none detected'}")
    ap(
        f"- signals: empty={_yesno(readability.looks_empty)}"
        f" · truncated={_yesno(readability.looks_truncated)}"
        f" · boilerplate-lines={readability.repeated_boilerplate_ratio:.0%}"
    )
    ap(
        f"- GEO signals: {readability.stat_sentences} sentence(s) with concrete stats"
        f" · {len(readability.question_headings)} question-phrased heading(s)"
        f" · longest paragraph {readability.longest_paragraph_words} words"
    )
    if readability.errors:
        ap(f"- fetch errors: {'; '.join(readability.errors)}")
    ap("")

    ap("### TinyFish Fetch — extraction gap (HTML view)")
    ap("")
    ap(
        f"- Raw server HTML carries {head.raw_content_tags} content tags (<p>/<h>/<li>/<td>), while the "
        f"browser-rendered extraction saw {readability.h1_count + readability.h2_count + readability.paragraphs} "
        "content elements — the gap is what only renders via JavaScript."
    )
    ap("")

    ap("### Origin HTML — what search & AI crawlers get")
    ap("")
    ap(f"- HTTP {head.status} · {head.html_bytes:,} bytes raw HTML · redirect={_yesno(head.redirect)}")
    extras = []
    if head.content_type:
        extras.append(f"content-type: {head.content_type}")
    if head.ua_retried and head.status == 200:
        extras.append("served only after an honest bot user-agent retry")
    if extras:
        ap("- " + " · ".join(extras))
    ap(f"- `<title>` ({head.title_len} chars): {head.title or '—'}")
    ap(f"- meta description ({head.meta_description_len} chars): {head.meta_description or '—'}")
    ap(f"- canonical: {head.canonical or '—'}")
    ap(f"- meta robots: {head.robots_meta or '—'}")
    ap(f"- og:title: {head.og_title or '—'} · og:image: {'present' if head.og_image else '—'}")
    ap(
        f"- JSON-LD: {head.jsonld_blocks} block(s), types: {', '.join(head.jsonld_types) or '—'}"
        + (f" · parse error: {head.jsonld_parse_error}" if head.jsonld_parse_error else "")
    )
    ap(f"- raw HTML headings: {head.h1_count} H1 · {head.h2_count} H2")
    ap(
        f"- images: {head.img_count} total · {head.img_missing_alt} missing alt · hreflang tags: {head.hreflang_count}"
    )
    ap("")

    ap("### robots.txt — AI crawler access")
    ap("")
    if robots.exists:
        ap(f"- AI crawlers allowed on this path: {', '.join(robots.ai_allowed) or 'none'}")
        if robots.ai_blocked:
            ap(f"- **AI crawlers blocked:** {', '.join(robots.ai_blocked)}")
        if robots.search_blocked:
            ap(f"- **Search crawlers blocked:** {', '.join(robots.search_blocked)}")
        ap(f"- sitemaps declared: {len(robots.sitemap_urls)}")
    else:
        ap(f"- robots.txt: {'not found' if robots.status else 'unreachable'} (HTTP {robots.status})")
    ap("")

    ap("### llms.txt")
    ap("")
    if llms.exists:
        ap(f"- found at `{llms.url}` · {llms.bytes:,} bytes · {llms.sections} sections · {llms.links} links")
    else:
        ap(f"- not found (HTTP {llms.status})")
    ap("")

    ap("### TinyFish Search — visibility for the target query")
    ap("")
    for p in visibility.probes:
        rank = f"#{p.page_rank}" if p.page_rank else "not in top-10"
        ap(f"- query “{p.query}” → this page: **{rank}** (of {p.total_results} results)")
        if p.page_entry_title:
            ap(f"  - shown as: “{p.page_entry_title}”")
            if p.page_entry_snippet:
                ap(f"  - snippet: “{p.page_entry_snippet}”")
    if visibility.competitors:
        ap("")
        ap("| # | Who outranks / ranks alongside | URL |")
        ap("|---|---|---|")
        for c in visibility.competitors[:5]:
            ap(f"| {c['position']} | {c['title']} ({c['site_name']}) | {c['url']} |")
    for note in visibility.notes:
        ap(f"- note: {note}")
    ap("")

    if gaps:
        ap("### TinyFish Fetch — competitor benchmark (pages outranking it, fetched live)")
        ap("")
        ap("| # | Competitor page | Words extracted | H2 sections |")
        ap("|---|---|---:|---:|")
        for g in gaps[:3]:
            b = g["benchmark"]
            ap(f"| {g['position']} | {g['title']} — `{g['url']}` | {b['words']:,} | {b['h2']} |")
        ap(f"| — | **This page** | {readability.md_words:,} | {readability.h2_count} |")
        ap("")

    if browser is not None:
        ap("### TinyFish Agent — browsing-AI comprehension probe")
        ap("")
        if browser.run_error and browser.understood is None:
            ap(f"- run failed: {browser.run_error}")
        else:
            ap(f"- page understood: {_yesno(browser.understood)}")
            if browser.summary:
                ap(f"- one-line read: “{browser.summary}”")
            if browser.key_facts:
                ap("- key facts extracted:")
                for kf in browser.key_facts:
                    ap(f"  - {kf}")
            ap(
                f"- js_required={_yesno(browser.js_required)} · rendered_chars="
                f"{browser.rendered_chars if browser.rendered_chars is not None else 'n/a'} · "
                f"nav_links={browser.nav_links if browser.nav_links is not None else 'n/a'}"
            )
            if browser.render_blockers:
                ap(f"- render blockers: {', '.join(browser.render_blockers)}")
        ap("")

    ap("---")
    ap("")
    ap(
        "*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page "
        "twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and "
        "llms.txt are checked for what search/AI crawlers are told; "
        "[TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target "
        "query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens "
        "the page in a real browser to test whether a browsing AI can understand it.*"
    )
    return "\n".join(L) + "\n"
