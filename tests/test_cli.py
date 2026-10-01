"""CLI tests: --fail-under score gate and report file writing (audit mocked)."""

from __future__ import annotations

from dataclasses import dataclass, field

from seo_auditor import cli


@dataclass
class _StubResult:
    scores: dict
    findings: list = field(default_factory=list)
    markdown: str = "# report\n"

    def __post_init__(self):
        self.scores.setdefault("ai_readability_score", self.scores["overall_score"])
        self.scores.setdefault("ai_visibility_score", self.scores["overall_score"])
        self.scores.setdefault("verdict", "ok")

    def json(self) -> str:
        return "{}"


def _run(monkeypatch, tmp_path, argv, overall):
    """Run cli.main with run_audit stubbed to return a fixed overall score."""
    stub = _StubResult(scores={"overall_score": overall})
    calls: dict = {}

    def fake_run_audit(url, query, **kwargs):
        calls["url"] = url
        calls["query"] = query
        calls["kwargs"] = kwargs
        return stub

    monkeypatch.setattr(cli, "run_audit", fake_run_audit)
    out = tmp_path / "report.md"
    rc = cli.main([*argv[:2], "-o", str(out)] + argv[2:])
    return rc, calls, out


def test_fail_under_passes(monkeypatch, tmp_path):
    rc, calls, out = _run(monkeypatch, tmp_path, ["https://x.example/", "q"], 75)
    assert rc == 0
    assert out.read_text() == "# report\n"
    assert calls["url"] == "https://x.example/"
    assert calls["query"] == "q"


def test_fail_under_gates(monkeypatch, tmp_path):
    rc, _calls, _out = _run(monkeypatch, tmp_path, ["https://x.example/", "q", "--fail-under", "70"], 69)
    assert rc == 1


def test_fail_under_boundary(monkeypatch, tmp_path):
    rc, _calls, _out = _run(monkeypatch, tmp_path, ["https://x.example/", None, "--fail-under", "70"], 70)
    assert rc == 0


def test_url_scheme_autocomplete(monkeypatch, tmp_path):
    rc, calls, _out = _run(monkeypatch, tmp_path, ["x.example/page", None], 90)
    assert rc == 0
    assert calls["url"] == "https://x.example/page"


def test_no_browser_flag_passthrough(monkeypatch, tmp_path):
    rc, calls, _out = _run(monkeypatch, tmp_path, ["https://x.example/", None, "--no-browser"], 90)
    assert rc == 0
    assert calls["kwargs"]["with_browser"] is False
