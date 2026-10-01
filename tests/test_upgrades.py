"""Tests for the upgrade layer: GEO findings, competitor gap, score impact, projection."""

from __future__ import annotations

from test_findings import _clean_head, _clean_llms, _clean_readability, _clean_robots

from seo_auditor.findings import (
    _READ_PENALTIES,
    _VIS_PENALTIES,
    compute_scores,
    finding_impact,
    findings_content_gap,
    findings_from_readability,
    project_after_fixes,
)
from seo_auditor.readability import ReadabilityReport, _count_stat_sentences, _question_headings
from seo_auditor.report import _access_matrix
from seo_auditor.technical import RobotsReport
from seo_auditor.visibility import VariantProbe, VisibilityReport

# ---------------------------------------------------------------- GEO signal helpers


def test_stat_sentence_counter():
    md = (
        "We cut p95 latency from 40 seconds to 12 seconds across 1,200 runs. "
        "The tool is fast. "
        "Over 30% of users upgraded within a week. "
        "Read more below."
    )
    assert _count_stat_sentences(md) == 2


def test_question_heading_detector():
    html = "<h2>How much does it cost?</h2><h2>Pricing overview</h2><h3>Why teams switch</h3>"
    qs = _question_headings(html)
    assert qs == ["How much does it cost?", "Why teams switch"]


# ---------------------------------------------------------------- GEO findings


def test_no_quotable_stats_fires_on_wordy_page():
    rep = _clean_readability()
    rep.stat_sentences = 0
    out = findings_from_readability(rep)
    f = next(f for f in out if f.id == "no-quotable-stats")
    assert f.severity == "low"
    assert "850 words" in f.evidence


def test_no_quotable_stats_silent_on_thin_page():
    rep = ReadabilityReport(md_words=120, md_chars=500, looks_empty=False, stat_sentences=0)
    out = findings_from_readability(rep)
    assert not any(f.id == "no-quotable-stats" for f in out)


def test_no_question_headings_fires():
    rep = _clean_readability()
    rep.question_headings = []
    out = findings_from_readability(rep)
    f = next(f for f in out if f.id == "no-question-headings")
    assert "6 H2" in f.evidence


def test_wall_of_text_fires():
    rep = _clean_readability()
    rep.longest_paragraph_words = 220
    out = findings_from_readability(rep)
    f = next(f for f in out if f.id == "wall-of-text")
    assert "220 words" in f.evidence


# ---------------------------------------------------------------- competitor gap


def test_content_depth_gap_fires_against_thinner_page():
    rep = VisibilityReport(url="https://me.example/x", target_query="best x")
    rep.brand = "me"
    probe = VariantProbe(
        query="best x",
        total_results=10,
        top_results=[
            {
                "position": 1,
                "title": "Big guide",
                "url": "https://big.example/x",
                "site_name": "big.example",
                "snippet": "s",
            },
            {
                "position": 2,
                "title": "Other",
                "url": "https://other.example/x",
                "site_name": "other.example",
                "snippet": "s",
            },
        ],
    )
    rep.probes = [probe]
    gaps = [
        {
            "url": "https://big.example/x",
            "position": 1,
            "title": "Big guide",
            "benchmark": {"words": 3200, "h2": 9, "has_faq_schema": False},
        }
    ]
    readability = _clean_readability()  # 850 words, 6 H2s
    out = findings_content_gap(rep, readability, _clean_head(), gaps)
    f = next(f for f in out if f.id == "content-depth-gap")
    assert f.severity == "medium"
    assert "3,200 words" in f.evidence
    assert "850 words" in f.evidence
    assert "2,350 words" in f.fix or "2,350" in f.fix  # max(200, 3200-850)


def test_content_gap_silent_when_page_is_deeper():
    rep = VisibilityReport(url="https://me.example/x", target_query="best x")
    rep.brand = "me"
    gaps = [
        {
            "url": "https://small.example/x",
            "position": 1,
            "title": "Small page",
            "benchmark": {"words": 900, "h2": 3, "has_faq_schema": False},
        }
    ]
    out = findings_content_gap(rep, _clean_readability(), _clean_head(), gaps)
    assert out == []


# ---------------------------------------------------------------- impact + projection


def test_every_penalty_table_finding_has_positive_impact():
    rep = _clean_readability()
    rep.description = None  # missing-description
    findings = findings_from_readability(rep)
    f = next(f for f in findings if f.id == "missing-description")
    impact = finding_impact(f, has_target_query=True)
    assert impact["readability"] == _READ_PENALTIES["missing-description"]
    assert impact["visibility"] == _VIS_PENALTIES["missing-description"]
    assert impact["overall"] > 0


