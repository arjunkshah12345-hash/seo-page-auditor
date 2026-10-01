"""Tests for raw-HTML head signal extraction (pure functions, no network)."""

from seo_auditor.technical import _extract_head_signals

HTML_GOOD = """
<html><head>
<title>Best Running Shoes 2026 — RunGuide</title>
<meta name="description" content="We tested 41 shoes. These are the best.">
<link rel="canonical" href="https://runguide.example/shoes">
<meta name="robots" content="index,follow">
<meta property="og:title" content="Best Running Shoes 2026">
<meta property="og:description" content="The full test.">
<meta property="og:image" content="https://runguide.example/og.jpg">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Article","headline":"Best shoes"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"Organization","name":"RunGuide"},
  {"@type":"WebPage","name":"Shoes"}]}
</script>
</head><body>
<h1>Best Running Shoes 2026</h1><h2>Top picks</h2>
<img src="a.jpg" alt="a shoe"><img src="b.jpg">
</body></html>
"""


def test_full_head_extraction():
    s = _extract_head_signals(HTML_GOOD)
    assert s["title"] == "Best Running Shoes 2026 — RunGuide"
    assert s["title_len"] == len(s["title"])
    assert s["meta_description"].startswith("We tested 41 shoes")
    assert s["canonical"] == "https://runguide.example/shoes"
    assert s["robots_meta"] == "index,follow"
    assert s["og_title"] == "Best Running Shoes 2026"
    assert s["og_image"] == "https://runguide.example/og.jpg"
    assert s["h1_count"] == 1
    assert s["h2_count"] == 1
    assert s["img_count"] == 2
    assert s["img_missing_alt"] == 1
    assert set(s["jsonld_types"]) >= {"Article", "Organization", "WebPage"}


def test_meta_content_with_escaped_entities():
    html = '<meta name="description" content=\'It&#39;s "great" — really\'>'
    s = _extract_head_signals(html)
    assert s["meta_description"] == 'It&#39;s "great" — really'


def test_jsonld_invalid_json_captured():
    html = '<script type="application/ld+json">{"@type":"Article", bad}</script>'
    s = _extract_head_signals(html)
    assert s["jsonld_blocks"] == 1
    assert s["jsonld_parse_error"] is not None


def test_no_head_at_all():
    s = _extract_head_signals("<html><body><p>hi</p></body></html>")
    assert s["title"] is None
    assert s["meta_description"] is None
    assert s["canonical"] is None
    assert s["jsonld_blocks"] == 0
