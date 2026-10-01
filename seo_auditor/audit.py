"""Audit orchestration: URL (+optional query) -> collected probes -> findings -> report."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from .browser_probe import BrowserReport, run_browser_probe
from .findings import (
    Finding,
    compute_scores,
    findings_content_gap,
    findings_from_browser,
    findings_from_readability,
    findings_from_technical,
    findings_from_visibility,
    prioritize,
    project_after_fixes,
)
from .readability import ReadabilityReport, probe_page
from .report import render_markdown
from .technical import HeadReport, LlmsTxtReport, RobotsReport, probe_head, probe_llms_txt, probe_robots
from .visibility import VisibilityReport, collect_content_gaps, registrable_domain, run_visibility


class AuditResult:
    def __init__(
        self,
        url: str,
        target_query: str | None,
        findings: list[Finding],
        scores: dict[str, Any],
        readability: ReadabilityReport,
        head: HeadReport,
        robots: RobotsReport,
        llms: LlmsTxtReport,
        visibility: VisibilityReport,
        browser: BrowserReport | None,
        gaps: list[dict[str, Any]] | None = None,
    ) -> None:
        self.url = url
        self.target_query = target_query
        self.findings = findings
        self.scores = scores
        self.readability = readability
        self.head = head
        self.robots = robots
        self.llms = llms
        self.visibility = visibility
        self.browser = browser
        self.gaps = gaps or []

    @property
    def markdown(self) -> str:
        return render_markdown(
            self.url,
            self.findings,
            self.scores,
            readability=self.readability,
            head=self.head,
            robots=self.robots,
            llms=self.llms,
            visibility=self.visibility,
            browser=self.browser,
            gaps=self.gaps,
            generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "target_query": self.target_query,
            "scores": self.scores,
            "findings": [f.to_dict() for f in self.findings],
            "readability": self.readability.to_dict(),
            "origin": self.head.to_dict(),
            "robots": self.robots.to_dict(),
            "llms_txt": self.llms.to_dict(),
            "visibility": self.visibility.to_dict(),
            "browser_agent": self.browser.to_dict() if self.browser else None,
            "competitor_benchmarks": self.gaps,
        }

    def json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)


def run_audit(
    url: str,
    target_query: str | None = None,
    *,
    with_browser: bool = True,
    location: str | None = None,
    language: str | None = None,
) -> AuditResult:
    """Run the full live audit. Raises tf.TinyFishError only if Search itself is unusable."""
    # 1. TinyFish Fetch: what an AI extraction layer sees (2 probes: markdown + html)
    readability = probe_page(url)

    # 2. Origin-side checks: raw HTML, robots.txt, llms.txt (what crawlers are told)
    head = probe_head(url)
    robots = probe_robots(url)
    llms = probe_llms_txt(url)

    # 3. TinyFish Search: visibility for the target query + brand
    page_title = readability.title or head.title
    visibility = run_visibility(
        url,
        target_query,
        page_title=page_title,
        location=location,
        language=language,
    )  # 3b. TinyFish Fetch: benchmark the pages outranking the audited one (live)
    gaps: list[dict[str, Any]] = []
    if target_query:
        gaps = [g.to_dict() for g in collect_content_gaps(visibility)]

    # 4. TinyFish Agent: browsing-AI comprehension (single metered run)
    browser: BrowserReport | None = None
    if with_browser:
        browser = run_browser_probe(url)

    # 5. Findings + scores
    findings: list[Finding] = []
    findings += findings_from_readability(readability)
    findings += findings_from_technical(head, robots, llms, readability, _registrable(url))
    findings += findings_from_visibility(visibility)
    if gaps:
        findings += findings_content_gap(visibility, readability, head, gaps)
    if browser is not None:
        findings += findings_from_browser(browser)
    findings = prioritize(findings)
    scores = compute_scores(findings, has_target_query=bool(target_query))
    projection = project_after_fixes(findings, has_target_query=bool(target_query))
    scores["projected_after_fixes"] = {
        k: projection[k] for k in ("overall_score", "ai_readability_score", "ai_visibility_score")
    }

    return AuditResult(
        url, target_query, findings, scores, readability, head, robots, llms, visibility, browser, gaps
    )


def _registrable(url: str) -> str:
    return registrable_domain((urlsplit(url).netloc or "").lower())