def test_projection_reflects_fixed_findings():
    dirty = _clean_readability()
    dirty.description = None
    findings = findings_from_readability(dirty)
    before = compute_scores(findings, has_target_query=True)
    proj = project_after_fixes(findings, has_target_query=True)
    assert proj["ai_readability_score"] > before["ai_readability_score"]
    assert proj["overall_score"] > before["overall_score"]


def test_projection_on_clean_page_is_perfect():
    findings = findings_from_readability(_clean_readability())
    proj = project_after_fixes(findings, has_target_query=True)
    assert proj["overall_score"] == 100


# ---------------------------------------------------------------- penalty-table tripwire


def test_penalty_tables_carry_all_known_finding_ids():
    """Guard: every id emitted by the findings engines must exist in the tables."""

    from seo_auditor.browser_probe import BrowserReport
    from seo_auditor.findings import findings_from_browser, findings_from_technical
    from seo_auditor.technical import LlmsTxtReport

    ids: set[str] = set()

    rep = _clean_readability()
    rep.description = None
    rep.looks_truncated = True
    rep.repeated_boilerplate_ratio = 0.4
    rep.longest_paragraph_words = 200
    rep.question_headings = []
    rep.stat_sentences = 0
    ids |= {f.id for f in findings_from_readability(rep)}
    ids |= {
        f.id for f in findings_from_readability(ReadabilityReport(md_words=10, md_chars=40, looks_empty=True))
    }

    head = _clean_head()
    head.jsonld_blocks = 0
    head.jsonld_types = []
    head.canonical = None
    head.og_title = None
    head.og_description = None
    head.img_missing_alt = 3
    head.status = 500
    robots = RobotsReport()
    robots.exists = False
    robots.status = 404
    llms = LlmsTxtReport()
    ids |= {f.id for f in findings_from_technical(head, robots, llms, rep, "x.example")}

    vis = VisibilityReport(url="https://zzqx.example/p", target_query=None)
    vis.brand = "zzqx"
    ids |= {
        f.id
        for f in __import__(
            "seo_auditor.findings", fromlist=["findings_from_visibility"]
        ).findings_from_visibility(vis)
    }

    ids |= {f.id for f in findings_from_browser(BrowserReport(understood=False, summary="x"))}
    ids |= {f.id for f in findings_from_browser(BrowserReport(run_error="boom"))}

    expected = set(_READ_PENALTIES) | set(_VIS_PENALTIES)
    unknown = ids - expected
    assert not unknown, f"finding ids missing from penalty tables: {sorted(unknown)}"


# ---------------------------------------------------------------- access matrix


def test_access_matrix_open_when_no_robots():
    robots = RobotsReport()
    rows = _access_matrix(robots)
    assert all(allowed for _, _, allowed in rows)


def test_access_matrix_partial_block():
    robots = RobotsReport()
    robots.exists = True
    robots.ai_blocked = ["GPTBot", "ClaudeBot", "PerplexityBot"]
    robots.ai_allowed = ["OAI-SearchBot", "ChatGPT-User", "Google-Extended"]
    rows = dict((label, allowed) for label, _, allowed in _access_matrix(robots))
    assert rows["OpenAI (ChatGPT search/chat)"] is True  # 2 of 3 OpenAI UAs allowed
    assert rows["Anthropic (Claude)"] is False
    assert rows["Perplexity"] is False
    assert rows["Google (Gemini / AI Overviews)"] is True


def test_access_matrix_blocks_everything():
    robots = RobotsReport()
    robots.exists = True
    robots.ai_blocked = list(__import__("seo_auditor.technical", fromlist=["AI_CRAWLERS"]).AI_CRAWLERS)
    rows = _access_matrix(robots)
    assert all(not allowed for _, _, allowed in rows)


# ---------------------------------------------------------------- round-3 hardening
# (found by stress-testing live edge cases: thin page, PDF, non-English, dead domain)


def test_brand_token_rejects_non_brands():
    from seo_auditor.visibility import _brand_token

    assert _brand_token("de.wikipedia.org") == ""  # TLD fragment, not a brand
    assert _brand_token("v2.mysite.io") == ""  # version token
    assert _brand_token("tinyfish.ai") == "tinyfish"
    assert _brand_token("stripe.com") == "stripe"


def test_brand_finding_not_emitted_without_brand():
    from seo_auditor.visibility import VisibilityReport

    vis = VisibilityReport(url="https://de.wikipedia.org/wiki/X", target_query="künstliche intelligenz")
    vis.brand = ""  # probe skipped: no meaningful brand token
    vis.probes = []
    out = __import__("seo_auditor.findings", fromlist=["findings_from_visibility"]).findings_from_visibility(
        vis
    )
    assert not any(f.id == "brand-not-found" for f in out)


