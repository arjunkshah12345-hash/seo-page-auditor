"""Tests for robots.txt parsing and AI-crawler verdicts (pure functions, no network)."""

from seo_auditor.technical import _longest_match, _parse_robots, _ua_verdict

ROBOTS_MIXED = """
User-agent: GPTBot
Disallow: /premium/

User-agent: ClaudeBot
Disallow: /

User-agent: *
Disallow: /admin/
Allow: /admin/public/

Sitemap: https://example.com/sitemap.xml
"""


def test_parse_extracts_star_group():
    rules = _parse_robots(ROBOTS_MIXED, ["GPTBot"])
    assert rules["*"]["disallow"] == ["/admin/"]
    assert rules["*"]["allow"] == ["/admin/public/"]


def test_parse_specific_ua_rules():
    rules = _parse_robots(ROBOTS_MIXED, ["GPTBot", "ClaudeBot"])
    assert rules["gptbot"]["disallow"] == ["/premium/"]
    assert rules["claudebot"]["disallow"] == ["/"]


def test_star_fallback_used_when_ua_has_no_group():
    rules = _parse_robots(ROBOTS_MIXED, ["PerplexityBot"])
    # Parser only fills UA-specific groups; callers merge the star group (see probe_robots)
    assert rules["perplexitybot"] == {"allow": [], "disallow": []}
    # ...and the merge uses longest-match over the star group's rules
    assert _ua_verdict(rules["*"], "/some/page") is True
    assert _ua_verdict(rules["*"], "/admin/private") is False
    assert _ua_verdict(rules["*"], "/admin/public/x") is True  # allow beats disallow


def test_specific_group_beats_star_for_same_ua():
    rules = _parse_robots(ROBOTS_MIXED, ["GPTBot"])
    # GPTBot group only disallows /premium/; star's /admin/ rules do NOT apply to it
    assert _ua_verdict(rules["gptbot"], "/admin/private") is True
    assert _ua_verdict(rules["gptbot"], "/premium/x") is False


def test_longest_match_semantics():
    assert _longest_match(["/admin/"], "/admin/private") == 7
    assert _longest_match(["/admin/", "/admin/public/"], "/admin/public/x") == 14
    assert _longest_match([], "/anything") == 0


def test_disallow_all():
    rules = _parse_robots("User-agent: *\nDisallow: /", ["GPTBot"])
    assert _ua_verdict(rules["*"], "/") is False


def test_comments_and_blank_lines_ignored():
    rules = _parse_robots("# comment\nUser-agent: GPTBot # inline\nDisallow: /x # trailing", ["GPTBot"])
    assert rules["gptbot"]["disallow"] == ["/x"]
