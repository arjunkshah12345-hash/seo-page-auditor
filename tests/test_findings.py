"""Findings-engine tests: measured condition -> expected finding id, severity, evidence, fix."""

from seo_auditor.browser_probe import BrowserReport
from seo_auditor.findings import (
    compute_scores,
    findings_from_browser,
    findings_from_readability,
    findings_from_technical,
    findings_from_visibility,
)
from seo_auditor.readability import ReadabilityReport
from seo_auditor.technical import HeadReport, LlmsTxtReport, RobotsReport
from seo_auditor.visibility import VariantProbe, VisibilityReport


def _clean_readability() -> ReadabilityReport:
    return ReadabilityReport(
        md_chars=5200,
        md_words=850,
        md_lexical_ratio=0.62,
        title="Best Running Shoes 2026 — RunGuide",
        description="We tested 41 shoes over 400 miles. These are the best for every kind of runner.",
        language="en",
        author="RunGuide Test Lab",
        published_date="2026-08-01",
        h1_count=1,
        h2_count=6,
        paragraphs=18,
        lists=3,
        semantic_tags=["main", "article", "section"],
        stat_sentences=5,
        question_headings=["How much should you spend on running shoes?"],
        longest_paragraph_words=62,
    )


def _clean_head() -> HeadReport:
    h = HeadReport()
    h.status = 200
    h.final_url = "https://runguide.example/shoes"
    h.html_bytes = 48000
    h.title = "Best Running Shoes 2026 — RunGuide"
    h.title_len = 36
    h.meta_description = "We tested 41 shoes over 400 miles."
    h.meta_description_len = 34
    h.canonical = "https://runguide.example/shoes"
    h.og_title = "Best Running Shoes 2026"
    h.og_description = "The full test."
    h.og_image = "https://runguide.example/og.jpg"
    h.jsonld_blocks = 1
    h.jsonld_types = ["Article"]
    h.img_count = 6
    h.img_missing_alt = 0
    h.raw_content_tags = 90  # healthy raw HTML: plenty of <p>/<h>/<li>
    return h


def _clean_robots() -> RobotsReport:
    r = RobotsReport()
    r.exists = True
    r.status = 200
    r.ai_allowed = ["GPTBot", "ClaudeBot", "PerplexityBot"]
    r.sitemap_urls = ["https://runguide.example/sitemap.xml"]
    return r


def _clean_llms() -> LlmsTxtReport:
    ll = LlmsTxtReport()
    ll.exists = True
    ll.status = 200
    ll.url = "https://runguide.example/llms.txt"
    return ll


def test_healthy_page_produces_no_action_findings():
    out = findings_from_readability(_clean_readability())
    assert [f.id for f in out] == []
    tech = findings_from_technical(
        _clean_head(), _clean_robots(), _clean_llms(), _clean_readability(), "runguide.example"
    )
    assert [f.id for f in tech] == []


def test_empty_extraction_is_critical_with_concrete_fix():
    rep = ReadabilityReport(md_words=4, md_chars=30, looks_empty=True)
    out = findings_from_readability(rep)
    ids = [f.id for f in out]
    assert "empty-extraction" in ids
    f = next(f for f in out if f.id == "empty-extraction")
    assert f.severity == "critical"
    assert "4 words" in f.evidence
    assert "SSR" in f.fix or "SSG" in f.fix


def test_missing_description_fires_high():
    rep = _clean_readability()
    rep.description = None
    out = findings_from_readability(rep)
    f = next(f for f in out if f.id == "missing-description")
    assert f.severity == "high"
    assert '<meta name="description"' in f.fix


def test_no_jsonld_fix_contains_ready_to_paste_schema():
    head = _clean_head()
    head.jsonld_blocks = 0
    head.jsonld_types = []
    out = findings_from_technical(
        head, _clean_robots(), _clean_llms(), _clean_readability(), "runguide.example"
    )
    f = next(f for f in out if f.id == "no-jsonld")
    assert f.severity == "high"
    assert "application/ld+json" in f.fix
    assert '"@type": "WebPage"' in f.fix
    assert "https://runguide.example" in f.fix