def test_pdf_serves_content_but_suppresses_head_findings():
    """A PDF that Fetch CAN extract must not spawn canonical/JSON-LD/OG 'fixes'."""
    from seo_auditor.findings import findings_from_technical

    head = _clean_head()
    head.content_type = "application/pdf"
    head.canonical = None
    head.jsonld_blocks = 0
    head.jsonld_types = []
    head.og_title = None
    head.og_description = None
    head.raw_content_tags = 3  # would normally fire js-only-rendering
    out = findings_from_technical(head, _clean_robots(), _clean_llms(), _clean_readability(), "arxiv.org")
    ids = [f.id for f in out]
    assert "pdf-content" in ids
    assert "no-canonical" not in ids
    assert "no-jsonld" not in ids
    assert "missing-og" not in ids
    assert "js-only-rendering" not in ids
    f = next(f for f in out if f.id == "pdf-content")
    assert f.severity == "critical"
    assert "Content-Type" in f.evidence


def test_pdf_content_in_penalty_tables():
    from seo_auditor.findings import _READ_PENALTIES, compute_scores, finding_impact

    assert "pdf-content" in _READ_PENALTIES
    impact = finding_impact(
        __import__("seo_auditor.findings", fromlist=["Finding"]).Finding(
            id="pdf-content",
            severity="critical",
            area="readability",
            title="t",
            evidence="e",
            fix="f",
            source="s",
        ),
        has_target_query=True,
    )
    assert impact["overall"] > 0
    scores = compute_scores(
        [
            __import__("seo_auditor.findings", fromlist=["Finding"]).Finding(
                id="pdf-content",
                severity="critical",
                area="readability",
                title="t",
                evidence="e",
                fix="f",
                source="s",
            )
        ],
        has_target_query=True,
    )
    assert scores["ai_readability_score"] == 60  # 100 - 40; floor(20) only stops deeper stack-up


def test_bot_ua_retry_semantics():
    """403-then-200 with honest UA => ua_retried True; page must not be judged unreachable
    by head-derived signals while Fetch extracted the same content fine."""
    import seo_auditor.technical as tech

    calls: list[str] = []

    class _R:
        def __init__(self, code: int, ua: str = "browser"):
            self.status_code = code
            self.text = "<html><head><title>t</title></head><body>" + "<p>x</p>" * 20 + "</body></html>"
            self.url = "https://gate.example/wiki/Page"
            self.history = []
            self.headers = {"content-type": "text/html"}
            self._ua = ua

        @property
        def request(self):  # kept for parity with httpx.Response
            class _Req:
                headers = {"user-agent": self._ua}

            return _Req()

    browser_403 = _R(403)

    def fake_get(url, headers=None, timeout=None, follow_redirects=False, **_kw):
        calls.append(url)
        if headers and "TinyFishAuditBot" in headers.get("User-Agent", ""):
            return _R(200, ua="TinyFishAuditBot/1.0")
        return browser_403

    monkey = __import__("pytest").MonkeyPatch()
    try:
        monkey.setattr(tech.httpx, "get", fake_get)
        rep = tech.probe_head("https://gate.example/wiki/Page")
        assert len(calls) == 2  # browser UA, then honest retry
        assert rep.status == 200
        assert rep.ua_retried is True
        assert rep.title == "t"
    finally:
        monkey.undo()


def test_bot_gate_finding_and_penalty_present():
    from seo_auditor.findings import findings_from_technical

    head = _clean_head()
    head.ua_retried = True
    out = findings_from_technical(head, _clean_robots(), _clean_llms(), _clean_readability(), "gate.example")
    ids = [f.id for f in out]
    assert "origin-blocked-bot-ua" in ids
    from seo_auditor.findings import _VIS_PENALTIES

    assert "origin-blocked-bot-ua" in _VIS_PENALTIES


def test_no_bot_gate_finding_on_hard_403_or_clean_page():
    from seo_auditor.findings import findings_from_technical

    head = _clean_head()
    out = findings_from_technical(
        head, _clean_robots(), _clean_llms(), _clean_readability(), "runguide.example"
    )
    assert not any(f.id == "origin-blocked-bot-ua" for f in out)

    head403 = _clean_head()
    head403.status = 403
    head403.ua_retried = True  # attempted, still denied: no "served" claim
    out403 = findings_from_technical(
        head403, _clean_robots(), _clean_llms(), _clean_readability(), "gate.example"
    )
    assert not any(f.id == "origin-blocked-bot-ua" for f in out403)
    f = next(f for f in out403 if f.id == "origin-non-200")
    assert "honest crawler user-agent" in f.evidence  # honesty note attached instead
