"""AI-readability probes via TinyFish Fetch.

Runs two live Fetch probes against the page and measures what an AI extraction
layer actually sees:
  * markdown probe — the clean text/metadata an LLM would be fed
  * html probe     — the semantic elements (headings, lists, tables) that survive extraction

Empirical note (verified against the live API): Fetch's `html` format returns
semantic content only — no <head>, no <meta>, no JSON-LD. That is the point:
it IS the extraction view. Everything in <head> (title/meta/JSON-LD/canonical)
is checked in techincal.py against raw origin HTML instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from . import tinyfish_client as tf

# Words that carry almost no meaning when judging "readable content".
_STOPWORDS = frozenset(
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


@dataclass
class ReadabilityReport:
    # markdown probe (what an LLM is fed)
    md_chars: int = 0
    md_words: int = 0
    md_lexical_ratio: float = 0.0  # fraction of words that are not stopwords
    title: str | None = None
    description: str | None = None
    language: str | None = None
    author: str | None = None
    published_date: str | None = None
    # html probe (semantic structure that survives extraction)
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0
    paragraphs: int = 0
    lists: int = 0
    tables: int = 0
    semantic_tags: list[str] = field(default_factory=list)
    # signals
    looks_empty: bool = False
    looks_truncated: bool = False
    repeated_boilerplate_ratio: float = 0.0
    # GEO signals (what answer engines like to quote)
    stat_sentences: int = 0  # sentences containing a concrete number/stat
    question_headings: list[str] = field(default_factory=list)  # h2/h3 phrased as questions
    longest_paragraph_words: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def _words(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z'-]+", text)


def _lexical_ratio(text: str) -> float:
    words = _words(text.lower())
    if not words:
        return 0.0
    meaningful = sum(1 for w in words if w not in _STOPWORDS)
    return round(meaningful / len(words), 3)


def _looks_empty(md: str) -> bool:
    """Empty enough that an LLM fed this page could not answer anything."""
    return len(_words(md)) < 60


def _looks_truncated(md: str) -> bool:
    """Trailing-fragment heuristics: page likely cut off mid-sentence.

    Conservative: fires only when the tail has NO sentence punctuation at all
    (a normal page ends a paragraph with . ! or ?).
    """
    tail = md.rstrip()[-120:]
    if not tail:
        return False
    return bool(re.search(r"[a-zA-Z]$,", tail) or re.search(r"[a-zA-Z]$", tail)) and not re.search(
        r"[.!?]", tail
    )


def _repeated_boilerplate_ratio(md: str) -> float:
    """Share of non-empty lines that repeat >=3 times (nav/footer/copyright residue)."""
    lines = [ln.strip() for ln in md.splitlines() if len(ln.strip()) >= 8]
    if len(lines) < 4:
        return 0.0
    counts: dict[str, int] = {}
    for ln in lines:
        counts[ln] = counts.get(ln, 0) + 1
    repeated = sum(c for ln, c in counts.items() if c >= 3)
    return round(repeated / len(lines), 3)


_P_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_P_STAT = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?(?:%|percent\b|x\b|hours?\b|days?\b|minutes?\b|seconds?\b|ms\b"
    r"|users?\b|customers?\b|countries\b|million\b|billion\b|thousand\b|k\b|bn\b|years?\b)",
    re.IGNORECASE,
)
_P_HEADING_TEXT = re.compile(r"<h([23])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
_P_PARA_TEXT = re.compile(r"<p\b[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
_P_TAGS = re.compile(r"<[^>]+>")
_QUESTION_STARTS = (
    "what",
    "why",
    "how",
    "when",
    "where",
    "which",
    "who",
    "can",
    "do",
    "does",
    "is",
    "are",
    "should",
)


def _count_stat_sentences(md: str) -> int:
    sentences = _P_SENTENCE_SPLIT.split(md)
    return sum(1 for s in sentences if _P_STAT.search(s))


def _question_headings(html: str) -> list[str]:
    out: list[str] = []
    for _, inner in _P_HEADING_TEXT.findall(html):
        text = _P_TAGS.sub("", inner).strip()
        low = text.lower()
        if text and (text.endswith("?") or low.startswith(_QUESTION_STARTS)):
            out.append(text[:120])
    return out


def _longest_paragraph_words(html: str) -> int:
    longest = 0
    for inner in _P_PARA_TEXT.findall(html):
        text = _P_TAGS.sub(" ", inner)
        longest = max(longest, len(_words(text)))
    return longest


def _semantic_tags(html: str) -> list[str]:
    tags = [
        "main",
        "article",
        "section",
        "nav",
        "header",
        "footer",
        "aside",
        "table",
        "figure",
        "summary",
        "details",
    ]
    present = []
    for t in tags:
        if re.search(rf"<{t}\b", html, re.IGNORECASE):
            present.append(t)
    return present


def probe_page(url: str) -> ReadabilityReport:
    """Run both Fetch probes live against `url` and compute readability signals."""
    rep = ReadabilityReport()
    purpose = tf.AUDIT_PURPOSE

    # --- Probe 1: markdown (the LLM view) ---
    md_results, md_errors = tf.fetch([url], fmt="markdown", purpose=purpose, ttl=0)
    md_text = ""
    if md_errors:
        rep.errors.append(f"fetch markdown: {md_errors[0].get('code', 'error')}")
    if md_results:
        r = md_results[0]
        md = r.text or ""
        md_text = md
        rep.title = r.title
        rep.description = r.description
        rep.language = r.language
        rep.author = r.author
        rep.published_date = r.published_date
        rep.md_chars = len(md)
        rep.md_words = len(_words(md))
        rep.md_lexical_ratio = _lexical_ratio(md)
        rep.looks_empty = _looks_empty(md)
        rep.looks_truncated = _looks_truncated(md)
        rep.repeated_boilerplate_ratio = _repeated_boilerplate_ratio(md)

    # --- Probe 2: html (semantic structure view) ---
    html_results, html_errors = tf.fetch([url], fmt="html", purpose=purpose, ttl=0)
    if html_errors:
        rep.errors.append(f"fetch html: {html_errors[0].get('code', 'error')}")
    if html_results:
        html = html_results[0].text or ""
        rep.h1_count = len(re.findall(r"<h1\b", html, re.IGNORECASE))
        rep.h2_count = len(re.findall(r"<h2\b", html, re.IGNORECASE))
        rep.h3_count = len(re.findall(r"<h3\b", html, re.IGNORECASE))
        rep.paragraphs = len(re.findall(r"<p\b", html, re.IGNORECASE))
        rep.lists = len(re.findall(r"<(ul|ol)\b", html, re.IGNORECASE))
        rep.tables = len(re.findall(r"<table\b", html, re.IGNORECASE))
        rep.semantic_tags = _semantic_tags(html)
        rep.question_headings = _question_headings(html)
        rep.longest_paragraph_words = _longest_paragraph_words(html)

    if rep.md_words:
        rep.stat_sentences = _count_stat_sentences(md_text)

    return rep