def test_robots_blocking_ai_crawlers_names_them():
    robots = RobotsReport()
    robots.exists = True
    robots.status = 200
    robots.ai_blocked = ["GPTBot", "ClaudeBot"]
    robots.raw_excerpts = {"GPTBot": "allow=[] disallow=['/']", "ClaudeBot": "allow=[] disallow=['/']"}
    out = findings_from_technical(
        _clean_head(), robots, _clean_llms(), _clean_readability(), "runguide.example"
    )
    f = next(f for f in out if f.id == "robots-blocks-ai")
    assert f.severity == "high"
    assert "GPTBot, ClaudeBot" in f.title
    assert "User-agent: GPTBot" in f.fix


def test_noindex_is_critical():
    head = _clean_head()
    head.robots_meta = "noindex,nofollow"
    out = findings_from_technical(
        head, _clean_robots(), _clean_llms(), _clean_readability(), "runguide.example"
    )
    f = next(f for f in out if f.id == "meta-noindex")
    assert f.severity == "critical"


def test_js_only_rendering_detected_from_content_tag_gap():
    head = _clean_head()
    head.raw_content_tags = 3  # shell: a nav + footer, no body content in raw HTML
    out = findings_from_technical(
        head, _clean_robots(), _clean_llms(), _clean_readability(), "runguide.example"
    )
    f = next(f for f in out if f.id == "js-only-rendering")
    assert f.severity == "critical"
    assert "3 content tags" in f.evidence and "850 words" in f.evidence


def test_visibility_not_ranked_names_competitors():
    rep = VisibilityReport(url="https://me.example/shoes", target_query="best running shoes")
    rep.brand = "me"
    p = VariantProbe(
        query="best running shoes",
        total_results=10,
        top_results=[
            {
                "position": i + 1,
                "title": f"Comp {i}",
                "url": f"https://comp{i}.example/x",
                "site_name": f"comp{i}.example",
                "snippet": "s",
            }
            for i in range(10)
        ],
    )
    rep.probes = [p]
    rep.competitors = p.top_results[:5]
    out = findings_from_visibility(rep)
    f = next(f for f in out if f.id == "not-ranked")
    assert f.severity == "high"
    assert "comp0.example" in f.evidence
    assert "best running shoes" in f.fix


def test_brand_missing_fires():
    rep = VisibilityReport(url="https://zzqx.example/page", target_query=None)
    rep.brand = "zzqx"
    rep.probes = []
    rep.notes = []
    out = findings_from_visibility(rep)
    assert any(f.id == "brand-not-found" and f.severity == "high" for f in out)


def test_agent_not_understood_is_high():
    rep = BrowserReport(understood=False, summary="unclear what page is about")
    out = findings_from_browser(rep)
    f = next(f for f in out if f.id == "agent-not-understood")
    assert f.severity == "high"


def test_render_blockers_reported():
    rep = BrowserReport(understood=True, summary="ok", render_blockers=["cookie consent wall"])
    out = findings_from_browser(rep)
    f = next(f for f in out if f.id == "render-blockers")
    assert f.severity == "high"
    assert "cookie consent wall" in f.evidence


def test_scores_drop_with_findings_and_recover_on_clean():
    clean = findings_from_readability(_clean_readability())
    s1 = compute_scores(
        clean
        + findings_from_technical(
            _clean_head(), _clean_robots(), _clean_llms(), _clean_readability(), "x.example"
        ),
        has_target_query=True,
    )
    dirty_rep = _clean_readability()
    dirty_rep.description = None
    dirty_head = _clean_head()
    dirty_head.jsonld_blocks = 0
    dirty_head.jsonld_types = []
    dirty = findings_from_readability(dirty_rep) + findings_from_technical(
        dirty_head, _clean_robots(), _clean_llms(), dirty_rep, "x.example"
    )
    s2 = compute_scores(dirty, has_target_query=True)
    assert s2["ai_readability_score"] < s1["ai_readability_score"]
    assert 0 <= s2["overall_score"] <= 100
    assert s1["verdict"]


def test_noindex_zeroes_visibility_score():
    head = _clean_head()
    head.robots_meta = "noindex"
    findings = findings_from_technical(
        head, _clean_robots(), _clean_llms(), _clean_readability(), "x.example"
    )
    s = compute_scores(findings, has_target_query=True)
    assert s["ai_visibility_score"] == 0
